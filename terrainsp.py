import json
"""Painted mountain and foothill pieces, chosen by region and stamped along the existing relief."""
import os
import numpy as np
import cairo
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "assets", "terrain")
DRYSTRIP = ["gravel-wasteland", "rocky-desert", "dry-scrub-steppe", "eroded-badlands", "salt-flat", "desert-escarpment", "dune-transition",
            "flat-desert-pavement", "flat-desert-sand-sheet", "shallow-desert-wash", "desert-gravel-sand-transition", "salt-flat-basin"]
DUNES = ["sand-dunes", "dune-transition", "dune-field-deep"]
LEB_P = ["lebanon-high-massif"]; LEB_M = ["lebanon-short-ridge", "lebanon-saddle", "lebanon-short-ridge", "sparse-cedar-woodland"]
PAL_P = ["palestine-limestone-ridge", "limestone-narrow-spine"]; PAL_M = ["limestone-narrow-spine", "palestine-limestone-ridge", "limestone-branching-spur", "limestone-valley-gap"]
TAU_P = ["taurus-ridge", "taurus-short-peaks", "taurus-ridge"]; TAU_M = ["taurus-cliff-spur", "anatolian-rocky-saddle", "taurus-short-peaks"]
GRK_P = ["pindus-forested-ridge", "greek-short-ridge"]; GRK_M = ["pine-slope-transition", "greek-narrow-spine", "greek-branching-spur", "greek-short-ridge", "greek-forested-foothills"]
DRY_P = ["high-rocky-ridge-spine", "open-plateau-escarpment", "dry-limestone-pass"]; DRY_M = ["dry-limestone-pass", "dry-wadi-connector", "limestone-narrow-spine", "open-plateau-escarpment"]
HILL = {"pal": ["palestine-foothills-east", "palestine-foothills-west", "coastal-foothill-transition", "rocky-foothill-fan"],
        "ana": ["anatolian-steppe-foothills", "coastal-foothill-transition", "mediterranean-scrub-fill"],
        "grk": ["greek-forested-foothills", "pine-slope-transition"], "dry": ["rocky-foothill-fan", "palestine-foothills-east", "palestine-foothills-west"]}


def _csv(*ids):
    out = []
    for i in ids:
        out += [os.path.basename(f)[:-4] for f in glob.glob(os.path.join(D, "CSV-%03d_*.png" % i))]
    return out


import glob
C_RICH = _csv(93, 95, 98, 110, 115, 118, 107, 106, 103)
C_FLAT = _csv(93, 98, 110, 118)
C_PAST = _csv(89, 99, 106, 103, 107, 111)
C_WASTE = _csv(91, 94, 100, 102, 105, 112, 114, 117)
G_GREEN = [0, 1, 2, 6, 7, 8, 10, 15, 23, 24, 26, 28, 29]
G_PAST = [12, 20, 25, 4, 14, 10]
G_ARID = [3, 11, 14, 17, 18, 19, 13, 21, 27, 5]
G_OASIS = [16, 22, 30]
_GS = {}
TUSED = {}
G2 = json.load(open(os.path.join(HERE, "assets", "generic2.json"))) if os.path.exists(os.path.join(HERE, "assets", "generic2.json")) else []
G2P = {}
for _r in G2:
    if _r["file"]:
        G2P.setdefault(_r["cls"], []).append(_r["file"])
GUSED = {}
POOL = {"green": G_GREEN + G2P.get("green", []), "past": G_PAST + G2P.get("past", []), "arid": G_ARID + G2P.get("arid", []),
        "oasis": G_OASIS + G2P.get("oasis", []), "vegg": G2P.get("vegg", []), "vegd": G2P.get("vegd", []), "vega": G2P.get("vega", []),
        "rock": G2P.get("rock", []), "ruin": G2P.get("ruin", []), "patchg": G2P.get("patchg", []), "patchw": G2P.get("patchw", []),
        "patchd": G2P.get("patchd", []), "patcha": G2P.get("patcha", []), "delta": G2P.get("delta", []) + G2P.get("green", [])[:4], "town": G2P.get("fb:town", [])}
POOL["sfort"] = G2P.get("fb:fort", []) + G2P.get("fb:tower", [])
POOL["schurch"] = G2P.get("fb:latin", []) + G2P.get("fb:greek", []) + G2P.get("fb:monastery", []) + G2P.get("fb:monastery_hill", []) + G2P.get("fb:monastery_cliff", []) + G2P.get("schurch", [])
POOL["coast"] = G2P.get("coast", []) + G2P.get("fb:harbour_town", []) + G2P.get("fb:harbour_fort", [])
POOL["river"] = G2P.get("river", [])
_DECK = {}


def pick(pool, r):
    """Deal the pool like a shuffled deck, so every piece is used before any repeats."""
    d = _DECK.get(pool)
    if not d:
        d = list(POOL[pool]); r.shuffle(d); _DECK[pool] = d
    return d.pop()


POOL_SHIP = G2P.get("ship", [])
GSIZE = {"green": (120, 150), "past": (120, 150), "arid": (115, 145), "oasis": (120, 150), "vegg": (70, 95), "vegd": (60, 85), "vega": (70, 90),
         "rock": (95, 130), "ruin": (105, 130), "patchg": (190, 240), "patchw": (190, 240), "patchd": (190, 240), "patcha": (200, 250), "delta": (115, 140), "town": (170, 205), "sfort": (130, 160), "schurch": (115, 140), "coast": (135, 170), "river": (150, 190)}


def _ragged(im, key, strength=1.0):
    """Eat the margins of a tile with soft noise so no tile ends on a straight edge."""
    from scipy.ndimage import gaussian_filter
    import zlib
    width, h = im.size
    rs = np.random.RandomState(zlib.crc32(("%s%d" % (key, width)).encode()))
    yy, xx = np.mgrid[0:h, 0:width].astype(np.float32)
    d = np.minimum(np.minimum(xx, width - 1 - xx), np.minimum(yy, h - 1 - yy)) / max(8.0, 0.30 * min(width, h))
    nz = gaussian_filter(rs.rand(h, width).astype(np.float32), max(2.0, width * 0.06)); nz = (nz - nz.min()) / max(1e-6, nz.max() - nz.min())
    nz2 = gaussian_filter(rs.rand(h, width).astype(np.float32), max(1.0, width * 0.02)); nz2 = (nz2 - nz2.min()) / max(1e-6, nz2.max() - nz2.min())
    thr = 0.10 + 1.10 * (0.65 * nz + 0.35 * nz2) * strength
    m_ = np.clip((d - thr * 0.85) * 2.0, 0, 1); m_ = m_ * m_ * (3 - 2 * m_)
    a2 = np.asarray(im.getchannel("A"), np.float32) * m_
    im.putalpha(Image.fromarray(np.clip(a2, 0, 255).astype(np.uint8)))
    return im


def gsurf(i, edition, width):
    width = int(max(8, round(width / 4.0) * 4))
    k = (i, edition, width)
    if k not in _GS:
        im = Image.open(os.path.join(HERE, "assets", "generic", "s%02d.png" % i) if isinstance(i, int) else os.path.join(HERE, "assets", "generic2", i)).convert("RGBA")
        if edition != "colour":
            a = im.getchannel("A")
            arr = np.asarray(ImageEnhance.Color(im.convert("RGB")).enhance(0.6), np.float32) * np.array([1.0, 0.97, 0.90], np.float32) * 0.94 + 12
            im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA"); im.putalpha(a)
        h = max(1, int(round(im.height * width / im.width)))
        im = im.resize((width, h), Image.LANCZOS)
        if isinstance(i, int) and i in _PATCH_IDS or (not isinstance(i, int) and "patch" in str(i)) or (isinstance(i, int) is False and str(i) in _PATCH_FILES):
            im = _ragged(im, i)
        a = np.asarray(im, np.float32); al = a[..., 3:4] / 255.0
        buf = np.empty((h, width, 4), np.uint8)
        buf[..., :3] = (a[..., [2, 1, 0]] * al).astype(np.uint8); buf[..., 3] = a[..., 3].astype(np.uint8)
        _GS[k] = cairo.ImageSurface.create_for_data(bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, width, h, width * 4)
    return _GS[k]


def gdraw(c, i, x, y, width, edition):
    s = gsurf(i, edition, width)
    GUSED[i] = GUSED.get(i, 0) + 1
    c.save()
    c.translate(x - s.get_width() / 2.0, y - 0.85 * s.get_height())
    c.set_source_surface(s, 0, 0)
    c.get_source().set_filter(cairo.FILTER_BEST)
    c.paint()
    c.restore()


DEEP = ["gravel-wasteland-deep", "steppe-basin-deep", "dune-field-deep", "badlands-tall-massif", "escarpment-tall-deep"]
FARM_RICH = ["levant-farmland", "orchard-field-mosaic", "river-floodplain-fields", "orchard-field-mosaic", "levant-farmland"]
FARM_FLAT = ["river-floodplain-fields", "levant-farmland", "river-floodplain-fields"]
FARM_PASTURE = ["dry-stone-pasture"]
FARM_AEG = ["aegean-terraced-farmland", "aegean-island-interior", "aegean-terraced-farmland"]
FEATHER = set(FARM_RICH + FARM_PASTURE + FARM_AEG + ["gravel-wasteland-deep", "steppe-basin-deep"])

BIG = json.load(open(os.path.join(HERE, "assets", "bigtiles.json"))) if os.path.exists(os.path.join(HERE, "assets", "bigtiles.json")) else {}
FARM_RICH = FARM_RICH + BIG.get("rich", []); FARM_AEG = FARM_AEG + BIG.get("aeg", []); FARM_PASTURE = FARM_PASTURE + BIG.get("past", [])
FARM_FLAT = FARM_FLAT + BIG.get("flat", []); DEEP = DEEP + BIG.get("waste", [])
FEATHER |= set(sum(BIG.values(), []))
FEATHER |= set(DEEP) | set(C_RICH + C_PAST + C_WASTE)


def choose(kind, lon, lat, waste, aegean, rnd):
    if kind == "hill":
        if waste:
            return rnd.choice(HILL["dry"])
        return rnd.choice(HILL["ana"] if lat > 35.3 else HILL["pal"])
    peak = kind == "peak"
    if aegean:
        if lon > 26.0 and lat > 36.4:
            return rnd.choice(TAU_P if peak else TAU_M)
        return rnd.choice(GRK_P if peak else GRK_M)
    if waste:
        return rnd.choice(DRY_P if peak else DRY_M)
    if lat > 35.4:
        return rnd.choice(TAU_P if peak else TAU_M)
    if 33.0 < lat < 34.9 and lon < 36.8:
        return rnd.choice(LEB_P if peak else LEB_M)
    return rnd.choice(PAL_P if peak else PAL_M)


_IMG = {}; _SURF = {}


def _img(name, edition):
    k = (name, edition)
    if k not in _IMG:
        im = Image.open(os.path.join(D, name + ".png")).convert("RGBA")
        if edition != "colour":
            a = im.getchannel("A")
            arr = np.asarray(ImageEnhance.Color(im.convert("RGB")).enhance(0.6), np.float32) * np.array([1.0, 0.97, 0.90], np.float32) * 0.94 + 12
            im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA"); im.putalpha(a)
        _IMG[k] = im
    return _IMG[k]


def _surf(name, edition, width):
    width = int(max(8, round(width / 6.0) * 6))
    k = (name, edition, width)
    if k not in _SURF:
        im = _img(name, edition)
        h = max(1, int(round(im.height * width / im.width)))
        im = im.resize((width, h), Image.LANCZOS)
        if name in FEATHER or name in DRYSTRIP or name in DUNES or name in DEEP:
            im = _ragged(im, name)
        if name in FEATHER:
            from PIL import ImageFilter
            a_ = im.getchannel("A")
            r_ = max(2, int(width * 0.035))
            a_ = a_.filter(ImageFilter.MinFilter(2 * (r_ // 2) + 1)).filter(ImageFilter.GaussianBlur(r_ * 0.9))
            im.putalpha(a_)
        a = np.asarray(im, np.float32); al = a[..., 3:4] / 255.0
        buf = np.empty((h, width, 4), np.uint8)
        buf[..., :3] = (a[..., [2, 1, 0]] * al).astype(np.uint8); buf[..., 3] = a[..., 3].astype(np.uint8)
        _SURF[k] = cairo.ImageSurface.create_for_data(bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, width, h, width * 4)
    return _SURF[k]


def draw(c, name, x, y, width, edition, alpha=0.96):
    TUSED[name] = TUSED.get(name, 0) + 1
    s = _surf(name, edition, width)
    c.save()
    c.translate(x - s.get_width() / 2.0, y - 0.93 * s.get_height())
    c.set_source_surface(s, 0, 0)
    c.get_source().set_filter(cairo.FILTER_BEST)
    c.paint_with_alpha(alpha)
    c.restore()

_PATCH_FILES = set(sum([G2P.get(k, []) for k in ('patchg', 'patchw', 'patchd', 'patcha')], []))
_PATCH_IDS = set(x for x in _PATCH_FILES if isinstance(x, int))
