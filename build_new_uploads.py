"""Stage the uploads of 12-13 November (intake assets not in the earlier manifest) for the build.
Named city and castle repaints replace the older primary for their site; large ground paintings become terrain tiles;
small cut-outs join the generic pools; sheets, concepts and water pieces are recorded with the reason they stay off.
Run after build_sprite_assets.py and build_generic_assets.py, before build_fallback_assets.py.
Usage: python3 build_new_uploads.py <new-root> <old-root>"""
import json, os, sys, re
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
NEW = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/w/main-1113"
OLD = sys.argv[2] if len(sys.argv) > 2 else "/home/claude/w/main-1112"
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
man = json.load(open(os.path.join(NEW, "data/sprites/automated-intake/manifest.json")))["assets"]
old = {a["id"] for a in json.load(open(os.path.join(OLD, "data/sprites/automated-intake/manifest.json")))["assets"]}
new = [a for a in man if a["id"] not in old]
S = [r for r in json.load(open(os.path.join(A, "sprites.json"))) if not r.get("generic")]
ALT = json.load(open(os.path.join(A, "sprite_alternates.json")))
G = json.load(open(os.path.join(A, "generic2.json")))
BIG = {"rich": [], "aeg": [], "past": [], "waste": [], "flat": []}
log = []

SITE = [("chateau_pelerin", "chateau-pelerin"), ("margat_review", "margat"), ("montfort_review", "montfort"), ("safed_review", "safed"),
        ("ascalon_1180", "ascalon"), ("caesarea_1180", "caesarea"), ("gaza_1180", "gaza"), ("jaffa_1180", "jaffa"), ("acre_1180", "acre"),
        ("beirut_1180", "beirut"), ("sidon_1180", "sidon"), ("tyre_1180", "tyre"), ("batroun_1180", "batroun"), ("byblos_1180", "byblos"),
        ("tartus_1180", "tortosa"), ("tripoli_1180", "tripoli"), ("constantinople-1180-south-pov", "constantinople"),
        ("alexandria-1180-north", "alexandria"), ("chalcedon-1180-south-view", "chalcedon"), ("kyrenia_north_harbor", "kyrenia"),
        ("antioch-1180-south-pov-review", "antioch"), ("cairo-medieval-nile-review", "cairo"), ("corinth-inland-review", "corinth")]


def load(a):
    return Image.open(os.path.join(NEW, "data/sprites", a["asset"])).convert("RGBA")


def clean(im):
    """Keep the main painted piece: drop stray fragments of neighbouring cut-outs."""
    al = np.asarray(im)[..., 3] > 24
    lab, n = ndi.label(ndi.binary_dilation(al, iterations=2))
    if n > 1:
        sz = ndi.sum(al, lab, range(1, n + 1)); keep = [i + 1 for i, s in enumerate(sz) if s >= 0.12 * sz.max()]
        if len(keep) < n:
            arr = np.asarray(im).copy(); arr[~np.isin(lab, keep)] = 0; im = Image.fromarray(arr, "RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    return im.crop(bb) if bb else im


def water_frac(im):
    a = np.asarray(im).astype(np.int32); r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    op = al > 60
    w = op & (b > r + 18) & (b > g - 12) & (b > 90)
    return float(w.sum()) / max(1, op.sum())


def arch(a):
    p = a["source"]["path"]
    return p.split("_zip_extract/")[1].split("/")[0] if "_zip_extract/" in p else "loose"


def off(a, why):
    G.append(dict(src="data/sprites/" + a["asset"], file="", cls="off", reason=why)); log.append((a["name"], "off", why))


def generic(a, cls, maxw=700):
    im = clean(load(a))
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    fn = re.sub(r"[^a-z0-9_.-]", "_", os.path.basename(a["asset"]).lower())
    im.save(os.path.join(A, "generic2", fn))
    G.append(dict(src="data/sprites/" + a["asset"], file=fn, cls=cls, w=im.width, h=im.height, reason="")); log.append((a["name"], cls, ""))


def big(a, pool):
    im = clean(load(a)); im.thumbnail((1100, 1100), Image.LANCZOS)
    nm = "up-" + re.sub(r"[^a-z0-9_-]", "_", os.path.splitext(os.path.basename(a["asset"]))[0].lower())
    im.save(os.path.join(A, "terrain", nm + ".png"))
    BIG[pool].append(nm)
    G.append(dict(src="data/sprites/" + a["asset"], file="", cls="tile:" + pool, tile=nm, reason="")); log.append((a["name"], "tile:" + pool, ""))


for a in new:
    n = a["name"].lower(); ar = arch(a); im0 = load(a); w = im0.width
    al = np.asarray(im0)[..., 3]
    if any(k in n for k in ("sheet", "master")) or (al < 16).mean() < 0.02 or n.startswith("a_detailed"):
        off(a, "source sheet or opaque master registered by intake as one image: reference only"); continue
    if n in ("rural smithy and forge", "tannery and dyeing yard"):
        off(a, "failed transparency: a checkerboard is painted into the background; needs re-export with real alpha"); continue
    hit = next((s for k, s in SITE if k in n), None)
    if hit:
        rec = next((r for r in S if str(r["site"]) == hit), None)
        if rec is None:
            off(a, "named repaint with no matching site record"); continue
        im = clean(im0); maxw = 1300 if rec.get("units", 512) >= 1000 else 900
        if im.width > maxw:
            im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
        fn = os.path.basename(a["asset"]); im.save(os.path.join(A, "sprites", fn))
        ALT.append(dict(path=rec["variant"], site=hit, reason="superseded by the 12-13 November repaint data/sprites/" + a["asset"]))
        rec.update(file=fn, w=im.width, h=im.height, variant="data/sprites/" + a["asset"], source="upload 12-13 Nov", review=True)
        log.append((a["name"], "site:" + hit, "")); continue
    if "repaint-required" in n or "repaint_required" in n:
        off(a, "marked repaint-required by its own file name"); continue
    if "tortosa-1180-coastal-review" in n:
        off(a, "alternate of Tortosa; the south-view repaint of the same batch series is used"); continue
    if "greek_islands" in ar:
        off(a, "concept island with no registered coordinate box"); continue
    if n.endswith("-concept") and "orientation_8" in ar:
        off(a, "orientation concept sketch (768 px wide strip), superseded by the south-view repaints"); continue
    if any(k in n for k in ("coastal-port-concept", "coastal-harbor-concept")) or n in ("generic_scene_01", "generic_scene_02", "generic_scene_03"):
        generic(a, "fb:harbour_town", 800); continue
    if "upland-castle-concept" in n:
        generic(a, "fb:fort", 700); continue
    if any(k in n for k in ("upland-town-concept", "inland-hilltown-concept")) or n in ("generic_scene_05", "generic_scene_06"):
        generic(a, "fb:town", 800); continue
    if n == "generic_scene_04":
        off(a, "generic scene with pyramids: reads as Cairo, which has its own painting"); continue
    wf = water_frac(im0)
    delta = "nile" in n or "delta" in n
    if w >= 1500:
        if wf > 0.035 and not delta:
            off(a, "large landscape with a painted river or marsh (%.0f%% water): needs aligning to a real river" % (wf * 100)); continue
        if delta:
            if wf > 0.06:
                off(a, "large Delta landscape with painted channels (%.0f%% water): would clash with the drawn Nile branches" % (wf * 100)); continue
            big(a, "flat"); continue
        if any(k in n for k in ("greek", "aegean", "island", "greenwood")):
            big(a, "aeg"); continue
        if any(k in n for k in ("syria_steppe", "sinai", "egyptian_desert", "gravel_steppe", "coastal_dune")):
            big(a, "waste"); continue
        if any(k in n for k in ("foothill", "maquis", "scrub", "steppe", "taurus", "anatolian", "limestone", "escarp", "coastal_margi", "forest", "ridge", "mountain")):
            big(a, "past"); continue
        big(a, "rich"); continue
    # small cut-outs
    if any(k in n for k in ("alpine", "taurus")) and "waterfall" not in n:
        generic(a, "patchd", 520); continue
    if delta:
        generic(a, "delta", 520); continue
    if any(k in n for k in ("coast", "shore", "littoral", "cliff", "rock_arch", "saline")) or (wf > 0.05 and any(k in n for k in ("11_greek",))):
        off(a, "coast or stream piece (%.0f%% water): needs registering to real shoreline or river" % (wf * 100)); continue
    if wf > 0.04 or any(k in n for k in ("marsh", "reed", "river", "channel", "wetland", "floodplain", "waterfall")):
        off(a, "river, reed or marsh piece (%.0f%% water): needs aligning to real water" % (wf * 100)); continue
    if any(k in n for k in ("woodland", "wooded", "forest", "cedar", "pine", "copse")):
        generic(a, "patchw", 520); continue
    if any(k in n for k in ("olive", "orchard", "vineyard", "citrus", "pasture", "meadow", "cultivat", "terrace", "11_greek")):
        generic(a, "patchg", 520); continue
    if any(k in n for k in ("dune", "oasis", "arid", "plateau", "escarpment", "sinai", "badlands", "volcanic", "basalt", "dry_")):
        generic(a, "patcha", 520); continue
    generic(a, "patchd", 520)

json.dump(S, open(os.path.join(A, "sprites.json"), "w"), indent=1)
json.dump(ALT, open(os.path.join(A, "sprite_alternates.json"), "w"), indent=1)
json.dump(G, open(os.path.join(A, "generic2.json"), "w"), indent=1)
json.dump(BIG, open(os.path.join(A, "bigtiles.json"), "w"), indent=1)
json.dump(log, open(os.path.join(HERE, "out", "new_uploads_log.json"), "w"), indent=1)
import collections
print(len(new), "new assets:", dict(collections.Counter(c.split(":")[0] if c.startswith("site") else c for _, c, _ in log)))
print({k: len(v) for k, v in BIG.items()})
