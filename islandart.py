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


HOLD = json.load(open(os.path.join(HERE, "assets", "islands_hold.json"))) if os.path.exists(os.path.join(HERE, "assets", "islands_hold.json")) else []
_FIT = {}
_ex = os.path.join(HERE, "assets", "islands_extra.json")
EXTRA = json.load(open(_ex))["islands"] if os.path.exists(_ex) else []


def _fit_hold():
    """Give each held island the bounding box of the real island polygon under its centre point."""
    if _FIT or not HOLD:
        return
    from shapely.geometry import Point
    import rough as RG
    small = [g_ for g in RG.LAND for g_ in getattr(g, "geoms", [g]) if (g_.bounds[2] - g_.bounds[0]) < 2.6 and 19 < g_.bounds[0] < 31]
    taken = [((r["w"] + r["e"]) / 2, (r["s"] + r["n"]) / 2) for r in ISL]
    for h in HOLD:
        p = Point(h["lon"], h["lat"])
        best = min(small, key=lambda g: g.distance(p), default=None)
        if best is None or best.distance(p) > 0.06:
            _FIT[h["id"]] = None; continue
        w, s, e, n = best.bounds
        if any(w <= x <= e and s <= y <= n for x, y in taken):
            _FIT[h["id"]] = "covered"; continue
        taken.append(((w + e) / 2, (s + n) / 2))
        _FIT[h["id"]] = dict(id=h["id"], name=h["name"], file=h["file"], src=h["src"], w=w, s=s, e=e, n=n)


def draw(c, reg, edition, key):
    _fit_hold()
    for h in HOLD:
        r = _FIT.get(h["id"])
        if isinstance(r, dict) and r not in ISL:
            ISL.append(r)
    # small islands placed by a centre point and length from general reference
    if EXTRA:
        mpp = (reg.x1 - reg.x0) / float(reg.w)
        boxes = [(r["w"], r["s"], r["e"], r["n"]) for r in ISL]
        for r in EXTRA:
            if any(w_ <= r["lon"] <= e_ and s_ <= r["lat"] <= n_ for w_, s_, e_, n_ in boxes):
                continue
            x, y = reg.ll_px(r["lon"], r["lat"])
            wd = max(46.0, r["km"] * 1000.0 / mpp * 1.15); ht = wd * r["aspect"]
            if not (wd < x < reg.w - wd and ht < y < reg.h - ht):
                continue
            s = _surf(r["file"], edition, int(round(wd)), int(round(ht)))
            c.save(); c.set_source_surface(s, x - wd / 2, y - ht / 2); c.get_source().set_filter(cairo.FILTER_BEST); c.paint(); c.restore()
            USED[r["id"]] = key
    for r in ISL:
        x0, y0 = reg.ll_px(r["w"], r["n"]); x1, y1 = reg.ll_px(r["e"], r["s"])
        xa, ya = reg.ll_px(r["w"], r["s"]); xb, yb = reg.ll_px(r["e"], r["n"])
        X0 = min(x0, xa); X1 = max(x1, xb); Y0 = min(y0, yb); Y1 = max(y1, ya)
        if X0 < 0 or Y0 < 0 or X1 > reg.w or Y1 > reg.h or X1 - X0 < 6:
            continue
        s = _surf(r["file"], edition, int(round(X1 - X0)), int(round(Y1 - Y0)))
        c.save(); c.set_source_surface(s, X0, Y0); c.get_source().set_filter(cairo.FILTER_BEST); c.paint(); c.restore()
        USED[r["id"]] = key
