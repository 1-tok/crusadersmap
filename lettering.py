"""Lettering that follows a curve: polity names with modern spelling and dates beneath."""
import math, bisect
import cairo

RED = (0.59, 0.125, 0.11); SEP = (0.42, 0.32, 0.22); INKC = (0.17, 0.13, 0.10)
HALO = (0.94, 0.90, 0.79, 0.8)


def catmull(pts, step=5.0):
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        L = math.dist(p1, p2)
        n = max(2, int(L / step))
        for j in range(n):
            t = j / n
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1)))
    out.append(pts[-1])
    return out


def orient(pts):
    dx = pts[-1][0] - pts[0][0]; dy = pts[-1][1] - pts[0][1]
    if abs(dx) < 0.35 * abs(dy):
        return pts[::-1] if dy > 0 else pts          # vertical: read bottom to top
    return pts if dx > 0 else pts[::-1]


def path_len(pts):
    return sum(math.dist(pts[i - 1], pts[i]) for i in range(1, len(pts)))


def natural_width(c, text, size, spacing_frac, fam="Fondamento", slant=cairo.FONT_SLANT_NORMAL):
    c.select_font_face(fam, slant, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    adv = [c.text_extents(ch).x_advance for ch in text]
    return sum(adv) + size * spacing_frac * (len(text) - 1)


def text_on_path(c, text, pts, size, spacing, color, fam="Fondamento", slant=cairo.FONT_SLANT_NORMAL, offset=0.0, halo=HALO):
    pts = orient(catmull(pts))
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + math.dist(pts[i - 1], pts[i]))
    c.select_font_face(fam, slant, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    adv = [c.text_extents(ch).x_advance for ch in text]
    total = sum(adv) + spacing * (len(text) - 1)
    s = max(0.0, (cum[-1] - total) / 2)
    for ch, a in zip(text, adv):
        mid = s + a / 2
        s += a + spacing
        if ch == " ":
            continue
        i = min(len(pts) - 2, max(0, bisect.bisect_left(cum, mid) - 1))
        seg = cum[i + 1] - cum[i] or 1
        t = (mid - cum[i]) / seg
        x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t
        y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
        j0 = max(0, i - 2); j1 = min(len(pts) - 1, i + 3)
        ang = math.atan2(pts[j1][1] - pts[j0][1], pts[j1][0] - pts[j0][0])
        c.save()
        c.translate(x, y); c.rotate(ang); c.translate(0, offset)
        c.move_to(-a / 2, 0)
        c.text_path(ch)
        if halo:
            c.set_source_rgba(*halo); c.set_line_width(size * 0.12); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
        c.set_source_rgb(*color); c.fill()
        c.restore()


def polity(c, name, modern, dates, pts, max_size, sp=0.5, fit=0.92):
    """Letter a polity along pts (sheet px). The caps are sized to fill the path, up to max_size.
    Returns the sampled disks (x, y, r) the lettering covers."""
    pts = orient(catmull(pts))
    L = path_len(pts)
    w100 = natural_width(c, name, 100.0, sp)
    size = min(max_size, 100.0 * fit * L / w100)
    text_on_path(c, name, pts, size, size * sp, RED)
    text_on_path(c, modern, pts, size * 0.52, size * 0.12, SEP, fam="IM FELL English", slant=cairo.FONT_SLANT_ITALIC, offset=size * 0.84)
    if dates:
        text_on_path(c, dates, pts, size * 0.46, size * 0.10, SEP, fam="IM FELL English", slant=cairo.FONT_SLANT_ITALIC, offset=size * 1.36)
    # disks to reserve
    disks = []
    cum = 0.0
    nxt = 0.0
    start = (L - w100 * size / 100.0) / 2
    for i in range(1, len(pts)):
        cum += math.dist(pts[i - 1], pts[i])
        if cum >= nxt:
            nxt += size * 0.6
            if start - size <= cum <= L - start + size:
                disks.append((pts[i][0], pts[i][1] + size * 0.55, size * 1.25))
    return disks
