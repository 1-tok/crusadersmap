"""Place symbols, arms, labels and battle marks on the sheet with collision avoidance.
Everything works in sheet print px (10800 x 14400)."""
import math
import numpy as np
import cairo
import profiles as PR, marks as MK, places as PL
from hand import Pen

INKC = (0.17, 0.13, 0.10); SEP = (0.42, 0.32, 0.22); RED = (0.59, 0.125, 0.11)
PAPER_HALO = (0.94, 0.90, 0.79, 0.78)
RF = {"main": 1.0, "aegean": 0.62, "delta": 0.82}
ORD = {"hosp": MK.ORDERS[0], "temp": MK.ORDERS[1], "teut": MK.ORDERS[2], "laz": MK.ORDERS[3], "thom": MK.ORDERS[4], "mont": MK.ORDERS[5]}
POW = {"ven": MK.POWERS[0], "gen": MK.POWERS[1], "pis": MK.POWERS[2], "byz": MK.POWERS[3]}
SINGLE = {"Dimashq", "Halab", "al-Qahira", "al-Iskandariyya", "al-Mansura", "Hamah", "Hims", "Masyaf", "Ajlun", "Shayzar", "Sis", "Mistras",
          "Sainte-Katherine", "Dimyat", "Baalbek", "Bosra", "Fariskur", "Tinnis", "Rashid", "al-Farama"}


class Occ:
    def __init__(self, W, H, cell=10):
        self.cell = cell
        self.g = np.zeros((H // cell + 2, W // cell + 2), bool)

    def _ix(self, r):
        c = self.cell
        return max(0, int(r[1] // c)), int(r[3] // c) + 1, max(0, int(r[0] // c)), int(r[2] // c) + 1

    def mark(self, r):
        y0, y1, x0, x1 = self._ix(r)
        self.g[y0:y1, x0:x1] = True

    def mark_disc(self, x, y, rad):
        self.mark((x - rad, y - rad, x + rad, y + rad))

    def free(self, r, pad=0):
        y0, y1, x0, x1 = self._ix((r[0] - pad, r[1] - pad, r[2] + pad, r[3] + pad))
        if y0 < 0 or x0 < 0 or y1 > self.g.shape[0] or x1 > self.g.shape[1]:
            return False
        return not self.g[y0:y1, x0:x1].any()

    def frac(self, r):
        y0, y1, x0, x1 = self._ix(r)
        blk = self.g[max(0, y0):y1, max(0, x0):x1]
        return float(blk.mean()) if blk.size else 1.0


def rect_inter(a, b):
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


class Item:
    pass


def mark_func(spec):
    kind, name = spec.split(":")
    return (PR if kind == "P" else MK), getattr(PR if kind == "P" else MK, name), kind


def symbol_size(spec, tier, name):
    kind, nm = spec.split(":")
    if kind == "P":
        return {1: 340, 2: 250}.get(tier, 215)
    base = 135
    if nm in ("tower_", "ruin"):
        base = 100
    elif nm in ("town", "village", "latin_church", "greek_monastery", "eastern_church", "shrine", "holy_spring", "point_of_interest"):
        base = 118
    elif nm in ("walled_town", "castle_frankish", "castle_muslim", "castle_armenian", "castle_byzantine", "castle_nizari", "sea_castle", "mosque", "latin_cathedral"):
        base = 140
    if tier >= 4:
        base *= 0.86
    return base


def symbol_rect(spec, px, py, w):
    kind = spec.split(":")[0]
    if kind == "P":
        s = w / 320.0
        return (px - 160 * s, py - 188 * s, px + 160 * s, py + 8 * s), s
    s = w / 100.0
    return (px - 50 * s, py - 82 * s, px + 50 * s, py + 7 * s), s


PAPERC = (0.937, 0.894, 0.788)
# (stone, top tint, share of height the top tint covers)
TINTS = {
    "mosque": ((0.93, 0.87, 0.72), (0.58, 0.72, 0.74), 0.40), "shrine": ((0.93, 0.87, 0.72), (0.58, 0.72, 0.74), 0.40),
    "castle_frankish": ((0.84, 0.81, 0.74), (0.88, 0.76, 0.66), 0.30), "castle_muslim": ((0.94, 0.84, 0.62), (0.90, 0.72, 0.52), 0.30),
    "castle_byzantine": ((0.89, 0.77, 0.62), (0.86, 0.60, 0.46), 0.30), "castle_armenian": ((0.80, 0.70, 0.58), (0.84, 0.66, 0.52), 0.25),
    "castle_nizari": ((0.80, 0.70, 0.58), (0.84, 0.66, 0.52), 0.25), "cave_fortress": ((0.80, 0.70, 0.58), (0.84, 0.66, 0.52), 0.2),
    "sea_castle": ((0.82, 0.80, 0.74), (0.80, 0.80, 0.82), 0.30), "tower_": ((0.84, 0.81, 0.74), (0.86, 0.70, 0.58), 0.25),
    "ruin": ((0.82, 0.78, 0.70), None, 0), "port": (PAPERC, None, 0),
    "town": ((0.92, 0.84, 0.68), (0.88, 0.58, 0.44), 0.45), "walled_town": ((0.90, 0.82, 0.66), (0.88, 0.60, 0.46), 0.40),
    "village": ((0.92, 0.84, 0.68), (0.88, 0.58, 0.44), 0.5),
    "latin_church": ((0.90, 0.86, 0.76), (0.80, 0.55, 0.45), 0.35), "latin_cathedral": ((0.90, 0.86, 0.76), (0.62, 0.66, 0.72), 0.40),
    "greek_monastery": ((0.92, 0.84, 0.70), (0.86, 0.52, 0.40), 0.40), "eastern_church": ((0.90, 0.82, 0.68), (0.86, 0.52, 0.40), 0.45),
    "holy_spring": (PAPERC, None, 0), "point_of_interest": (PAPERC, None, 0), "jewish_holy": ((0.92, 0.86, 0.72), None, 0),
}
PTINT = ((0.91, 0.83, 0.68), (0.90, 0.72, 0.60), 0.34)
MOSQUE_CITIES = {"damascus", "aleppo", "cairo_", "hama", "hims", "mansura", "tabor"}
GROUND = (0.62, 0.66, 0.42)


def _mix(a, b, t):
    return tuple(a[i] * (1 - t) + b[i] * t for i in range(3))


def draw_symbol(c, spec, px, py, w, seed, edition="colour"):
    mod, fn, kind = mark_func(spec)
    rect, s = symbol_rect(spec, px, py, w)
    nm = spec.split(":")[1]
    stone, top, frac = (PTINT if kind == "P" else TINTS.get(nm, (PAPERC, None, 0)))
    if kind == "P" and nm in MOSQUE_CITIES:
        stone, top, frac = (0.93, 0.85, 0.68), (0.62, 0.72, 0.72), 0.40
    ground = GROUND
    if edition != "colour":
        stone = _mix(stone, PAPERC, 0.5); ground = _mix(GROUND, PAPERC, 0.55)
        if top: top = _mix(top, (1, 1, 1), 0.5)
    # a soft patch of earth under the foot of the symbol
    if nm not in ("sea_castle", "port"):
        gw = (rect[2] - rect[0]) * 0.50
        gy = py - 2
        c.save()
        c.translate(px, gy); c.scale(1.0, 0.16)
        rg = cairo.RadialGradient(0, 0, 0, 0, 0, gw)
        rg.add_color_stop_rgba(0, *ground, 0.62 if edition == "colour" else 0.40)
        rg.add_color_stop_rgba(0.7, *ground, 0.34 if edition == "colour" else 0.2)
        rg.add_color_stop_rgba(1, *ground, 0.0)
        c.set_source(rg); c.arc(0, 0, gw, 0, 2 * math.pi); c.fill()
        c.restore()
    c.save()
    if kind == "P":
        c.translate(px - 160 * s, py - 200 * s); ty, by_ = 12.0, 208.0
    else:
        c.translate(px - 50 * s, py - 84 * s); ty, by_ = 2.0, 91.0
    c.scale(s, s)
    paper = stone
    if top:
        g = cairo.LinearGradient(0, ty, 0, by_)
        tc = _mix(stone, top, 0.62)
        g.add_color_stop_rgb(0, *tc); g.add_color_stop_rgb(frac, *tc)
        g.add_color_stop_rgb(min(0.95, frac + 0.18), *stone); g.add_color_stop_rgb(1, *stone)
        paper = g
    fn(Pen(c, seed=seed, amp=0.8, paper=paper))
    c.restore()


def land_fn_for(TER, BOX, region):
    t = TER[region]; bx, by = BOX[region]
    sc = t.lw / t.W

    def f(x, y):
        ix = int((x - bx) * sc); iy = int((y - by) * sc)
        if ix < 0 or iy < 0 or ix >= t.lw or iy >= t.lh:
            return False
        return bool(t.land_l[iy, ix])
    return f


NO_NUDGE = {"sea_castle", "port"}


def nudge(it, LF):
    """Move a symbol inland until its foot stands wholly on land."""
    if it.kind != "place" or it.mark.split(":")[1] in NO_NUDGE:
        return
    f = LF[it.region]
    half = 0.40 * it.w

    def ok(x, y):
        return f(x - half, y - 6) and f(x + half, y - 6) and f(x, y - 6)
    if ok(it.x, it.y):
        return
    for r in range(8, 169, 8):
        for k in range(16):
            a = 2 * math.pi * k / 16
            x = it.x + r * math.cos(a); y = it.y + r * math.sin(a)
            if ok(x, y):
                it.x, it.y = x, y
                return


def build_items(TER, REG, BOX):
    LF = {k: land_fn_for(TER, BOX, k) for k in TER}
    items = []
    for t in PL.PLACES:
        region, tier, mark, lon, lat, name, alt, modern, dates, arms = t
        it = Item(); it.__dict__.update(region=region, tier=tier, mark=mark, name=name, alt=alt, modern=modern, dates=dates, arms=arms, kind="place")
        bx, by = BOX[region]
        px, py = REG[region].ll_px(lon, lat)
        it.x, it.y = bx + px, by + py
        it.rf = RF[region]
        it.w = symbol_size(mark, tier, name) * it.rf
        nudge(it, LF)
        items.append(it)
    for b in PL.BATTLES:
        region, kind, lon, lat, name, modern, year = b
        it = Item(); it.__dict__.update(region=region, tier=2, mark="M:" + {"battle": "battle", "siege": "siege", "sea": "sea_battle"}[kind], name=name, alt="", modern=modern, dates=year, arms=(), kind=kind)
        bx, by = BOX[region]
        px, py = REG[region].ll_px(lon, lat)
        it.x, it.y = bx + px, by + py
        it.rf = RF[region]
        it.w = 112 * it.rf
        items.append(it)
    for region, lon, lat, name, modern in PL.ISLES:
        it = Item(); it.__dict__.update(region=region, tier=3, mark="", name=name, alt="", modern=modern, dates="", arms=(), kind="isle")
        bx, by = BOX[region]
        px, py = REG[region].ll_px(lon, lat)
        it.x, it.y = bx + px, by + py
        it.rf = RF[region]; it.w = 6
        items.append(it)
    return items


def avoid_rects(TER, REG, BOX):
    """Per region: rects (region px) round every place where trees, hills and mountains must keep clear."""
    out = {k: [] for k in TER}
    for it in build_items(TER, REG, BOX):
        if it.kind == "isle":
            continue
        bx, by = BOX[it.region]
        if it.kind == "place":
            r, _ = symbol_rect(it.mark, it.x, it.y, it.w)
            ex = 0.0
            if it.arms:
                ws = max(30.0, it.w * 0.17)
                ex = ws * (1.12 * min(3, len([a for a in it.arms if a in ORD])) + 1.4 * (1 if any(a in POW for a in it.arms) else 0)) + ws * 0.2
            w = r[2] - r[0]
            rect = (r[0] - 0.14 * w, r[1] - 0.22 * w, r[2] + ex + 0.14 * w, r[3] + 0.16 * w)
        else:
            h = 50 * it.w / 100
            rect = (it.x - h * 1.4, it.y - h * 1.4, it.x + h * 1.4, it.y + h * 1.4)
        out[it.region].append((rect[0] - bx, rect[1] - by, rect[2] - bx, rect[3] - by))
    return out


def draw_arms(c, arms, rect, w, mode, seed, edition_hatched):
    """Shields and banners along the foot of the symbol, to its right."""
    if not arms:
        return (rect[2], rect[3], rect[2], rect[3])
    orders = [a for a in arms if a in ORD]
    powers = [a for a in arms if a in POW]
    ws = max(30.0, w * 0.17)
    x = rect[2] + ws * 0.15
    ybase = rect[3] - 4
    boxes = []
    n = 0
    for k in orders:
        row, col = divmod(n, 3)
        bx = x + col * (ws * 1.12); by = ybase - ws * 1.18 - row * (ws * 1.32)
        name, desc, field, charge = ORD[k]
        MK.badge(c, bx, by, ws, field, charge, mode=mode, kind="shield", seed=seed + n)
        boxes.append((bx, by, bx + ws, by + ws * 1.18)); n += 1
    m = 0
    for k in powers:
        name, desc, field, charge = POW[k]
        bw = ws * 1.05
        row, col = divmod(m, 3)
        bx = x + (len(orders[:3]) and min(len(orders), 3) * ws * 1.12 + ws * 0.2 or 0) + col * (bw * 1.22)
        by = ybase - ws * 1.6 + ws * 0.12 - row * (ws * 1.7)
        MK.badge(c, bx, by, bw, field, charge, mode=mode, kind="banner", seed=seed + 20 + m)
        boxes.append((bx - 2, by - bw * 0.12, bx + bw, by + bw * 1.5)); m += 1
    if not boxes:
        return rect
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes))


def label_lines(it):
    name = it.name
    if it.kind == "siege" and not name.startswith("Siege"):
        name = "Siege of " + name
    first = name if (not it.alt or name in SINGLE or it.alt == name) else f"{name} / {it.alt}"
    lines = [(first, 1.0, "n")]
    if it.modern and it.modern != name:
        lines.append((it.modern, 0.80, "m"))
    if it.dates:
        lines.append((it.dates, 0.66, "d"))
    return lines


FONTS = {"n": ("Fondamento", cairo.FONT_SLANT_NORMAL), "m": ("IM FELL English", cairo.FONT_SLANT_ITALIC), "d": ("IM FELL English", cairo.FONT_SLANT_ITALIC)}


def measure(c, lines, size):
    out = []
    for text, f, k in lines:
        fam, sl = FONTS[k]
        c.select_font_face(fam, sl, cairo.FONT_WEIGHT_NORMAL)
        c.set_font_size(size * f)
        e = c.text_extents(text)
        out.append((text, size * f, k, e.x_advance, size * f * 1.18))
    return out


def draw_label(c, block, x, y_top, align, w_total):
    y = y_top
    for text, fs, k, wd, hh in block:
        fam, sl = FONTS[k]
        c.select_font_face(fam, sl, cairo.FONT_WEIGHT_NORMAL)
        c.set_font_size(fs)
        if align == "r":
            xx = x - wd
        elif align == "c":
            xx = x - wd / 2
        else:
            xx = x
        y += hh * 0.86
        c.move_to(xx, y)
        c.text_path(text)
        c.set_source_rgba(*PAPER_HALO); c.set_line_width(fs * 0.16); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
        c.set_source_rgb(*(INKC if k == "n" else SEP)); c.fill()
        y += hh * 0.14


def land_ok(land_fn, rect, want_sea):
    xs = np.linspace(rect[0], rect[2], 5); ys = np.linspace(rect[1], rect[3], 3)
    for x in xs:
        for y in ys:
            is_land = land_fn(x, y)
            if want_sea and is_land:
                return False
            if (not want_sea) and (not is_land):
                return False
    return True


def draw_places(c, edition, TER, REG, BOX, hard_rects, soft_disks, inset_hard=(), log=print):
    """c: context in sheet px (unscaled). hard_rects: rects nothing may touch. soft_disks: (x, y, r) of lettering."""
    W, H = 10800, 14400
    mode = "colour"
    MK.MUTE = 0.0 if edition == "colour" else 0.30
    hard = Occ(W, H); hard2 = Occ(W, H); soft = Occ(W, H); sym = Occ(W, H); labs = Occ(W, H); terr = Occ(W, H)
    for k in TER:
        bx0, by0 = BOX[k]
        for r in getattr(TER[k], 'glyph_rects', []):
            terr.mark((r[0] + bx0, r[1] + by0, r[2] + bx0, r[3] + by0))
    for r in hard_rects:
        hard.mark(r)
    for r in inset_hard:
        hard2.mark(r)
    HARD = {"main": hard, "aegean": hard2, "delta": hard2}
    for x, y, rad in soft_disks:
        soft.mark_disc(x, y, rad)

    def land_fn_for(region):
        t = TER[region]; bx, by = BOX[region]
        sc = t.lw / t.W

        def f(x, y):
            ix = int((x - bx) * sc); iy = int((y - by) * sc)
            if ix < 0 or iy < 0 or ix >= t.lw or iy >= t.lh:
                return False
            return bool(t.land_l[iy, ix])
        return f

    def dsea_fn_for(region):
        t = TER[region]; bx, by = BOX[region]
        sc = t.lw / t.W

        def f(x, y):
            ix = min(t.lw - 1, max(0, int((x - bx) * sc))); iy = min(t.lh - 1, max(0, int((y - by) * sc)))
            return float(t.dsea[iy, ix]), float(t.dland[iy, ix])
        return f

    LF = {k: land_fn_for(k) for k in TER}; DF = {k: dsea_fn_for(k) for k in TER}

    items = build_items(TER, REG, BOX)

    # ---- symbols: skip anything that falls under an inset or a plate; avoid overlap by tier
    ordered = sorted(items, key=lambda i: (i.tier + (0.5 if i.kind != "place" else 0), i.y))
    kept = []
    for it in ordered:
        if it.kind != "place":
            rect = (it.x - 50 * it.w / 100, it.y - 50 * it.w / 100, it.x + 50 * it.w / 100, it.y + 50 * it.w / 100)
            # battle boxes are centred on the site
        else:
            rect, _ = symbol_rect(it.mark, it.x, it.y, it.w)
        if HARD[it.region].frac(rect) > 0.04:
            log("under panel:", it.name)
            continue
        if it.kind == "isle":
            it.rect = (it.x - 3, it.y - 3, it.x + 3, it.y + 3); it.arm_rect = None
            kept.append(it)
            continue
        placed = False
        x0, y0 = it.x, it.y
        offs = [(0, 0)]
        if it.kind != "place":
            for rr_ in (1.05, 1.7):
                for k in range(8):
                    a_ = 2 * math.pi * k / 8 + 0.4
                    offs.append((rr_ * it.w * math.cos(a_), rr_ * it.w * math.sin(a_)))
        for ox, oy in offs:
          it.x, it.y = x0 + ox, y0 + oy
          for shrink in (1.0, 0.82, 0.68):
            w = it.w * shrink
            if it.kind != "place":
                rect = (it.x - 50 * w / 100, it.y - 50 * w / 100, it.x + 50 * w / 100, it.y + 50 * w / 100)
            else:
                rect, _ = symbol_rect(it.mark, it.x, it.y, w)
            if (ox or oy) and (HARD[it.region].frac(rect) > 0.04 or not LF[it.region](it.x, it.y)):
                continue
            if sym.frac(rect) < 0.12 and soft.frac(rect) < 0.35:
                it.w = w; it.rect = rect; placed = True
                break
            if it.tier <= 1 and shrink == 0.82 and not (ox or oy):
                it.w = w; it.rect = rect; placed = True; break
          if placed:
            break
        if not placed:
            it.x, it.y = x0, y0
        if not placed:
            log("skipped symbol:", it.name)
            continue
        # reserve symbol with arms
        sym.mark(it.rect)
        it.arm_rect = None
        if it.arms:
            ws = max(30.0, it.w * 0.17)
            ex = ws * (1.12 * min(3, len([a for a in it.arms if a in ORD])) + 1.4 * (1 if any(a in POW for a in it.arms) else 0)) + ws * 0.2
            it.arm_rect = (it.rect[2], it.rect[3] - ws * 2.8, it.rect[2] + ex, it.rect[3])
            sym.mark(it.arm_rect)
        kept.append(it)

    # ---- draw symbols back to front
    for it in sorted(kept, key=lambda i: i.y):
        if it.kind == "isle":
            continue
        if it.kind == "place":
            draw_symbol(c, it.mark, it.x, it.y, it.w, seed=hash(it.name) % 100000, edition=edition)
            if it.arms:
                draw_arms(c, it.arms, it.rect, it.w, mode, hash(it.name) % 1000, mode == "hatched")
        else:
            nm = it.mark.split(":")[1]
            fn = getattr(MK, nm)
            s = it.w / 100.0
            c.save(); c.translate(it.x - 50 * s, it.y - 50 * s); c.scale(s, s)
            fn(Pen(c, seed=hash(it.name) % 100000, amp=0.8))
            c.restore()

    # ---- labels
    order = sorted(kept, key=lambda i: (i.tier + (0.4 if i.kind != "place" else 0), -i.w))
    misses = []
    for it in order:
        t = it.tier
        base = {1: 62, 2: 50, 3: 42, 4: 36}[t] * it.rf * (1.12 if it.rf < 1 else 1.0)
        if it.kind != "place":
            base = (62 if it.kind == "isle" else 44) * it.rf * (1.12 if it.rf < 1 else 1.0)
        lines = label_lines(it)
        if it.kind == "isle":
            lines = [(it.name, 1.0, "m")] + ([(it.modern, 0.8, "d")] if it.modern and it.modern != it.name else [])
        reg = it.region
        dsea, dland = DF[reg](it.x, it.y)
        coastal = dsea < 1e-6 and dland < (12 if reg == "main" else 30)
        # distance to coast measured in the low-res grid (km); coastal if the symbol stands within ~14 km of sea
        near_sea = any(not LF[reg](it.x + dx, it.y + dy) for dx in (-260, 260, 0) for dy in (-100, 100, 0)) if it.kind in ("place",) else False
        if it.kind == "sea":
            near_sea = True
        coastal = near_sea or it.kind == "isle"
        rr = it.rect
        h_sym = rr[3] - rr[1]
        done = False
        for thr in (0.10, 0.45):
          for scale in (1.0, 0.86, 0.74, 0.64):
            blk = measure(c, lines, base * scale)
            bw = max(b[3] for b in blk); bh = sum(b[4] for b in blk)
            gap = 11 * it.rf + 8
            cy = (rr[1] + rr[3]) / 2
            cands = []
            def add(x0, y0, anchor, align, sea):
                cands.append(((x0, y0, x0 + bw, y0 + bh), anchor, align, y0, sea))
            xl = rr[0] - gap; xr = (it.arm_rect[2] if it.arm_rect else rr[2]) + gap
            yc = cy - bh / 2
            if it.kind == "isle":
                add(it.x - bw / 2, it.y - bh / 2, it.x, "c", "land")
            if coastal:
                for sea in (True, False):
                    add(xl - bw, yc, xl, "r", sea)
                    add(xl - bw, rr[3] - bh * 0.9, xl, "r", sea)
                    add(xl - bw, rr[1] - bh * 0.1, xl, "r", sea)
                    add(xr, yc, xr, "l", sea)
                    add((rr[0] + rr[2]) / 2 - bw / 2, rr[3] + gap, (rr[0] + rr[2]) / 2, "c", sea)
                    add((rr[0] + rr[2]) / 2 - bw / 2, rr[1] - gap - bh, (rr[0] + rr[2]) / 2, "c", sea)
            else:
                sea = False
                add(xr, yc, xr, "l", sea)
                add((rr[0] + rr[2]) / 2 - bw / 2, rr[3] + gap, (rr[0] + rr[2]) / 2, "c", sea)
                add(xl - bw, yc, xl, "r", sea)
                add((rr[0] + rr[2]) / 2 - bw / 2, rr[1] - gap - bh, (rr[0] + rr[2]) / 2, "c", sea)
                add(xr, rr[3] - bh * 0.9, xr, "l", sea)
                add(xl - bw, rr[3] - bh * 0.9, xl, "r", sea)
                add(xr, rr[1] - bh * 0.2, xr, "l", sea)
                add(xl - bw, rr[1] - bh * 0.2, xl, "r", sea)
            valid = []
            gb = (rr[0], rr[3] - 0.38 * h_sym, rr[2], rr[3])
            for rect, anchor, align, ytop, sea in cands:
                if rect[0] < 110 or rect[2] > W - 110 or rect[1] < 110 or rect[3] > H - 110:
                    continue
                if not HARD[it.region].free(rect, 4):
                    continue
                if not sym.free(rect, 6) or not labs.free(rect, 8) or soft.frac(rect) > 0.2 or terr.frac(rect) > thr:
                    continue
                if sea == "land":
                    if not land_ok(LF[reg], rect, False):
                        continue
                elif it.kind in ("place", "isle"):
                    if sea:
                        if not land_ok(LF[reg], rect, True):
                            continue
                    elif not coastal and not land_ok(LF[reg], rect, False):
                        continue
                dx = max(gb[0] - rect[2], rect[0] - gb[2], 0); dy = max(gb[1] - rect[3], rect[1] - gb[3], 0)
                valid.append((math.hypot(dx, dy) + (0 if sea else 18), rect, anchor, align, ytop))
            if valid:
                valid.sort(key=lambda v: v[0])
                _, rect, anchor, align, ytop = valid[0]
                draw_label(c, blk, anchor, ytop, align, bw)
                labs.mark(rect)
                done = True
                break
            if done:
                break
          if done:
            break
        if not done:
            misses.append(it.name)
    if misses:
        log("no label room:", ", ".join(misses))
    log("placed", len(kept), "symbols of", len(items))
