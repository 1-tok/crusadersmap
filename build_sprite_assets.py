"""Build assets/sprites.json and trimmed sprite PNGs from the repository checkout.
Sources, in order: data/sprites/catalog.json (best selection_priority per site), then every located named-site
record in data/manifests/CLAUDE-BUILD-IMAGE-LEDGER.json for sites the catalogue does not cover.
One primary variant per site. Usage: python3 build_sprite_assets.py <repo-root>"""
import json, os, sys, shutil, math, re
from PIL import Image
ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/w/main-1112"
SRC = os.path.join(ROOT, "data", "sprites")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SPAN = (1095, 1571)
cat = json.load(open(os.path.join(SRC, "catalog.json")))["assets"]
best = {}
for a in cat:
    if a.get("longitude") is None and not a.get("coordinates"):
        continue
    k = a["site_id"]
    if k not in best or a.get("selection_priority", 0) > best[k].get("selection_priority", 0):
        best[k] = a
shutil.rmtree(os.path.join(OUT, "sprites"), ignore_errors=True); os.makedirs(os.path.join(OUT, "sprites"))
recs = []; alts = []


def region_of(lon, lat, r=None):
    if r in ("main", "aegean", "delta"):
        return r
    if 29.55 < lon < 32.65 and 29.85 < lat < 31.68:
        return "delta"
    if lon < 30.4 and lat > 34.7:
        return "aegean"
    return "main"


def add(name, site, catg, region, lon, lat, path, units, variant, source, year, review=True):
    im = Image.open(path).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    if not bb:
        return False
    im = im.crop(bb)
    maxw = 1300 if units >= 1000 else 900
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    fn = os.path.basename(path)
    im.save(os.path.join(OUT, "sprites", fn))
    recs.append(dict(name=name, site=site, cat=catg, region=region, lon=lon, lat=lat, file=fn, w=im.width, h=im.height,
                     units=units, variant=variant, review=review, source=source, year=year))
    return True


for k, a in best.items():
    lon, lat = a.get("longitude"), a.get("latitude")
    if lon is None:
        lon, lat = a["coordinates"]
    p = os.path.join(SRC, a["asset"])
    if not os.path.exists(p):
        print("missing", a["asset"]); continue
    av = a.get("availability") or {}
    add(a["name"], k, a["category"], a.get("map_region", "main"), lon, lat, p, a.get("display_width_units", 512),
        "data/sprites/" + a["asset"], "catalog", av.get("from_year"))
for a in cat:
    if a["site_id"] in best and best[a["site_id"]] is not a and (a.get("longitude") is not None or a.get("coordinates")):
        alts.append(dict(path="data/sprites/" + a["asset"], site=a["site_id"], reason="alternate variant; primary is " + best[a["site_id"]]["asset"]))

led = json.load(open(os.path.join(ROOT, "data", "manifests", "CLAUDE-BUILD-IMAGE-LEDGER.json")))["records"]
ORDER = {"base-1180": 0, "review-1180": 1, "review-multi-period": 2, "automated-intake": 3, "review-1250": 4, "review-1245": 5}
have_files = {r["variant"] for r in recs} | {a["path"] for a in alts}
cands = [r for r in led if r.get("geometry") and r["kind"] in ("named-site", "named-candidate") and r.get("file_exists")
         and r["source"] in ORDER]
cands.sort(key=lambda r: (ORDER[r["source"]], r["path"]))


def norm(s):
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


taken = {}                                    # site key -> record already chosen
for r in recs:
    taken[norm(r["site"])] = r
for r in cands:
    if r["path"] in have_files:
        continue
    lon, lat = r["geometry"]
    key = norm(r.get("matched_site_id") or r["label"])
    near = [q for q in recs if math.hypot(q["lon"] - lon, q["lat"] - lat) < 0.008]
    if key in taken or near:
        prim = taken.get(key) or near[0]
        alts.append(dict(path=r["path"], site=r.get("matched_site_id") or r["label"], reason="alternate variant; primary is " + prim["variant"]))
        have_files.add(r["path"]); continue
    yr = r.get("depiction_year")
    if yr and not (SPAN[0] <= yr <= SPAN[1]):
        alts.append(dict(path=r["path"], site=r["label"], reason="depiction year %s outside the map span" % yr)); continue
    if add(r["label"], r.get("matched_site_id") or key, "review", region_of(lon, lat, r.get("region")), lon, lat,
           os.path.join(ROOT, r["path"]), 512, r["path"], r["source"], yr):
        taken[key] = recs[-1]; have_files.add(r["path"])
# Geographic recovery: independently sourced map-review anchors for named
# candidates previously absent from the 226-item technical-intake geography.
# This opt-in file does NOT imply production or period artwork approval.
geo_recovery = os.path.join(SRC, "placements-geographic-recovery-1095-1571.json")
if os.path.isfile(geo_recovery):
    recovered = json.load(open(geo_recovery))
    for p in recovered.get("placements", []):
        if not p.get("review_only") or p.get("production_approved") is not False:
            continue
        if not p.get("coordinate_source_url"):
            continue
        lon, lat = p["coordinates"]
        key = p["site_id"]
        path = os.path.join(ROOT, p["asset_path"])
        if not os.path.isfile(path):
            print("unavailable geographic recovery asset:", p["asset_path"]); continue
        if any(math.hypot(q["lon"] - lon, q["lat"] - lat) < 0.016 for q in recs):
            print("skip duplicate map position for recovered site:", p["name"]); continue
        if add(p["name"], key, p["category"], p.get("map_region", "main"),
               lon, lat, path, p.get("display_width_units", 300),
               p["asset_path"], "geo-recovery-review", p.get("approximate_year"),
               review=True):
            print("new geographically sourced map-review sprite:", p["name"])
json.dump(recs, open(os.path.join(OUT, "sprites.json"), "w"), indent=1)
json.dump(alts, open(os.path.join(OUT, "sprite_alternates.json"), "w"), indent=1)
print(len(recs), "primary sprites;", len(alts), "alternates")
