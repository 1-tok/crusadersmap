"""Painted sea from the Dutch map's layered-water set: deep and shallow underpaints stretched once over the
whole sheet, blended by distance from shore, then thousands of small transparent wave patches."""
import os, math
import numpy as np
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets", "sea")


def _stretch_rows(img, WS, HS, y0, y1):
    return np.asarray(img.resize((WS, y1 - y0), Image.BICUBIC, box=(0, y0 * img.height / HS, img.width, y1 * img.height / HS)), np.float32)


def _v62_field(WS, HS, S, seed=1662):
    """Approved fine painted wave field (2 Nov), laid as random flipped soft-edged crops, as the Dutch map's v62 does."""
    import random
    from PIL import ImageFilter
    rng = random.Random(seed)
    field = Image.open(os.path.join(A, "field", "fine-painted-wave-field.png")).convert("RGB")
    fw, fh = field.size
    out = field.resize((WS, HS), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40 * S)).convert("RGBA")
    CROP = 560
    size = max(32, int(CROP * 2.0 * S))
    r = np.arange(size, dtype=np.float32)
    ramp = np.clip(np.minimum(r, size - 1 - r) / (size * 0.28), 0, 1); ramp = ramp * ramp * (3 - 2 * ramp)
    mask = Image.fromarray(np.rint(np.outer(ramp, ramp) * 255).astype(np.uint8))
    n = int(3.0 * WS * HS / (size * size * 0.6))
    for _ in range(n):
        sx = rng.randrange(0, fw - CROP); sy = rng.randrange(0, fh - CROP)
        patch = field.crop((sx, sy, sx + CROP, sy + CROP)).resize((size, size), Image.BICUBIC)
        if rng.random() < 0.5:
            patch = patch.transpose(Image.FLIP_LEFT_RIGHT)
        if rng.random() < 0.5:
            patch = patch.transpose(Image.ROTATE_180)
        patch = patch.convert("RGBA"); patch.putalpha(mask)
        out.alpha_composite(patch, (rng.randrange(-size // 2, WS - size // 2), rng.randrange(-size // 2, HS - size // 2)))
    return out.convert("RGB")


def paint_sea(out, seam, S, edition, seed=16621101, count=None, method=None):
    method = method or os.environ.get("SEA_METHOD", "v62")
    HS, WS = seam.shape
    if method == "v62":
        return _paint_v62(out, seam, S, edition)
    if method == "oct31":
        return _paint_oct31(out, seam, S, edition)
    deep = Image.open(os.path.join(A, "underlays", "deep_underpaint_v01.png")).convert("RGB")
    shallow = Image.open(os.path.join(A, "underlays", "shallow_underpaint_v01.png")).convert("RGB")
    # distance from shore, measured on a quarter-size grid
    q = 4
    small = np.asarray(Image.fromarray(seam).resize((WS // q, HS // q), Image.BILINEAR)) > 127
    d = ndimage.distance_transform_edt(small) * q            # in working px
    d = np.asarray(Image.fromarray(d.astype(np.float32), mode="F").resize((WS, HS), Image.BICUBIC), np.float32)
    d = np.maximum(d, 0)
    ref = 96.0 * S                                           # 96 px on the 10800 sheet
    colour = edition == "colour"
    a_sea = 0.97 if colour else 0.34
    for y0 in range(0, HS, 900):
        y1 = min(HS, y0 + 900)
        w = np.exp(-((d[y0:y1] / ref) ** 1.15))[..., None]
        dp = _stretch_rows(deep, WS, HS, y0, y1); sh = _stretch_rows(shallow, WS, HS, y0, y1)
        field = sh * w + dp * (1 - w)
        if not colour:                                       # parchment: a faint grey-green wash over the paper
            field = field * 0.55 + np.array([200, 205, 178], np.float32) * 0.45
        m = (seam[y0:y1].astype(np.float32) / 255.0)[..., None] * a_sea
        out[y0:y1] = out[y0:y1] * (1 - m) + field * m
        del dp, sh, field, w, m
    del d
    # wave patches
    rng = np.random.default_rng(seed)
    waves = []
    for i in range(1, 7):
        im = Image.open(os.path.join(A, "waves", f"wave_v0{i}.png")).convert("RGBA")
        bb = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
        waves.append(im.crop(bb))
    n = count or int(11000 * (S / 0.8) ** 0 * (1.0))
    levels = [(0.35, 36, 92, 0.16, 0.30), (0.40, 44, 112, 0.18, 0.33), (0.25, 36, 96, 0.20, 0.38)]
    if not colour:
        levels = [(a, b, c, lo * 0.55, hi * 0.55) for a, b, c, lo, hi in levels]
    cache = {}
    done = 0
    for frac, wmin, wmax, omin, omax in levels:
        for _ in range(int(n * frac)):
            x = rng.uniform(0, WS); y = rng.uniform(0, HS)
            ix, iy = int(x), int(y)
            if seam[iy, ix] < 250:
                continue
            wid = rng.uniform(wmin, wmax) * S
            k = int(rng.integers(0, 6)); ang = float(rng.uniform(-25, 25)); op = float(rng.uniform(omin, omax))
            key = (k, int(wid / 3), int(ang / 8))
            if key not in cache:
                im = waves[k]; h = max(2, int(round(im.height * wid / im.width)))
                im = im.resize((max(2, int(round(wid))), h), Image.LANCZOS).rotate(ang, expand=True, resample=Image.BICUBIC)
                cache[key] = (np.asarray(im, np.float32), )
                if len(cache) > 900:
                    cache.pop(next(iter(cache)))
            arr = cache[key][0]
            h, w_ = arr.shape[:2]
            x0, y0 = int(x - w_ / 2), int(y - h / 2)
            if x0 < 0 or y0 < 0 or x0 + w_ >= WS or y0 + h >= HS:
                continue
            sm = seam[y0:y0 + h, x0:x0 + w_].astype(np.float32) / 255.0
            a = arr[..., 3:4] / 255.0 * op * (sm[..., None] > 0.98)
            out[y0:y0 + h, x0:x0 + w_] = out[y0:y0 + h, x0:x0 + w_] * (1 - a) + arr[..., :3] * a
            done += 1
    print("sea waves placed", done, flush=True)


def _shore_weight(seam, S, sigma=96.0):
    HS, WS = seam.shape
    q = 4
    small = np.asarray(Image.fromarray(seam).resize((WS // q, HS // q), Image.BILINEAR)) > 127
    d = ndimage.distance_transform_edt(small) * q
    d = np.asarray(Image.fromarray(d.astype(np.float32), mode="F").resize((WS, HS), Image.BICUBIC), np.float32)
    return np.exp(-((np.maximum(d, 0) / (sigma * S)) ** 1.15))


def _paint_v62(out, seam, S, edition):
    HS, WS = seam.shape
    F = _v62_field(WS, HS, S)
    shallow = Image.open(os.path.join(A, "underlays", "shallow_underpaint_v01.png")).convert("RGB")
    wt = _shore_weight(seam, S)
    colour = edition == "colour"
    a_sea = 0.97 if colour else 0.40
    for y0 in range(0, HS, 900):
        y1 = min(HS, y0 + 900)
        fld = np.asarray(F.crop((0, y0, WS, y1)), np.float32)
        sh = _stretch_rows(shallow, WS, HS, y0, y1)
        w = (wt[y0:y1] * 0.6)[..., None]
        fld = sh * w + fld * (1 - w)
        if not colour:
            fld = fld * 0.45 + np.array([205, 208, 182], np.float32) * 0.55
        m = (seam[y0:y1].astype(np.float32) / 255.0)[..., None] * a_sea
        out[y0:y1] = out[y0:y1] * (1 - m) + fld * m
    print("sea v62 field", flush=True)


def _paint_oct31(out, seam, S, edition):
    HS, WS = seam.shape
    under = Image.open(os.path.join(A, "oct31", "sea_continuous_underpaint_1662_v01.png")).convert("RGB")
    colour = edition == "colour"
    a_sea = 0.97 if colour else 0.40
    for y0 in range(0, HS, 900):
        y1 = min(HS, y0 + 900)
        fld = _stretch_rows(under, WS, HS, y0, y1)
        if not colour:
            fld = fld * 0.45 + np.array([205, 208, 182], np.float32) * 0.55
        m = (seam[y0:y1].astype(np.float32) / 255.0)[..., None] * a_sea
        out[y0:y1] = out[y0:y1] * (1 - m) + fld * m
    rng = np.random.default_rng(31)
    waves = [Image.open(os.path.join(A, "oct31", f"sea_wave_cluster_painted_1662_v0{i}.png")).convert("RGBA") for i in (1, 2, 3)]
    for _ in range(int(160 * (WS * HS) / (10800 * 14400 * 0.8 * 0.8) * 0.8 * 0.8 / 0.64 * 0.64 * 1.0) + 160):
        x = rng.uniform(0, WS); y = rng.uniform(0, HS)
        if seam[int(y), int(x)] < 250:
            continue
        wid = rng.uniform(380, 700) * S
        im = waves[int(rng.integers(0, 3))]
        h = int(im.height * wid / im.width)
        a = np.asarray(im.resize((int(wid), h), Image.LANCZOS), np.float32)
        x0, y0 = int(x - wid / 2), int(y - h / 2)
        if x0 < 0 or y0 < 0 or x0 + a.shape[1] >= WS or y0 + h >= HS:
            continue
        sm = (seam[y0:y0 + h, x0:x0 + a.shape[1]] > 250)[..., None]
        al = a[..., 3:4] / 255.0 * (0.5 if colour else 0.3) * sm
        out[y0:y0 + h, x0:x0 + a.shape[1]] = out[y0:y0 + h, x0:x0 + a.shape[1]] * (1 - al) + a[..., :3] * al
