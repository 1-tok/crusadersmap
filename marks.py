"""Generic marks (box 100 x 100, ground y 84) and heraldic badges for orders and powers."""
import math
from hand import *
import profiles as PR

GY = 84
MUTE = 0.0


# ------------------------------------------------------------------ settlements
def walled_town(p):
    p.ground(8, 92, GY)
    p.wall(14, 86, GY, 18)
    p.tower(18, GY, 11, 30); p.tower(50, GY, 14, 36); p.tower(82, GY, 11, 30)
    p.arch_open(50, GY, 6, 12)

def town(p):
    p.ground(8, 92, GY)
    p.house(28, GY, 18, 16, roof="gable"); p.house(52, GY, 16, 22, roof="flat"); p.house(72, GY, 16, 14, roof="dome")
    p.house(40, GY, 10, 8)

def village(p):
    p.ground(20, 80, GY)
    p.house(42, GY, 16, 12, roof="gable"); p.house(60, GY, 12, 9, roof="flat")

def ruin(p):
    p.ground(10, 90, GY)
    p.shape([(20, GY), (20, GY - 30), (25, GY - 26), (27, GY - 34), (32, GY - 20), (32, GY)], hatch=dict(angle=60, gap=3, w=0.45))
    p.shape([(40, GY), (40, GY - 12), (52, GY - 16), (64, GY - 10), (64, GY)])
    p.shape([(70, GY), (72, GY - 24), (80, GY - 18), (82, GY)], hatch=dict(angle=60, gap=3, w=0.45))
    for x, y in ((50, GY - 4), (88, GY - 3), (36, GY - 3)):
        p.shape([(x - 4, y + 3), (x - 3, y - 1), (x + 3, y - 2), (x + 4, y + 3)], w=0.8)

# ------------------------------------------------------------------ castles
def castle_frankish(p):
    p.hill(5, 95, GY, 14, hatch=True)
    p.wall(22, 78, GY - 10, 16)
    p.tower(26, GY - 10, 12, 28); p.tower(50, GY - 10, 20, 44, corbel=True); p.tower(76, GY - 10, 12, 26)
    p.flag(50, GY - 54)

def castle_muslim(p):
    p.hill(5, 95, GY, 14, hatch=True)
    p.wall(22, 78, GY - 10, 16, merlon="round")
    p.tower(26, GY - 10, 14, 30, merlon="round", round_=True)
    p.tower(74, GY - 10, 14, 30, merlon="round", round_=True)
    p.minaret(50, GY - 26, 7, 30)

def castle_byzantine(p):
    p.hill(5, 95, GY, 14, hatch=True)
    p.wall(22, 78, GY - 10, 16)
    for x, h in ((26, 30), (50, 38), (74, 30)):
        p.tower(x, GY - 10, 14, h)
        for f in (0.35, 0.65):
            p.line([(x - 7, GY - 10 - h * f), (x + 7, GY - 10 - h * f)], w=0.7)
            p.line([(x - 7, GY - 8.5 - h * f), (x + 7, GY - 8.5 - h * f)], w=0.7)

def castle_armenian(p):
    c = p.crag(8, 92, GY, 34, peaks=2, seed=3)
    tops = [c[i] for i in range(1, len(c) - 1, 2)]
    p.wall(tops[0][0], tops[-1][0], tops[0][1] + 6, 10, y1=tops[-1][1] + 6, merlon="swallow")
    for x, y in tops:
        p.tower(x, y + 6, 12, 22, merlon="swallow")

def castle_nizari(p):
    p.crag(14, 86, GY, 40, peaks=1, seed=9)
    p.tower(50, GY - 32, 20, 26, merlon="round")
    p.tower(36, GY - 26, 10, 16, merlon="round")

def tower_(p):
    p.ground(25, 75, GY)
    p.tower(50, GY, 18, 50, corbel=True, windows=2)

def cave_fortress(p):
    """Fortress in a cliff: a craggy rock face with dark cave mouths and a small wall and tower on the crest."""
    p.crag(8, 92, GY, 54, peaks=2, seed=5)
    p.wall(22, 50, GY - 44, 8)
    p.tower(54, GY - 44, 12, 18)
    for x, y, w, h in ((30, GY - 4, 10, 12), (52, GY - 6, 10, 13), (72, GY - 4, 9, 11), (42, GY - 24, 7, 9), (64, GY - 26, 7, 9)):
        p.arch_open(x, y, w, h)

def sea_castle(p):
    p.sea(5, 95, GY - 2, rows=3, gap=5)
    p.crag(20, 80, GY - 4, 8, peaks=1, seed=2)
    p.wall(26, 74, GY - 8, 14)
    p.tower(32, GY - 8, 14, 32); p.tower(68, GY - 8, 12, 24)

def port(p):
    # anchor
    p.circle(50, 22, 5, w=1.4)
    p.line([(50, 27), (50, 76)], w=2.0)
    p.line([(36, 38), (64, 38)], w=1.8)
    arc = [(50 + 26 * math.cos(a), 54 + 22 * math.sin(a)) for a in [math.radians(d) for d in range(10, 171, 10)]]
    p.line(arc, w=2.0)
    for x, s in ((arc[0][0], 1), (arc[-1][0], -1)):
        y = arc[0][1]
        p.line([(x, y), (x + 5 * s, y - 7)], w=1.6)
        p.line([(x, y), (x - 6 * s, y - 3)], w=1.6)

# ------------------------------------------------------------------ holy places
def latin_cathedral(p):
    p.ground(8, 92, GY)
    p.facade(50, GY, 62, 40)

def latin_church(p):
    p.ground(8, 92, GY)
    p.church(56, GY, 46, 22, style="gothic")

def greek_monastery(p):
    p.ground(5, 95, GY)
    # church first, so the wall stands in front of it
    p.shape([(36, GY - 12), (36, GY - 38), (64, GY - 38), (64, GY - 12)], hatch=dict(angle=60, gap=3, w=0.45, xmin=55))
    p.dome(50, GY - 38, 9, drum=6, drum_w=7, finial="cross")
    p.wall(10, 90, GY, 16)
    p.cypress(20, GY - 16, 22); p.cypress(82, GY - 16, 18)

def eastern_church(p):
    """Armenian, Syriac and other eastern churches: drum with a conical roof."""
    p.ground(15, 85, GY)
    p.shape([(26, GY), (26, GY - 24), (74, GY - 24), (74, GY)], hatch=dict(angle=60, gap=3, w=0.45, xmin=60))
    p.gable(26, 74, GY - 24, 9)
    p.tower(50, GY - 30, 16, 14, top="cone", windows=0, slits=False, roof_h=16)
    p.line([(50, GY - 60), (50, GY - 68)], w=1.1); p.line([(47, GY - 65), (53, GY - 65)], w=1.1)
    p.arch_open(50, GY, 6, 12)

def mosque(p):
    p.ground(8, 92, GY)
    p.shape([(16, GY), (16, GY - 18), (70, GY - 18), (70, GY)], hatch=dict(angle=60, gap=3, w=0.45, xmin=55))
    p.dome(43, GY - 18, 15, finial="crescent")
    p.minaret(82, GY, 9, 56, style="square")

def shrine(p):
    """Shrine or maqam: small domed tomb."""
    p.ground(20, 80, GY)
    p.shape([(33, GY), (33, GY - 18), (67, GY - 18), (67, GY)], hatch=dict(angle=60, gap=3, w=0.45, xmin=58))
    p.dome(50, GY - 18, 13, finial="crescent")
    p.arch_open(50, GY, 8, 12)

def jewish_holy(p):
    """Synagogue or Jewish holy tomb: domed tomb with the tablets above."""
    p.ground(20, 80, GY)
    p.shape([(30, GY), (30, GY - 22), (70, GY - 22), (70, GY)], hatch=dict(angle=60, gap=3, w=0.45, xmin=60))
    p.gable(30, 70, GY - 22, 8)
    for x in (44, 56):
        pts = [(x - 5, GY - 34), (x - 5, GY - 44)] + [(x + 5 * math.cos(a), GY - 44 + 5 * math.sin(a)) for a in [math.pi + math.pi * i / 8 for i in range(9)]] + [(x + 5, GY - 34)]
        p.shape(pts, w=1.0)
    p.arch_open(50, GY, 8, 12)

def point_of_interest(p):
    """Place of Gospel memory: a cross on a small mound with rays, for lakes, rivers and hills with no building."""
    p.ground(22, 78, GY)
    p.hill(30, 70, GY, 12)
    p.line([(50, GY - 12), (50, GY - 50)], w=1.8)
    p.line([(40, GY - 40), (60, GY - 40)], w=1.8)
    for ang in (-60, -35, 35, 60):
        a = math.radians(ang - 90)
        p.line([(50 + 13 * math.cos(a), GY - 40 + 13 * math.sin(a)), (50 + 22 * math.cos(a), GY - 40 + 22 * math.sin(a))], w=0.9)

def holy_spring(p):
    p.ground(15, 85, GY)
    p.shape([(30, GY), (30, GY - 20), (70, GY - 20), (70, GY)])
    p.arch_open(50, GY, 22, 18)
    p.sea(28, 74, GY + 4, rows=2, gap=4)
    p.line([(50, GY - 20), (50, GY - 32)], w=1.1); p.line([(46, GY - 28), (54, GY - 28)], w=1.1)

# ------------------------------------------------------------------ war
def battle(p):
    for s in (1, -1):
        x0, x1 = 50 - 30 * s, 50 + 28 * s
        p.line([(x0, 82), (x1, 14)], w=2.4)
        mx = x0 + (x1 - x0) * 0.2; my = 82 + (14 - 82) * 0.2
        p.line([(mx - 9, my - 4 * s * 0 - 4), (mx + 9, my + 4)], w=2.0) if s == 1 else p.line([(mx - 9, my + 4), (mx + 9, my - 4)], w=2.0)
        p.dot(x0, 82, 3.2)

def siege(p):
    """Siege: a trebuchet."""
    p.ground(10, 90, GY)
    p.line([(30, GY), (50, GY - 40), (70, GY)], w=1.8)
    p.line([(36, GY - 12), (64, GY - 12)], w=1.2)
    p.line([(20, GY - 8), (78, GY - 60)], w=2.0)   # arm
    p.shape([(14, GY - 12), (14, GY - 1), (28, GY - 1), (28, GY - 12)], hatch=dict(angle=45, gap=2.2, w=0.5))
    p.line([(78, GY - 60), (84, GY - 44)], w=0.8)
    p.circle(84, GY - 41, 3.4, w=1.0, fill=INK)
    p.dot(50, GY - 40, 2.4)

def sea_battle(p):
    p.sea(5, 95, 74, rows=2, gap=5)
    p.ship(50, 74, s=1.5, sail=False)
    for s in (1, -1):
        p.line([(50 - 16 * s, 34), (50 + 16 * s, 6)], w=1.8)


SETTLE = [(walled_town, "Walled city"), (town, "Town"), (village, "Village or casal"), (ruin, "Ruin or destroyed place")]
CASTLE = [(castle_frankish, "Frankish castle"), (castle_muslim, "Muslim castle"), (castle_byzantine, "Byzantine castle"),
          (castle_armenian, "Armenian castle"), (castle_nizari, "Nizari castle"), (tower_, "Tower or fortified house"),
          (cave_fortress, "Cave fortress"), (sea_castle, "Sea castle"), (port, "Harbour")]
HOLY = [(latin_cathedral, "Latin cathedral"), (latin_church, "Latin church, abbey or priory"), (greek_monastery, "Greek church or monastery"),
        (eastern_church, "Armenian, Syriac or Coptic church"), (mosque, "Great mosque"), (shrine, "Shrine or maqam"),
        (jewish_holy, "Synagogue or Jewish holy tomb"), (point_of_interest, "Place of Gospel memory"), (holy_spring, "Holy spring or baptism place")]
WAR = [(battle, "Battle in the field"), (siege, "Siege or storming"), (sea_battle, "Battle at sea")]


# ------------------------------------------------------------------ heraldry
def shield_path(x, y, w):
    """Heater shield, top-left at (x, y), width w, height 1.18 w."""
    h = w * 1.18
    pts = [(x, y), (x + w, y), (x + w, y + h * 0.45)]
    for i in range(1, 13):
        t = i / 12
        pts.append((x + w - (w / 2) * (1 - math.cos(t * math.pi / 2)) * 1.0, y + h * 0.45 + (h * 0.55) * math.sin(t * math.pi / 2)))
    pts[-1] = (x + w / 2, y + h)
    left = [(2 * x + w - px, py) for px, py in reversed(pts[3:-1])]
    return pts + left + [(x, y + h * 0.45)]


def banner_path(x, y, w):
    """Swallow-tailed banner on a staff; staff at x."""
    h = w * 0.82
    return [(x, y), (x + w, y), (x + w * 0.84, y + h / 2), (x + w, y + h), (x, y + h)]


def tincture(c, pen, region, tinc, mode, gap):
    """Fill the clipped region with a tincture, or its Petra Sancta hatching in ink."""
    xs = [p[0] for p in region]; ys = [p[1] for p in region]
    bb = (min(xs) - 2, min(ys) - 2, max(xs) + 2, max(ys) + 2)
    if mode == "colour":
        col = dict(gules=GULES, sable=SABLE, argent=ARGENT, or_=OR, vert=VERT, azure=AZURE)[tinc]
        if MUTE:
            col = tuple(col[i] * (1 - MUTE) + PAPER[i] * MUTE for i in range(3))
        pen._path(region); c.close_path(); c.set_source_rgb(*col); c.fill()
        return
    pen._path(region); c.close_path(); c.set_source_rgb(*ARGENT if False else PAPER); c.fill()
    c.save(); pen._path(region); c.close_path(); c.clip()
    def lines(angle):
        pen.hatch_region([(bb[0], bb[1]), (bb[2], bb[3])], angle=angle, gap=gap, w=gap * 0.28, col=INK)
    if tinc == "gules":
        lines(90)
    elif tinc == "azure":
        lines(0)
    elif tinc == "vert":
        lines(45)
    elif tinc == "sable":
        lines(90); lines(0)
    elif tinc == "or_":
        y = bb[1]
        k = 0
        while y < bb[3]:
            x = bb[0] + (k % 2) * gap * 0.6
            while x < bb[2]:
                pen.dot(x, y, gap * 0.16); x += gap * 1.2
            y += gap * 0.9; k += 1
    c.restore()


def cross_pts(cx, cy, arm, t, kind="plain"):
    """Cross polygon centred at cx, cy; arm = half length, t = half thickness."""
    if kind == "pattee":
        f = arm * 0.55
        return [(cx - t * 0.5, cy - t * 0.5), (cx - f, cy - arm), (cx + f, cy - arm), (cx + t * 0.5, cy - t * 0.5),
                (cx + arm, cy - f), (cx + arm, cy + f), (cx + t * 0.5, cy + t * 0.5), (cx + f, cy + arm),
                (cx - f, cy + arm), (cx - t * 0.5, cy + t * 0.5), (cx - arm, cy + f), (cx - arm, cy - f)]
    a, b = arm, t
    return [(cx - b, cy - a), (cx + b, cy - a), (cx + b, cy - b), (cx + a, cy - b), (cx + a, cy + b), (cx + b, cy + b),
            (cx + b, cy + a), (cx - b, cy + a), (cx - b, cy + b), (cx - a, cy + b), (cx - a, cy - b), (cx - b, cy - b)]


def maltese(cx, cy, r):
    """Eight-pointed cross of the Hospital (four notched arms)."""
    pts = []
    for k in range(4):
        a = math.radians(90 * k - 90)
        def P(rr, da):
            return (cx + rr * math.cos(a + math.radians(da)), cy + rr * math.sin(a + math.radians(da)))
        pts += [P(r * 0.1, -45), P(r, -26), P(r * 0.72, 0), P(r, 26)]
    return pts


def badge(c, x, y, w, field, charge, mode="colour", kind="shield", seed=1):
    pen = Pen(c, seed=seed, amp=0.25)
    region = (shield_path if kind == "shield" else banner_path)(x, y, w)
    gap = max(1.6, w * 0.065)
    if kind == "banner":
        pen.line([(x, y - w * 0.12), (x, y + w * 1.5)], w=max(1.0, w * 0.06))
    tincture(c, pen, region, field, mode, gap)
    h = w * (1.18 if kind == "shield" else 0.82)
    cx = x + (w / 2 if kind == "shield" else w * 0.44)
    cy = y + h * (0.45 if kind == "shield" else 0.5)
    c.save(); pen._path(region); c.close_path(); c.clip()
    for ch in charge:
        name, tinc = ch[0], ch[1]
        if name == "cross":        # throughout
            poly = cross_pts(cx, cy, w * 1.2, w * 0.1)
        elif name == "cross_pattee":
            poly = cross_pts(cx, cy, w * 0.38, w * 0.12, "pattee")
        elif name == "maltese":
            poly = maltese(cx, cy, w * 0.38)
        elif name == "cross_half":   # Montjoie: half red, half white
            poly = cross_pts(cx, cy, w * 0.36, w * 0.11, "pattee")
            tincture(c, pen, poly, "argent", mode, gap)
            c.save(); c.rectangle(cx, y - 5, w, h + 10); c.clip(); tincture(c, pen, poly, "gules", mode, gap); c.restore()
            pen._path(poly); c.close_path(); c.set_source_rgb(*INK); c.set_line_width(max(0.6, w * 0.03)); c.stroke()
            continue
        elif name == "scallop":
            sx, sy, r = cx, cy, w * 0.11
            poly = [(sx + r * math.cos(a), sy - r * 0.2 + r * math.sin(a)) for a in [math.radians(d) for d in range(200, 341, 10)]] + [(sx, sy + r * 1.1)]
        elif name == "cross_pommee":
            poly = cross_pts(cx, cy, w * 0.3, w * 0.07)
            for dx, dy in ((0, -1), (0, 1), (1, 0), (-1, 0)):
                bx, by = cx + dx * w * 0.33, cy + dy * w * 0.33
                tincture(c, pen, [(bx + w * 0.07 * math.cos(t / 8 * 6.283), by + w * 0.07 * math.sin(t / 8 * 6.283)) for t in range(8)], tinc, mode, gap)
        elif name == "lion":       # the lion of St Mark, simplified
            s = w * 0.012
            poly = [(cx + s * px, cy + s * py) for px, py in
                    [(-28, 4), (-22, -6), (-10, -8), (6, -8), (14, -16), (22, -16), (26, -10), (24, -2), (18, 0), (16, 10),
                     (20, 20), (12, 20), (8, 8), (-6, 8), (-10, 20), (-18, 20), (-16, 6), (-24, 10), (-34, 2), (-38, -10), (-32, -6)]]
            wing = [(cx + s * px, cy + s * py) for px, py in [(-6, -8), (-14, -24), (0, -30), (6, -14)]]
            tincture(c, pen, wing, tinc, mode, gap)
            pen._path(wing); c.close_path(); c.set_source_rgb(*INK); c.set_line_width(max(0.5, w * 0.02)); c.stroke()
        elif name == "betas":      # the Palaiologan cross with four B's
            poly = cross_pts(cx, cy, w * 1.2, w * 0.07)
            tincture(c, pen, poly, tinc, mode, gap)
            pen._path(poly); c.close_path(); c.set_source_rgb(*INK); c.set_line_width(max(0.5, w * 0.025)); c.stroke()
            for dx, dy, fl in ((-1, -1, -1), (1, -1, 1), (-1, 1, -1), (1, 1, 1)):
                bx, by = cx + dx * w * 0.22, cy + dy * h * 0.22
                bh = w * 0.18; bw = bh * 0.6 * fl
                bp = [(bx - bw / 2, by - bh / 2), (bx + bw * 0.3, by - bh / 2), (bx + bw / 2, by - bh / 4), (bx + bw * 0.3, by),
                      (bx + bw / 2, by + bh / 4), (bx + bw * 0.3, by + bh / 2), (bx - bw / 2, by + bh / 2)]
                tincture(c, pen, bp, tinc, mode, gap)
                pen._path(bp); c.close_path(); c.set_source_rgb(*INK); c.set_line_width(max(0.5, w * 0.02)); c.stroke()
            continue
        tincture(c, pen, poly, tinc, mode, gap)
        pen._path(poly); c.close_path(); c.set_source_rgb(*INK); c.set_line_width(max(0.5, w * 0.025)); c.stroke()
    c.restore()
    pen._path(region); c.close_path()
    c.set_source_rgb(*INK); c.set_line_width(max(0.9, w * 0.045)); c.stroke()


ORDERS = [
    ("Hospitallers", "Order of St John of Jerusalem, 1113", "gules", [("cross", "argent")]),
    ("Templars", "Poor Knights of the Temple, 1120", "argent", [("cross_pattee", "gules")]),
    ("Teutonic Knights", "Hospital of St Mary of the Germans, 1190", "argent", [("cross_pattee", "sable")]),
    ("Order of St Lazarus", "lepers' order of Jerusalem, c. 1130", "argent", [("cross", "vert")]),
    ("Order of St Thomas of Acre", "English order, 1191", "argent", [("cross", "gules"), ("scallop", "argent")]),
    ("Order of Montjoie", "Spanish order, 1173", "argent", [("cross_half", "gules")]),
]
POWERS = [
    ("Venice", "Commune of St Mark", "gules", [("lion", "or_")]),
    ("Genoa", "Commune of St George", "argent", [("cross", "gules")]),
    ("Pisa", "Commune of Pisa", "gules", [("cross_pommee", "argent")]),
    ("Byzantium", "Empire of the Romans, Palaiologan", "gules", [("betas", "or_")]),
]
