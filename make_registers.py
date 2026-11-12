"""Registers for the composite: site coverage, terrain gaps, and every image that is not on the map, with the reason."""
import json, csv, os, sys, collections, math, re
import places as PL, sprites as SP, terrainsp as TSP
ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/w/main-1112"
OUT = "deliver"
log = {(r["name"], r["kind"]): r for r in json.load(open("out/placement_log.json"))}
usage = json.load(open("out/usage.json"))
gaz = json.load(open(os.path.join(ROOT, "data/manifests/crusader-period/site-history.json")))["sites"]
gid = {g["name"]: g for g in gaz}
LATER = {"Chastel Pelerin": "begun 1218", "Montfort": "begun 1226", "Ajlun": "begun 1184", "Clermont": "Chlemoutsi, 1220s", "Colos": "surviving tower is 15th century",
         "Chastellet": "standing only 1178-79; a ruin by 1180", "Saphet": "Templar rebuilding 1240", "Mistras": "founded 1249", "Saint-Pierre": "Bodrum castle begun 1402",
         "Buffavent": "painting shows about 1250", "La Candare": "painting shows about 1250", "Courc": "painting shows about 1250"}

# ---------- 1. site coverage
rows = []; used_paths = {}
for t in PL.PLACES:
    reg, tier, mark, lon, lat, name, alt, modern, held = t[:9]
    kind = "battle" if mark.startswith("M:battle") else ("siege" if mark.startswith("M:siege") else ("sea" if mark.startswith("M:sea") else "place"))
    L = log.get((name, kind)) or log.get((name, "isle")) or next((v for k, v in log.items() if k[0] == name), None)
    rec = SP.MATCH.get(name)
    if L is None:
        vis = "not in this build's item list"
    elif L["status"] != "shown":
        vis = L["status"]
    else:
        vis = "shown"
    if kind != "place":
        cov = "battle or siege marker (drawn)"
    elif rec and rec.get("generic"):
        cov = "generic fallback painting"
    elif rec:
        cov = "dedicated painting"
    elif name == "Mer de Galilee":
        cov = "dedicated painting"; rec = dict(variant="data/landscape-assets/png/sea-of-galilee.png", source="landscape painting fitted to the lake", year=None, w=995)
    else:
        cov = "drawn symbol (no painting)"
    g = gid.get(name, {})
    rows.append(dict(gazetteer_id=g.get("id", ""), name=name, alternate=alt, modern=modern, type=mark, tier=tier, frame=reg, lon=lon, lat=lat,
                     held=held, coverage=cov, on_map=vis, label=(L or {}).get("label", ""), sheet_x=(L or {}).get("x", ""), sheet_y=(L or {}).get("y", ""),
                     image=(rec or {}).get("variant", ""), image_source=(rec or {}).get("source", ""), depiction_year=(rec or {}).get("year") or "",
                     strict_1180_note=LATER.get(name, ""), native_width_px=(rec or {}).get("w", "")))
    if rec:
        used_paths[rec["variant"]] = (cov, name, vis)
with open(os.path.join(OUT, "site-coverage-register.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
pl = [r for r in rows if r["coverage"] != "battle or siege marker (drawn)"]
cc = collections.Counter((r["coverage"], "shown" if r["on_map"] == "shown" else "hidden") for r in pl)

# ---------- 2. off-map and usage ledger
led = json.load(open(os.path.join(ROOT, "data/manifests/CLAUDE-BUILD-IMAGE-LEDGER.json")))["records"]
paths = {}
for r in led:
    paths.setdefault(r["path"], r)
alts = {a["path"]: a for a in json.load(open("assets/sprite_alternates.json"))}
g2 = {r["src"]: r for r in json.load(open("assets/generic2.json"))}
isl = {r["src"]: r for r in json.load(open("assets/islands.json"))}
kit = {os.path.splitext(f)[0] for f in os.listdir("assets/terrain")}
C_ALL = set(TSP.C_RICH + TSP.C_PAST + TSP.C_WASTE + TSP.C_FLAT)
res = []
for p, r in sorted(paths.items()):
    base = os.path.basename(p); stem = os.path.splitext(base)[0]; use = "no"; why = ""
    if not r.get("file_exists", True) or not os.path.exists(os.path.join(ROOT, p)):
        why = "file is missing from the repository (broken manifest path)"
    elif p in used_paths:
        cov, nm, vis = used_paths[p]
        if vis == "shown":
            use = "yes"; why = "%s for %s" % (cov, nm)
        else:
            why = "primary painting for %s, but the symbol is %s" % (nm, vis)
    elif p in alts:
        why = alts[p]["reason"]
    elif p in isl:
        if isl[p]["id"] in usage["islands"]:
            use = "yes"; why = "island overlay registered by its coordinate box (%s inset)" % usage["islands"][isl[p]["id"]]
        else:
            why = "island overlay: its coordinate box falls outside the frames"
    elif p in g2:
        g = g2[p]; n = usage["generic"].get(g["file"], 0)
        fb = [k for k, v in used_paths.items() if k == p]
        if g["cls"] == "off":
            why = g["reason"]
        elif g["cls"].startswith("fb:"):
            why = "generic fallback held in reserve: no unpainted site of this kind is left to use it"
        elif n:
            use = "yes"; why = "generic %s piece, placed %d times" % (g["cls"], n)
        else:
            why = "generic %s piece: in the pool but not drawn in this build (random selection)" % g["cls"]
    elif p.startswith("data/terrain/png/") or p.startswith("data/terrain/sources/"):
        n = usage["terrain"].get(stem, 0)
        if p.startswith("data/terrain/sources/"):
            why = "source master of a terrain stamp: reference only"
        elif n:
            use = "yes"; why = "terrain stamp, placed %d times" % n
        elif stem in kit:
            why = "terrain stamp in the kit but not drawn in this build"
        else:
            why = "terrain stamp not in the build kit"
    elif "rural-landscapes" in p:
        m = re.search(r"CSV-(\d+)", base); nm = next((c for c in C_ALL if m and c.startswith("CSV-%s" % m.group(1))), None)
        n = usage["terrain"].get(nm, 0) if nm else 0
        if n:
            use = "yes"; why = "regional landscape tile, placed %d times" % n
        elif nm:
            why = "regional landscape tile in the pool but not drawn in this build"
        else:
            why = "regional landscape with painted sea or river: would clash with the real coast and rivers"
    elif "archive-1180" in p:
        why = "source sheet: reference only" if "reference_sheets" in p else "archived earlier version of a site that has a current primary painting"
    elif "/intake/" in p or "/sources/" in p or "sheet" in base or "atlas" in base:
        why = "source sheet or upload master: reference only, never placed"
    elif "greek-islands/batch-03" in p:
        why = "island on hold for visual review (repaint or geometry reconciliation) in its placement index"
    elif "greek-islands/" in p:
        why = "draft or concept island with no registered coordinate box"
    elif "natural-landmarks" in p:
        why = "landmark landscape queued: not yet fitted to its mountain or plateau"
    elif r.get("kind") == "island-outline":
        why = "extracted island outline with no registered coordinate box; the registered overlay of the same island is used where one exists"
    elif r["source"] == "filesystem-discovery":
        why = "uncatalogued original or earlier cut of a site painting; the catalogued variant of that site is the one used"
    else:
        why = "no coordinates or matched site in the repository"
    res.append(dict(image=p, source=r["source"], kind=r.get("kind") or "", label=r.get("label") or "", on_map=use, explanation=why))
with open(os.path.join(OUT, "image-usage-and-off-map-list.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(res[0].keys())); w.writeheader(); w.writerows(res)
oc = collections.Counter(r["explanation"].split(":")[0].split(",")[0][:70] for r in res if r["on_map"] == "no")

# ---------- 3. terrain gap report
cells = json.load(open("out/terrain_cells.json"))
Z = collections.OrderedDict()
for c in cells:
    z = Z.setdefault(c["zone"], [0, 0, 0, []]); z[0] += 1
    if c["detail"] < 12:
        z[1] += 1; z[3].append(c)
    elif c["detail"] < 16:
        z[2] += 1
with open(os.path.join(OUT, "terrain-gap-cells.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(cells[0].keys())); w.writeheader(); w.writerows([c for c in cells if c["detail"] < 16])
md = ["# Terrain gap report", "",
      "Measured on the composite preview. Each frame is cut into square cells (320 px on the main sheet, 200 px in the insets, at print scale). "
      "A land cell counts as flat when its painted detail (brightness spread) is under 12, and thin when it is 12 to 16. Panels and sea are left out.", "",
      "| Zone | Land cells | Flat | Thin | Share flat or thin |", "|---|---:|---:|---:|---:|"]
for z, (n, fl, th, lst) in sorted(Z.items(), key=lambda kv: -(kv[1][1] + kv[1][2]) / max(1, kv[1][0])):
    md.append("| %s | %d | %d | %d | %d%% |" % (z, n, fl, th, round(100 * (fl + th) / n)))
tot = len(cells); tf = sum(v[1] for v in Z.values()); tt = sum(v[2] for v in Z.values())
md += ["", "Whole sheet: %d land cells, %d flat, %d thin (%d%% flat or thin)." % (tot, tf, tt, round(100 * (tf + tt) / tot)), "",
       "## Flat cells by position", "", "| Zone | Lon | Lat | Sheet x | Sheet y | Detail |", "|---|---:|---:|---:|---:|---:|"]
for z, (n, fl, th, lst) in Z.items():
    for c in lst:
        md.append("| %s | %.2f | %.2f | %d | %d | %.1f |" % (z, c["lon"], c["lat"], c["sheet_x"], c["sheet_y"], c["detail"]))
md += ["", "The thin cells are listed with the flat ones in terrain-gap-cells.csv.", "",
       "## What covers the land now", "",
       "- Terrain stamps and landscape tiles: %d different pieces, %d placements" % (len(usage["terrain"]), sum(usage["terrain"].values())),
       "- Generic settlement, farm, tree, rock and ruin pieces: %d different pieces, %d placements" % (len(usage["generic"]), sum(usage["generic"].values())),
       "- Greek island overlays: %d" % len(usage["islands"]), "- Ships at sea: %d" % len(usage["ships"])]
open(os.path.join(OUT, "terrain-gap-report.md"), "w").write("\n".join(md) + "\n")
print("sites", cc); print("images", len(res), collections.Counter(r["on_map"] for r in res)); print(oc.most_common(30))
print("gaps", tot, tf, tt)
