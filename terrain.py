"""Hand-drawn terrain for the Crusader States sheet: washes (two editions) and an ink layer
(coasts, water-lines, rivers, mountains, hills, forests, marshes, dunes)."""
import math, random
import numpy as np
import cairo
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage as nd
from shapely.geometry import box, LineString, Polygon, MultiPolygon, Point
from shapely.ops import unary_union
import rough as RG
from rough import Region, TILES, LAND, LAKES, dem
from hand import Pen, INK, SEPIA
import ridges as RD
import terrainsp as TSP
from lettering import catmull as _catmull
from shapely.affinity import scale as _sscale

BLUEINK = (0.20, 0.33, 0.45)
MODERN_LAKES = ("Assad", "Ataturk", "Keban", "Tuz", "Great Bitter", "Saksak", "Egirdir", "Eğirdir", "Beyşehir", "Beysehir")
EXTRA_RIVERS = [  # medieval courses missing from the modern dataset (lon, lat)
    [(36.4, 34.2), (36.55, 34.45), (36.72, 34.73), (36.75, 35.13), (36.55, 35.4), (36.38, 35.7), (36.3, 35.95), (36.2, 36.2), (36.08, 36.12), (35.97, 36.08)],
    [(36.1, 33.9), (35.85, 33.6), (35.6, 33.35), (35.25, 33.33)],
    [(36.2, 32.75), (35.9, 32.7), (35.65, 32.68)],
    [(35.95, 37.6), (35.65, 37.2), (35.4, 36.95), (35.05, 36.75)],
    [(34.9, 37.0), (34.9, 36.8)],
]


# ------------------------------------------------------------------ elevation
def dem_best(lon, lat):
    """Elevation, from z7 tiles where present, otherwise z6."""
    e = dem(lon, lat, 7)
    n = 2 ** 7
    xt = np.floor((lon + 180) / 360 * n).astype(int)
    lr = np.radians(lat)
    yt = np.floor((1 - np.log(np.tan(lr) + 1 / np.cos(lr)) / math.pi) / 2 * n).astype(int)
    have = np.zeros(lon.shape, bool)
    for key in set(zip(xt.ravel(), yt.ravel())):
        if (7,) + key in TILES:
            have |= (xt == key[0]) & (yt == key[1])
    if not have.all():
        e6 = dem(lon, lat, 6)
        e = np.where(have, e, e6)
    return e


def lonlat_km(lon, lat, lo0, la0):
    return (lon - lo0) * 111.0 * math.cos(math.radians(la0)), (lat - la0) * 111.0


def zone_field(lon, lat, zones):
    f = np.zeros(lon.shape, np.float32)
    for lo, la, r in zones:
        dx = (lon - lo) * 111.0 * math.cos(math.radians(la))
        dy = (lat - la) * 111.0
        f = np.maximum(f, np.exp(-(dx * dx + dy * dy) / (r * r)).astype(np.float32))
    return f


# ------------------------------------------------------------------ per-region content
MAIN = dict(
    green=[(35.5, 36.9, 75), (36.4, 36.1, 60), (37.0, 36.2, 45), (35.9, 35.3, 55), (36.1, 34.0, 45), (36.3, 33.5, 38),
           (35.4, 32.8, 55), (34.95, 32.2, 45), (35.2, 31.7, 35), (34.5, 31.45, 38), (36.7, 34.9, 38), (33.4, 35.1, 55),
           (35.2, 33.5, 35), (35.6, 34.4, 30), (35.9, 34.7, 28), (36.3, 33.5, 32), (36.55, 32.7, 40)],
    desert=[(35.2, 30.2, 110), (36.9, 33.0, 90), (37.4, 34.2, 70), (36.9, 31.5, 100)],
    conifer=[(36.2, 36.8, 30), (34.3, 37.1, 55), (36.15, 35.4, 30), (35.75, 34.2, 28), (32.9, 34.95, 30), (33.3, 35.3, 10), (36.5, 37.4, 35)],
    decid=[(35.2, 32.9, 28), (35.75, 32.35, 22), (35.4, 33.2, 18), (36.4, 36.3, 18)],
    marsh=[(36.3, 35.55, 17, 6), (36.3, 36.3, 13, 9), (35.6, 33.1, 8, 7), (33.6, 34.9, 7, 5), (35.55, 32.0, 6, 4)],
    dune=[(35.2, 30.0, 70), (36.9, 31.5, 70)],
    oasis=[(36.83, 31.9)],
    spacing=1.0,
)
AEGEAN = dict(
    green=[(22.0, 37.8, 80), (23.7, 38.0, 60), (22.9, 40.6, 70), (26.0, 38.4, 80), (28.0, 37.5, 90), (25.0, 35.3, 40), (21.0, 39.5, 70), (27.0, 40.3, 60)],
    desert=[(29.5, 38.9, 60)],
    conifer=[(22.2, 37.6, 40), (22.0, 40.1, 50), (24.0, 41.4, 70), (29.2, 37.3, 60), (26.0, 40.4, 50), (20.9, 39.8, 60)],
    decid=[(23.4, 38.6, 40), (21.2, 38.5, 50), (27.5, 38.5, 40), (25.0, 35.3, 20)],
    marsh=[],
    dune=[],
    spacing=1.0,
)
DELTA = dict(
    green=[(31.0, 31.0, 110), (31.3, 30.3, 60), (32.1, 30.7, 60), (32.0, 29.8, 18)],
    desert=[(33.5, 30.0, 150), (30.2, 30.0, 150), (34.3, 28.8, 90)],
    conifer=[],
    decid=[],
    marsh=[(31.7, 31.45, 38, 14), (30.9, 31.5, 22, 8), (31.3, 31.3, 35, 10), (30.1, 31.0, 35, 8), (32.3, 31.2, 28, 10), (32.4, 30.3, 12, 8)],
    dune=[(33.5, 30.3, 140), (30.2, 29.5, 120), (34.4, 28.6, 70)],
    oasis=[(33.65, 28.72), (32.65, 29.88), (33.78, 29.9), (33.85, 31.12), (30.1, 29.62)],
    spacing=1.0,
    palms=True,
)


class Terrain:
    def __init__(self, reg, content, seed=1, S=0.4):
        """reg: Region at print scale (w, h in print px). S: preview scale."""
        self.reg = reg
        self.c = content
        self.S = S
        self.seed = seed
        self.W, self.H = reg.w, reg.h
        self.ws, self.hs = int(round(reg.w * S)), int(round(reg.h * S))
        self.mpp = (reg.x1 - reg.x0) / reg.w
        self.m = float(np.clip((61.0 / self.mpp) ** 0.55, 0.45, 1.0))
        if self.mpp > 150:
            self.m *= 0.62
        self.rs = Region.__new__(Region)
        self.rs.__dict__.update(reg.__dict__)
        self.rs.w, self.rs.h = self.ws, self.hs
        self._fields()

    # -------------------------------------------------------------- fields at low resolution
    def _fields(self):
        S = self.S
        lw = max(200, int(self.W * 0.1)); lh = int(round(lw * self.H / self.W))
        self.lw, self.lh = lw, lh
        lr = Region.__new__(Region); lr.__dict__.update(self.reg.__dict__); lr.w, lr.h = lw, lh
        self.lr = lr
        lon, lat = lr.lonlat_grid()
        self.lon, self.lat = lon, lat
        mask = Image.new("L", (lw, lh), 0)
        lr.polys(LAND, ImageDraw.Draw(mask), fill=255)
        self.land_l = np.asarray(mask) > 127
        # sea, lakes and rivers together: sprites without a harbour keep off all of it
        wm = Image.new("L", (lw, lh), 0)
        wd = ImageDraw.Draw(wm)
        lr.polys(self._lakes(), wd, fill=255)
        bbl = lr.bbox_ll()
        for g in list(RIVERS) + [LineString(r) for r in EXTRA_RIVERS]:
            if not g.intersects(bbl):
                continue
            gi = g.intersection(bbl)
            for ln in getattr(gi, "geoms", [gi]):
                if ln.geom_type == "LineString" and not ln.is_empty and len(ln.coords) > 1:
                    wd.line([lr.ll_px(x, y) for x, y in ln.coords], fill=255, width=2)
        self.water_l = (~self.land_l) | (np.asarray(wm) > 127)
        self.elev = np.where(self.land_l, nd.gaussian_filter(dem_best(lon, lat), 1.0), 0).astype(np.float32)
        km_px = self.mpp * self.W / lw / 1000.0
        self.km_px = km_px
        sg = max(2.0, 30.0 / (self.mpp * self.W / lw / 1000.0)); lf = self.land_l.astype(np.float32)
        self.rel = (self.elev - nd.gaussian_filter(self.elev, sg) / np.maximum(nd.gaussian_filter(lf, sg), 0.05)).astype(np.float32)
        self.rel[~self.land_l] = 0
        self.dsea = nd.distance_transform_edt(~self.land_l) * km_px          # km offshore
        self.dland = nd.distance_transform_edt(self.land_l) * km_px          # km inland
        self.green = zone_field(lon, lat, self.c["green"])
        self.desert = zone_field(lon, lat, self.c["desert"]) if self.c["desert"] else np.zeros_like(lon)
        self.fert = np.clip(np.maximum(self.green * 0.95, np.exp(-self.dland / 55.0) * 0.55) * (1 - 0.8 * self.desert), 0, 1).astype(np.float32)
        self.avoid_rects = []
        self.avoid_disks = []

    # -------------------------------------------------------------- wash
    def wash(self, edition, r0=0, r1=None):
        """RGB float array for rows r0:r1 of the region at its working size; parchment edition is lighter."""
        ws, hs = self.ws, self.hs
        r1 = hs if r1 is None else r1
        P = 6
        R0, R1 = max(0, r0 - P), min(hs, r1 + P)
        nh = R1 - R0

        def up(a):
            sh, sw = a.shape
            im = Image.fromarray(a.astype(np.float32), mode="F").resize((ws, nh), Image.BICUBIC, box=(0, R0 * sh / hs, sw, R1 * sh / hs))
            return np.asarray(im)

        rsS = Region.__new__(Region); rsS.__dict__.update(self.rs.__dict__)
        dy = self.reg.y1 - self.reg.y0
        rsS.y1 = self.reg.y1 - dy * R0 / hs; rsS.y0 = self.reg.y1 - dy * R1 / hs; rsS.h = nh; rsS.w = ws
        mask = Image.new("L", (ws, nh), 0)
        rsS.polys(LAND, ImageDraw.Draw(mask), fill=255)
        lakes = Image.new("L", (ws, nh), 0)
        rsS.polys(self._lakes(), ImageDraw.Draw(lakes), fill=255)
        land = np.asarray(mask.filter(ImageFilter.GaussianBlur(0.8)), np.float32)[..., None] / 255
        lake = np.asarray(lakes.filter(ImageFilter.GaussianBlur(0.8)), np.float32)[..., None] / 255
        dsea = up(self.dsea)[..., None]
        dland = up(self.dland)[..., None]
        elev = np.clip(up(self.elev), 0, 4000)[..., None]
        green = np.clip(up(self.green), 0, 1)[..., None]
        desert = np.clip(up(self.desert), 0, 1)[..., None]
        coastal = np.exp(-dland / 55.0)
        fert = np.clip(up(self.fert), 0, 1)[..., None]
        fert = np.clip((fert - 0.12) / 0.62, 0, 1)
        fert = fert * fert * (3 - 2 * fert)
        high = np.clip((elev - 700) / 1100, 0, 1)
        mid = np.clip((elev - 250) / 500, 0, 1) * (1 - high)

        if edition == "colour":
            sea_far = np.array([150, 186, 202], np.float32)
            sea_near = np.array([108, 152, 178], np.float32)
            wsea = np.exp(-dsea / 30.0)
            sea = sea_far * (1 - wsea) + sea_near * wsea
            c_des = np.array([234, 206, 138], np.float32); c_ste = np.array([216, 192, 112], np.float32)
            c_fer = np.array([116, 164, 84], np.float32); c_hil = np.array([176, 160, 112], np.float32)
            c_mnt = np.array([172, 150, 126], np.float32)
            lake_c = np.array([112, 158, 184], np.float32)
            a_land, a_sea = 0.92, 0.88
        else:
            sea_far = np.array([228, 226, 206], np.float32)
            sea_near = np.array([201, 213, 203], np.float32)
            wsea = np.exp(-dsea / 22.0)
            sea = sea_far * (1 - wsea) + sea_near * wsea
            c_des = np.array([240, 221, 170], np.float32); c_ste = np.array([230, 212, 160], np.float32)
            c_fer = np.array([178, 198, 134], np.float32); c_hil = np.array([208, 192, 150], np.float32)
            c_mnt = np.array([200, 182, 156], np.float32)
            lake_c = np.array([186, 205, 204], np.float32)
            a_land, a_sea = 0.62, 0.70
        ground = c_des * (1 - fert) * (1 - 0.0) + (c_ste * (1 - fert) * 0)  # placeholder to keep shapes
        base = c_ste * (1 - desert) + c_des * desert
        ground = base * (1 - fert) + c_fer * fert
        ground = ground * (1 - mid * 0.55) + c_hil * mid * 0.55
        ground = ground * (1 - high * 0.8) + c_mnt * high * 0.8
        col = ground * land + sea * (1 - land)
        col = col * (1 - lake) + lake_c * lake
        alpha = a_land * land + a_sea * (1 - land)
        sl = slice(r0 - R0, r0 - R0 + (r1 - r0))
        self._ml = land[sl, :, 0].copy(); self._lk = lake[sl, :, 0].copy()
        return col[sl].astype(np.float32), alpha[sl].astype(np.float32)

    def _lakes(self):
        out = []
        for f in LAKES:
            pass
        return LAKES_OK

    # -------------------------------------------------------------- ink
    def ink(self, ctx, edition, rng_seed=None):
        """Draw the ink layer into ctx (already translated and scaled to this region's print px)."""
        seed = self.seed if rng_seed is None else rng_seed
        rnd = random.Random(seed)
        c = ctx
        W, H = self.W, self.H
        reg = self.reg
        bb = reg.bbox_ll(pad=3.0)
        c.save(); c.rectangle(0, 0, W, H); c.clip()
        fill_h = (0.90, 0.85, 0.74) if edition == "parchment" else (0.84, 0.79, 0.69)
        fill_m = (0.88, 0.83, 0.74) if edition == "parchment" else (0.80, 0.75, 0.67)
        pen = Pen(c, seed=seed, amp=0.8, ink=INK, paper=fill_h)

        # --- coasts and water-lines
        land_parts = []
        for g in LAND:
            if g.intersects(bb):
                land_parts.append(g.intersection(bb))
        land_u = unary_union(land_parts).simplify(self.mpp / 111000.0 * 2.0)
        polys = list(land_u.geoms) if hasattr(land_u, "geoms") else [land_u]
        cw = 1.8
        k = 1.4
        c.save(); c.scale(k, k)
        p2 = Pen(c, seed=seed + 1, amp=0.9, ink=INK, paper=fill_h)
        for poly in polys:
            if poly.geom_type != "Polygon" or poly.is_empty:
                continue
            q = reg.geom_px(poly)
            pts = [(x / k, y / k) for x, y in q.exterior.coords]
            if len(pts) > 4 and Polygon(q.exterior).length > 60:
                p2.line(pts, w=cw)
        c.restore()
        # water-lines: contour echoes offshore, drawn lighter each time
        for i, (px, wd, al) in enumerate(((16, 1.2, 0.8), (40, 1.0, 0.55), (74, 0.9, 0.35))):
            d = px * self.mpp / 111000.0
            buf = land_u.buffer(d)
            geoms = list(buf.geoms) if hasattr(buf, "geoms") else [buf]
            c.save(); c.scale(1.0, 1.0)
            for gg in geoms:
                if gg.is_empty or gg.geom_type != "Polygon":
                    continue
                q = reg.geom_px(gg)
                pts = list(q.exterior.coords)
                if Polygon(pts).length < 200:
                    continue
                # break the line into dashes, a hand-ruled broken contour
                n = len(pts)
                j = 0
                while j < n - 2:
                    L = rnd.randint(14, 34)
                    seg = pts[j:j + L]
                    if len(seg) > 2:
                        pw = Pen(c, seed=rnd.randint(1, 10 ** 6), amp=0.8, ink=BLUEINK)
                        c.save(); c.set_source_rgba(*BLUEINK, al)
                        pw.line(seg, w=wd, col=BLUEINK)
                        c.restore()
                    j += L + rnd.randint(1, 5)
            c.restore()

        # --- rivers: smoothed, meandering, and broken off at every lake
        rivers = []
        for g in RIVERS:
            if g.intersects(bb):
                rivers.append(g)
        ccf = []
        for g in rivers:
            gi = g.intersection(bb)
            for ln in getattr(gi, "geoms", [gi]):
                if ln.geom_type == "LineString" and not ln.is_empty:
                    ccf.append(list(ln.coords))
        ccf = [r for r in ccf if len(r) > 1]
        lk_list = [g for g in self._lakes() if g.intersects(bb)]
        lk = unary_union(lk_list).buffer(0.002) if lk_list else None
        for r in EXTRA_RIVERS + ccf:
            ll = [(x, y) for x, y in r]
            if not any(bb.contains(Point(x, y)) for x, y in ll[::max(1, len(ll) // 6)]):
                continue
            ls = LineString(ll)
            parts = [ls]
            if lk is not None:
                d = ls.difference(lk)
                parts = list(getattr(d, "geoms", [d]))
            for part in parts:
                if part.geom_type != "LineString" or part.is_empty or len(part.coords) < 2:
                    continue
                pts = [reg.ll_px(x, y) for x, y in part.coords]
                pts = _catmull(pts, step=7.0) if len(pts) > 2 else pts
                if len(pts) < 3:
                    continue
                cum = [0.0]
                for i in range(1, len(pts)):
                    cum.append(cum[-1] + math.dist(pts[i - 1], pts[i]))
                ph = rnd.uniform(0, 6.28); wl = rnd.uniform(110, 190); amp = min(9.0, cum[-1] / 40.0) * self.m
                out = []
                for i, (x, y) in enumerate(pts):
                    j = min(len(pts) - 1, i + 1); k0 = max(0, i - 1)
                    tx, ty = pts[j][0] - pts[k0][0], pts[j][1] - pts[k0][1]
                    L = math.hypot(tx, ty) or 1.0
                    o = amp * math.sin(cum[i] / wl * 6.283 + ph) * min(1.0, cum[i] / 60.0, (cum[-1] - cum[i]) / 60.0 + 0.2)
                    out.append((x - ty / L * o, y + tx / L * o))
                pr = Pen(c, seed=rnd.randint(1, 10 ** 6), amp=0.6, ink=BLUEINK)
                pr.line(out, w=2.2, col=BLUEINK)

        # --- lakes
        for g in self._lakes():
            if not g.intersects(bb):
                continue
            for pg in getattr(g, "geoms", [g]):
                if pg.geom_type != "Polygon":
                    continue
                q = reg.geom_px(pg)
                pts = [(x / 1.5, y / 1.5) for x, y in q.exterior.coords]
                if len(pts) < 5:
                    continue
                c.save(); c.scale(1.5, 1.5)
                pl = Pen(c, seed=rnd.randint(1, 10 ** 6), amp=0.7, ink=BLUEINK)
                pl.line(pts, w=1.4, col=BLUEINK)
                c.restore()

        # --- placement fields
        S_l = (self.lw / self.W)

        def at(x, y):
            ix = min(self.lw - 1, max(0, int(x * S_l))); iy = min(self.lh - 1, max(0, int(y * S_l)))
            return ix, iy

        def elev_at(x, y):
            ix, iy = at(x, y); return float(self.elev[iy, ix])

        def rel_at(x, y):
            ix, iy = at(x, y); return float(self.rel[iy, ix])

        m = self.m

        def land_at(x, y):
            ix, iy = at(x, y); return bool(self.land_l[iy, ix])

        items = []  # (y, kind, x, y, size, seed, extra)

        # mountains and hills from elevation: one jittered grid
        cell = 112 * m
        grid = {}
        for gy in range(0, int(H // cell) + 1):
            for gx in range(0, int(W // cell) + 1):
                x = (gx + 0.5 + rnd.uniform(-0.42, 0.42)) * cell
                y = (gy + 0.5 + rnd.uniform(-0.42, 0.42)) * cell
                if not (30 < x < W - 30 and 30 < y < H - 20) or not land_at(x, y):
                    continue
                e = elev_at(x, y); rl = rel_at(x, y)
                if rl < 150 and e < 1100:
                    continue
                if rl < 150 and rnd.random() > 0.35:
                    continue
                if e > 1700 or rl > 450:
                    kind, size = "peak", (rnd.uniform(150, 200) + min(60, max(0, e - 1700) / 20)) * m
                elif rl > 260 or e > 1100:
                    kind, size = "mount", rnd.uniform(120, 170) * m
                else:
                    kind, size = "mount", rnd.uniform(95, 130) * m
                items.append((y, kind, x, y, size, rnd.randint(1, 10 ** 6), None))
                grid.setdefault((int(x // (90 * m)), int(y // (90 * m))), []).append((x, y))
        # low hills
        cell2 = 52 * m
        for gy in range(0, int(H // cell2) + 1):
            for gx in range(0, int(W // cell2) + 1):
                x = (gx + 0.5 + rnd.uniform(-0.45, 0.45)) * cell2
                y = (gy + 0.5 + rnd.uniform(-0.45, 0.45)) * cell2
                if not (30 < x < W - 30 and 30 < y < H - 20) or not land_at(x, y):
                    continue
                e = elev_at(x, y); rl = rel_at(x, y)
                if not (55 < rl < 150):
                    continue
                if rnd.random() > (rl - 55) / 95 * 0.85:
                    continue
                near = False
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        for mx, my in grid.get((int(x // (90 * m)) + dx, int(y // (90 * m)) + dy), []):
                            if (mx - x) ** 2 + (my - y) ** 2 < (70 * m) ** 2:
                                near = True
                if near:
                    continue
                items.append((y, "hill", x, y, rnd.uniform(36, 54) * m, rnd.randint(1, 10 ** 6), None))
        hill_grid = grid

        # forests
        def zone_p(x, y, zones):
            lo, la = self.reg.inv.transform(self.reg.x0 + x / W * (self.reg.x1 - self.reg.x0), self.reg.y1 - y / H * (self.reg.y1 - self.reg.y0))
            f = 0.0
            for zlo, zla, r in zones:
                dx = (lo - zlo) * 111 * math.cos(math.radians(zla)); dy = (la - zla) * 111
                f = max(f, math.exp(-(dx * dx + dy * dy) / (r * r)))
            return f

        cellf = 46 * m
        for kind, zones in (("conifer", self.c["conifer"]), ("decid", self.c["decid"])):
            if not zones:
                continue
            for gy in range(0, int(H // cellf) + 1):
                for gx in range(0, int(W // cellf) + 1):
                    x = (gx + 0.5 + rnd.uniform(-0.45, 0.45)) * cellf
                    y = (gy + 0.5 + rnd.uniform(-0.45, 0.45)) * cellf
                    if not (30 < x < W - 30 and 30 < y < H - 20) or not land_at(x, y):
                        continue
                    if rnd.random() > zone_p(x, y, zones) * 0.9:
                        continue
                    e = elev_at(x, y)
                    if e > 2200:
                        continue
                    clash = False
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            for mx, my in hill_grid.get((int(x // (90 * m)) + dx, int(y // (90 * m)) + dy), []):
                                if (mx - x) ** 2 + (my - y) ** 2 < (62 * m) ** 2:
                                    clash = True
                    if clash:
                        continue
                    items.append((y, kind, x, y, rnd.uniform(44, 62) * m, rnd.randint(1, 10 ** 6), None))
        # marshes
        for lo, la, rx, ry in self.c["marsh"]:
            cx, cy = reg.ll_px(lo, la)
            rpx = rx * 1000 / self.mpp; rpy = ry * 1000 / self.mpp
            n = int(rpx * rpy / ((60 * m) ** 2) * 3.2) + 3
            for _ in range(n):
                a = rnd.uniform(0, 2 * math.pi); r = math.sqrt(rnd.random())
                x = cx + rpx * r * math.cos(a); y = cy + rpy * r * math.sin(a)
                if 20 < x < W - 20 and 20 < y < H - 20:
                    items.append((y, "marsh", x, y, rnd.uniform(40, 56) * m, rnd.randint(1, 10 ** 6), None))
        # dunes
        cellg = 150 * m
        if self.c["dune"]:
            for gy in range(0, int(H // cellg) + 1):
                for gx in range(0, int(W // cellg) + 1):
                    x = (gx + 0.5 + rnd.uniform(-0.45, 0.45)) * cellg
                    y = (gy + 0.5 + rnd.uniform(-0.45, 0.45)) * cellg
                    if not (30 < x < W - 30 and 30 < y < H - 20) or not land_at(x, y):
                        continue
                    if rnd.random() > zone_p(x, y, self.c["dune"]) * 0.7:
                        continue
                    if elev_at(x, y) > 700:
                        continue
                    items.append((y - 1e6, "drystrip", x, y, rnd.uniform(300, 400) * m, rnd.randint(1, 10 ** 6), "dune"))
        # palms along the Nile branches
        if self.c.get("palms"):
            for g in RIVERS:
                if not g.intersects(bb):
                    continue
                gi = g.intersection(bb)
                for ln in getattr(gi, "geoms", [gi]):
                    if ln.geom_type != "LineString" or ln.is_empty:
                        continue
                    pts = [reg.ll_px(x, y) for x, y in ln.coords]
                    if len(pts) < 2:
                        continue
                    L = LineString(pts)
                    if L.length < 200:
                        continue
                    s = 40.0
                    while s < L.length:
                        pnt = L.interpolate(s)
                        for sgn in (-1, 1):
                            if rnd.random() < 0.55:
                                x = pnt.x + sgn * rnd.uniform(14, 40) * m; y = pnt.y + rnd.uniform(-12, 12)
                                if 20 < x < W - 20 and 20 < y < H - 20 and land_at(x, y):
                                    items.append((y, "palm", x, y, rnd.uniform(34, 46) * m, rnd.randint(1, 10 ** 6), None))
                        s += rnd.uniform(34, 62)

        # --- fertile land and wasteland: tufts of grass against scrub and stipple
        fert_l = self.fert
        def fert_at(x, y):
            ix, iy = at(x, y); return float(fert_l[iy, ix])
        cellt = 64 * m
        for gy in range(0, int(H // cellt) + 1):
            for gx in range(0, int(W // cellt) + 1):
                x = (gx + 0.5 + rnd.uniform(-0.45, 0.45)) * cellt
                y = (gy + 0.5 + rnd.uniform(-0.45, 0.45)) * cellt
                if not (30 < x < W - 30 and 30 < y < H - 20) or not land_at(x, y):
                    continue
                f = fert_at(x, y); e = elev_at(x, y)
                if f > 0.5 and e < 800:
                    if rnd.random() < (f - 0.45) * 0.55:
                        items.append((y, "tuft", x, y, rnd.uniform(24, 34) * m, rnd.randint(1, 10 ** 6), None))
                elif f < 0.28 and e < 1500 and self.dland[at(x, y)[1], at(x, y)[0]] > 6:
                    if rnd.random() < 0.40:
                        items.append((y, "scrub", x, y, rnd.uniform(26, 38) * m, rnd.randint(1, 10 ** 6), None))
        cellw = 230 * m
        for gy in range(0, int(H // cellw) + 1):
            for gx in range(0, int(W // cellw) + 1):
                x = (gx + 0.5 + rnd.uniform(-0.4, 0.4)) * cellw
                y = (gy + 0.5 + rnd.uniform(-0.4, 0.4)) * cellw
                if not (30 < x < W - 30 and 30 < y < H - 20) or not land_at(x, y):
                    continue
                if fert_at(x, y) < 0.22 and elev_at(x, y) < 1200 and self.dland[at(x, y)[1], at(x, y)[0]] > 10 and rnd.random() < 0.55:
                    items.append((y - 1e6, "drystrip", x, y, rnd.uniform(320, 440) * m, rnd.randint(1, 10 ** 6), "waste"))
        for lo, la in self.c.get("oasis", []):
            cx, cy = reg.ll_px(lo, la)
            if 20 < cx < W - 20 and 20 < cy < H - 20:
                items.append((cy, "oasis", cx, cy, 120 * m, rnd.randint(1, 10 ** 6), None))

        # --- keep glyphs on real land (islands included), clear of the coast
        import shapely
        keep = []
        arr = np.array([(it[2], it[3]) for it in items]) if items else np.zeros((0, 2))
        if len(arr):
            X = reg.x0 + arr[:, 0] / W * (reg.x1 - reg.x0); Y = reg.y1 - arr[:, 1] / H * (reg.y1 - reg.y0)
            lo, la = reg.inv.transform(X, Y)
            lo = np.asarray(lo); la = np.asarray(la)
            deg = self.mpp / 111000.0
            inner = {}
            def inner_geom(frac):
                if frac not in inner:
                    inner[frac] = land_u.buffer(-frac * deg)
                return inner[frac]
            for i, it in enumerate(items):
                kind, size = it[1], it[4]
                if kind in ("marsh", "oasis"):
                    keep.append(it); continue
                if kind in ("tuft", "scrub"):
                    frac = 0
                    if shapely.contains_xy(land_u, lo[i], la[i]):
                        keep.append(it)
                    continue
                frac = 0.42 * size * (2.6 if kind == "hill" else 2.2)
                if self.mpp > 150:                      # Aegean: keep islands clear
                    if kind == "hill":
                        continue
                    frac = 0.75 * size
                frac = round(frac / 8) * 8
                g = inner_geom(frac) if frac > 0 else land_u
                if shapely.contains_xy(g, lo[i], la[i]):
                    keep.append(it)
        def blocked(it):
            kd, x, y, sz = it[1], it[2], it[3], it[4]
            if kd == "oasis":
                return False
            if kd == "drystrip":
                gr = (x - 0.45 * sz, y - 0.18 * sz, x + 0.45 * sz, y + 0.05 * sz)
                return any(not (gr[2] < r[0] or r[2] < gr[0] or gr[3] < r[1] or r[3] < gr[1]) for r in self.avoid_rects)
            if kd in ("peak", "mount", "hill"):
                gr = (x - 0.9 * sz, y - 0.55 * sz, x + 0.9 * sz, y + 0.06 * sz)
            else:
                gr = (x - 0.5 * sz, y - 0.9 * sz, x + 0.5 * sz, y + 0.1 * sz)
            for r in self.avoid_rects:
                if not (gr[2] < r[0] or r[2] < gr[0] or gr[3] < r[1] or r[3] < gr[1]):
                    return True
            for dx_, dy_, rad in self.avoid_disks:
                if (x - dx_) ** 2 + (y - 0.4 * sz - dy_) ** 2 < (rad + 0.45 * sz) ** 2:
                    return True
            return False
        items = [it for it in keep if not blocked(it)]
        self.glyph_rects = [(x - 0.9 * sz, y - 0.55 * sz, x + 0.9 * sz, y + 0.06 * sz) for _, kd, x, y, sz, _s, _e in items if kd in ("peak", "mount", "hill")]
        # --- draw back to front
        items.sort(key=lambda t: t[0])
        for _, kind, x, y, size, sd, _x in items:
            c.save(); c.translate(x, y)
            r = random.Random(sd)
            if kind in ("peak", "mount", "hill"):
                ix_ = min(self.lw - 1, max(0, int(x * self.lw / self.W))); iy_ = min(self.lh - 1, max(0, int(y * self.lh / self.H)))
                waste = float(self.fert[iy_, ix_]) < 0.30
                X_ = reg.x0 + x / W * (reg.x1 - reg.x0); Y_ = reg.y1 - y / H * (reg.y1 - reg.y0)
                lo_, la_ = reg.inv.transform(X_, Y_)
                name = TSP.choose(kind, lo_, la_, waste, self.mpp > 150, r)
                wid = size * (2.6 if kind == "hill" else 2.2)
                c.restore(); c.save()
                TSP.draw(c, name, x, y, wid, edition)
            elif kind in ("conifer", "decid"):
                k = size / 40.0
                c.scale(k, k)
                tf = ((0.45, 0.58, 0.38) if kind == "conifer" else (0.58, 0.70, 0.42)) if edition == "colour" else ((0.72, 0.76, 0.60) if kind == "conifer" else (0.80, 0.82, 0.64))
                p = Pen(c, seed=sd, amp=0.5, ink=INK, paper=tf)
                if kind == "conifer":
                    p.line([(0, 0), (0, -6)], w=1.2)
                    for i, (wd, yy) in enumerate(((11, -6), (8.5, -13), (6, -19))):
                        p.shape([(-wd / 2, yy), (0, yy - 10), (wd / 2, yy)], fill=tf, w=1.1, hatch=dict(angle=70, gap=2.4, w=0.4, xmin=0))
                else:
                    p.line([(0, 0), (0, -9)], w=1.4)
                    pts = [(7 * math.cos(a) * (1 + r.uniform(-0.12, 0.12)), -16 + 6.5 * math.sin(a) * (1 + r.uniform(-0.12, 0.12))) for a in [i * math.pi / 8 for i in range(16)]]
                    p.shape(pts, fill=tf, w=1.1, hatch=dict(angle=70, gap=2.4, w=0.4, xmin=0))
            elif kind == "marsh":
                k = size / 40.0
                c.scale(k, k)
                p = Pen(c, seed=sd, amp=0.4, ink=BLUEINK)
                for dx in (-7, 0, 7):
                    hh = r.uniform(9, 14)
                    p.line([(dx, 0), (dx - 1.5, -hh * 0.6), (dx - 3, -hh)], w=0.9, col=BLUEINK)
                    p.line([(dx, 0), (dx + 0.5, -hh * 0.6), (dx + 1.5, -hh * 1.1)], w=0.9, col=BLUEINK)
                p.line([(-14, 3), (-5, 3)], w=0.8, col=BLUEINK); p.line([(3, 3), (14, 3)], w=0.8, col=BLUEINK)
                p.line([(-9, 7), (0, 7)], w=0.7, col=BLUEINK)
            elif kind == "palm":
                k = size / 40.0
                c.scale(k, k)
                p = Pen(c, seed=sd, amp=0.4, ink=INK)
                p.palm(0, 0, 26)
            elif kind == "tuft":
                k = size / 30.0
                c.scale(k, k)
                gc = (0.30, 0.42, 0.20) if edition == "colour" else (0.42, 0.45, 0.28)
                p = Pen(c, seed=sd, amp=0.3, ink=gc)
                for dx, hh in ((-5, 8), (0, 11), (5, 7)):
                    p.line([(dx, 0), (dx + r.uniform(-2, 2), -hh * 0.55), (dx + r.uniform(-4, 4), -hh)], w=0.9, col=gc)
                p.line([(-9, 2), (9, 2)], w=0.6, col=gc)
            elif kind == "scrub":
                k = size / 30.0
                c.scale(k, k)
                p = Pen(c, seed=sd, amp=0.3, ink=SEPIA)
                if r.random() < 0.55:
                    for dx, hh in ((-4, 6), (0, 8), (4, 5)):
                        p.line([(dx, 0), (dx + r.uniform(-2, 2), -hh)], w=0.8, col=SEPIA)
                for i in range(r.randint(4, 8)):
                    p.dot(r.uniform(-13, 13), r.uniform(-4, 8), 0.7, col=SEPIA)
            elif kind == "oasis":
                k = size / 60.0
                c.scale(k, k)
                p = Pen(c, seed=sd, amp=0.3, ink=BLUEINK)
                pool = [(16 * math.cos(a), 6 * math.sin(a) + 14) for a in [i * math.pi / 8 for i in range(16)]]
                c.save(); p._path(pool); c.close_path()
                c.set_source_rgb(*((0.50, 0.70, 0.78) if edition == "colour" else (0.74, 0.82, 0.78))); c.fill_preserve()
                c.set_source_rgb(*BLUEINK); c.set_line_width(1.1); c.stroke(); c.restore()
                q = Pen(c, seed=sd + 1, amp=0.3, ink=INK)
                for px_, py_, hh in ((-20, 10, 24), (18, 8, 28), (-2, -2, 22)):
                    q.palm(px_, py_, hh)
                for px_ in (-12, 11):
                    q.line([(px_, 20), (px_ - 1, 14), (px_ - 3, 9)], w=0.8, col=BLUEINK)
            elif kind == "drystrip":
                c.restore(); c.save()
                nm = r.choice(TSP.DUNES if _x == "dune" else TSP.DRYSTRIP)
                TSP.draw(c, nm, x, y, size, edition, alpha=0.9)
            elif kind == "dune":
                k = size / 60.0
                c.scale(k, k)
                p = Pen(c, seed=sd, amp=0.4, ink=SEPIA, paper=fill_h)
                p.line([(-22, 0), (-8, -8), (6, -3), (22, 2)], w=0.9, col=SEPIA)
                p.line([(-14, 6), (0, 2), (12, 6)], w=0.8, col=SEPIA)
                c.save(); c.move_to(-8, -8); c.curve_to(-4, -6, 2, -5, 6, -3); c.line_to(22, 2); c.curve_to(10, 1, 0, 3, -6, 4)
                c.close_path(); c.set_source_rgba(0.55, 0.40, 0.22, 0.28); c.fill(); c.restore()
                for i in range(9):
                    p.dot(r.uniform(-20, 20), r.uniform(8, 16), 0.55, col=SEPIA)
            c.restore()
        c.restore()


LAKES_OK = []
RIVERS = []


def roughen(g):
    """Break a smooth lake outline into a natural shore: densify, then push the points in and out."""
    parts = list(getattr(g, "geoms", [g]))
    out = []
    for pg in parts:
        if pg.geom_type != "Polygon" or pg.is_empty:
            continue
        amp = min(0.010, 0.05 * math.sqrt(pg.area))
        if amp < 0.0006:
            out.append(pg); continue
        ring = pg.exterior.segmentize(0.0035) if hasattr(pg.exterior, "segmentize") else pg.exterior
        co = list(ring.coords)
        rr = random.Random(int(abs(pg.centroid.x * 1000 + pg.centroid.y * 100)))
        p1, p2, p3 = rr.uniform(0, 6.28), rr.uniform(0, 6.28), rr.uniform(0, 6.28)
        res = []; s_ = 0.0
        for i, (x, y) in enumerate(co):
            if i:
                s_ += math.hypot(x - co[i - 1][0], y - co[i - 1][1])
            d = amp * (0.55 * math.sin(s_ * 55 + p1) + 0.3 * math.sin(s_ * 130 + p2) + 0.2 * math.sin(s_ * 290 + p3))
            nx, ny = (0.0, 0.0)
            j = min(len(co) - 1, i + 1); k = max(0, i - 1)
            tx, ty = co[j][0] - co[k][0], co[j][1] - co[k][1]
            L = math.hypot(tx, ty) or 1.0
            res.append((x - ty / L * d, y + tx / L * d))
        try:
            q = Polygon(res).buffer(0)
            out.append(q if not q.is_empty else pg)
        except Exception:
            out.append(pg)
    return unary_union(out) if out else g


def init_lakes():
    import json
    global LAKES_OK
    from shapely.geometry import shape
    LAKES_OK = []
    def ell(lo, la, rx, ry):
        rr = random.Random(int(lo * 100 + la * 10))
        ph = [rr.uniform(0, 6.28) for _ in range(6)]
        pts = []
        for i in range(120):
            a = i / 120 * 2 * math.pi
            k = 1 + 0.16 * math.sin(2 * a + ph[0]) + 0.11 * math.sin(3 * a + ph[1]) + 0.08 * math.sin(5 * a + ph[2]) + 0.05 * math.sin(8 * a + ph[3]) + 0.03 * math.sin(13 * a + ph[4])
            pts.append((lo + rx * k * math.cos(a), la + ry * k * math.sin(a)))
        return Polygon(pts)
    LAKES_OK += [ell(36.45, 36.33, 0.12, 0.05), ell(35.61, 33.08, 0.035, 0.05), ell(32.10, 31.27, 0.36, 0.09),
                 ell(30.85, 31.52, 0.30, 0.04), ell(30.65, 29.47, 0.20, 0.035), ell(32.42, 30.30, 0.07, 0.07)]
    for f in json.load(open("data/ne_10m_lakes.geojson"))["features"]:
        nm = f["properties"].get("name") or ""
        if any(m in nm for m in MODERN_LAKES):
            continue
        LAKES_OK.append(roughen(shape(f["geometry"])))
    global RIVERS
    RIVERS = []
    for f in json.load(open("data/ne_10m_rivers_lake_centerlines.geojson"))["features"]:
        nm = f["properties"].get("name") or ""
        if "Canal" in nm:
            continue
        RIVERS.append(shape(f["geometry"]))


init_lakes()
