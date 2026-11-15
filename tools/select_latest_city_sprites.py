#!/usr/bin/env python3
"""Select the newest painted city sprite for each coastal site, and pin Constantinople to its original layout.

The 13 November "historical redo" batches (v2) show the sea on the west / left of the Levantine coast,
so they replace the earlier south-view v1 primaries. Beirut and Tartus keep the owner-approved azure
sprites. Constantinople keeps its original double-size painting with the three companions (Galata/Sykai,
Chrysopolis, Chalcedon). Replaced primaries are kept in the alternates list.
Run after build_new_uploads.py, before build_stage2.py. Changes only generated assets.
"""
import glob, json, os, sys
import numpy as np
from PIL import Image
from scipy.ndimage import label

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "assets")
INTAKE = os.path.join(ROOT, "data", "sprites", "automated-intake", "png")
sys.path.insert(0, ROOT)

# file prefix in the intake folder -> (site id, key matching the place catalogue when the site has no record yet)
CITIES = {
    "acre": ("acre", None), "caesarea": ("caesarea", None), "jaffa": ("jaffa", None), "ascalon": ("ascalon", None),
    "tyre": ("tyre", None), "sidon": ("sidon", None), "batroun": ("batroun", None), "byblos": ("byblos", None),
    "tripoli": ("tripoli", None), "gaza": ("gaza", None), "jableh": ("jableh", None), "latakia": ("latakia", None),
    "chastel-pelerin-atlit": ("chateau-pelerin", None), "baniyas-syria": ("baniyas-syria", None),
    "ruad-arwad": ("ruad", "Ruad"), "alexandria": ("alexandria", None), "damietta": ("damietta", None),
    "ile-de-graye-pharaohs-island": ("ile-de-graye", "Ile de Graye"),
    "famagusta": ("famagusta", None), "limassol": ("limassol", None), "paphos": ("paphos", None), "ayas-laiazzo-c1300-east-gulf": ("ayas", "Lajazzo"),
    "chios": ("chios", None), "smyrna": ("smyrna", "Smyrne"), "ayasoluk-ephesus": ("ayasoluk", "Ayasoluk"),
    "monemvasia": ("monemvasia", None), "nafpaktos": ("nafpaktos", None), "methoni": ("methoni", None), "koroni": ("koroni", None),
    "chania-kydonia": ("chania", None), "rethymno": ("rethymno", None), "candia-chandax-heraklion": ("candia", "Candie"),
    "petronion-halicarnassus-bodrum": ("halicarnassus", "Saint-Pierre"), "mount-athos-great-lavra": ("mount-athos", "Mont Athos"),
    "gallipoli-gelibolu": ("gallipoli", "Gallipoli"), "patmos-st-john-monastery": ("patmos", "Patmos"),
    "naxos": ("naxos", None), "kos": ("kos", None), "mytilene": ("mytilene", None), "patras": ("patras", None),
    "leros-panteli": ("leros", None), "lemnos-myrina": ("lemnos", None), "phocaea-foca": ("phocaea", "Foglie"), "corfu-kerkyra": ("corfu", None),
}
KEEP = {"beirut", "tortosa", "rhodes", "kyrenia"}      # azure sprites chosen by the owner; Rhodes stays as is; Kyrenia has an orientation review of its own
PIN = {   # site -> original file (kept as the primary regardless of later repaints)
    "constantinople": "data/sprites/greece-egypt-1180-constantinople/constantinople-1180-v1.png",
    "galata-sykai": "data/sprites/greece-egypt-1180-bosphorus/galata-sykai-1180-v1.png",
    "chrysopolis": "data/sprites/greece-egypt-1180-bosphorus/chrysopolis-1180-v1.png",
    "chalcedon": "data/sprites/greece-egypt-1180-bosphorus/chalcedon-1180-v1.png",
}


def best_file(prefix):
    """Newest painting for a prefix: historical redo v2 first, then a south / south-to-north / harbour review, never concepts or sheets."""
    cands = []
    for p in glob.glob(os.path.join(INTAKE, prefix + "-*.png")):
        n = os.path.basename(p)
        if any(k in n for k in ("concept", "source-sheet", "checkerboard", "repaint-required", "provisional", "azure")):
            continue
        rest = n[len(prefix) + 1:]
        if not (rest.startswith("1180") or rest.startswith("c1300") or rest.startswith("1096") or rest.startswith("south")):
            continue
        rank = 4 if "historical-redo-review-v2" in n else 3 if "south-southwest-harbor" in n else 2 if "south" in n or "review" in n else 1
        cands.append((rank, n, p))
    return sorted(cands)[-1][2] if cands else None


def clean(im, maxw):
    a = np.asarray(im.getchannel("A")) > 16
    lab, n = label(a)
    if n > 1:
        sizes = np.bincount(lab.ravel())[1:]
        keep = [i + 1 for i, s in enumerate(sizes) if s >= 0.02 * sizes.max()]
        mask = np.isin(lab, keep)
        al = np.asarray(im.getchannel("A")).copy(); al[~mask] = 0
        im = im.copy(); im.putalpha(Image.fromarray(al))
    bb = im.getchannel("A").point(lambda v: 255 if v > 16 else 0).getbbox()
    im = im.crop(bb)
    if im.width > maxw:
        im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
    return im


def main():
    import places as PL
    reg = os.path.join(A, "sprites.json"); recs = json.load(open(reg)); alt = json.load(open(os.path.join(A, "sprite_alternates.json")))
    by_site = {r.get("site"): r for r in recs}
    done = []
    for prefix, (site, pname) in CITIES.items():
        if site in KEEP or site in PIN:
            continue
        src = best_file(prefix)
        if not src:
            continue
        fn = os.path.basename(src)
        r = by_site.get(site)
        if r is not None and r.get("file") == fn:
            continue
        if r is None:
            t = next((t for t in PL.PLACES if t[5] == pname), None)
            if t is None:
                continue
            r = dict(name=t[5], site=site, cat="city", region=t[0], lon=t[3], lat=t[4], units=512, year=1180)
            recs.append(r); by_site[site] = r
        else:
            alt.append(dict(path=r.get("variant"), site=site, reason="superseded by the newer painting " + fn))
        im = clean(Image.open(src).convert("RGBA"), 900)
        im.save(os.path.join(A, "sprites", fn))
        r.update(file=fn, w=im.width, h=im.height, variant="data/sprites/automated-intake/png/" + fn, source="13-15 Nov city repaint", review=True)
        done.append((site, fn))
    for site, rel in PIN.items():
        r = by_site.get(site); p = os.path.join(ROOT, rel)
        if r is None or not os.path.isfile(p):
            continue
        fn = os.path.basename(p)
        im = clean(Image.open(p).convert("RGBA"), 1300 if r.get("units", 512) >= 1000 else 900); im.save(os.path.join(A, "sprites", fn))
        alt.append(dict(path=r.get("variant"), site=site, reason="replaced by the original Constantinople layout chosen by the owner"))
        r.update(file=fn, w=im.width, h=im.height, variant=rel, source="original layout", review=True)
        done.append((site, fn))
    seen = set(); alt2 = []
    for a_ in alt:
        k_ = (a_.get("site"), a_.get("path"), a_.get("reason"))
        if k_ not in seen:
            seen.add(k_); alt2.append(a_)
    alt = alt2
    json.dump(recs, open(reg, "w"), indent=1); json.dump(alt, open(os.path.join(A, "sprite_alternates.json"), "w"), indent=1)
    for d in done:
        print(*d)
    print(len(done), "sprites updated")


if __name__ == "__main__":
    main()
