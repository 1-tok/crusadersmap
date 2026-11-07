"""Stage 2: stage 1 plus places, arms, labels (city names offshore where they can), battles."""
import sys, time, math
import numpy as np, cairo
from PIL import Image
from build_stage1 import *          # regions, terrain, base_for, composite, plate, centred, compass, S ...
import lettering as LT
import placer as PC
import keypanel as KP

def _rng(a, b, st):
    n = int(round((b - a) / st))
    return [round(a + i * st, 3) for i in range(n + 1)]


# name, modern, dates, base path (lon, lat), max size, dlon candidates, dlat candidates, may sit at sea
POL = {
    "main": [
        ("KINGDOM OF IHERUSALEM", "Kingdom of Jerusalem", "1099 - 1291", [(34.75, 31.55), (34.95, 32.0), (35.15, 32.55), (35.35, 33.05), (35.55, 33.55)], 110, _rng(-0.15, 0.5, 0.05), _rng(-0.2, 0.2, 0.1), False),
        ("COUNTY OF TRIPLE", "County of Tripoli", "1109 - 1289", [(35.95, 34.15), (36.05, 34.55), (36.15, 34.95)], 80, _rng(-0.1, 0.5, 0.05), _rng(-0.2, 0.2, 0.1), False),
        ("PRINCIPALITY OF ANTIOCHE", "Principality of Antioch", "1098 - 1268", [(35.95, 35.3), (36.1, 35.7), (36.25, 36.05)], 80, _rng(-0.1, 0.5, 0.05), _rng(-0.2, 0.2, 0.1), False),
        ("KINGDOM OF ARMENIA", "Armenian Cilicia", "1198 - 1375", [(34.6, 36.95), (35.2, 37.0), (35.8, 37.1)], 76, _rng(-0.4, 0.3, 0.1), _rng(-0.3, 0.2, 0.1), False),
        ("KINGDOM OF CYPRUS", "Kingdom of Cyprus", "1192 - 1489", [(32.7, 35.0), (33.4, 35.05), (34.0, 35.2)], 90, _rng(-0.3, 0.3, 0.1), _rng(-0.3, 0.2, 0.1), False),
        ("OUTREJORDAIN", "Transjordan", "1118 - 1189", [(35.95, 31.9), (35.9, 31.3), (35.85, 30.8)], 70, _rng(-0.2, 0.5, 0.1), _rng(-0.1, 0.3, 0.1), False),
        ("EMIRATE OF DIMASHQ", "Damascus", "1104 - 1260", [(35.95, 33.88), (36.35, 33.9), (36.75, 33.82)], 58, _rng(-0.2, 0.3, 0.1), _rng(-0.6, 0.2, 0.1), False),
    ],
    "aegean": [
        ("PRINCIPALITY OF ACHAIE", "Achaea", "1205 - 1432", [(21.4, 37.45), (22.05, 37.55), (22.9, 37.4)], 90, _rng(-0.3, 0.3, 0.1), _rng(-0.3, 0.3, 0.1), False),
        ("DUCHY OF ATHENES", "Duchy of Athens", "1205 - 1456", [(22.9, 38.7), (23.7, 38.8), (24.5, 38.65)], 80, _rng(-0.5, 0.3, 0.1), _rng(-0.3, 0.5, 0.1), False),
        ("CANDIA", "Crete (Venice)", "1211 - 1669", [(24.2, 35.85), (25.0, 35.9), (25.8, 35.85)], 80, _rng(-0.2, 0.2, 0.1), _rng(-0.2, 0.3, 0.1), True),
        ("EMPIRE OF NICAEA", "Nicaea", "1204 - 1261", [(27.3, 39.45), (28.2, 39.6), (29.0, 39.6)], 80, _rng(-0.5, 0.5, 0.1), _rng(-0.6, 0.6, 0.1), False),
        ("EMPIRE OF CONSTANTINOPLE", "Latin Empire", "1204 - 1261", [(26.0, 41.35), (27.4, 41.5), (28.6, 41.35)], 70, _rng(-0.6, 0.4, 0.1), _rng(-0.5, 0.3, 0.1), False),
    ],
    "delta": [
        ("SOUDANIE OF EGYPT", "Fatimid, Ayyubid, Mamluk", "969 - 1517", [(30.4, 30.55), (31.1, 30.6), (31.8, 30.45)], 100, _rng(-0.3, 0.3, 0.1), _rng(-0.5, 0.4, 0.1), False),
    ],
}

ROADS = [
    [(36.15, 36.2), (35.95, 35.9), (35.82, 35.55), (35.95, 34.95), (35.92, 34.45), (35.6, 33.95), (35.45, 33.58), (35.28, 33.28), (35.13, 32.93), (34.98, 32.5), (34.82, 32.05), (34.65, 31.7)],
    [(35.13, 32.93), (35.32, 32.78), (35.53, 32.79), (35.7, 33.2), (36.3, 33.5)],
    [(34.82, 32.05), (35.02, 31.88), (35.23, 31.78)],
    [(35.23, 31.78), (35.12, 31.53)],
    [(36.15, 36.2), (36.5, 36.2), (37.15, 36.2)],
    [(37.15, 36.2), (36.9, 35.6), (36.75, 35.13), (36.72, 34.73), (36.5, 34.2), (36.3, 33.5)],
    [(35.92, 34.45), (36.25, 34.6), (36.72, 34.73)],
    [(33.32, 35.34), (33.38, 35.17), (33.95, 35.12)],
    [(33.38, 35.17), (33.0, 34.85), (33.04, 34.68)],
]


def choose_polities(items):
    """Pick, for each polity, the lettering path over land that clears places, panels and wasteland best."""
    dummy = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10))
    out = {}
    for k, lst in POL.items():
        bx, by = BOX[k]
        pts_items = [(it.x, it.y, it.w, it.tier) for it in items if it.region == k and it.kind != "isle"]
        t = TER[k]; sc = t.lw / t.W
        out[k] = []
        for nm, mod, dt, base, mx, dlons, dlats, sea_ok in lst:
            best = None
            for dlo in dlons:
                for dla in dlats:
                    ll = [(lo + dlo, la + dla) for lo, la in base]
                    p = to_sheet(k, ll)
                    sp = LT.orient(LT.catmull(p))
                    L = LT.path_len(sp)
                    w100 = LT.natural_width(dummy, nm, 100.0, 0.5)
                    size = min(mx, 100.0 * 0.92 * L / w100)
                    if size < mx * 0.25:
                        continue
                    pen = 0.0
                    for i in range(0, len(sp), 6):
                        x, y = sp[i]; yy = y + size * 0.9
                        ix, iy = int((x - bx) * sc), int((yy - by) * sc)
                        if not (0 <= ix < t.lw and 0 <= iy < t.lh):
                            pen += 6; continue
                        if not sea_ok and not t.land_l[iy, ix]:
                            pen += 4
                        if t.fert[iy, ix] < 0.30:
                            pen += 1.2
                        if t.rel[iy, ix] > 160:
                            pen += 0.5
                        for hx0, hy0, hx1, hy1 in HARD_ALL:
                            if hx0 - size < x < hx1 + size and hy0 - size < yy < hy1 + size:
                                pen += 10
                        for ix_, iy_, iw, tr in pts_items:
                            if abs(ix_ - x) < size * 1.2 + iw * 0.6 and abs(iy_ - (y + size * 0.5)) < size * 1.1 + iw * 0.5:
                                pen += {1: 8, 2: 4, 3: 2, 4: 1}.get(tr, 1)
                    pen /= max(1, len(sp) / 6)
                    score = pen - size * 0.01 * 0.2 + 0.02 * (abs(dlo) + abs(dla))
                    if best is None or score < best[0]:
                        best = (score, ll, size)
            if best is None:
                print('no path for', nm); best = (0, base, 0)
            out[k].append((nm, mod, dt, best[1], mx))
            print('polity', nm, best[1][0], round(best[2]))
    return out


def to_sheet(region, ll):
    bx, by = BOX[region]
    return [(bx + x, by + y) for x, y in (REG[region].ll_px(lo, la) for lo, la in ll)]


HARD_ALL = [(JX - 40, JY - 40, JX + JW + 40, JY + JH + 40), (270, 4770, 2330, 9130), (2680, 6730, 5430, 7770), (150, 13890, 10650, 14270),
            (4300 - 480, 8950 - 480, 4300 + 480, 8950 + 480)]
for _k in ("aegean", "delta"):
    _bx, _by = BOX[_k]
    HARD_ALL.append((_bx - 40, _by - 40, _bx + REG[_k].w + 40, _by + REG[_k].h + 40))
EDESSA = (8650, 1560, 10600, 1980)


_LAND_IN = []


def land_inner():
    if not _LAND_IN:
        from terrain import LAND
        from shapely.geometry import box
        from shapely.ops import unary_union
        bb = box(32.0, 29.0, 38.5, 38.6)
        u = unary_union([g.intersection(bb) for g in LAND if g.intersects(bb)])
        _LAND_IN.append(u.buffer(-0.03))
    return _LAND_IN[0]


def draw_roads(c, edition):
    from shapely.geometry import LineString
    bx, by = BOX["main"]
    c.save()
    c.translate(bx, by)
    c.set_source_rgba(0.40, 0.29, 0.18, 0.62 if edition == "colour" else 0.55)
    c.set_line_width(3.4); c.set_dash([16, 11]); c.set_line_cap(cairo.LINE_CAP_ROUND)
    inner = land_inner()
    for road in ROADS:
        sm = LT.catmull(road, step=0.02)
        inter = LineString(sm).intersection(inner)
        for part in getattr(inter, "geoms", [inter]):
            if part.geom_type != "LineString" or len(part.coords) < 2:
                continue
            pts = [REG["main"].ll_px(lo, la) for lo, la in part.coords]
            c.move_to(*pts[0])
            for x, y in pts[1:]:
                c.line_to(x, y)
            c.stroke()
    c.restore()


def draw_ink2(edition, surf=None, scale=None, mode=None):
    items = PC.build_items(TER, REG, BOX)
    avoid = PC.avoid_rects(TER, REG, BOX)
    chosen = choose_polities(items)
    dummy = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10))
    disks = []
    for k, lst in chosen.items():
        bx, by = BOX[k]
        ad = []
        for nm, mod, dt, ll, mx in lst:
            for x, y, r in LT.polity(dummy, nm, mod, dt, to_sheet(k, ll), mx):
                disks.append((x, y, r * 0.62)); ad.append((x - bx, y - by, r * 0.85))
        TER[k].avoid_disks = ad
    for k in TER:
        TER[k].avoid_rects = avoid[k]
    if surf is None:
        surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, WS, HS)
    c = cairo.Context(surf)
    if mode:
        from splitctx import SplitCtx
        c = SplitCtx(c, mode)
    sc_ = S if scale is None else scale
    c.scale(sc_, sc_)
    for k in ("main", "aegean", "delta"):
        bx, by = BOX[k]
        c.save(); c.translate(bx, by)
        c.rectangle(0, 0, REG[k].w, REG[k].h)
        if k == "main":
            c.rectangle(JX - 20, JY - 20, JW + 40, JH + 40)
            for kk in ("aegean", "delta"):
                ax, ay = BOX[kk]
                c.rectangle(ax - 20 - bx, ay - 20 - by, REG[kk].w + 40, REG[kk].h + 40)
            c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        c.clip()
        TER[k].ink(c, edition)
        c.restore()
        if k == "main":
            c.save()
            c.rectangle(bx, by, REG[k].w, REG[k].h)
            c.rectangle(JX - 20, JY - 20, JW + 40, JH + 40)
            for kk in ("aegean", "delta"):
                ax, ay = BOX[kk]
                c.rectangle(ax - 20, ay - 20, REG[kk].w + 40, REG[kk].h + 40)
            c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD); c.clip()
            draw_roads(c, edition)
            c.restore()
    # polity lettering, then the places keep clear of it
    for k, lst in chosen.items():
        bx, by = BOX[k]
        c.save(); c.rectangle(bx, by, REG[k].w, REG[k].h); c.clip()
        for nm, mod, dt, ll, mx in lst:
            LT.polity(c, nm, mod, dt, to_sheet(k, ll), mx)
        c.restore()
    # rectangles nothing may touch
    hard = list(HARD_ALL[:5]) + [EDESSA]
    for k in ("aegean", "delta"):
        bx, by = BOX[k]
        hard.append((bx - 40, by - 40, bx + REG[k].w + 40, by + REG[k].h + 40))
    ihard = [(BOX['aegean'][0] - 10, BOX['aegean'][1] - 10, BOX['aegean'][0] + 1950, BOX['aegean'][1] + 190),
             (BOX['delta'][0] - 10, BOX['delta'][1] - 10, BOX['delta'][0] + 1650, BOX['delta'][1] + 190)]
    PC.draw_places(c, edition, TER, REG, BOX, hard, disks, ihard)
    # inset frames and title plates
    for k, title in (("aegean", FR.INSETS["aegean"]["title"]), ("delta", FR.INSETS["delta"]["title"])):
        bx, by = BOX[k]; w, h = REG[k].w, REG[k].h
        c.set_source_rgb(*INKC)
        for off, lw in ((0, 6), (16, 3)):
            c.set_line_width(lw); c.rectangle(bx - off, by - off, w + 2 * off, h + 2 * off); c.stroke()
        c.select_font_face("Fondamento", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); c.set_font_size(92)
        tw = c.text_extents(title).x_advance
        c.rectangle(bx + 30, by + 28, tw + 70, 138); c.set_source_rgb(0.95, 0.915, 0.82); c.fill_preserve()
        c.set_source_rgb(*INKC); c.set_line_width(4); c.stroke()
        c.move_to(bx + 65, by + 122); c.show_text(title)
    c.set_source_rgb(*INKC)
    for off, lw in ((0, 6), (16, 3)):
        c.set_line_width(lw); c.rectangle(JX - off, JY - off, JW + 2 * off, JH + 2 * off); c.stroke()
    plate(c, 300, 4800, 2000, 4300)
    KP.draw_key(c, edition, 300, 4800, 2000, 4300)
    plate(c, 2700, 6750, 2700, 1000)
    centred(c, "Outremer", 4050, 7300, 190)
    centred(c, "The Crusader States and their Neighbours", 4050, 7480, 62)
    centred(c, "1095 - 1571", 4050, 7640, 52, SEP, "IM FELL English", cairo.FONT_SLANT_ITALIC)
    plate(c, 190, 13920, 10420, 330)
    KP.draw_sources(c, 190, 13920, 10420, 330, {k: (REG[k].x1 - REG[k].x0) / REG[k].w for k in ("main", "aegean", "delta")})
    c.new_path()
    compass(c, 4300, 8950, 330)
    c.new_path()
    ex0, ey = 9150, 1780
    c.set_source_rgba(*SEP, 0.9); c.set_line_width(5); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(ex0, ey); c.curve_to(ex0 + 300, ey - 12, ex0 + 700, ey + 10, 10380, ey - 4); c.stroke()
    c.move_to(10380, ey - 4); c.line_to(10318, ey - 40); c.move_to(10380, ey - 4); c.line_to(10316, ey + 30); c.stroke()
    centred(c, "To Rohais (Edessa) and Harran", 9780, 1700, 66, SEP, "IM FELL English", cairo.FONT_SLANT_ITALIC)
    centred(c, "Frankish 1098 - 1150", 9780, 1900, 52, SEP, "IM FELL English", cairo.FONT_SLANT_ITALIC)
    c.new_path()
    c.set_source_rgb(*INKC)
    for off, lw in ((30, 8), (70, 3)):
        c.set_line_width(lw); c.rectangle(off, off, W - 2 * off, H - 2 * off); c.stroke()
    return surf


if __name__ == "__main__":
    eds = sys.argv[2].split(",") if len(sys.argv) > 2 else ["parchment", "colour"]
    for ed in eds:
        t0 = time.time()
        base = base_for(ed)
        surf = draw_ink2(ed)
        img = composite(base, surf)
        Image.fromarray(img).save(f"out/stage2-{ed}.jpg", quality=88)
        print("saved", ed, round(time.time() - t0), "s", flush=True)
        del surf, base
