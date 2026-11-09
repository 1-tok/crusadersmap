"""Build assets/sprites.json and the trimmed sprite PNGs from the repository's sprite catalogue (data/sprites/catalog.json).
One preferred variant per site: the highest selection_priority. Usage: python3 build_sprite_assets.py <repo-sprites-dir>"""
import json, os, sys, shutil
from PIL import Image
SRC = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/w/provisional-sprite-expansion/data/sprites"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
cat = json.load(open(os.path.join(SRC, "catalog.json")))["assets"]
best = {}
for a in cat:
    k = a["site_id"]
    if k not in best or a.get("selection_priority", 0) > best[k].get("selection_priority", 0):
        best[k] = a
shutil.rmtree(os.path.join(OUT, "sprites"), ignore_errors=True); os.makedirs(os.path.join(OUT, "sprites"))
recs = []
for k, a in best.items():
    lon, lat = a.get("longitude"), a.get("latitude")
    if lon is None:
        lon, lat = a["coordinates"]
    p = os.path.join(SRC, a["asset"])
    if not os.path.exists(p):
        print("missing", a["asset"]); continue
    im = Image.open(p).convert("RGBA")
    bb = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox(); im = im.crop(bb)
    maxw = 1300 if a.get("display_width_units", 512) >= 1000 else 900
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    fn = os.path.basename(a["asset"])
    im.save(os.path.join(OUT, "sprites", fn))
    recs.append(dict(name=a["name"], site=k, cat=a["category"], region=a.get("map_region", "main"), lon=lon, lat=lat,
                     file=fn, w=im.width, h=im.height, units=a.get("display_width_units", 512),
                     variant=a["asset"], review=bool(a.get("review_required"))))
json.dump(recs, open(os.path.join(OUT, "sprites.json"), "w"), indent=1)
print(len(recs), "sprites")
