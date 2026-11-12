"""Key panel and sources strip."""
import math
import cairo
from hand import Pen, INK, SEPIA
import marks as MK
import placer as PC
import ridges as RD
import sprites as SPR
import terrainsp as TSP

BLUEINK = (0.20, 0.33, 0.45)
RED = (0.59, 0.125, 0.11)


def _txt(c, s, x, y, size, col=INK, fam="Fondamento", slant=cairo.FONT_SLANT_NORMAL, align="l"):
    c.select_font_face(fam, slant, cairo.FONT_WEIGHT_NORMAL); c.set_font_size(size)
    e = c.text_extents(s)
    if align == "c":
        x -= e.x_advance / 2
    c.move_to(x, y); c.set_source_rgb(*col); c.show_text(s)
    return e.x_advance


def _heading(c, s, x, y, w):
    _txt(c, s, x, y, 54, RED)
    c.set_source_rgba(*SEPIA, 0.8); c.set_line_width(3)
    c.move_to(x, y + 22); c.line_to(x + w, y + 22); c.stroke()


def _mark(c, name, cx, gy, w, edition, seed=7):
    PC.draw_symbol(c, "M:" + name, cx, gy, w, seed, edition)


def _battle(c, name, cx, cy, w):
    s = w / 100.0
    c.save(); c.translate(cx - 50 * s, cy - 50 * s); c.scale(s, s)
    getattr(MK, name)(Pen(c, seed=5, amp=0.8))
    c.restore()


def _trees(c, cx, gy, edition):
    for kind, dx, sz in (("conifer", -26, 52), ("decid", 24, 50), ("conifer", 2, 44)):
        k = sz / 40.0
        tf = ((0.45, 0.58, 0.38) if kind == "conifer" else (0.58, 0.70, 0.42)) if edition == "colour" else ((0.72, 0.76, 0.60) if kind == "conifer" else (0.80, 0.82, 0.64))
        c.save(); c.translate(cx + dx, gy); c.scale(k, k)
        p = Pen(c, seed=11 + dx, amp=0.5, ink=INK, paper=tf)
        if kind == "conifer":
            p.line([(0, 0), (0, -6)], w=1.2)
            for wd, yy in ((11, -6), (8.5, -13), (6, -19)):
                p.shape([(-wd / 2, yy), (0, yy - 10), (wd / 2, yy)], fill=tf, w=1.1, hatch=dict(angle=70, gap=2.4, w=0.4, xmin=0))
        else:
            p.line([(0, 0), (0, -9)], w=1.4)
            pts = [(7 * math.cos(a), -16 + 6.5 * math.sin(a)) for a in [i * math.pi / 8 for i in range(16)]]
            p.shape(pts, fill=tf, w=1.1, hatch=dict(angle=70, gap=2.4, w=0.4, xmin=0))
        c.restore()


def _marsh(c, cx, gy):
    c.save(); c.translate(cx, gy); k = 2.0; c.scale(k, k)
    p = Pen(c, seed=3, amp=0.4, ink=BLUEINK)
    for dx, hh in ((-7, 11), (0, 13), (7, 10)):
        p.line([(dx, 0), (dx - 1.5, -hh * 0.6), (dx - 3, -hh)], w=0.9, col=BLUEINK)
        p.line([(dx, 0), (dx + 0.5, -hh * 0.6), (dx + 1.5, -hh * 1.1)], w=0.9, col=BLUEINK)
    p.line([(-14, 3), (-5, 3)], w=0.8, col=BLUEINK); p.line([(3, 3), (14, 3)], w=0.8, col=BLUEINK)
    c.restore()


def _dune(c, cx, gy):
    c.save(); c.translate(cx, gy); k = 2.0; c.scale(k, k)
    p = Pen(c, seed=4, amp=0.4, ink=SEPIA)
    p.line([(-22, 0), (-8, -8), (6, -3), (22, 2)], w=0.9, col=SEPIA)
    p.line([(-14, 6), (0, 2), (12, 6)], w=0.8, col=SEPIA)
    c.move_to(-8, -8); c.curve_to(-4, -6, 2, -5, 6, -3); c.line_to(22, 2); c.curve_to(10, 1, 0, 3, -6, 4)
    c.close_path(); c.set_source_rgba(0.55, 0.40, 0.22, 0.28); c.fill()
    for dx, dy in ((-16, 10), (-8, 13), (2, 11), (10, 14), (18, 10)):
        p.dot(dx, dy, 0.6, col=SEPIA)
    c.restore()


def _oasis(c, cx, gy, edition):
    c.save(); c.translate(cx, gy - 10); k = 1.7; c.scale(k, k)
    p = Pen(c, seed=2, amp=0.3, ink=BLUEINK)
    pool = [(16 * math.cos(a), 6 * math.sin(a) + 14) for a in [i * math.pi / 8 for i in range(16)]]
    p._path(pool); c.close_path()
    c.set_source_rgb(*((0.50, 0.70, 0.78) if edition == "colour" else (0.74, 0.82, 0.78))); c.fill_preserve()
    c.set_source_rgb(*BLUEINK); c.set_line_width(1.1); c.stroke()
    q = Pen(c, seed=3, amp=0.3, ink=INK)
    for px_, py_, hh in ((-20, 10, 24), (18, 8, 28), (-2, -2, 22)):
        q.palm(px_, py_, hh)
    c.restore()


def _grass(c, cx, gy, edition):
    gc = (0.30, 0.42, 0.20) if edition == "colour" else (0.42, 0.45, 0.28)
    c.save(); c.translate(cx, gy); c.scale(2.2, 2.2)
    p = Pen(c, seed=9, amp=0.3, ink=gc)
    for dx, hh in ((-5, 8), (0, 11), (5, 7)):
        p.line([(dx, 0), (dx, -hh * 0.55), (dx + 1, -hh)], w=0.9, col=gc)
    p.line([(-9, 2), (9, 2)], w=0.6, col=gc)
    c.restore()


def _scrub(c, cx, gy):
    c.save(); c.translate(cx, gy); c.scale(2.2, 2.2)
    p = Pen(c, seed=6, amp=0.3, ink=SEPIA)
    for dx, hh in ((-4, 6), (0, 8), (4, 5)):
        p.line([(dx, 0), (dx, -hh)], w=0.8, col=SEPIA)
    for dx, dy in ((-11, 3), (-8, 6), (9, 5), (12, 2), (5, 7), (-3, 7)):
        p.dot(dx, dy, 0.7, col=SEPIA)
    c.restore()


def draw_key(c, edition, X, Y, Wd, Ht):
    fill_h = (0.90, 0.85, 0.74) if edition == "parchment" else (0.84, 0.79, 0.69)
    fill_m = (0.88, 0.83, 0.74) if edition == "parchment" else (0.80, 0.75, 0.67)
    PC_ = (0.95, 0.915, 0.82)
    MK.MUTE = 0.0 if edition == "colour" else 0.30
    _txt(c, "KEY", X + Wd / 2, Y + 150, 96, INK, align="c")
    c.set_source_rgba(*SEPIA, 0.8); c.set_line_width(3)
    c.move_to(X + Wd * 0.2, Y + 190); c.line_to(X + Wd * 0.8, Y + 190); c.stroke()
    cw = (Wd - 90) / 2
    x1 = X + 40; x2 = X + 50 + cw
    RH = 134

    def column(x, y, sections, RH=RH):
        for title, rows in sections:
            _heading(c, title, x, y + 40, cw - 30)
            y += 98
            for fn, label, sub in rows:
                cx = x + 85; gy = y + 96
                fn(cx, gy)
                _txt(c, label, x + 185, y + (62 if sub else 76), 46, INK)
                if sub:
                    _txt(c, sub, x + 185, y + 106, 33, SEPIA, "IM FELL English", cairo.FONT_SLANT_ITALIC)
                y += RH
        return y

    M = lambda nm, w=124: (lambda cx, gy: _mark(c, nm, cx, gy, w * 1.18, edition))
    BYNAME = {r["name"]: r for r in SPR._META}

    def city(nm, w=150):
        return lambda cx, gy: SPR.draw(c, BYNAME[nm], cx, gy, w, edition)

    def gen(i, w=150):
        return lambda cx, gy: TSP.gdraw(c, i, cx, gy + 6, w, edition)

    def tile(nm, w=200, dy=24):
        return lambda cx, gy: TSP.draw(c, nm, cx, gy + dy, w, edition, alpha=1.0)

    col1 = [
        ("Cities and castles", [(city("Acre"), "Walled city", "Acre"), (city("Tyre (Sur)"), "Port city", "Sur"),
                                (city("Krak des Chevaliers", 140), "Castle", "Crac des Chevaliers"),
                                (city("Montfort (begun 1226)", 100), "Rock castle", "Montfort"),
                                (city("Château Pèlerin (begun 1218)", 140), "Sea castle", "Chastel Pelerin"),
                                (city("St Catherine's", 150), "Monastery", "Sainte-Katherine"),
                                (city("Bethlehem", 150), "Pilgrim town", "Bethlehem")]),
        ("Villages and farms", [(gen(0), "Hamlet", ""), (gen(10), "Farmstead and vines", ""), (gen(12), "Farm and flock", ""),
                                (gen(1), "Chapel", ""), (gen(8), "Domed shrine", ""), (gen(5), "Mosque and village", ""),
                                (gen(4, 120), "Watch tower", ""), (gen(9), "Watermill", ""), (gen(11), "Ruin", ""),
                                (gen(19, 110), "Well", "")]),
        ("Desert and pasture", [(gen(13), "Bedouin camp", ""), (gen(27), "Caravan halt", ""), (gen(16), "Oasis", ""),
                                (gen(20), "Sheepfold", ""), (gen(25), "Seasonal pasture", "")]),
    ]

    def hill(cx, gy):
        c.save(); c.translate(cx, gy); c.scale(1.9, 1.9); RD.hill(c, 5, fill_h, h=12, w=56); c.restore()

    def massif(cx, gy):
        c.save(); c.translate(cx, gy); c.scale(1.2, 1.2); RD.massif(c, 21, fill_m, h=42, w=110); c.restore()

    def mesa(cx, gy):
        c.save(); c.translate(cx, gy); c.scale(1.2, 1.2); RD.mesa(c, 8, fill_m, h=34, w=96); c.restore()

    def alpine(cx, gy):
        c.save(); c.translate(cx, gy); c.scale(1.1, 1.1); RD.mountain(c, 33, fill_m, h=60, peaks=2); c.restore()

    def river(cx, gy):
        pts = [(cx - 70 + i * 10, gy - 36 + 7 * math.sin(i * 0.9)) for i in range(15)]
        c.save(); Pen(c, seed=3, amp=0.5, ink=BLUEINK).line(pts, w=3.0, col=BLUEINK); c.restore()

    def road(cx, gy):
        c.save(); c.set_source_rgba(0.40, 0.29, 0.18, 0.7); c.set_line_width(4); c.set_dash([16, 11]); c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.move_to(cx - 70, gy - 34); c.curve_to(cx - 20, gy - 52, cx + 20, gy - 14, cx + 70, gy - 36); c.stroke(); c.restore()

    def swatch(col):
        def f(cx, gy):
            c.save(); c.rectangle(cx - 70, gy - 70, 140, 70); c.set_source_rgb(*col); c.fill_preserve()
            c.set_source_rgb(*INK); c.set_line_width(2.5); c.stroke(); c.restore()
        return f

    fer = (116, 164, 84) if edition == "colour" else (178, 198, 134)
    des = (234, 206, 138) if edition == "colour" else (240, 221, 170)
    Q = lambda t: tuple(v / 255 for v in t)

    def arms(kind, key):
        def f(cx, gy):
            ws = 66
            if kind == "o":
                name, desc, field, charge = PC.ORD[key]
                MK.badge(c, cx - ws / 2, gy - ws * 1.35, ws, field, charge, mode="colour", kind="shield", seed=3)
            else:
                name, desc, field, charge = PC.POW[key]
                MK.badge(c, cx - ws / 2, gy - ws * 1.1, ws * 1.15, field, charge, mode="colour", kind="banner", seed=4)
        return f

    col2 = [
        ("Battles and sieges", [(lambda cx, gy: _battle(c, "battle", cx, gy - 44, 100), "Battle", ""),
                                (lambda cx, gy: _battle(c, "siege", cx, gy - 44, 100), "Siege", ""),
                                (lambda cx, gy: _battle(c, "sea_battle", cx, gy - 44, 100), "Sea battle", "")]),
        ("Land", [(tile("levant-farmland", 190), "Fields and orchards", ""), (tile("dry-stone-pasture", 190), "Pasture", ""),
                  (tile("gravel-wasteland-deep", 190), "Desert waste", ""), (swatch(Q(fer)), "Fertile land", ""), (swatch(Q(des)), "Steppe", ""),
                  (hill, "Hills", ""), (massif, "Mountains", ""), (alpine, "High peaks", ""),
                  (lambda cx, gy: _trees(c, cx, gy, edition), "Forest", ""), (lambda cx, gy: _marsh(c, cx, gy), "Marsh", ""),
                  (lambda cx, gy: _dune(c, cx, gy), "Dunes", ""), (river, "River", ""), (road, "Road", "")]),
        ("Military orders", [(arms("o", k), PC.ORD[k][0], PC.ORD[k][1]) for k in ("hosp", "temp", "teut", "laz", "thom", "mont")]),
        ("Maritime powers", [(arms("p", k), PC.POW[k][0], PC.POW[k][1]) for k in ("ven", "gen", "pis", "byz")]),
    ]
    y0 = Y + 250
    def fit(cols):
        n = sum(len(r) for _, r in cols)
        return min(134, (Y + Ht - 70 - y0 - 98 * len(cols)) / n)
    column(x1, y0, col1, fit(col1))
    column(x2, y0, col2, fit(col2))
    c.set_source_rgba(*SEPIA, 0.5); c.set_line_width(2)
    c.move_to(X + Wd / 2, Y + 270); c.line_to(X + Wd / 2, Y + Ht - 60); c.stroke()


def scale_bar(c, x, y, km, mpp, ticks, label):
    L = km * 1000.0 / mpp
    n = ticks
    for i in range(n):
        c.rectangle(x + L * i / n, y, L / n, 22)
        c.set_source_rgb(*(INK if i % 2 == 0 else (0.95, 0.915, 0.82))); c.fill_preserve()
        c.set_source_rgb(*INK); c.set_line_width(3); c.stroke()
    _txt(c, "0", x, y + 66, 40, INK, "IM FELL English", cairo.FONT_SLANT_ITALIC, "c")
    _txt(c, f"{km} km", x + L, y + 66, 40, INK, "IM FELL English", cairo.FONT_SLANT_ITALIC, "c")
    _txt(c, label, x + L / 2, y - 18, 42, SEPIA, "Fondamento", cairo.FONT_SLANT_NORMAL, "c")
    return L


def draw_sources(c, X, Y, Wd, Ht, mpps):
    yb = Y + 160
    x = X + 130
    L = scale_bar(c, x, yb, 100, mpps["main"], 5, "Outremer (main map)")
    x += L + 260
    L = scale_bar(c, x, yb, 200, mpps["aegean"], 4, "Romania inset")
    x += L + 260
    L = scale_bar(c, x, yb, 100, mpps["delta"], 4, "Egypt and Sinai inset")
    x += L + 200
    c.set_source_rgba(*SEPIA, 0.6); c.set_line_width(2.5); c.move_to(x, Y + 50); c.line_to(x, Y + Ht - 50); c.stroke()
    tx = x + 120
    lines = ["Coasts, rivers and lakes: Natural Earth. Elevation: Mapzen terrain tiles.",
             "Each place carries its Frankish, Greek or Latin name, with the modern name beneath.",
             "Dates show the years a place or polity was held; no borders are drawn."]
    for i, s in enumerate(lines):
        _txt(c, s, tx, Y + 95 + i * 72, 52, INK if i == 0 else SEPIA, "IM FELL English", cairo.FONT_SLANT_ITALIC)
