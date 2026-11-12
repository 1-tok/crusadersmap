"""Painted Sea of Galilee, Dead Sea and Lower Jordan, fitted to the real lake extents (Natural Earth) on the main sheet."""
import math
import cairo
import terrainsp as TSP

# lon/lat boxes: Natural Earth polygons, joined for the Dead Sea's two basins; a margin lets the painted shore cover the old outline
GAL = (35.517, 32.718, 35.641, 32.898)
DEAD = (35.358, 31.086, 35.588, 31.766)
JOR_N = (35.567, 32.700)     # Galilee outlet
JOR_S = (35.545, 31.775)     # Dead Sea inlet


def _fit_box(c, reg, name, box, edition, margin=1.10, alpha=1.0):
    x0, y0 = reg.ll_px(box[0], box[3]); x1, y1 = reg.ll_px(box[2], box[1])
    w, h = (x1 - x0) * margin, (y1 - y0) * margin
    s = TSP._surf(name, edition, max(8, int(round(w))))
    # stretch to the box: scale in y separately
    sy = h / s.get_height()
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    c.save(); c.translate(cx, cy); c.scale(1.0, sy); c.translate(-s.get_width() / 2, -s.get_height() / 2)
    c.set_source_surface(s, 0, 0); c.get_source().set_filter(cairo.FILTER_BEST); c.paint_with_alpha(alpha); c.restore()


def draw(c, reg, edition):
    # river first so the lake shores sit on top of its ends
    nx, ny = reg.ll_px(*JOR_N); sx, sy = reg.ll_px(*JOR_S)
    L = math.hypot(sx - nx, sy - ny)
    s = TSP._surf("jordan-river", edition, max(8, int(round(L * 297 / 2048.0 * 1.0))))
    ang = math.atan2(sy - ny, sx - nx) - math.pi / 2          # painting runs top (north) to bottom
    c.save(); c.translate((nx + sx) / 2, (ny + sy) / 2); c.rotate(ang)
    c.scale(1.0, L / s.get_height()); c.translate(-s.get_width() / 2, -s.get_height() / 2)
    c.set_source_surface(s, 0, 0); c.get_source().set_filter(cairo.FILTER_BEST); c.paint(); c.restore()
    _fit_box(c, reg, "sea-of-galilee", GAL, edition)
    _fit_box(c, reg, "dead-sea", DEAD, edition)
