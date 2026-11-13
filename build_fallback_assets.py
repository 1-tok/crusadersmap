"""Give a generic painted fallback to named places that have no painting of their own. Run after build_sprite_assets.py
and build_generic_assets.py. Adds records (generic=True) to assets/sprites.json; places with no suitable generic keep their drawn symbol."""
import json, os, shutil, math
import places as PL
HERE = os.path.dirname(os.path.abspath(__file__))
S = [r for r in json.load(open(os.path.join(HERE, "assets", "sprites.json"))) if not r.get("generic")]
G = json.load(open(os.path.join(HERE, "assets", "generic2.json")))
pool = {}
for r in G:
    if r["cls"].startswith("fb:"):
        pool.setdefault(r["cls"][3:], []).append(r)
WANT = {"Li Vaux Moyse": "fort", "Blanchegarde": "fort", "Ibelin": "fort", "Toron des Chevaliers": "fort", "Scandalion": "fort",
        "Gallipoli": "fort", "Aila": "fort", "Shayzar": "fort", "Masyaf": "fort", "Qadmus": "fort", "Smyrne": "harbour_fort",
        "Saint-Pierre": "harbour_fort", "Darum": "tower", "Montjoie": "tower", "Mont Thabor": "monastery_hill", "Sebaste": "latin",
        "Mont Carmel": "monastery_hill", "Cicho": "greek", "Lapais": "latin", "Mont Athos": "monastery_cliff", "Patmos": "monastery_cliff"}
have = set()
for r in S:
    for t in PL.PLACES:
        if t[0] == r.get("region", t[0]) and math.hypot(t[3] - r["lon"], t[4] - r["lat"]) < 0.08:
            have.add(t[5])
nxt = {}; n = 0
for t in PL.PLACES:
    nm = t[5]
    if nm in have or nm not in WANT or not pool.get(WANT[nm]):
        continue
    lst = pool[WANT[nm]]; g = lst[nxt.get(WANT[nm], 0) % len(lst)]; nxt[WANT[nm]] = nxt.get(WANT[nm], 0) + 1
    fn = "generic-" + g["file"]
    shutil.copy(os.path.join(HERE, "assets", "generic2", g["file"]), os.path.join(HERE, "assets", "sprites", fn))
    S.append(dict(name=nm, site="generic:" + nm, cat="generic", region=t[0], lon=t[3], lat=t[4], file=fn, w=g["w"], h=g["h"],
                  units=380, variant=g["src"], review=True, source="generic-fallback", year=None, generic=True))
    n += 1
json.dump(S, open(os.path.join(HERE, "assets", "sprites.json"), "w"), indent=1)
print(n, "generic fallbacks;", len(S), "sprite records")
