import json
"""Painted mountain and foothill pieces, chosen by region and stamped along the existing relief."""
import os
import numpy as np
import cairo
from PIL import Image, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "assets", "terrain")
DRYSTRIP = ["gravel-wasteland", "rocky-desert", "dry-scrub-steppe", "eroded-badlands", "salt-flat", "desert-escarpment", "dune-transition"]
DUNES = ["sand-dunes", "dune-transition"]
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
        "patchd": G2P.get("patchd", []), "patcha": G2P.get("patcha", []), "delta": G2P.get("delta", []) + G2P.get("green", [])[:4]}
POOL_SHIP = G2P.get("ship", [])
GSIZE = {"green": (120, 150), "past": (120, 150), "arid": (115, 145), "oasis": (120, 150), "vegg": (70, 95), "vegd": (60, 85), "vega": (70, 90),
         "rock": (95, 130), "ruin": (105, 130), "patchg": (190, 240), "patchw": (190, 240), "patchd": (190, 240), "patcha": (200, 250), "delta": (115, 140)}


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


DEEP = ["gravel-wasteland-deep", "steppe-basin-deep"]
FARM_RICH = ["levant-farmland", "orchard-field-mosaic", "river-floodplain-fields", "orchard-field-mosaic", "levant-farmland"]
FARM_FLAT = ["river-floodplain-fields", "levant-farmland", "river-floodplain-fields"]
FARM_PASTURE = ["dry-stone-pasture"]
FARM_AEG = ["aegean-terraced-farmland", "aegean-island-interior", "aegean-terraced-farmland"]
FEATHER = set(FARM_RICH + FARM_PASTURE + FARM_AEG + ["gravel-wasteland-deep", "steppe-basin-deep"])

FEATHER |= set(C_RICH + C_PAST + C_WASTE)


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
