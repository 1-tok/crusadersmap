"""Classify the generic (unlocated) artwork in the repository and copy what the map can use into assets/generic2.
Writes assets/generic2.json: one record per source image with class, or the reason it stays off the map."""
import glob, json, os, sys, re
from PIL import Image
ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/w/main-1112"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
recs = []


def put(path, cls, reason=""):
    fn = ""
    if not cls.startswith("off"):
        im = Image.open(os.path.join(ROOT, path)).convert("RGBA")
        bb = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
        if bb:
            im = im.crop(bb)
        fn = re.sub(r"[^a-z0-9_.-]", "_", os.path.basename(path).lower())
        im.save(os.path.join(OUT, "generic2", fn))
        recs.append(dict(src=path, file=fn, cls=cls, w=im.width, h=im.height, reason=reason)); return
    recs.append(dict(src=path, file="", cls="off", reason=reason))


# --- automated intake (unlocated, sorted by kind then label, as in the review sheet)
led = json.load(open(os.path.join(ROOT, "data", "manifests", "CLAUDE-BUILD-IMAGE-LEDGER.json")))["records"]
ai = [r for r in led if r["source"] == "automated-intake" and not r.get("geometry") and r["kind"] not in ("source-master", "island-outline")]
ai.sort(key=lambda r: (r["kind"], r["label"]))
AI = {}
def setr(idx, cls, reason=""):
    for i in idx:
        AI[i] = (cls, reason)
setr([0, 13, 14, 15, 16, 18, 19, 20, 21, 95, 99, 111, 112, 113, 114, 115, 118, 137, 138, 139, 140, 145, 30, 32, 60, 66], "green")
setr([108], "delta")
setr([6, 7, 8, 9, 10, 68], "patchg")
setr([1, 2, 3, 4, 5, 11, 12, 17, 147, 148, 152, 153, 154, 155], "vegg")
setr([150, 156, 157], "vegd")
setr([149], "vega")
setr([22, 23, 24], "patcha")
setr([34, 36, 37, 38, 151], "rock")
setr([39, 40, 41, 42, 43], "patchd")
setr([109, 116, 117, 119], "past")
setr([110, 26], "ruin")
setr([141, 142, 143, 144], "arid")
setr([132, 133, 134, 135], "ship")
setr([25], "fb:harbour_fort"); setr([27], "fb:tower"); setr([33, 35], "fb:fort"); setr([28], "fb:town"); setr([29, 31], "fb:harbour_town")
setr([57, 65, 75, 80, 83], "fb:monastery_hill"); setr([63, 85, 86, 90, 91, 92, 93, 56], "fb:latin"); setr([62, 69, 70, 74, 77, 78, 89, 73], "fb:greek")
setr([71, 72, 81], "fb:monastery_cliff"); setr([82, 59], "fb:monastery")
setr([61, 84, 87], "off", "depicts a named monument (Dome of the Rock, Hagia Sophia) that already has its city painting")
setr([64, 76, 79, 88, 58], "schurch")
setr([67, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 146], "coast")
setr([94, 96, 97, 98, 100, 101, 102, 103, 104, 105, 106, 107], "river")
setr([131, 136], "coast")
setr(list(range(44, 56)), "off", "named fortress candidate with no coordinates or matched site in the repository")
for i, r in enumerate(ai):
    cls, why = AI.get(i, ("off", "unclassified"))
    put(r["path"], cls, why)
for r in led:
    if r["source"] == "automated-intake" and r["kind"] == "source-master":
        put(r["path"], "off", "source sheet: reference only, never placed")

# --- batch 13 map fillers
fl = sorted(glob.glob(os.path.join(ROOT, "data/sprites/map-fillers-2026-11-11/**/*.png"), recursive=True))
FL = {}
def setf(idx, cls, reason=""):
    for i in idx:
        FL[i] = (cls, reason)
setf([19, 20, 21, 22, 25, 27, 55, 58, 59, 62, 8], "green"); setf([28, 29, 30, 65, 66], "vegg"); setf([23], "vega"); setf([26, 67], "arid")
setf([60], "oasis"); setf([53, 61, 64], "past"); setf([6, 7, 54, 68], "ruin"); setf([37, 63], "rock"); setf([32, 33, 34, 35], "ship")
setf([0, 9, 11, 43, 50, 56], "fb:fort"); setf([10, 12, 24, 40, 48], "fb:tower"); setf([17, 18], "fb:town"); setf([1, 42, 44], "fb:harbour_town")
setf([5, 45, 47], "fb:latin"); setf([46, 2], "fb:greek"); setf([3, 38], "fb:harbour_fort")
setf([51], "off", "depicts the Dome of the Rock, already inside the Jerusalem painting")
setf([4, 16, 31], "river")
setf([13, 14, 15, 36, 39, 41, 49, 57], "coast")
setf([52], "off", "two pieces joined in one cut-out: needs splitting")
for i, f in enumerate(fl):
    cls, why = FL.get(i, ("off", "unclassified"))
    put(os.path.relpath(f, ROOT), cls, why)

# --- terrain batches 05 and 06
for f in sorted(glob.glob(os.path.join(ROOT, "data/sprites/terrain-batch0[56]/**/*.png"), recursive=True)):
    n = os.path.basename(f).lower(); p = os.path.relpath(f, ROOT)
    if "atlas" in n or "sheet" in n:
        put(p, "off", "atlas sheet: reference only, the individual cut-outs are used"); continue
    if any(k in n for k in ("reed", "delta", "stream", "riverbank", "horseshoe", "meander", "wadi", "lily")):
        put(p, "river"); continue
    if any(k in n for k in ("volcan", "basalt", "cinder")):
        put(p, "off", "volcano or basalt piece: removed from the map at Daryl's request"); continue
    if any(k in n for k in ("oasis", "palm")):
        put(p, "oasis"); continue
    if any(k in n for k in ("dune", "badland", "pavement", "bare_rocky", "sandy", "arid_scrub", "volcanic")):
        put(p, "patcha"); continue
    if any(k in n for k in ("grain", "wheat", "vineyard", "terrace", "garden", "field", "orchard", "olive", "cultivated")):
        put(p, "patchg"); continue
    if any(k in n for k in ("woodland", "conifer", "forest", "copse", "grove", "wooded", "cedar")):
        put(p, "patchw"); continue
    put(p, "patchd")
# --- the three landmark landscapes, placed at their own coordinates by landmarkart.py
for f in sorted(glob.glob(os.path.join(ROOT, "data/sprites/natural-landmarks/png/*.png"))):
    put(os.path.relpath(f, ROOT), "landmark")
# --- regional landscapes that carry painted rivers or coast: used as riverside or shore pieces
for i in (90, 92, 96, 97, 101, 104, 108, 109, 113, 116):
    for f in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "terrain", "CSV-%03d_*.png" % i)):
        im = Image.open(f).convert("RGBA"); im.thumbnail((640, 640), Image.LANCZOS)
        fn = os.path.basename(f).lower(); im.save(os.path.join(OUT, "generic2", fn))
        coastal = any(k in fn for k in ("coast", "bay", "shore", "sea", "harbor", "harbour", "fishing"))
        recs.append(dict(src="data/sprites/rural-landscapes/png/CSV-%03d.png" % i, file=fn, cls="coast" if coastal else "river", w=im.width, h=im.height, reason=""))
json.dump(recs, open(os.path.join(OUT, "generic2.json"), "w"), indent=1)
import collections
print(collections.Counter(r["cls"] for r in recs))
