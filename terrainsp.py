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
        a = np.asarray(im, np.float32); al = a[..., 3:4] / 255.0
        buf = np.empty((h, width, 4), np.uint8)
        buf[..., :3] = (a[..., [2, 1, 0]] * al).astype(np.uint8); buf[..., 3] = a[..., 3].astype(np.uint8)
        _SURF[k] = cairo.ImageSurface.create_for_data(bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, width, h, width * 4)
    return _SURF[k]


def draw(c, name, x, y, width, edition, alpha=0.96):
    s = _surf(name, edition, width)
    c.save()
    c.translate(x - s.get_width() / 2.0, y - 0.93 * s.get_height())
    c.set_source_surface(s, 0, 0)
    c.get_source().set_filter(cairo.FILTER_BEST)
    c.paint_with_alpha(alpha)
    c.restore()
