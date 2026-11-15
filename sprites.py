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
    ys_, xs_ = np.nonzero(op)
    rec["bb"] = ((xs_.min() / float(W), ys_.min() / float(H), (xs_.max() + 1) / float(W), (ys_.max() + 1) / float(H)) if len(xs_) else (0.0, 0.0, 1.0, 1.0))
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


def _water_side(rec):
    """Horizontal centre of the painted water in a sprite, as a share of its width (-0.5 left .. 0.5 right); None if it shows little water."""
    im = Image.open(os.path.join(HERE, "assets", "sprites", rec["file"])).convert("RGBA")
    a = np.asarray(im.resize((140, max(8, int(140 * rec["h"] / rec["w"])))), np.float32)
    op = a[..., 3] > 128
    wat = op & (a[..., 2] > a[..., 0] + 14) & (a[..., 2] >= a[..., 1] - 10)
    if wat.sum() < 0.04 * max(1, op.sum()):
        return None
    xs = np.nonzero(wat)[1]
    return float(xs.mean() / a.shape[1] - 0.5)


def _sea_dir(lon, lat, land, r=0.07):
    """Unit-ish vector (east, north) from the site towards the nearest open sea, from a ring of probe points."""
    from shapely.geometry import Point
    vx = vy = 0.0; n = 0
    for k in range(24):
        ang = 2 * math.pi * k / 24
        for rr in (r, 2 * r):
            p = Point(lon + rr * math.cos(ang) / math.cos(math.radians(lat)), lat + rr * math.sin(ang))
            if not land.contains(p):
                vx += math.cos(ang); vy += math.sin(ang); n += 1
    return (vx / n, vy / n) if n else (0.0, 0.0)


def _decide_flips():
    """A city painted with its harbour on one side is mirrored when the real sea lies on the other side of the site."""
    try:
        import rough as RG
        from shapely.geometry import box
        from shapely.ops import unary_union
        from shapely.prepared import prep
        win = box(18, 28, 38, 43)
        land = prep(unary_union([g.intersection(win) for g in RG.LAND if g.intersects(win)]))
    except Exception:
        return
    for rec in _META:
        rec["flip"] = False
        if rec.get("cat") not in ("city", "castle", "port", "harbour", "town", None):
            pass
        side = _water_side(rec)
        if side is None or abs(side) < 0.10:
            continue
        sx, sy = _sea_dir(rec["lon"], rec["lat"], land)
        if abs(sx) < 0.35:
            continue                                  # sea on both sides, or north/south of the site: leave as painted
        if (side > 0) != (sx > 0):
            rec["flip"] = True
            rec["foot"] = [(-dx, dy) for dx, dy in rec.get("foot", [])]
            FLIPPED.append((rec["name"], round(side, 2), round(sx, 2), round(sy, 2)))


FLIPPED = []
_decide_flips()
_IMG = {}
_SURF = {}


def _img(rec, edition):
    k = (rec["file"], edition)
    if k not in _IMG:
        im = Image.open(os.path.join(HERE, "assets", "sprites", rec["file"])).convert("RGBA")
        # Only a reviewed water mask can safely distinguish harbor water from blue roofs.
        if edition == "colour":
            from water_palette import grade_masked_sprite
            mask_path = os.path.join(HERE, "assets", "sprites", "water-masks", rec["file"])
            if os.path.isfile(mask_path):
                with Image.open(mask_path) as mask:
                    im = grade_masked_sprite(im, mask)
        if edition != "colour":
            a = im.getchannel("A")
            rgb = ImageEnhance.Color(im.convert("RGB")).enhance(0.62)
            arr = np.asarray(rgb, np.float32) * np.array([1.0, 0.965, 0.89], np.float32)
            arr = arr * 0.92 + 14
            im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
            im.putalpha(a)
        if rec.get("flip"):
            from PIL import ImageOps
            im = ImageOps.mirror(im)
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
    """Box of the painted part of the sprite (transparent margins left out), so names can sit right against the picture."""
    h = w * rec["h"] / rec["w"]
    b = rec.get("bb", (0.0, 0.0, 1.0, 1.0))
    if rec.get("flip"):
        b = (1.0 - b[2], b[1], 1.0 - b[0], b[3])
    return (x - w / 2 + b[0] * w, y - h + b[1] * h, x - w / 2 + b[2] * w, y - h + b[3] * h + 4)


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
