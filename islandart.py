"""Painted Greek island overlays, registered by their WGS84 render boxes and drawn into whichever region holds them."""
import json, os
import numpy as np
import cairo
from PIL import Image, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
ISL = json.load(open(os.path.join(HERE, "assets", "islands.json")))
USED = {}


def _surf(fn, edition, w, h):
    im = Image.open(os.path.join(HERE, "assets", "islands", fn)).convert("RGBA")
    if edition != "colour":
        a = im.getchannel("A")
        arr = np.asarray(ImageEnhance.Color(im.convert("RGB")).enhance(0.6), np.float32) * np.array([1.0, 0.97, 0.90], np.float32) * 0.94 + 12
        im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA"); im.putalpha(a)
    im = im.resize((max(2, w), max(2, h)), Image.LANCZOS)
    a = np.asarray(im, np.float32); al = a[..., 3:4] / 255.0
    buf = np.empty((im.height, im.width, 4), np.uint8)
    buf[..., :3] = (a[..., [2, 1, 0]] * al).astype(np.uint8); buf[..., 3] = a[..., 3].astype(np.uint8)
    return cairo.ImageSurface.create_for_data(bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, im.width, im.height, im.width * 4)


def draw(c, reg, edition, key):
    """c is in region pixel units. Draw every overlay whose box lies inside this region."""
    for r in ISL:
        x0, y0 = reg.ll_px(r["w"], r["n"]); x1, y1 = reg.ll_px(r["e"], r["s"])
        xa, ya = reg.ll_px(r["w"], r["s"]); xb, yb = reg.ll_px(r["e"], r["n"])
        X0 = min(x0, xa); X1 = max(x1, xb); Y0 = min(y0, yb); Y1 = max(y1, ya)
        if X0 < 0 or Y0 < 0 or X1 > reg.w or Y1 > reg.h or X1 - X0 < 6:
            continue
        s = _surf(r["file"], edition, int(round(X1 - X0)), int(round(Y1 - Y0)))
        c.save(); c.set_source_surface(s, X0, Y0); c.get_source().set_filter(cairo.FILTER_BEST); c.paint(); c.restore()
        USED[r["id"]] = key
