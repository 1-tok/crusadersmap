"""Rough frame preview: main map, inset boxes and panel placeholders, at quarter size."""
import json, math, glob
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pyproj import Transformer
from shapely.geometry import shape, box, mapping
from shapely.ops import transform as stransform
import frame as FR

Q = 4                                   # preview at 1/4 of print size
PW, PH = FR.W // Q, FR.H // Q
F = "fonts/"
def font(n, s): return ImageFont.truetype(F + n, s)
INK = (44, 33, 26); SEP = (107, 82, 56); RED = (150, 32, 28); BLUE = (52, 84, 112)


# ------------------------------------------------------------------ data
def load_dem():
    tiles = {}
    for f in glob.glob("data/tiles/*.png"):
        z, x, y = map(int, f.split("/")[-1][:-4].split("_"))
        a = np.asarray(Image.open(f).convert("RGB"), np.float32)
        tiles[(z, x, y)] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    return tiles

TILES = load_dem()

def dem(lon, lat, z):
    n = 2 ** z
    xf = (lon + 180) / 360 * n
    lr = np.radians(lat)
    yf = (1 - np.log(np.tan(lr) + 1 / np.cos(lr)) / math.pi) / 2 * n
    xt, yt = np.floor(xf).astype(int), np.floor(yf).astype(int)
    px = np.clip(((xf - xt) * 256).astype(int), 0, 255)
    py = np.clip(((yf - yt) * 256).astype(int), 0, 255)
    out = np.zeros(lon.shape, np.float32)
    for key in set(zip(xt.ravel(), yt.ravel())):
        t = TILES.get((z,) + key)
        if t is None:
            continue
        m = (xt == key[0]) & (yt == key[1])
        out[m] = t[py[m], px[m]]
    return out

LAND = [shape(f["geometry"]) for f in json.load(open("data/ne_10m_land.geojson"))["features"]] + \
       [shape(f["geometry"]) for f in json.load(open("data/ne_10m_minor_islands.geojson"))["features"]]
LAKES = [shape(f["geometry"]) for f in json.load(open("data/ne_10m_lakes.geojson"))["features"]]
RIVERS = [shape(f["geometry"]) for f in json.load(open("data/ne_10m_rivers_lake_centerlines.geojson"))["features"]]


# ------------------------------------------------------------------ region renderer
class Region:
    def __init__(self, proj, x0, x1, y0, y1, w, h):
        self.fwd = Transformer.from_crs("EPSG:4326", proj, always_xy=True)
        self.inv = Transformer.from_crs(proj, "EPSG:4326", always_xy=True)
        self.x0, self.x1, self.y0, self.y1, self.w, self.h = x0, x1, y0, y1, w, h

    @classmethod
    def from_lonlat(cls, proj, ext, w):
        f = Transformer.from_crs("EPSG:4326", proj, always_xy=True)
        lo0, la0, lo1, la1 = ext
        xs, ys = [], []
        for t in np.linspace(0, 1, 30):
            for lo, la in ((lo0 + (lo1 - lo0) * t, la0), (lo0 + (lo1 - lo0) * t, la1), (lo0, la0 + (la1 - la0) * t), (lo1, la0 + (la1 - la0) * t)):
                x, y = f.transform(lo, la); xs.append(x); ys.append(y)
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        # trim to the inner rectangle so no blank corners: use mid-edge values
        cx = (x0 + x1) / 2
        _, ytop = f.transform((lo0 + lo1) / 2, la1)
        _, ybot = f.transform(lo0, la0)
        xl, _ = f.transform(lo0, la1); xr, _ = f.transform(lo1, la1)
        x0, x1, y0, y1 = xl, xr, ybot, ytop
        h = int(round(w * (y1 - y0) / (x1 - x0)))
        return cls(proj, x0, x1, y0, y1, w, h)

    def px(self, x, y):
        return (x - self.x0) / (self.x1 - self.x0) * self.w, (self.y1 - y) / (self.y1 - self.y0) * self.h

    def ll_px(self, lon, lat):
        return self.px(*self.fwd.transform(lon, lat))

    def lonlat_grid(self, step=1):
        xs = self.x0 + (np.arange(0, self.w, step) + 0.5) / self.w * (self.x1 - self.x0)
        ys = self.y1 - (np.arange(0, self.h, step) + 0.5) / self.h * (self.y1 - self.y0)
        X, Y = np.meshgrid(xs, ys)
        lon, lat = self.inv.transform(X, Y)
        return np.asarray(lon), np.asarray(lat)

    def bbox_ll(self, pad=1.0):
        lon, lat = self.lonlat_grid(step=max(1, self.w // 40))
        return box(lon.min() - pad, lat.min() - pad, lon.max() + pad, lat.max() + pad)

    def geom_px(self, g):
        return stransform(lambda x, y, z=None: self.px(*self.fwd.transform(x, y)), g)

    def polys(self, geoms, draw, fill=None, outline=None, width=1):
        bb = self.bbox_ll()
        for g in geoms:
            if not g.intersects(bb):
                continue
            g = g.intersection(bb)
            for p in getattr(g, "geoms", [g]):
                if p.geom_type != "Polygon" or p.is_empty:
                    continue
                q = self.geom_px(p)
                draw.polygon(list(q.exterior.coords), fill=fill, outline=outline)
                if outline is not None and width > 1:
                    draw.line(list(q.exterior.coords), fill=outline, width=width)
                for r in q.interiors:
                    draw.polygon(list(r.coords), fill=fill and (0,) * len(fill) if isinstance(fill, tuple) else 0)

    def render(self, z, relief_scale=1.0, river_w=2):
        W, H = self.w, self.h
        mask = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(mask)
        self.polys(LAND, md, fill=255)
        lakes = Image.new("L", (W, H), 0)
        self.polys(LAKES, ImageDraw.Draw(lakes), fill=255)
        lon, lat = self.lonlat_grid()
        e = dem(lon, lat, z)
        from scipy import ndimage as _nd
        e = _nd.gaussian_filter(e, 1.2)
        land = np.asarray(mask) > 127
        # parchment
        rng = np.random.default_rng(1)
        n = rng.normal(0, 1, (H // 12 + 2, W // 12 + 2))
        n = np.asarray(Image.fromarray(((n - n.min()) / np.ptp(n) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
        img = np.zeros((H, W, 3), np.float32)
        for k, b in enumerate((240, 229, 203)):
            img[..., k] = b - (n - 0.5) * 14
        # height tint and hill shade on land
        gy, gx = np.gradient(e)
        cell = (self.x1 - self.x0) / W
        shade = np.clip(0.5 + (-gx + gy) / cell * 1.6 * relief_scale, 0, 1)   # light from the north-west
        tint = np.clip(e / 2200, 0, 1)
        for k, (lo, hi) in enumerate(((198, 172), (196, 160), (150, 130))):
            pass
        low = np.array([214, 214, 168], np.float32); mid = np.array([205, 182, 140], np.float32); high = np.array([170, 160, 150], np.float32)
        t1 = np.clip(tint * 2, 0, 1)[..., None]; t2 = np.clip(tint * 2 - 1, 0, 1)[..., None]
        col = low * (1 - t1) + mid * t1
        col = col * (1 - t2) + high * t2
        col = col * (0.82 + 0.36 * shade[..., None])
        a = 0.55
        img[land] = img[land] * (1 - a) + col[land] * a
        lk = np.asarray(lakes) > 127
        img[lk] = img[lk] * 0.6 + np.array([150, 176, 186]) * 0.4
        out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(out)
        # coast and lake shores
        edge = mask.filter(ImageFilter.FIND_EDGES)
        ed = np.asarray(edge) > 60
        o = np.asarray(out).copy(); o[ed] = SEP; out = Image.fromarray(o); d = ImageDraw.Draw(out)
        ledge = np.asarray(lakes.filter(ImageFilter.FIND_EDGES)) > 60
        o = np.asarray(out).copy(); o[ledge] = BLUE; out = Image.fromarray(o); d = ImageDraw.Draw(out)
        # water-lines offshore
        from scipy import ndimage
        dt = ndimage.distance_transform_edt(~land)
        o = np.asarray(out).copy()
        for kk in (5, 11, 19):
            ring = (~land) & (np.abs(dt - kk) < 0.6)
            o[ring] = (o[ring] * 0.6 + np.array(BLUE) * 0.4)
        out = Image.fromarray(o); d = ImageDraw.Draw(out)
        # rivers
        bb = self.bbox_ll()
        for g in RIVERS:
            if not g.intersects(bb):
                continue
            for ln in getattr(g, "geoms", [g]):
                c = [self.ll_px(x, y) for x, y in ln.coords]
                d.line(c, fill=BLUE, width=river_w)
        return out, land


