"""Painted city and castle sprites, matched to the catalogue of places by position."""
import json, math, os
import numpy as np
import cairo
from PIL import Image, ImageEnhance
import places as PL

HERE = os.path.dirname(os.path.abspath(__file__))
_META = json.load(open(os.path.join(HERE, "assets", "sprites.json")))
WIDTH = {1: 440, 2: 340, 3: 285, 4: 245}
# Belvoir: shrunk for now; replacement sprite requested (see spec, "needs update")
SCALE = {"Belvoir": 0.72, "Konstantinoupolis": 1.35}
NEEDS_UPDATE = ["Belvoir"]
MATCH = {}            # place name -> sprite record
_pairs = []
for _i, rec in enumerate(_META):
    for t in PL.PLACES:
        if t[0] != rec.get("region", t[0]):
            continue
        d = math.hypot(t[3] - rec["lon"], t[4] - rec["lat"])
        if d < (0.2 if "Natrun" in rec["name"] else 0.08):
            _pairs.append((d, _i, t[5]))
_used = set()
for d, i, nm in sorted(_pairs):
    if i in _used or nm in MATCH:
        continue
    MATCH[nm] = _META[i]; _used.add(i)
UNMATCHED = [r["name"] for i, r in enumerate(_META) if i not in _used]

def _analyse(rec):
    im = Image.open(os.path.join(HERE, "assets", "sprites", rec["file"])).convert("RGBA")
    a = np.asarray(im.resize((140, max(8, int(140 * rec["h"] / rec["w"])))), np.float32)
    op = a[..., 3] > 128
    wat = op & (a[..., 2] > a[..., 0] + 14) & (a[..., 2] >= a[..., 1] - 10)
    rec["harbour"] = bool(wat.sum() / max(1, op.sum()) >= 0.01)       # the picture shows its own water
    # ground contact: cells of the lower half that are mostly painted
    H, W = op.shape
    foot = []
    for gy in range(10):
        y0 = int(H * (0.3 + 0.7 * gy / 10)); y1 = int(H * (0.3 + 0.7 * (gy + 1) / 10))
        for gx in range(14):
            x0 = int(W * gx / 14); x1 = int(W * (gx + 1) / 14)
            if (op & ~wat)[y0:y1, x0:x1].mean() > 0.5:
                foot.append(((gx + 0.5) / 14 - 0.5, 1.0 - (y0 + y1) / 2.0 / H))    # dx as share of width, rise above foot as share of height
    rec["foot"] = foot


for _rec in _META:
    _analyse(_rec)
_IMG = {}
_SURF = {}


def _img(rec, edition):
    k = (rec["file"], edition)
    if k not in _IMG:
        im = Image.open(os.path.join(HERE, "assets", "sprites", rec["file"])).convert("RGBA")
        if edition != "colour":
            a = im.getchannel("A")
            rgb = ImageEnhance.Color(im.convert("RGB")).enhance(0.62)
            arr = np.asarray(rgb, np.float32) * np.array([1.0, 0.965, 0.89], np.float32)
            arr = arr * 0.92 + 14
            im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
            im.putalpha(a)
        _IMG[k] = im
    return _IMG[k]


def _surface(rec, edition, width):
    width = int(max(8, round(width / 8.0) * 8))
    k = (rec["file"], edition, width)
    if k not in _SURF:
        im = _img(rec, edition)
        h = max(1, int(round(im.height * width / im.width)))
        im = im.resize((width, h), Image.LANCZOS)
        a = np.asarray(im, np.float32)
        al = a[..., 3:4] / 255.0
        buf = np.empty((h, width, 4), np.uint8)
        buf[..., :3] = (a[..., [2, 1, 0]] * al).astype(np.uint8)      # cairo wants premultiplied BGRA
        buf[..., 3] = a[..., 3].astype(np.uint8)
        surf = cairo.ImageSurface.create_for_data(bytearray(buf.tobytes()), cairo.FORMAT_ARGB32, width, h, width * 4)
        _SURF[k] = surf
    return _SURF[k]


def width_for(tier, rf, units=512):
    return WIDTH.get(tier, 245) * rf * (min(units / 512.0, 1.4) if units != 512 else 1.0)


def rect(rec, x, y, w):
    h = w * rec["h"] / rec["w"]
    return (x - w / 2, y - h, x + w / 2, y + 7)


def draw(c, rec, x, y, w, edition):
    surf = _surface(rec, edition, w)
    sw, sh = surf.get_width(), surf.get_height()
    gw = w * 0.46
    c.save()
    c.translate(x, y - 1); c.scale(1.0, 0.14)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, gw)
    col = (0.30, 0.27, 0.18)
    g.add_color_stop_rgba(0, *col, 0.30); g.add_color_stop_rgba(1, *col, 0.0)
    c.set_source(g); c.arc(0, 0, gw, 0, 2 * math.pi); c.fill()
    c.restore()
    c.save()
    c.translate(x - sw / 2.0, y - sh)
    c.set_source_surface(surf, 0, 0)
    c.get_source().set_filter(cairo.FILTER_BEST)
    c.paint()
    c.restore()
