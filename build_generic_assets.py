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
# Keep the vetted placement/scatter classes keyed to an immutable source path.
# The previous array-index rules silently reclassified unrelated art whenever
# new ZIPs changed the sorting order: an unsafe placement regression.
stable = json.load(open(os.path.join(ROOT, "data/manifests/automated-intake-stable-scatter-classes.json")))["entries"]
for r in ai:
    decision = stable.get(r["path"], {})
    cls = decision.get("cls", "off")
    why = decision.get("reason", "new intake sprite: pending classification and geographic QA")
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
setf([4, 16, 31], "off", "river or reed piece: needs aligning to a real river course before use")
setf([13, 14, 15, 36, 39, 41, 49, 57], "off", "coast, lighthouse or sea-rock piece: needs registering to a real stretch of shoreline before use")
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
        put(p, "off", "river, reed or marsh piece: needs aligning to real water before use"); continue
    if any(k in n for k in ("oasis", "palm")):
        put(p, "oasis"); continue
    if any(k in n for k in ("dune", "badland", "pavement", "bare_rocky", "sandy", "arid_scrub", "volcanic")):
        put(p, "patcha"); continue
    if any(k in n for k in ("grain", "wheat", "vineyard", "terrace", "garden", "field", "orchard", "olive", "cultivated")):
        put(p, "patchg"); continue
    if any(k in n for k in ("woodland", "conifer", "forest", "copse", "grove", "wooded", "cedar")):
        put(p, "patchw"); continue
    put(p, "patchd")
json.dump(recs, open(os.path.join(OUT, "generic2.json"), "w"), indent=1)
import collections
print(collections.Counter(r["cls"] for r in recs))
