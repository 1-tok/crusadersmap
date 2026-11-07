"""Symbol review sheets for the Crusader States map."""
import cairo, numpy as np
from PIL import Image, ImageDraw, ImageFont
import profiles as PR, marks as MK
from hand import *

F = "fonts/"
def font(name, size): return ImageFont.truetype(F + name, size)
INKc = (44, 33, 26); SEPc = (107, 82, 56); REDc = (150, 32, 28)

# places that never changed hands between Franks and Muslims (or Greeks and Latins): one name only
SINGLE = {"Dimashq", "Halab", "al-Qahira", "al-Iskandariyya", "al-Mansura", "Hamah", "Hims", "Masyaf", "Ajlun",
          "Shayzar", "Sis", "Mistras", "Sainte-Katherine", "Dimyat"}


def to_pil(surf):
    w, h = surf.get_width(), surf.get_height()
    a = np.ndarray((h, w, 4), np.uint8, surf.get_data())
    return Image.fromarray(a[:, :, [2, 1, 0]].copy())


def paper(W, H, seed=3):
    rng = np.random.default_rng(seed)
    base = np.array([239, 228, 201], np.float32)
    n = rng.normal(0, 1, (H // 16 + 2, W // 16 + 2))
    n = np.asarray(Image.fromarray(((n - n.min()) / (n.max() - n.min()) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    xx = ((np.arange(W, dtype=np.float32) / W - 0.5) ** 2)[None, :]
    yy = ((np.arange(H, dtype=np.float32) / H - 0.5) ** 2)[:, None]
    v = xx + yy
    out = np.empty((H, W, 3), np.uint8)
    for k, (amp, vig) in enumerate(((14, 40), (16, 46), (20, 54))):
        out[..., k] = np.clip(base[k] - (n - 0.5) * amp - v * vig, 0, 255)
    return out


def draw_cells(W, H, cells, S, cw, ch, x0, y0, cols, unit_w, unit_h, seed0=10):
    """Render drawings into a cairo surface (transparent bg) and return it."""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    for i, fn in enumerate(cells):
        cx = x0 + (i % cols) * cw + (cw - unit_w * S) / 2
        cy = y0 + (i // cols) * ch
        c.save(); c.translate(cx, cy); c.scale(S, S)
        fn(Pen(c, seed=seed0 + i), c) if fn.__code__.co_argcount == 2 else fn(Pen(c, seed=seed0 + i))
        c.restore()
    return surf


def composite(bg, surf):
    w, h = surf.get_width(), surf.get_height()
    a = np.ndarray((h, w, 4), np.uint8, surf.get_data())
    out = bg.copy()
    flat = np.array([239, 228, 201], np.float32)
    step = 512
    for y0 in range(0, h, step):
        blk = a[y0:y0 + step].astype(np.float32)
        rgb = blk[:, :, [2, 1, 0]]; al = blk[:, :, 3:4] / 255
        bgf = bg[y0:y0 + step].astype(np.float32)
        o = rgb + bgf * (1 - al)
        # drawings fill with flat paper to hide what lies behind; let the textured paper show there instead
        near = (np.abs(rgb / np.maximum(al, 1e-3) - flat).sum(axis=2, keepdims=True) < 12) & (al > 0.95)
        o = np.where(near, bgf, o)
        out[y0:y0 + step] = np.clip(o, 0, 255).astype(np.uint8)
    return out


def centred(d, x, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text((x - w / 2, y), text, font=f, fill=fill)


def header(d, W, y, title, sub=None):
    centred(d, W / 2, y, title, font("Fondamento-Regular.ttf", 92), INKc)
    if sub:
        centred(d, W / 2, y + 112, sub, font("IMFeENit28P.ttf", 46), SEPc)
    d.line([(W * 0.2, y + (180 if sub else 120)), (W * 0.8, y + (180 if sub else 120))], fill=SEPc, width=3)


# ------------------------------------------------------------------ sheet 1: profiles
def sheet_profiles():
    groups = [("Cities", PR.CITIES), ("Castles", PR.CASTLES), ("Holy places", PR.HOLY)]
    cols, S = 6, 2.55
    cw, ch = 900, 780
    W = cols * cw + 200
    y = 420
    layout = []
    for g, items in groups:
        layout.append(("h", g, y)); y += 170
        rows = (len(items) + cols - 1) // cols
        layout.append(("c", items, y)); y += rows * ch
        y += 60
    H = y + 120
    bg = paper(W, H)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    k = 0
    for item in layout:
        if item[0] != "c":
            continue
        for i, (fn, *_r) in enumerate(item[1]):
            cx = 100 + (i % cols) * cw + (cw - 320 * S) / 2
            cy = item[2] + (i // cols) * ch
            c.save(); c.translate(cx, cy); c.scale(S, S); fn(Pen(c, seed=40 + k)); c.restore(); k += 1
    img = Image.fromarray(composite(bg, surf))
    d = ImageDraw.Draw(img)
    header(d, W, 80, "Cities, Castles and Holy Places",
           "each drawn in its own profile; holder's name first, both forms where the place changed hands, modern name beneath")
    fM = font("Fondamento-Regular.ttf", 50); fA = font("Fondamento-Italic.ttf", 40)
    fN = font("IMFeENit28P.ttf", 38); fNote = font("IMFeENit28P.ttf", 32)
    for item in layout:
        if item[0] == "h":
            centred(d, W / 2, item[2], item[1], font("Fondamento-Regular.ttf", 72), REDc)
            continue
        for i, (fn, main, alt, modern, note) in enumerate(item[1]):
            x = 100 + (i % cols) * cw + cw / 2
            yb = item[2] + (i // cols) * ch + 220 * S + 4
            name = main if (main in SINGLE or not alt) else f"{main} / {alt}"
            f = fM
            while d.textlength(name, font=f) > cw - 40 and f.size > 30:
                f = font("Fondamento-Regular.ttf", f.size - 2)
            centred(d, x, yb, name, f, INKc)
            centred(d, x, yb + 58, modern, fN, SEPc)
            centred(d, x, yb + 102, note, fNote, SEPc)
    return img


# ------------------------------------------------------------------ sheet 2: marks and badges
def sheet_marks():
    cols, S = 6, 4.6
    cw, ch = 860, 600
    W = cols * cw + 200
    sections = [("Towns and villages", MK.SETTLE), ("Castles and strongholds", MK.CASTLE),
                ("Churches, mosques and holy places", MK.HOLY), ("War", MK.WAR)]
    y = 420
    layout = []
    for t, items in sections:
        layout.append(("h", t, y)); y += 150
        layout.append(("m", items, y)); y += ((len(items) + cols - 1) // cols) * ch + 30
    layout.append(("h", "Military orders: holdings marked with the order's arms", y)); y += 150
    layout.append(("b", MK.ORDERS, y, "shield", 3)); y += 2 * 520 + 30
    layout.append(("h", "Maritime republics and Byzantium: holdings marked with a banner", y)); y += 150
    layout.append(("b", MK.POWERS, y, "banner", 4)); y += 500 + 30
    layout.append(("h", "How the marks combine", y)); y += 150
    layout.append(("x", None, y)); y += 760
    H = y + 80
    bg = paper(W, H, seed=5)
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    c = cairo.Context(surf)
    labels = []
    k = 0
    for item in layout:
        if item[0] == "m":
            for i, (fn, lab) in enumerate(item[1]):
                cx = 100 + (i % cols) * cw + (cw - 100 * S) / 2
                cy = item[2] + (i // cols) * ch
                c.save(); c.translate(cx, cy); c.scale(S, S); fn(Pen(c, seed=70 + k)); c.restore(); k += 1
                labels.append((100 + (i % cols) * cw + cw / 2, cy + 92 * S, lab, None))
        elif item[0] == "b":
            per_row = item[4]
            bw = 160
            colw = (W - 200) / per_row
            for i, (name, sub, field, charge) in enumerate(item[1]):
                col = i % per_row; row = i // per_row
                mid = 100 + col * colw + colw / 2
                cy = item[2] + row * 520
                for j, mode in enumerate(("colour", "hatched")):
                    MK.badge(c, mid - 215 + j * 270, cy + 20, bw, field, charge, mode=mode, kind=item[3], seed=i * 3 + j)
                labels.append((mid, cy + 250, name, sub))
        elif item[0] == "x":
            # example: Crac des Chevaliers with the Hospital's arms and its years; Acre with three badges
            yy = item[2]
            c.save(); c.translate(300, yy); c.scale(2.2, 2.2); PR.krak(Pen(c, seed=3)); c.restore()
            MK.badge(c, 1060, yy + 210, 90, "gules", [("cross", "argent")])
            c.save(); c.translate(2250, yy); c.scale(2.2, 2.2); PR.acre(Pen(c, seed=4)); c.restore()
            for j, (f_, ch_) in enumerate((("gules", [("cross", "argent")]), ("argent", [("cross_pattee", "gules")]), ("argent", [("cross_pattee", "sable")]))):
                MK.badge(c, 3000 + j * 110, yy + 210, 90, f_, ch_)
            for j, (f_, ch_) in enumerate((("gules", [("lion", "or_")]), ("argent", [("cross", "gules")]), ("gules", [("cross_pommee", "argent")]))):
                MK.badge(c, 3020 + j * 130, yy + 370, 80, f_, ch_, kind="banner")
            c.save(); c.translate(4300, yy + 40); c.scale(3.4, 3.4); MK.battle(Pen(c, seed=9)); c.restore()
    img = Image.fromarray(composite(bg, surf))
    d = ImageDraw.Draw(img)
    header(d, W, 80, "Marks of the Map", "lesser places, holy places, war, and the arms of the orders and powers")
    fL = font("Fondamento-Regular.ttf", 50); fS = font("IMFeENit28P.ttf", 38)
    for item in layout:
        if item[0] == "h":
            centred(d, W / 2, item[2], item[1], font("Fondamento-Regular.ttf", 64), REDc)
        if item[0] == "b":
            centred(d, 100 + (W - 200) / 6, item[2] + 0, "", fS, SEPc)
    for x, y, lab, sub in labels:
        centred(d, x, y, lab, fL, INKc)
        if sub:
            centred(d, x, y + 54, sub, fS, SEPc)
            centred(d, x, y + 100, "colour  |  parchment, in heraldic hatching", font("IMFeENit28P.ttf", 32), SEPc)
    for item in layout:
        if item[0] == "x":
            yy = item[2]
            fM = font("Fondamento-Regular.ttf", 50); fI = font("IMFeENit28P.ttf", 38)
            centred(d, 300 + 352, yy + 520, "Crac des Chevaliers / Hisn al-Akrad", fM, INKc)
            centred(d, 300 + 352, yy + 580, "Qal'at al-Hisn", fI, SEPc)
            centred(d, 300 + 352, yy + 626, "Hospitaller 1142 - 1271", fI, REDc)
            centred(d, 2250 + 352, yy + 520, "Acre / Akka", fM, INKc)
            centred(d, 2250 + 352, yy + 580, "Akko", fI, SEPc)
            centred(d, 2250 + 352, yy + 626, "Frankish 1104 - 1187, 1191 - 1291", fI, REDc)
            centred(d, 4300 + 170, yy + 400, "Hattin 1187", fM, INKc)
            centred(d, 4300 + 170, yy + 460, "Hittin", fI, SEPc)
    return img


if __name__ == "__main__":
    a = sheet_profiles(); a.save("out/crusader-symbols-profiles.jpg", quality=88)
    b = sheet_marks(); b.save("out/crusader-symbols-marks.jpg", quality=88)
    print(a.size, b.size)
