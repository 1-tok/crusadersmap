"""Stage 1: sheet layout, hand-drawn terrain, curved polity lettering. Both editions, preview scale."""
import sys, math, time
import numpy as np, cairo
from PIL import Image
import frame as FR
import terrain as T
from rough import Region

S = float(sys.argv[1]) if len(sys.argv) > 1 else 0.4
W, H = FR.W, FR.H
WS, HS = int(round(W * S)), int(round(H * S))
RED = (0.59, 0.125, 0.11); SEP = (0.42, 0.32, 0.22); INKC = (0.17, 0.13, 0.10)

# ------------------------------------------------------------------ regions and boxes
main = Region(FR.PROJ, FR.X0, FR.X1, FR.Y0, FR.Y1, W, H)
ae = Region.from_lonlat(FR.INSETS["aegean"]["proj"], FR.INSETS["aegean"]["ext"], 4800)
de = Region.from_lonlat(FR.INSETS["delta"]["proj"], FR.INSETS["delta"]["ext"], 4800)
BOX = {"main": (0, 0), "aegean": (190, 190), "delta": (190, 13760 - de.h)}
JW = 2410
JH = int(round(JW * 1491 / 1055))
JX, JY = 10600 - JW, 13760 - JH
JSRC = Image.open("data/jerusalem-src.png").convert("RGB")
REG = {"main": main, "aegean": ae, "delta": de}
CONT = {"main": T.MAIN, "aegean": T.AEGEAN, "delta": T.DELTA}
TER = {k: T.Terrain(REG[k], CONT[k], seed=i + 3, S=S) for i, k in enumerate(("main", "aegean", "delta"))}


def paper_tex(w, h, seed=3):
    rng = np.random.default_rng(seed)
    n = rng.normal(0, 1, (h // 10 + 2, w // 10 + 2))
    n = np.asarray(Image.fromarray(((n - n.min()) / np.ptp(n) * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC), np.float32) / 255
    xx = ((np.arange(w, dtype=np.float32) / w - 0.5) ** 2)[None, :]
    yy = ((np.arange(h, dtype=np.float32) / h - 0.5) ** 2)[:, None]
    v = xx + yy
    out = np.empty((h, w, 3), np.float32)
    for k, (b, amp, vig) in enumerate(((239, 14, 40), (228, 16, 46), (201, 20, 54))):
        out[..., k] = b - (n - 0.5) * amp - v * vig
    return out


def base_for(edition):
    tex = paper_tex(WS, HS)
    out = tex.copy()
    for k in ("main", "aegean", "delta"):
        bx, by = BOX[k]
        x, y = int(round(bx * S)), int(round(by * S))
        hk = TER[k].hs
        for r0 in range(0, hk, 900):
            r1 = min(hk, r0 + 900)
            col, a = TER[k].wash(edition, r0, r1)
            h_, w_ = col.shape[:2]
            sl = (slice(y + r0, y + r0 + h_), slice(x, x + w_))
            mod = tex[sl] / np.array([239, 228, 201], np.float32)
            out[sl] = tex[sl] * (1 - a) + col * mod * a
    g = grade_jerusalem(out, S, edition)
    jh, jw = g.shape[:2]
    x0, y0 = int(round(JX * S)), int(round(JY * S))
    out[y0:y0 + jh, x0:x0 + jw] = g
    return out


def grade_jerusalem(out, S_, edition):
    """The Jerusalem plate resampled to scale S_ and graded to the edition, sampling the map land in `out` for colour."""
    from skimage import color as skc
    jw, jh = int(round(JW * S_)), int(round(JH * S_))
    im = np.asarray(JSRC.resize((jw, jh), Image.LANCZOS), np.float32) / 255
    ref_sl = (slice(int(9000 * S_), int(12000 * S_)), slice(int(6200 * S_), int(7800 * S_)))
    ref = np.clip(out[ref_sl], 0, 255).astype(np.float32) / 255
    lab = skc.rgb2lab(im); rl = skc.rgb2lab(ref)
    if edition == "colour":
        # keep the picture's own life but pull its palette toward the coloured map
        k = 0.45
        for ch in range(3):
            m, s = lab[..., ch].mean(), lab[..., ch].std() + 1e-6
            rm, rs = rl[..., ch].mean(), rl[..., ch].std() + 1e-6
            tgt = (lab[..., ch] - m) / s * (rs * 0.55 + s * 0.45) + (rm * k + m * (1 - k))
            lab[..., ch] = tgt if ch else lab[..., ch]
        lab[..., 1:] *= 1.05
        g = skc.lab2rgb(lab)
    else:
        lab[..., 1:] *= 0.50                      # mute the colour
        lab[..., 0] = 0.78 * lab[..., 0] + 0.22 * 92 + 3
        g = skc.lab2rgb(lab)
        tone = np.array([0.985, 0.955, 0.86], np.float32)
        g = g * tone
    g = np.clip(g, 0, 1) * 255
    return g


# ------------------------------------------------------------------ lettering
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


def text_on_path(c, text, pts, size, spacing, color, fam="Fondamento", slant=cairo.FONT_SLANT_NORMAL, offset=0.0, halo=None):
    pts = orient(catmull(pts))
    cum = [0.0]
    for i in range(1, len(pts)):
        cum.append(cum[-1] + math.dist(pts[i - 1], pts[i]))
    c.select_font_face(fam, slant, cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)
    adv = [c.text_extents(ch).x_advance for ch in text]
    total = sum(adv) + spacing * (len(text) - 1)
    s = (cum[-1] - total) / 2
    if s < 0:
        s = 0
    import bisect
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
        # tangent from a short window for smooth rotation
        j0 = max(0, i - 2); j1 = min(len(pts) - 1, i + 3)
        ang = math.atan2(pts[j1][1] - pts[j0][1], pts[j1][0] - pts[j0][0])
        c.save()
        c.translate(x, y); c.rotate(ang)
        c.translate(0, offset)
        c.move_to(-a / 2, 0)
        c.text_path(ch)
        if halo:
            c.set_source_rgba(*halo); c.set_line_width(size * 0.12); c.set_line_join(cairo.LINE_JOIN_ROUND); c.stroke_preserve()
        c.set_source_rgb(*color); c.fill()
        c.restore()


def polity(c, reg, name, modern, dates, ll, size, off=0.0, sp=0.55, halo=(0.94, 0.90, 0.79, 0.8)):
    size = size * (1.4 if reg is main else 1.0)
    pts = [reg.ll_px(lo, la) for lo, la in ll]
    text_on_path(c, name, pts, size, size * sp, RED, offset=off, halo=halo)
    text_on_path(c, modern, pts, size * 0.52, size * 0.12, SEP, fam="IM FELL English", slant=cairo.FONT_SLANT_ITALIC, offset=off + size * 0.84, halo=halo)
    text_on_path(c, dates, pts, size * 0.46, size * 0.10, SEP, fam="IM FELL English", slant=cairo.FONT_SLANT_ITALIC, offset=off + size * 1.36, halo=halo)


MAIN_POL = [
    ("KINGDOM OF IHERUSALEM", "Kingdom of Jerusalem", "1099 - 1291", [(35.6, 33.25), (35.42, 32.7), (35.28, 32.15), (35.08, 31.7), (34.85, 31.5)], 100),
    ("COUNTY OF TRIPLE", "County of Tripoli", "1109 - 1289", [(35.98, 34.95), (36.1, 34.55), (36.0, 34.15)], 72),
    ("PRINCIPALITY OF ANTIOCHE", "Principality of Antioch", "1098 - 1268", [(35.95, 35.55), (36.3, 35.78), (36.75, 36.05)], 66),
    ("KINGDOM OF CYPRUS", "Kingdom of Cyprus", "1192 - 1489", [(32.7, 34.82), (33.25, 35.05), (33.9, 35.25)], 82),
    ("KINGDOM OF ARMENIA", "Armenian Cilicia", "1198 - 1375", [(34.8, 36.8), (35.45, 37.0), (36.0, 37.2)], 66),
    ("OUTREJORDAIN", "Transjordan", "1118 - 1189", [(35.88, 32.0), (35.8, 31.35), (35.7, 30.75)], 70),
    ("EMIRATE OF DIMASHQ", "Damascus", "1104 - 1260", [(35.98, 33.78), (36.35, 33.8), (36.75, 33.7)], 56),
    ("SULTANATE OF RUM", "Seljuk Anatolia", "1077 - 1308", [(34.4, 37.82), (35.2, 37.92), (36.0, 37.85)], 56),
]
AEG_POL = [
    ("PRINCIPALITY OF ACHAIE", "Achaea", "1205 - 1432", [(21.45, 37.55), (22.05, 37.65), (22.65, 37.55)], 170),
    ("DUCHY OF ATHENES", "Duchy of Athens", "1205 - 1456", [(22.7, 38.55), (23.3, 38.45), (24.0, 38.35)], 130),
    ("CANDIA", "Crete (Venice)", "1211 - 1669", [(24.0, 35.4), (24.7, 35.35), (25.5, 35.3)], 130),
    ("EMPIRE OF NICAEA", "Nicaea", "1204 - 1261", [(26.9, 39.1), (27.9, 39.3), (28.9, 39.35)], 130),
    ("EMPIRE OF CONSTANTINOPLE", "Latin Empire", "1204 - 1261", [(26.2, 41.25), (27.6, 41.4), (29.0, 41.3)], 120),
]
DEL_POL = [
    ("SOUDANIE OF EGYPT", "Egypt: Fatimid, Ayyubid, Mamluk", "969 - 1517", [(30.55, 29.5), (31.3, 29.35), (32.0, 29.4)], 170),
]


def plate(c, x, y, w, h):
    c.save()
    c.rectangle(x, y, w, h); c.set_source_rgb(0.95, 0.915, 0.82); c.fill()
    for k, lw in ((0, 5), (13, 2.5)):
        c.set_source_rgb(*INKC); c.set_line_width(lw)
        c.rectangle(x - k, y - k, w + 2 * k, h + 2 * k); c.stroke()
    c.restore()


def centred(c, s, cx, y, size, color=INKC, fam="Fondamento", slant=cairo.FONT_SLANT_NORMAL):
    c.select_font_face(fam, slant, cairo.FONT_WEIGHT_NORMAL); c.set_font_size(size)
    e = c.text_extents(s)
    c.move_to(cx - e.x_advance / 2, y); c.set_source_rgb(*color); c.show_text(s)


def compass(c, cx, cy, R):
    c.new_path()
    c.save()
    c.translate(cx, cy)
    c.set_source_rgb(*INKC)
    for rr, lw in ((R, 5), (R * 0.88, 2.5)):
        c.set_line_width(lw); c.arc(0, 0, rr, 0, 2 * math.pi); c.stroke()
    for ang, L, wdt in [(a, R * 1.12 if a % 90 == 0 else R * 0.78, 0.12 if a % 90 == 0 else 0.09) for a in range(0, 360, 45)]:
        c.save(); c.rotate(math.radians(ang))
        c.move_to(0, -L); c.line_to(-L * wdt * 1.3, 0); c.line_to(0, 0); c.close_path()
        c.set_source_rgb(0.95, 0.915, 0.82); c.fill_preserve(); c.set_source_rgb(*INKC); c.set_line_width(2.5); c.stroke()
        c.move_to(0, -L); c.line_to(L * wdt * 1.3, 0); c.line_to(0, 0); c.close_path()
        c.set_source_rgb(*INKC); c.fill()
        c.restore()
    centred(c, "N", 0, -R * 1.22, R * 0.34)
    c.restore()


def draw_ink(edition):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, WS, HS)
    c = cairo.Context(surf)
    c.scale(S, S)
    for k in ("main", "aegean", "delta"):
        bx, by = BOX[k]
        c.save(); c.translate(bx, by)
        c.rectangle(0, 0, REG[k].w, REG[k].h)
        if k == "main":
            c.rectangle(JX - 20, JY - 20, JW + 40, JH + 40)
            c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        c.clip()
        t0 = time.time()
        TER[k].ink(c, edition)
        # lettering
        pol = {"main": MAIN_POL, "aegean": AEG_POL, "delta": DEL_POL}[k]
        for nm, mod, dt, ll, sz in pol:
            polity(c, REG[k], nm, mod, dt, ll, sz)
        c.restore()
        print(edition, k, round(time.time() - t0, 1), "s", flush=True)
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
    # Jerusalem panel frame
    c.set_source_rgb(*INKC)
    for off, lw in ((0, 6), (16, 3)):
        c.set_line_width(lw); c.rectangle(JX - off, JY - off, JW + 2 * off, JH + 2 * off); c.stroke()
    # panels
    plate(c, 300, 4800, 2000, 4300)
    centred(c, "KEY", 1300, 4990, 90, SEP)
    plate(c, 2700, 6750, 2700, 1000)
    centred(c, "Outremer", 4050, 7300, 190)
    centred(c, "The Crusader States and their Neighbours", 4050, 7480, 62)
    centred(c, "1095 - 1571", 4050, 7640, 52, SEP, "IM FELL English", cairo.FONT_SLANT_ITALIC)
    plate(c, 190, 13920, 10420, 330)
    centred(c, "SOURCES AND SCALE", 5400, 14125, 84, SEP)
    compass(c, 4300, 8950, 330)
    # off-sheet note for Edessa and Harran
    plate(c, 8300, 1500, 2300, 560)
    centred(c, "County of Rohais (Edessa) and", 9450, 1705, 62, SEP, "IM FELL English", cairo.FONT_SLANT_ITALIC)
    centred(c, "Harran lie off the sheet to the east", 9450, 1790, 62, SEP, "IM FELL English", cairo.FONT_SLANT_ITALIC)
    centred(c, "1098 - 1150", 9450, 1925, 56, SEP, "IM FELL English", cairo.FONT_SLANT_ITALIC)
    # neatline
    c.set_source_rgb(*INKC)
    for off, lw in ((30, 8), (70, 3)):
        c.set_line_width(lw); c.rectangle(off, off, W - 2 * off, H - 2 * off); c.stroke()
    return surf


def composite(base, surf):
    a = np.ndarray((HS, WS, 4), np.uint8, surf.get_data())
    out = np.empty((HS, WS, 3), np.uint8)
    for y0 in range(0, HS, 512):
        blk = a[y0:y0 + 512].astype(np.float32)
        al = blk[..., 3:4] / 255
        rgb = blk[..., [2, 1, 0]]
        out[y0:y0 + 512] = np.clip(rgb + base[y0:y0 + 512] * (1 - al), 0, 255).astype(np.uint8)
    return out


if __name__ == "__main__":
    for ed in ("parchment", "colour"):
        base = base_for(ed)
        surf = draw_ink(ed)
        img = composite(base, surf)
        Image.fromarray(img).save(f"out/stage1-{ed}.jpg", quality=88)
        print("saved", ed, flush=True)
        del surf, base
