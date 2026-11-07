"""Rough sheet: main map with the two insets, panels and orientation names, at quarter size."""
import numpy as np
from PIL import Image, ImageDraw
import frame as FR
from rough import *

base = Image.open("out/rough-main-base.png").convert("RGB")
r = Region(FR.PROJ, FR.X0, FR.X1, FR.Y0, FR.Y1, PW, PH)
d = ImageDraw.Draw(base)

def q(v): return int(round(v / Q))

# faint graticule
for lo in range(30, 42):
    d.line([r.ll_px(lo, la) for la in np.linspace(27, 39, 50)], fill=(196, 180, 150), width=1)
for la in range(27, 39):
    d.line([r.ll_px(lo, la) for lo in np.linspace(29, 42, 50)], fill=(196, 180, 150), width=1)

# orientation names (holder's name, modern beneath)
PLACES = [
    ("Iherusalem / al-Quds", "Jerusalem", 35.23, 31.78), ("Acre / Akka", "Akko", 35.07, 32.92),
    ("Antioche / Antakiya", "Antakya", 36.16, 36.2), ("Triple / Tarabulus", "Tripoli", 35.84, 34.44),
    ("Sur / Tyr", "Tyre", 35.2, 33.27), ("Rohais / al-Ruha", "Sanliurfa", 38.79, 37.15),
    ("Dimashq", "Damascus", 36.3, 33.51), ("Halab", "Aleppo", 37.16, 36.2), ("Famagouste", "Famagusta", 33.94, 35.12),
    ("Nicosie / Lefkosia", "Nicosia", 33.36, 35.17), ("Crac des Chevaliers", "Qal'at al-Hisn", 36.29, 34.76),
    ("Crac de Moab / al-Karak", "Kerak", 35.7, 31.18), ("Montreal / al-Shawbak", "Shobak", 35.56, 30.53),
    ("Escalone / Asqalan", "Ashkelon", 34.55, 31.66), ("Japhe / Yafa", "Jaffa", 34.75, 32.05),
    ("Sis", "Kozan", 35.81, 37.45), ("Ile de Graye / Ayla", "Pharaoh's Island", 34.86, 29.45),
    ("Tadmur", "Palmyra", 38.27, 34.56),
    ("Margat / al-Marqab", "Qal'at al-Marqab", 35.95, 35.15), ("Hims", "Homs", 36.72, 34.73),
    ("Hamah", "Hama", 36.75, 35.13), ("Baalbek", "Baalbek", 36.2, 34.0), ("Bosra", "Bosra", 36.48, 32.52),
    ("Harran", "Harran", 39.03, 36.86), ("al-Raqqa", "Raqqa", 39.0, 35.95), ("Marash", "Kahramanmaras", 36.92, 37.58),
    ("Tarse", "Tarsus", 34.9, 36.92), ("Lajazzo / Ayas", "Yumurtalik", 35.79, 36.77), ("Selefke", "Silifke", 33.93, 36.38),
    ("Gaza / Ghazza", "Gaza", 34.45, 31.5), ("Darum", "Deir al-Balah", 34.35, 31.42),
]
fN = font("Fondamento-Regular.ttf", 22); fI = font("IMFeENit28P.ttf", 17)
for nm, mod, lo, la in PLACES:
    x, y = r.ll_px(lo, la)
    d.ellipse([x - 4, y - 4, x + 4, y + 4], outline=INK, width=2)
    d.text((x + 7, y - 14), nm, font=fN, fill=INK)
    d.text((x + 7, y + 9), mod, font=fI, fill=SEP)

# region names to show where the lettering of the polities will sit (settled land only)
REG = [("KINGDOM OF IHERUSALEM", 35.05, 31.9, 1099), ("COUNTY OF TRIPLE", 36.0, 34.3, 1109),
       ("PRINCIPALITY OF ANTIOCHE", 36.35, 35.9, 1098), ("COUNTY OF ROHAIS", 38.3, 37.0, 1098),
       ("KINGDOM OF CYPRUS", 33.2, 35.05, 1192), ("ARMENIAN CILICIA", 35.7, 37.3, 1198),
       ("OULTREJORDAIN", 35.75, 30.9, 1118)]
fR = font("Fondamento-Regular.ttf", 34)
for nm, lo, la, yr in REG:
    x, y = r.ll_px(lo, la)
    txt = " ".join(nm)
    w = d.textlength(txt, font=fR)
    d.text((x - w / 2, y), txt, font=fR, fill=(150, 32, 28))

# ---------------------------------------------------------------- insets
def inset(name, bx, by, bw):
    spec = FR.INSETS[name]
    reg = Region.from_lonlat(spec["proj"], spec["ext"], q(bw))
    img, _ = reg.render(6, relief_scale=0.6, river_w=2)
    return reg, img

frames = {}
H_ = base.size[1]
for name, bw, corner in (("aegean", 4800, "tl"), ("delta", 4800, "bl")):
    bx = 190
    probe = FR.INSETS[name]
    reg, img = inset(name, 0, 0, bw)
    h_print = img.size[1] * Q
    by = 190 if corner == "tl" else FR.H - 190 - h_print
    x, y = q(bx), q(by)
    base.paste(img, (x, y))
    frames[name] = (x, y, img.size[0], img.size[1], reg)
    print(name, "box", bx, by, bw, h_print)

d = ImageDraw.Draw(base)
INS_PLACES = {
    "aegean": [("Konstantinoupolis", "Istanbul", 28.97, 41.01), ("Rhodes", "Rhodes", 28.22, 36.44),
               ("Candia", "Heraklion", 25.13, 35.34), ("Negroponte", "Chalkida", 23.6, 38.46), ("Athenes / Setines", "Athens", 23.73, 37.97),
               ("Andreville", "Andravida", 21.27, 37.9), ("Mistras", "Mystras", 22.37, 37.07), ("Modon", "Methoni", 21.7, 36.82),
               ("Coron", "Koroni", 21.96, 36.8), ("Naxie", "Naxos", 25.38, 37.1), ("Scio / Chios", "Chios", 26.14, 38.37),
               ("Mitylene", "Mytilene", 26.55, 39.1), ("Saint-Pierre", "Bodrum", 27.43, 37.03), ("Thessalonike", "Thessaloniki", 22.94, 40.64),
               ("Gallipoli", "Gelibolu", 26.67, 40.41), ("Smyrne / Izmir", "Izmir", 27.14, 38.42), ("Monemvasia", "Monemvasia", 23.04, 36.69),
               ("Corfou", "Corfu", 19.92, 39.62)],
    "delta": [("al-Qahira", "Cairo", 31.26, 30.04), ("al-Iskandariyya", "Alexandria", 29.9, 31.2), ("Dimyat / Damiete", "Damietta", 31.81, 31.42),
              ("al-Mansura", "Mansoura", 31.38, 31.04), ("Fariskur", "Faraskur", 31.73, 31.33), ("Rashid", "Rosetta", 30.42, 31.4),
              ("Tinnis", "Tinnis", 32.23, 31.2), ("al-Farama", "Pelusium", 32.56, 31.04), ("Bilbays", "Bilbeis", 31.56, 30.42),
              ("Wadi al-Natrun", "Wadi El Natrun", 30.33, 30.38),
              ("Ile de Graye", "Pharaoh's Island", 34.85, 29.55), ("Sainte-Katherine", "St Catherine's", 33.97, 28.56), ("Suez / al-Suways", "Suez", 32.55, 29.97), ("Sur", "al-Tur", 33.6, 28.24)],
}
for name, (x, y, w, h, reg) in frames.items():
    for nm, mod, lo, la in INS_PLACES[name]:
        px, py = reg.ll_px(lo, la)
        if 0 < px < w and 0 < py < h:
            px += x; py += y
            d.ellipse([px - 4, py - 4, px + 4, py + 4], outline=INK, width=2)
            off = 7
            if px + d.textlength(nm, font=fN) + 10 > x + w:
                off = -7 - d.textlength(nm, font=fN)
            d.text((px + off, py - 14), nm, font=fN, fill=INK)
            d.text((px + off, py + 9), mod, font=fI, fill=SEP)
    # double rule border and title plate
    for k, wd in ((0, 4), (9, 2)):
        d.rectangle([x - k, y - k, x + w + k, y + h + k], outline=INK, width=wd)
    t = FR.INSETS[name]["title"]
    ft = font("Fondamento-Regular.ttf", 34)
    tw = d.textlength(t, font=ft)
    d.rectangle([x + 18, y + 16, x + 46 + tw, y + 66], fill=(240, 229, 203), outline=INK, width=2)
    d.text((x + 32, y + 22), t, font=ft, fill=INK)

# ---------------------------------------------------------------- panels (print px boxes)
fP = font("Fondamento-Regular.ttf", 30)
def plate(bx, by, bw, bh):
    x, y, w, h = q(bx), q(by), q(bw), q(bh)
    d.rectangle([x, y, x + w, y + h], fill=(242, 233, 208))
    for k, wd in ((0, 3), (7, 1)):
        d.rectangle([x - k, y - k, x + w + k, y + h + k], outline=INK, width=wd)
    return x, y, w, h

# key: recurring symbols, arms of the orders and powers only
x, y, w, h = plate(300, 5500, 2000, 4300)
d.text((x + 20, y + 20), "KEY", font=fP, fill=SEP)
d.text((x + 20, y + 70), "marks, arms of orders and powers", font=font("IMFeENit28P.ttf", 17), fill=SEP)
# sources and scale
x, y, w, h = plate(2700, 9200, 1800, 800)
tw = d.textlength("SOURCES AND SCALE", font=fP)
d.text((x + w / 2 - tw / 2, y + h / 2 - 18), "SOURCES AND SCALE", font=fP, fill=SEP)
# title cartouche
x, y, w, h = plate(2700, 6750, 2500, 950)
for txt, f_, dy, c in (("Outremer", font("Fondamento-Regular.ttf", 52), 6, INK),
                       ("The Crusader States and their Neighbours", font("Fondamento-Regular.ttf", 17), 70, INK),
                       ("1095 - 1571", font("IMFeENit28P.ttf", 20), 98, SEP)):
    tw = d.textlength(txt, font=f_)
    d.text((x + w / 2 - tw / 2, y + dy), txt, font=f_, fill=c)

# compass rose placeholder in open sea
cx, cy, R = q(4200), q(8650), q(280)
d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=INK, width=2)
d.polygon([(cx, cy - R - 18), (cx - 16, cy), (cx, cy + R), (cx + 16, cy)], outline=INK, fill=(242, 233, 208))
d.polygon([(cx - R, cy), (cx, cy - 12), (cx + R, cy), (cx, cy + 12)], outline=INK)
d.text((cx - 9, cy - R - 52), "N", font=fR, fill=INK)

# neatline with border band
for k, wd in ((6, 3), (18, 6)):
    d.rectangle([k, k, PW - 1 - k, PH - 1 - k], outline=INK, width=wd)
base.save("out/crusader-frame-rough.jpg", quality=86)
print(base.size)
