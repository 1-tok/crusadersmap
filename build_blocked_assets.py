"""Bring blocked images onto the map with coordinates from general reference (unverified, flagged as such):
small Greek islands that have no coordinate box in the repository, and named fortresses that have no coordinates.
Run after build_new_uploads.py and before build_fallback_assets.py. Usage: python3 build_blocked_assets.py <repo-root>"""
import json, os, sys, re, glob
from PIL import Image
ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/claude/w/main-1113"
HERE = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(HERE, "assets")
# number: (name, lon, lat, longest dimension in km)
ISL = {48: ("Aegina", 23.43, 37.75, 13), 49: ("Salamis", 23.49, 37.94, 16), 50: ("Poros", 23.47, 37.52, 8), 51: ("Hydra", 23.47, 37.33, 20),
       52: ("Spetses", 23.13, 37.26, 7), 53: ("Agistri", 23.35, 37.70, 5), 54: ("Paxos", 20.18, 39.20, 10), 55: ("Antipaxos", 20.23, 39.15, 4),
       56: ("Antiparos", 25.05, 37.00, 12), 57: ("Delos", 25.27, 37.39, 5), 58: ("Rhenia", 25.22, 37.41, 7), 59: ("Sikinos", 25.12, 36.68, 14),
       60: ("Donousa", 25.81, 37.10, 5), 61: ("Irakleia", 25.45, 36.84, 7), 62: ("Schinoussa", 25.52, 36.87, 5), 63: ("Koufonisia", 25.60, 36.93, 6),
       64: ("Chalki", 27.57, 36.23, 10), 65: ("Lipsi", 26.76, 37.30, 8), 66: ("Kastellorizo", 29.59, 36.15, 6), 67: ("Imbros", 25.84, 40.16, 30),
       68: ("Tenedos", 26.05, 39.82, 11), 69: ("Psara", 25.59, 38.57, 9), 70: ("Gavdos", 24.08, 34.84, 10), 71: ("Elafonisos", 22.97, 36.49, 6),
       72: ("Arki and Marathi", 26.74, 37.39, 6), 73: ("Oinousses", 26.22, 38.52, 8), 74: ("Fournoi", 26.48, 37.58, 12), 75: ("Antikythera", 23.30, 35.87, 10),
       76: ("Othonoi", 19.40, 39.85, 5), 77: ("Ereikoussa", 19.58, 39.88, 3), 78: ("Mathraki", 19.52, 39.77, 3), 79: ("Saria", 27.22, 35.87, 8),
       80: ("Agathonisi", 26.97, 37.46, 6), 81: ("Pserimos", 27.14, 36.93, 5), 82: ("Telendos", 26.92, 37.00, 3), 83: ("Meganisi", 20.78, 38.65, 9),
       84: ("Kinaros", 26.29, 36.98, 5), 85: ("Levitha", 26.47, 37.00, 6), 86: ("Polyaigos", 24.63, 36.77, 7), 87: ("Gyaros", 24.72, 37.61, 8),
       88: ("Makronisos", 24.12, 37.70, 13), 89: ("Dokos", 23.33, 37.34, 7), 90: ("Sapientza", 21.70, 36.75, 6), 91: ("Schiza", 21.78, 36.72, 6),
       92: ("Thirasia", 25.34, 36.43, 6), 93: ("Despotiko", 25.00, 36.96, 5), 94: ("Dia", 25.22, 35.44, 5), 95: ("Antimilos", 24.24, 36.79, 4),
       96: ("Gramvousa", 23.58, 35.61, 2), 97: ("Chrysi", 25.71, 34.87, 5), 98: ("Agios Efstratios", 25.00, 39.52, 11), 99: ("Peristera", 23.98, 39.20, 8),
       100: ("Kyra Panagia", 24.07, 39.33, 8), 101: ("Gioura", 24.17, 39.39, 7), 102: ("Piperi", 24.32, 39.35, 5), 103: ("Skantzoura", 24.11, 39.08, 5),
       104: ("Kalamos", 20.92, 38.62, 10), 105: ("Kastos", 20.91, 38.57, 7), 106: ("Atokos", 20.81, 38.48, 4), 107: ("Arkoudi", 20.71, 38.55, 3),
       108: ("Oxia", 21.10, 38.30, 5), 109: ("Petalas", 21.11, 38.41, 4)}
cands = {}
for f in glob.glob(os.path.join(ROOT, "data/sprites/greek-islands/**/*.png"), recursive=True) + glob.glob(os.path.join(ROOT, "data/sprites/automated-intake/png/*.png")):
    m = re.match(r"(\d{2,3})[-_]", os.path.basename(f))
    if not m or int(m.group(1)) not in ISL or "sheet" in f.lower():
        continue
    rank = (0 if "automated-intake" in f else 1, 1 if "DRAFT" in f else 0)        # the cleaned intake cut first, drafts last
    cands.setdefault(int(m.group(1)), []).append((rank, f))
out = []; dup = []
for n, lst in sorted(cands.items()):
    lst.sort(); f = lst[0][1]
    im = Image.open(f).convert("RGBA"); bb = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    if not bb:
        continue
    im = im.crop(bb); im.thumbnail((500, 500), Image.LANCZOS)
    fn = "x" + os.path.basename(f); im.save(os.path.join(A, "islands", fn))
    nm, lo, la, km = ISL[n]
    out.append(dict(id="X%d" % n, name=nm, file=fn, src=os.path.relpath(f, ROOT), lon=lo, lat=la, km=km, aspect=im.height / im.width))
    dup += [dict(path=os.path.relpath(g, ROOT), primary=os.path.relpath(f, ROOT)) for _, g in lst[1:]]
json.dump(dict(islands=out, duplicates=dup), open(os.path.join(A, "islands_extra.json"), "w"), indent=1)

# named fortresses with no coordinates in the repository
FORT = {"birecik": ("al-Bira", "Birecik", "M:castle_muslim", 37.975, 37.025), "harran": ("Qal'at Harran", "Harran citadel", "M:castle_muslim", 39.03, 36.865),
        "lampron": ("Lampron", "Namrun", "M:castle_armenian", 34.63, 37.17), "ja-bar": ("Qal'at Ja'bar", "Qal'at Ja'bar", "M:castle_muslim", 38.48, 35.90),
        "najm": ("Qal'at Najm", "Qal'at Najm", "M:castle_muslim", 38.26, 36.55), "ravanda": ("Ravendel", "Ravanda Kalesi", "M:castle_frankish", 37.03, 36.87),
        "savranda": ("Servantikar", "Savranda Kalesi", "M:castle_armenian", 36.44, 37.14), "silifke": ("Selefke", "Silifke", "M:castle_armenian", 33.93, 36.38),
        "toprakkale": ("Til Hamdoun", "Toprakkale", "M:castle_armenian", 36.146, 37.06)}
S = json.load(open(os.path.join(A, "sprites.json"))); S = [r for r in S if not r.get("located_by_reference")]
have = {r["variant"] for r in S}; extra = []
for key, (nm, modern, mark, lo, la) in FORT.items():
    fs = [f for f in glob.glob(os.path.join(ROOT, "data/sprites/automated-intake/png/*.png")) if key in os.path.basename(f)]
    if not fs or os.path.relpath(fs[0], ROOT) in have:
        continue
    if any(abs(r["lon"] - lo) < 0.03 and abs(r["lat"] - la) < 0.03 for r in S):
        continue
    f = fs[0]; im = Image.open(f).convert("RGBA"); bb = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox(); im = im.crop(bb)
    fn = os.path.basename(f); im.save(os.path.join(A, "sprites", fn))
    S.append(dict(name=modern, site="ref:" + key, cat="review", region="main", lon=lo, lat=la, file=fn, w=im.width, h=im.height, units=512,
                  variant=os.path.relpath(f, ROOT), review=True, source="coordinates from general reference, unverified", year=None, located_by_reference=True))
    extra.append(["main", 4, mark, lo, la, nm, "", modern, "", []])
json.dump(S, open(os.path.join(A, "sprites.json"), "w"), indent=1)
json.dump(extra, open(os.path.join(A, "places_extra.json"), "w"), indent=1)
print(len(out), "islands by reference,", len(dup), "duplicate island images;", len(extra), "fortresses by reference")
