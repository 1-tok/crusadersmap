"""Unique hand-drawn profiles of the great cities and castles. Box 320 x 220, ground at y 200."""
import math
from hand import *

G = 200

# ------------------------------------------------------------------ cities

def jerusalem(p):
    p.hill(10, 310, G, 34, peak=0.45, steep=0.8)
    yb = G - 26
    p.wall(30, 290, yb + 4, 26, gate=False)
    # Tower of David, left
    p.tower(52, yb + 6, 26, 62, windows=2)
    p.tower(270, yb + 6, 18, 40)
    # Holy Sepulchre: two domes and the bell tower
    p.church(120, yb - 4, 46, 26, style="romanesque", tower="left", spire=False)
    p.dome(130, yb - 30, 13, drum=8, drum_w=13, finial="cross")
    p.dome(108, yb - 30, 9, finial="cross")
    # Dome of the Rock on the Temple platform, right
    p.shape([(175, yb + 4), (175, yb - 6), (250, yb - 6), (250, yb + 4)], hatch=dict(angle=60, gap=4, w=0.45, xmin=225), grounded=True)
    p.shape([(192, yb - 6), (192, yb - 26), (233, yb - 26), (233, yb - 6)], hatch=dict(angle=90, gap=2.4, w=0.5, xmin=220), grounded=True)
    for k in range(5):
        p.pointed_arch(196 + k * 8, yb - 8, 3.5, 12)
    p.dome(212.5, yb - 26, 15, drum=7, drum_w=12, finial="crescent", ribs=2)
    p.dome(244, yb - 6, 6, shade=False)  # al-Aqsa


def acre(p):
    p.sea(5, 315, 196, rows=3)
    p.ground(5, 150, G - 14)
    # landward double walls and towers
    p.wall(8, 150, G - 14, 30)
    for x in (16, 60, 104, 146):
        p.tower(x, G - 14, 16, 46)
    # Templar castle at the point
    p.tower(176, G - 12, 34, 70, windows=2, corbel=True)
    p.tower(196, G - 12, 16, 50)
    p.flag(176, G - 12 - 75)
    # houses and Hospitaller compound
    p.house(84, G - 44, 22, 18, roof="gable")
    p.church(120, G - 44, 30, 18)
    # mole and the Tower of Flies
    p.line([(200, G - 6), (300, G - 6)], w=1.6)
    for x in range(204, 296, 12):
        p.arch_open(x + 6, G - 3, 7, 5)
    p.tower(292, G - 6, 18, 42, round_=True)
    p.ship(250, G + 4, s=0.8)


def antioch(p):
    # walls climb Mount Silpius to the citadel
    pts = p.hill(40, 310, G, 150, peak=0.62, steep=0.9)
    for i in range(4, 26, 3):
        x, y = pts[i]
        x2, y2 = pts[i + 3]
        p.wall(x, x2, y + 4, 10, y1=y2 + 4)
        p.tower(x, y + 6, 9, 18)
    p.tower(pts[18][0] + 5, pts[18][1] + 6, 24, 34, windows=1)  # citadel
    # lower town and Orontes bridge
    p.ground(5, 120, G)
    p.church(60, G, 40, 22, style="romanesque")
    p.house(20, G, 16, 12)
    p.house(100, G, 14, 10, roof="dome")
    p.sea(5, 140, 206, rows=1, gap=4)


def tripoli(p):
    p.sea(5, 315, 198, rows=2)
    # town by the sea
    for x, w, h, r in ((40, 18, 16, "flat"), (62, 16, 12, "dome"), (84, 20, 18, "gable"), (30, 12, 10, "flat")):
        p.house(x, G - 6, w, h, r)
    p.church(115, G - 6, 30, 18)
    # Mont Pelerin castle on its ridge
    pts = p.hill(140, 312, G - 4, 70, peak=0.5)
    p.wall(178, 270, G - 70, 22)
    p.tower(186, G - 66, 20, 48)
    p.tower(230, G - 72, 28, 58, windows=2)
    p.tower(266, G - 66, 16, 36)
    p.flag(230, G - 72 - 63)


def tyre(p):
    p.sea(5, 315, 196, rows=3)
    # causeway from the mainland
    p.line([(10, G - 6), (100, G - 6)], w=1.5)
    for x in range(14, 96, 10):
        p.arch_open(x + 5, G - 3, 6, 4)
    # island city with triple landward walls
    p.ground(100, 300, G - 6)
    for i, h in enumerate((24, 34, 44)):
        x0 = 104 + i * 14
        p.wall(x0, x0 + 10, G - 6, h, crenel=True)
    p.tower(112, G - 6, 12, 40); p.tower(126, G - 6, 12, 50); p.tower(140, G - 6, 12, 60)
    p.wall(150, 300, G - 6, 30)
    p.facade(200, G - 30, 50, 34)
    p.tower(262, G - 6, 18, 56)
    p.tower(296, G - 6, 14, 42)


def edessa(p):
    pts = p.hill(150, 312, G, 90, peak=0.4, steep=0.6)
    p.wall(178, 290, G - 82, 18)
    p.tower(184, G - 76, 16, 38)
    # the two columns ("Throne of Nimrod")
    for x in (220, 238):
        p.shape([(x - 3, G - 84), (x - 3, G - 138), (x + 3, G - 138), (x + 3, G - 84)], hatch=dict(angle=90, gap=1.5, w=0.4, xmin=x), grounded=True)
        p.shape([(x - 5.5, G - 138), (x - 5.5, G - 143), (x + 5.5, G - 143), (x + 5.5, G - 138)])
    p.tower(282, G - 76, 16, 34)
    # town and the fish pools of Abraham
    p.ground(5, 150, G)
    p.wall(10, 150, G, 22)
    p.church(60, G - 22, 36, 18, style="romanesque", spire=False)
    p.house(110, G - 22, 18, 14, roof="dome")
    p.sea(30, 140, 206, rows=1, gap=4)


def damascus(p):
    p.ground(5, 315, G)
    p.wall(10, 310, G, 24)
    # Umayyad mosque: long prayer hall, the Eagle dome, three minarets
    p.shape([(70, G - 24), (70, G - 48), (230, G - 48), (230, G - 24)], hatch=dict(angle=60, gap=4, w=0.45, xmin=180), grounded=True)
    p.gable(110, 190, G - 48, 14)
    p.dome(150, G - 62, 18, drum=6, drum_w=12, finial="crescent")
    p.minaret(80, G - 48, 12, 74, style="square")
    p.minaret(220, G - 48, 12, 82, style="round")
    p.minaret(160, G - 24, 9, 54, style="square") if False else None
    # citadel, left
    p.tower(30, G, 22, 54); p.tower(52, G, 18, 44)
    # Bride minaret on the north wall
    p.minaret(270, G - 24, 10, 64, style="square")
    for x in (296,):
        p.tower(x, G, 16, 40)
    for x in range(110, 200, 18):
        p.cypress(x - 40 + 0, G - 24, 0) if False else None


def aleppo(p):
    # the citadel mound with its glacis and bridge
    p.hill(70, 310, G, 92, peak=0.55, steep=0.35)
    p.wall(118, 270, G - 86, 26)
    p.tower(124, G - 84, 18, 44); p.tower(196, G - 88, 36, 60, windows=2); p.tower(264, G - 84, 16, 40)
    p.minaret(232, G - 112, 9, 46, style="square")
    # gate bastion and stepped bridge
    p.tower(52, G, 26, 66, windows=2)
    pts = [(64, G - 48), (150, G - 76)]
    p.line(pts, w=1.6)
    p.line([(64, G - 42), (148, G - 70)], w=1.0)
    for k in range(4):
        x = 76 + k * 18
        y = G - 46 - k * 6
        p.line([(x, y + 3), (x, G - (G - y - 3) * 0 - 2)], w=1.0)
    p.ground(5, 70, G)


def cairo_(p):
    p.ground(5, 315, G)
    # Muqattam ridge and the citadel of Salah al-Din
    p.hill(150, 315, G, 66, peak=0.7, steep=0.6)
    p.wall(196, 300, G - 62, 22)
    p.tower(204, G - 56, 16, 42, round_=True); p.tower(288, G - 58, 16, 40, round_=True)
    p.dome(250, G - 84, 14, finial="crescent")
    # town: minarets and domes
    p.house(30, G, 22, 20, roof="dome")
    p.minaret(56, G, 10, 92, style="round")
    p.house(84, G, 24, 26)
    p.dome(84, G - 26, 12, finial="crescent")
    p.minaret(112, G, 9, 78, style="round")
    p.house(138, G, 16, 14, roof="flat")
    p.minaret(160, G - 0, 9, 70, style="round")
    p.palm(10, G, 46)


def alexandria(p):
    p.sea(5, 315, 196, rows=3)
    # Pharos on its island
    p.ground(190, 315, G - 6)
    p.tower(250, G - 6, 44, 60, top=None, windows=2, batter=0.08)
    p.tower(250, G - 66, 28, 46, top=None, windows=1)
    p.tower(250, G - 112, 16, 28, top="dome", windows=0, round_=True)
    # town and Pompey's pillar
    p.ground(5, 175, G - 6)
    p.wall(10, 170, G - 6, 26)
    for x in (16, 90, 166):
        p.tower(x, G - 6, 14, 40)
    p.shape([(56, G - 32), (56, G - 120), (62, G - 120), (62, G - 32)], hatch=dict(angle=90, gap=1.6, w=0.4, xmin=59))
    p.shape([(52, G - 120), (52, G - 126), (66, G - 126), (66, G - 120)])
    p.minaret(130, G - 32, 9, 60, style="round")


def damietta(p):
    p.sea(5, 315, 194, rows=4, gap=5)
    p.ground(5, 150, G - 8)
    p.wall(10, 150, G - 8, 30)
    for x in (16, 62, 108, 146):
        p.tower(x, G - 8, 16, 46)
    p.minaret(86, G - 38, 9, 50, style="round")
    # chain tower in the Nile with the chain to the shore
    p.tower(250, G - 4, 34, 66, windows=2, corbel=True)
    p.line([(150, G - 26), (180, G - 18), (233, G - 30)], w=1.0)
    for k in range(9):
        x = 154 + k * 9
        p.circle(x, G - 24 + 4 * math.sin(k / 8 * math.pi), 2.0, w=0.8)
    p.ship(300, G + 6, s=0.6)


def constantinople(p):
    p.sea(5, 315, 198, rows=2)
    # Theodosian land walls, left
    p.ground(5, 315, G - 6)
    p.wall(8, 60, G - 6, 22)
    p.wall(18, 66, G - 6, 34)
    for x in (22, 44, 66):
        p.tower(x, G - 6, 14, 48)
    # Hagia Sophia
    cx = 170
    p.shape([(118, G - 6), (118, G - 38), (222, G - 38), (222, G - 6)], hatch=dict(angle=60, gap=4, w=0.45, xmin=190), grounded=True)
    p.dome(140, G - 38, 14, shade=False)
    p.dome(200, G - 38, 14, shade=False)
    p.dome(cx, G - 50, 30, drum=12, drum_w=28, finial="cross", ribs=3)
    # Galata tower across the Golden Horn
    p.tower(290, G - 6, 18, 74, top="cone", round_=True, windows=2)
    p.house(262, G - 6, 18, 14, roof="gable")


def rhodes(p):
    p.sea(5, 315, 196, rows=3)
    p.ground(5, 230, G - 6)
    p.wall(10, 230, G - 6, 30, merlon="square")
    # Palace of the Grand Masters
    p.tower(60, G - 6, 30, 70, windows=2)
    p.tower(96, G - 6, 30, 70, windows=2)
    p.wall(44, 112, G - 6, 54)
    p.flag(78, G - 60, col=GULES)
    p.church(160, G - 36, 40, 20)
    p.tower(214, G - 6, 26, 54, round_=True)
    # Tower of St Nicholas on the mole
    p.line([(230, G - 6), (290, G - 6)], w=1.6)
    p.tower(292, G - 4, 26, 62, round_=True, windows=2)
    p.ship(258, G + 8, s=0.6)


def famagusta(p):
    p.sea(200, 315, 196, rows=3)
    p.ground(5, 230, G)
    p.wall(10, 240, G, 26)
    p.facade(110, G - 26, 92, 68)   # St Nicholas
    # Othello's tower (citadel)
    p.tower(242, G + 2, 46, 46, windows=1)
    p.tower(28, G, 26, 44, round_=True)
    p.ship(290, G + 6, s=0.7)


def nicosia(p):
    p.ground(5, 315, G)
    # Venetian circuit: low bastions
    for x0 in (10, 230):
        p.shape([(x0, G), (x0 + 10, G - 24), (x0 + 70, G - 24), (x0 + 80, G)], hatch=dict(angle=60, gap=3.5, w=0.45, xmin=x0 + 40), grounded=True)
    p.facade(160, G - 2, 98, 70, towers=True)   # St Sophia
    p.minaret(116, G - 72, 7, 46, style="pencil")
    p.minaret(204, G - 72, 7, 46, style="pencil")
    p.palm(282, G - 24, 40)


def ascalon(p):
    p.sea(5, 315, 196, rows=3)
    p.ground(5, 315, G - 6)
    # the semicircle of walls on its dunes
    p.hill(5, 315, G - 6, 26, peak=0.5, steep=0.5, hatch=False)
    pts = [(20, G - 14), (60, G - 26), (110, G - 32), (160, G - 34), (210, G - 32), (260, G - 26), (300, G - 14)]
    for i in range(len(pts) - 1):
        p.wall(pts[i][0], pts[i + 1][0], pts[i][1], 24, y1=pts[i + 1][1])
    for x, y in pts:
        p.tower(x, y + 2, 18, 42)
    p.house(160, G - 58, 24, 14, roof="dome")


def jaffa(p):
    p.sea(5, 315, 196, rows=3)
    p.hill(30, 260, G - 4, 70, peak=0.45, steep=0.7)
    p.wall(70, 200, G - 62, 20)
    p.tower(80, G - 58, 18, 42); p.tower(136, G - 70, 28, 46, windows=2); p.tower(196, G - 58, 16, 34)
    p.church(160, G - 66, 22, 12, spire=False)
    p.ship(290, G + 6, s=0.6)


def caesarea(p):
    p.sea(5, 315, 196, rows=3)
    p.ground(5, 230, G - 6)
    # glacis and moat walls of St Louis
    p.shape([(10, G - 6), (24, G - 30), (220, G - 30), (232, G - 6)], hatch=dict(angle=60, gap=3.0, w=0.45), grounded=True)
    p.wall(24, 220, G - 30, 22)
    for x in (30, 90, 150, 214):
        p.tower(x, G - 30, 16, 40)
    p.church(130, G - 52, 30, 14, spire=False)
    p.line([(232, G - 8), (300, G - 8)], w=1.6)
    p.tower(300, G - 6, 18, 40)


def bethlehem(p):
    p.hill(10, 310, G, 46, peak=0.4)
    yb = G - 40
    # Church of the Nativity behind its fortified monastery
    p.wall(70, 250, yb + 8, 28)
    p.church(160, yb - 18, 70, 26, style="romanesque", tower="right", spire=False)
    p.tower(80, yb + 8, 22, 52)
    p.tower(244, yb + 8, 18, 46)
    p.cypress(40, G - 20, 34); p.cypress(286, G - 24, 30)


def nazareth(p):
    p.hill(10, 310, G, 70, peak=0.6, steep=0.8)
    p.house(60, G - 30, 18, 14); p.house(90, G - 44, 16, 12, roof="dome"); p.house(250, G - 40, 16, 12)
    p.church(180, G - 64, 64, 32, style="gothic", tower="left", spire=False)
    p.cypress(130, G - 54, 26)


def hebron(p):
    p.hill(10, 310, G, 36, peak=0.5)
    yb = G - 32
    # Herodian enclosure with drafted masonry, two minarets
    p.shape([(80, yb + 8), (80, yb - 40), (240, yb - 40), (240, yb + 8)], grounded=True)
    for k in range(1, 6):
        p.line([(82, yb - 40 + k * 8), (238, yb - 40 + k * 8)], w=0.5, col=SEPIA)
    for x in range(92, 240, 16):
        p.line([(x, yb - 38), (x, yb - 6)], w=1.0)
    p.gable(130, 200, yb - 40, 14)
    p.minaret(94, yb - 40, 10, 54, style="square")
    p.minaret(226, yb - 40, 10, 54, style="square")


def tabor(p):
    p.hill(20, 300, G, 150, peak=0.5, steep=1.2)
    p.wall(120, 200, G - 146, 14)
    p.church(160, G - 160, 30, 16, style="romanesque", spire=False)
    p.tower(124, G - 144, 12, 24); p.tower(196, G - 144, 12, 24)


def sinai(p):
    p.crag(10, 140, G, 130, peaks=3, seed=4)
    p.crag(200, 316, G, 110, peaks=2, seed=7)
    p.wall(110, 230, G, 40)
    p.tower(120, G, 14, 52); p.tower(222, G, 14, 52)
    p.church(170, G - 40, 40, 18, style="romanesque", spire=True)
    p.minaret(140, G - 40, 7, 30, style="square")


# ------------------------------------------------------------------ castles

def krak(p):
    pts = p.hill(10, 312, G, 60, peak=0.45, steep=0.7)
    yb = G - 54
    # outer ward
    p.wall(48, 280, yb + 12, 30)
    for x in (52, 110, 170, 230, 276):
        p.tower(x, yb + 12, 20, 46, round_=True)
    # inner ward with talus and the great towers
    p.shape([(88, yb - 18), (100, yb - 54), (232, yb - 54), (244, yb - 18)], hatch=dict(angle=60, gap=3.0, w=0.45, xmin=170), grounded=True)
    p.wall(100, 232, yb - 54, 18)
    p.tower(108, yb - 18, 34, 72, round_=True, windows=2, corbel=True)
    p.tower(160, yb - 18, 26, 64, round_=True)
    p.tower(222, yb - 18, 30, 70, round_=True, windows=2, corbel=True)
    p.flag(108, yb - 90, col=GULES)


def margat(p):
    pts = p.hill(10, 312, G, 120, peak=0.5, steep=0.9)
    yb = G - 112
    p.wall(70, 260, yb + 10, 22)
    for x in (76, 130, 254):
        p.tower(x, yb + 10, 16, 34, round_=True)
    p.tower(196, yb + 6, 46, 70, round_=True, windows=2, corbel=True)  # the great round donjon
    p.church(140, yb - 12, 30, 14, spire=False)
    p.sea(10, 120, 206, rows=1, gap=4)


def kerak(p):
    pts = p.hill(5, 315, G, 100, peak=0.5, steep=0.35)
    yb = G - 96
    # long castle on the ridge, deep ditches at either end
    p.wall(40, 286, yb + 6, 26)
    for x in (44, 96, 150, 204, 258, 284):
        p.tower(x, yb + 6, 18, 44 if x not in (150, 204) else 56, windows=1)
    p.line([(30, yb + 4), (36, yb + 26)], w=1.4); p.line([(292, yb + 4), (286, yb + 26)], w=1.4)
    for k in range(3):
        p.line([(60 + k * 80, yb + 10), (60 + k * 80, yb + 20)], w=0.6, col=SEPIA)


def montreal(p):
    p.hill(70, 270, G, 128, peak=0.5, steep=1.6)
    yb = G - 122
    p.wall(130, 210, yb + 8, 20)
    p.tower(136, yb + 8, 14, 32); p.tower(170, yb + 4, 22, 44, windows=1); p.tower(204, yb + 8, 14, 30)
    p.church(170, yb - 16, 18, 10, spire=False) if False else None


def belvoir(p):
    # square concentric castle on the plateau edge above the Jordan
    p.hill(5, 315, G, 70, peak=0.7, steep=0.25)
    yb = G - 68
    p.shape([(40, yb + 14), (52, yb - 8), (268, yb - 8), (280, yb + 14)], hatch=dict(angle=60, gap=3.2, w=0.45, xmin=200), grounded=True)
    p.wall(52, 268, yb - 8, 24)
    for x in (58, 112, 160, 208, 262):
        p.tower(x, yb - 8, 22, 40)
    p.wall(110, 210, yb - 32, 18)
    for x in (116, 204):
        p.tower(x, yb - 32, 20, 40)
    p.tower(160, yb - 32, 18, 34)


def pelerin(p):
    p.sea(5, 315, 194, rows=4)
    p.ground(40, 260, G - 8)
    p.wall(50, 250, G - 8, 34)
    # the two great towers facing the land
    p.tower(84, G - 8, 38, 96, windows=2, corbel=True)
    p.tower(150, G - 8, 38, 102, windows=2, corbel=True)
    p.church(212, G - 42, 30, 16, spire=False)
    p.flag(150, G - 110, col=ARGENT)


def montfort(p):
    pts = p.hill(5, 315, G, 110, peak=0.55, steep=0.5)
    yb = G - 106
    # narrow ridge: D-shaped keep at the east, the hall below
    p.wall(90, 260, yb + 8, 22)
    p.tower(250, yb + 6, 40, 60, round_=True, windows=2)
    p.house(150, yb - 14, 50, 24, roof="gable")
    p.tower(100, yb + 8, 16, 34)
    p.flag(250, yb - 60, col=ARGENT)


def safed(p):
    hp = p.hill(10, 310, G, 120, peak=0.5, steep=1.0)
    for x, r in ((70, "flat"), (100, "dome"), (236, "flat")):
        p.house(x, p.surf(hp, x) + 4, 14, 10, roof=r)
    yb = G - 116
    p.wall(90, 230, yb + 8, 22)
    p.tower(160, yb + 4, 60, 70, round_=True, windows=2, corbel=True)   # the great round keep
    p.tower(96, yb + 8, 16, 32, round_=True); p.tower(224, yb + 8, 16, 32, round_=True)



def beaufort(p):
    # castle above a sheer cliff over the Litani gorge
    pts = [(5, G), (5, G - 100), (40, G - 140), (240, G - 140), (250, G - 110), (262, G - 60), (300, G - 20), (315, G)]
    p.shape(pts, hatch=dict(angle=70, gap=2.6, w=0.5, xmin=240), terrain=True)
    for y in (G - 120, G - 95, G - 70):
        p.line([(240, y), (252, y + 10)], w=0.6, col=SEPIA)
    p.wall(30, 240, G - 140, 26)
    p.tower(50, G - 140, 24, 48); p.tower(160, G - 140, 36, 70, windows=2); p.tower(234, G - 140, 18, 46)
    p.sea(240, 315, 206, rows=1, gap=4)


def sidon(p):
    p.sea(5, 315, 192, rows=4)
    # sea castle on its islet, joined by a bridge of arches
    p.line([(10, G - 12), (130, G - 12)], w=1.6)
    for x in range(16, 126, 14):
        p.arch_open(x + 7, G - 2, 9, 9, fill=INK)
    p.crag(120, 300, G - 2, 18, peaks=2, seed=2)
    p.wall(140, 280, G - 16, 26)
    p.tower(160, G - 16, 34, 58, windows=2)
    p.tower(254, G - 16, 40, 52, windows=1)


def tortosa(p):
    p.sea(5, 315, 196, rows=3)
    p.ground(5, 250, G - 6)
    p.facade(80, G - 6, 90, 62, towers=False, rose=False)   # Our Lady of Tortosa
    p.tower(200, G - 6, 50, 84, windows=2, corbel=True)                 # Templar keep
    p.wall(150, 250, G - 6, 30)
    # Ruad island offshore
    p.crag(262, 315, G + 2, 16, peaks=1, seed=5)
    p.tower(290, G - 6, 14, 26)


def saone(p):
    # the rock needle left standing in the great rock-cut ditch
    p.ground(5, 315, G)
    p.shape([(5, G), (5, G - 80), (110, G - 80), (110, G)], hatch=dict(angle=70, gap=3, w=0.45, xmin=60), terrain=True)
    p.shape([(150, G), (150, G - 82), (315, G - 82), (315, G)], hatch=dict(angle=70, gap=3, w=0.45, xmin=250), terrain=True)
    p.shape([(124, G), (125, G - 78), (135, G - 78), (136, G)], hatch=dict(angle=90, gap=1.6, w=0.45, xmin=131), terrain=True)
    p.line([(130, G - 78), (130, G - 100)], w=1.0)   # bridge pier
    p.line([(110, G - 100), (165, G - 100)], w=1.2)
    p.tower(186, G - 82, 44, 64, windows=2, corbel=True)  # the great keep
    p.wall(205, 310, G - 82, 24)
    for x in (240, 300):
        p.tower(x, G - 82, 16, 36, round_=True)


def baghras(p):
    p.crag(30, 290, G, 120, peaks=2, seed=11)
    yb = G - 112
    p.wall(110, 230, yb + 10, 22)
    p.tower(120, yb + 10, 18, 40); p.tower(170, yb + 4, 26, 52, windows=1); p.tower(224, yb + 10, 16, 34)
    p.flag(170, yb - 52, col=ARGENT)


def sis(p):
    # Armenian royal castle strung along a long rock ridge
    pts = p.crag(5, 315, G, 110, peaks=4, seed=13)
    tops = [pts[i] for i in range(1, len(pts) - 1, 2)]
    for (xa, ya), (xb, yb) in zip(tops, tops[1:]):
        p.wall(xa, xb, ya + 10, 12, y1=yb + 10, merlon="swallow")
    for x, y in tops:
        p.tower(x, y + 10, 18, 30, merlon="swallow")
    p.church(60, G, 30, 16, style="romanesque", spire=False)
    p.dome(60, G - 16, 8, finial="cross") if False else None
    p.tower(45, G - 16, 7, 0.1, top="cone", windows=0) if False else None


def hilarion(p):
    c = p.crag(10, 310, G, 150, peaks=3, seed=21)
    for i in range(1, len(c) - 1, 2):
        x, y = c[i]
        p.tower(x, y + 8, 18 + (i % 3) * 3, 26 + (i % 2) * 8, corbel=True)
    p.wall(70, 250, G - 40, 16)
    for x in (80, 150, 240):
        p.tower(x, G - 40, 12, 28)
    p.cypress(30, G, 40); p.cypress(290, G, 34)


def masyaf(p):
    p.crag(60, 260, G, 70, peaks=2, seed=17)
    yb = G - 66
    p.wall(80, 240, yb + 6, 28, merlon="round")
    p.tower(90, yb + 6, 18, 46, merlon="round"); p.tower(162, yb, 30, 58, merlon="round", windows=1); p.tower(232, yb + 6, 16, 40, merlon="round")
    p.ground(5, 315, G)
    p.house(34, G, 16, 12, roof="dome"); p.house(288, G, 14, 10)


def shayzar(p):
    pts = p.hill(5, 315, G, 70, peak=0.5, steep=0.4)
    yb = G - 66
    p.wall(30, 290, yb + 6, 20, merlon="round")
    p.tower(40, yb + 6, 22, 56, merlon="round", windows=1)
    p.tower(270, yb + 6, 20, 40, merlon="round")
    p.minaret(150, yb - 14, 9, 44)
    p.sea(5, 315, 206, rows=1, gap=4)


def hama(p):
    p.ground(5, 315, G)
    # the norias on the Orontes
    for cx, r in ((80, 58), (200, 44)):
        p.circle(cx, G - r - 2, r, w=1.4)
        p.circle(cx, G - r - 2, r * 0.82, w=0.6)
        for k in range(16):
            a = k / 16 * 6.283
            p.line([(cx, G - r - 2), (cx + r * math.cos(a), G - r - 2 + r * math.sin(a))], w=0.6)
        p.dot(cx, G - r - 2, 3)
    p.wall(240, 315, G, 22, merlon="round")
    p.minaret(270, G - 22, 9, 56, style="square")
    p.sea(5, 240, 206, rows=1, gap=4)


def hims(p):
    p.hill(30, 230, G, 76, peak=0.5, steep=0.4)
    p.wall(70, 190, G - 72, 22, merlon="round")
    for x in (76, 130, 184):
        p.tower(x, G - 72, 18, 38, merlon="round")
    p.ground(230, 315, G)
    p.dome(270, G - 10, 16, drum=10, drum_w=18, finial="crescent")   # Khalid ibn al-Walid
    p.minaret(298, G, 8, 60)


def ajlun(p):
    p.hill(5, 315, G, 110, peak=0.5, steep=0.9)
    yb = G - 106
    p.wall(100, 220, yb + 8, 22, merlon="round")
    for x in (106, 214):
        p.tower(x, yb + 8, 22, 46, merlon="round")
    p.tower(160, yb + 4, 30, 56, merlon="round", windows=1)


def bodrum(p):
    p.sea(5, 315, 196, rows=3)
    p.ground(60, 270, G - 6)
    p.wall(70, 260, G - 6, 26)
    for x, w, h in ((100, 26, 64), (150, 22, 74), (214, 26, 66)):
        p.tower(x, G - 6, w, h, windows=1, corbel=(w > 24))
    p.tower(254, G - 6, 26, 40, round_=True)
    p.flag(150, G - 80, col=GULES)


def mistra(p):
    pts = p.hill(5, 315, G, 150, peak=0.6, steep=1.0)
    s = lambda x: p.surf(pts, x) + 5
    p.wall(160, 225, s(170), 14, y1=s(222))
    p.tower(194, s(194), 22, 36)    # Villehardouin castle
    p.house(60, s(60), 20, 14, roof="gable"); p.house(150, s(150), 16, 12, roof="gable")
    p.shape([(94, s(94)), (94, s(110) - 14), (126, s(110) - 14), (126, s(126))], grounded=True)
    p.dome(110, s(110) - 14, 12, drum=8, drum_w=10, finial="cross")   # Pantanassa
    p.dome(36, s(36), 9, finial="cross")
    p.cypress(30, G, 30)


def athens(p):
    pts = p.hill(20, 300, G, 80, peak=0.5, steep=0.3)
    yb = G - 80
    # the Parthenon, then the cathedral of Notre Dame, with the Frankish tower
    p.shape([(100, yb), (100, yb - 6), (230, yb - 6), (230, yb)], grounded=True)
    for x in range(106, 230, 11):
        p.shape([(x - 2.5, yb - 6), (x - 2.5, yb - 40), (x + 2.5, yb - 40), (x + 2.5, yb - 6)], hatch=dict(angle=90, gap=1.4, w=0.35, xmin=x))
    p.shape([(98, yb - 40), (98, yb - 46), (232, yb - 46), (232, yb - 40)])
    p.gable(98, 232, yb - 46, 14)
    p.tower(270, yb + 6, 16, 70, windows=1)   # Frankish tower at the Propylaia
    p.tower(60, yb + 30, 14, 26)


def candia(p):
    p.sea(5, 315, 196, rows=3)
    p.ground(5, 200, G - 6)
    p.wall(10, 200, G - 6, 28)
    p.church(80, G - 34, 40, 20, style="gothic", tower="right")   # San Marco
    p.tower(20, G - 6, 18, 44)
    # Rocca a Mare on the mole
    p.line([(200, G - 6), (250, G - 6)], w=1.6)
    p.tower(276, G - 4, 56, 44, windows=2, corbel=True)
    p.tower(292, G - 48, 18, 18)
    p.flag(276, G - 48, col=GULES)


def galata(p):
    p.sea(5, 315, 196, rows=3)
    p.hill(30, 315, G - 4, 70, peak=0.55, steep=0.7)
    p.tower(200, G - 66, 30, 90, top="cone", round_=True, windows=3)
    p.wall(60, 300, G - 22, 16, y1=G - 26)
    p.house(110, G - 40, 18, 14, roof="gable"); p.house(250, G - 50, 18, 14, roof="gable")
    p.flag(200, G - 66 - 90 - 34, col=ARGENT)


def negroponte(p):
    p.sea(5, 315, 196, rows=3)
    p.ground(5, 120, G - 6); p.ground(200, 315, G - 6)
    p.wall(10, 120, G - 6, 26); p.wall(200, 310, G - 6, 26)
    p.tower(30, G - 6, 18, 44); p.tower(290, G - 6, 18, 44)
    # bridge across the Euripus with its tower
    p.line([(120, G - 18), (200, G - 18)], w=1.6)
    for x in (134, 186):
        p.arch_open(x, G - 4, 16, 14)
    p.tower(160, G - 18, 22, 54, windows=1)
    p.flag(160, G - 72, col=GULES)


def mansura(p):
    p.sea(5, 315, 198, rows=2)
    p.ground(5, 315, G - 6)
    p.wall(30, 290, G - 6, 22, merlon="round")
    p.minaret(100, G - 28, 9, 60, style="round")
    p.dome(170, G - 28, 16, finial="crescent")
    p.minaret(232, G - 28, 9, 50, style="round")
    p.palm(18, G - 6, 50); p.palm(304, G - 6, 44)


def chios(p):
    p.sea(5, 315, 196, rows=3)
    p.ground(5, 315, G - 6)
    p.wall(20, 220, G - 6, 30)
    for x in (24, 120, 216):
        p.tower(x, G - 6, 22, 52, round_=(x == 120))
    p.church(170, G - 36, 30, 16, spire=True)
    p.flag(120, G - 58, col=ARGENT)
    p.ship(280, G + 6, s=0.6)


# key: function, holder's name, other form, modern name, note
CITIES = [
    (jerusalem, "Iherusalem", "al-Quds", "Jerusalem", "Holy Sepulchre and Dome of the Rock"),
    (acre, "Acre", "Akka", "Akko", "harbour, Templar castle and Tower of Flies"),
    (antioch, "Antioche", "Antakiya", "Antakya", "walls up Mount Silpius"),
    (tripoli, "Triple", "Tarabulus", "Tripoli", "Mont Pelerin above the town"),
    (tyre, "Sur", "Tyr", "Tyre (Sour)", "island city, triple walls"),
    (edessa, "Rohais", "al-Ruha", "Sanliurfa", "citadel and its two columns"),
    (damascus, "Dimashq", "Damas", "Damascus", "Umayyad mosque and citadel"),
    (aleppo, "Halab", "Halape", "Aleppo", "citadel on its mound"),
    (cairo_, "al-Qahira", "Babilonie", "Cairo", "citadel of Salah al-Din"),
    (alexandria, "al-Iskandariyya", "Alixandre", "Alexandria", "Pharos and Pompey's pillar"),
    (damietta, "Dimyat", "Damiete", "Damietta", "chain tower in the Nile"),
    (mansura, "al-Mansura", "la Massoure", "Mansoura", "founded 1219"),
    (constantinople, "Konstantinoupolis", "Kostantiniyye", "Istanbul", "Hagia Sophia and the land walls"),
    (galata, "Pera", "Galata", "Beyoglu", "Genoese tower, 1348"),
    (rhodes, "Rhodes", "Rodos", "Rhodes", "palace of the Grand Masters"),
    (famagusta, "Famagouste", "Ammochostos", "Gazimagusa", "St Nicholas and the citadel"),
    (nicosia, "Nicosie", "Lefkosia", "Nicosia", "St Sophia"),
    (ascalon, "Escalone", "Asqalan", "Ashkelon", "the arc of walls"),
    (jaffa, "Japhe", "Yafa", "Jaffa (Yafo)", "citadel on the hill"),
    (caesarea, "Cesaire", "Qaysariyya", "Caesarea", "glacis and moat of St Louis"),
    (candia, "Candia", "Chandax", "Heraklion", "Rocca a Mare, San Marco"),
    (negroponte, "Negroponte", "Evripos", "Chalkida", "the Euripus bridge"),
    (chios, "Scio", "Chios", "Chios", "Genoese Maona"),
    (athens, "Athenes", "Setines", "Athens", "Notre Dame on the Acropolis"),
    (mistra, "Mistras", "Myzithras", "Mystras", "despots' city below the castle"),
    (hama, "Hamah", "", "Hama", "the norias"),
    (hims, "Hims", "la Chamelle", "Homs", "citadel mound"),
]
CASTLES = [
    (krak, "Crac des Chevaliers", "Hisn al-Akrad", "Qal'at al-Hisn", "Hospitaller"),
    (margat, "Margat", "al-Marqab", "Qal'at al-Marqab", "Hospitaller"),
    (kerak, "Crac de Moab", "al-Karak", "Kerak", "lords of Oultrejordain"),
    (montreal, "Montreal", "al-Shawbak", "Shobak", "lords of Oultrejordain"),
    (belvoir, "Belvoir", "Kawkab al-Hawa", "Kokhav HaYarden", "Hospitaller"),
    (pelerin, "Chastel Pelerin", "Athlith", "Atlit", "Templar"),
    (montfort, "Montfort", "Qal'at al-Qurain", "Montfort", "Teutonic"),
    (safed, "Saphet", "Safad", "Safed (Tsfat)", "Templar"),
    (beaufort, "Beaufort", "Qal'at al-Shaqif", "Arnoun", "Templar from 1260"),
    (sidon, "Saiete", "Sayda", "Sidon (Saida)", "sea castle"),
    (tortosa, "Tortose", "Tartus", "Tartus", "Templar keep and Our Lady"),
    (saone, "Saone", "Sahyun", "Qal'at Salah ad-Din", "the rock needle"),
    (baghras, "Gastin", "Baghras", "Bagras", "Templar"),
    (sis, "Sis", "", "Kozan", "Armenian royal seat"),
    (hilarion, "Dieudamour", "Saint-Hilarion", "St Hilarion", "Lusignan"),
    (masyaf, "Masyaf", "", "Masyaf", "Nizari"),
    (shayzar, "Shayzar", "Cesare", "Shaizar", "Banu Munqidh"),
    (ajlun, "Ajlun", "Qal'at al-Rabad", "Ajloun", "Ayyubid, 1184"),
    (bodrum, "Saint-Pierre", "Petronion", "Bodrum", "Hospitaller, 1404"),
]
HOLY = [
    (bethlehem, "Bethleem", "Bayt Lahm", "Bethlehem", "Church of the Nativity"),
    (nazareth, "Nazareth", "al-Nasira", "Nazareth", "Church of the Annunciation"),
    (hebron, "Saint-Abraham", "al-Khalil", "Hebron", "Cave of the Patriarchs"),
    (tabor, "Mont Thabor", "Jabal al-Tur", "Mount Tabor", "Church of the Transfiguration"),
    (sinai, "Sainte-Katherine", "Dayr Sant Katrin", "St Catherine's", "monastery under Sinai"),
]
