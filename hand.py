"""Hand-drawn ink primitives for the Crusader States sheet (cairo, y down).

All profile drawings work in a 320 x 220 unit box with the ground at y = 200.
"""
import math, random
import cairo

PAPER = (0.937, 0.894, 0.788)
PAPER_DK = (0.905, 0.851, 0.725)
INK = (0.17, 0.13, 0.10)
SEPIA = (0.42, 0.32, 0.22)
SEA = (0.30, 0.38, 0.45)

# heraldic tinctures for the colour edition
GULES = (0.70, 0.12, 0.11)
SABLE = (0.12, 0.10, 0.09)
ARGENT = (0.97, 0.95, 0.90)
OR = (0.86, 0.66, 0.18)
VERT = (0.13, 0.45, 0.22)
AZURE = (0.16, 0.30, 0.58)


class Pen:
    def __init__(self, ctx, seed=1, amp=0.8, ink=INK, paper=PAPER, jitter=0.75, sketch=True):
        self.c = ctx
        self.r = random.Random(seed)
        self.amp = amp
        self.ink = ink
        self.paper = paper
        self.supports = []        # (outline, kind): kind "t" terrain, "b" building
        self.jitter = jitter      # corners shift by up to this much, so nothing is quite square
        self.sketch = sketch      # outlines get a second, fainter pass

    # ---- grounding: every wall and tower stands on whatever lies beneath it
    @staticmethod
    def surf_at(pts, x):
        """Highest point (smallest y) of a closed outline at x, or None if x is outside it."""
        best = None
        P = list(pts) + [pts[0]]
        for (x0, y0), (x1, y1) in zip(P, P[1:]):
            if x1 == x0:
                continue
            if min(x0, x1) <= x <= max(x0, x1):
                y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
                best = y if best is None else min(best, y)
        return best

    @staticmethod
    def span_at(pts, x):
        """(top, bottom) of a closed outline at x, or None if x is outside it."""
        ys = []
        P = list(pts) + [pts[0]]
        for (x0, y0), (x1, y1) in zip(P, P[1:]):
            if x1 != x0 and min(x0, x1) <= x <= max(x0, x1):
                ys.append(y0 + (y1 - y0) * (x - x0) / (x1 - x0))
        return (min(ys), max(ys)) if ys else None

    def support_below(self, x, y):
        """Ground under a base at (x, y). None if the base already sits on rock or on a building.
        A base standing inside a wall (a tower in front of it) is carried down to the wall's foot."""
        below = []
        for pts, kind in self.supports:
            sp = self.span_at(pts, x)
            if sp is None:
                continue
            top, bot = sp
            if kind == "t":
                if top <= y + 0.6:
                    return None
                below.append(top + 2.0)
            else:
                if top - 1.5 <= y <= top + 7:
                    return None            # resting on the building below (battlements included)
                if top < y < bot - 0.6:
                    below.append(bot)      # in front of a wall: go down to its foot
                elif top > y:
                    below.append(top + 0.3)
        return min(below) if below else None

    def _bottom(self, xa, ya, xb, yb, step=2.0):
        """Bottom edge from (xb, yb) back to (xa, ya), dropped onto the ground beneath."""
        n = max(2, int(abs(xb - xa) / step))
        out = []
        for i in range(n + 1):
            t = i / n
            x = xb + (xa - xb) * t
            y = yb + (ya - yb) * t
            s = self.support_below(x, y)
            out.append((x, s if s is not None else y))
        return out

    def footing(self, bottom, base_y):
        """Stone footing strokes where a wall was carried down onto the slope."""
        for x, y in bottom[::4]:
            if y - base_y > 4:
                self.line([(x - 1.5, y - 1.2), (x + 1.5, y - 1.2)], w=0.5, col=SEPIA, amp=0.1)

    # ---- wobble -------------------------------------------------------
    def wob(self, pts, closed=False, amp=None, step=2.5):
        amp = self.amp if amp is None else amp
        if amp <= 0 or len(pts) < 2:
            return list(pts)
        j = self.jitter * min(1.0, amp / 0.8)
        P = [(x + self.r.uniform(-j, j), y + self.r.uniform(-j, j)) for x, y in pts]
        P = P + ([P[0]] if closed else [])
        out = []
        ph = [self.r.uniform(0, 6.28) for _ in range(4)]
        fq = [self.r.uniform(0.02, 0.035), self.r.uniform(0.05, 0.08), self.r.uniform(0.13, 0.19), self.r.uniform(0.3, 0.4)]
        dist = 0.0
        for i in range(len(P) - 1):
            (x0, y0), (x1, y1) = P[i], P[i + 1]
            L = math.hypot(x1 - x0, y1 - y0)
            n = max(1, int(L / step))
            nx, ny = (-(y1 - y0) / L, (x1 - x0) / L) if L else (0, 0)
            for k in range(n):
                t = k / n
                d = dist + t * L
                o = amp * (0.55 * math.sin(fq[0] * d + ph[0]) + 0.45 * math.sin(fq[1] * d + ph[1])
                           + 0.22 * math.sin(fq[2] * d + ph[2]) + 0.1 * math.sin(fq[3] * d + ph[3]))
                out.append((x0 + (x1 - x0) * t + nx * o, y0 + (y1 - y0) * t + ny * o))
            dist += L
        out.append(P[-1] if not closed else out[0])
        return out

    def _path(self, pts):
        c = self.c
        c.move_to(*pts[0])
        for p in pts[1:]:
            c.line_to(*p)

    # ---- strokes and shapes ------------------------------------------
    def _stroke(self, q, w, col, alpha=1.0, closed=False):
        c = self.c
        self._path(q)
        if closed:
            c.close_path()
        r, g, b = col
        c.set_source_rgba(r, g, b, alpha)
        c.set_line_width(w)
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        c.stroke()

    def line(self, pts, w=1.4, col=None, amp=None):
        col = col or self.ink
        pts = list(pts)
        if len(pts) >= 2 and w >= 0.9:
            # the pen runs a little past where it was aimed
            (x0, y0), (x1, y1) = pts[0], pts[1]
            L = math.hypot(x1 - x0, y1 - y0) or 1
            e = self.r.uniform(0, 1.3)
            pts[0] = (x0 - (x1 - x0) / L * e, y0 - (y1 - y0) / L * e)
            (x0, y0), (x1, y1) = pts[-2], pts[-1]
            L = math.hypot(x1 - x0, y1 - y0) or 1
            e = self.r.uniform(0, 1.3)
            pts[-1] = (x1 + (x1 - x0) / L * e, y1 + (y1 - y0) / L * e)
        q = self.wob(pts, amp=amp)
        self._stroke(q, w * self.r.uniform(0.8, 1.1), col)
        if self.sketch and w >= 0.9:
            self._stroke(self.wob(pts, amp=(amp if amp is not None else self.amp) * 1.2), w * 0.5, col, alpha=0.45)

    def shape(self, pts, fill="paper", w=1.4, col=None, amp=None, hatch=None, stroke=True,
              grounded=False, terrain=False):
        """Closed shape: fill (occludes what is behind), optional hatch, stroke.
        grounded: pts run from bottom-left round to bottom-right, and the bottom edge is carried
        down onto the ground below; the shape then becomes ground for what is drawn later.
        terrain: the shape is ground (rock, cliff) for what is drawn later."""
        c = self.c
        footing = None
        if grounded:
            base = max(pts[0][1], pts[-1][1])
            bot = self._bottom(pts[0][0], pts[0][1], pts[-1][0], pts[-1][1])
            if max(y for _, y in bot) - base > 3:
                footing = (min(pts[0][1], pts[-1][1]), max(y for _, y in bot),
                           min(p[0] for p in pts), max(p[0] for p in pts))
            pts = list(pts) + bot
            self.supports.append((pts, "b"))
        elif terrain:
            self.supports.append((list(pts), "t"))
        q = self.wob(pts, closed=True, amp=amp)
        if fill is not None:
            self._path(q); c.close_path()
            if fill == "paper" and isinstance(self.paper, cairo.Pattern):
                c.set_source(self.paper)
            else:
                c.set_source_rgb(*(self.paper if fill == "paper" else fill))
            c.fill()
        if hatch:
            c.save()
            self._path(q); c.close_path(); c.clip()
            self.hatch_region(pts, **hatch)
            c.restore()
        if footing and fill is not None:
            # masonry carried down onto the rock: coursed stone with staggered joints
            y0, y1, xa, xb = footing
            c.save()
            self._path(q); c.close_path(); c.clip()
            c.rectangle(xa - 2, y0 + 1, xb - xa + 4, y1 - y0 + 4); c.clip()
            y = y0 + 5.0
            row = 0
            while y < y1 + 2:
                self.line([(xa - 2, y), (xb + 2, y)], w=0.5, col=SEPIA, amp=0.25)
                xj = xa + (row % 2) * 4.5 + self.r.uniform(0, 3)
                while xj < xb:
                    self.line([(xj, y - 5.0), (xj, y)], w=0.45, col=SEPIA, amp=0.05)
                    xj += self.r.uniform(8, 12)
                y += 5.0
                row += 1
            c.restore()
        if stroke:
            self._stroke(q, w * self.r.uniform(0.8, 1.1), col or self.ink, closed=True)
            if self.sketch and w >= 0.9:
                self._stroke(self.wob(pts, closed=True, amp=(amp if amp is not None else self.amp) * 1.3),
                             w * 0.45, col or self.ink, alpha=0.4, closed=True)
        return q

    def hatch_region(self, pts, angle=60, gap=3.2, w=0.7, xmin=None, xmax=None, ymin=None,
                     col=None, cross=False):
        c = self.c
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        x0, x1 = min(xs) - 5, max(xs) + 5
        y0, y1 = min(ys) - 5, max(ys) + 5
        if xmin is not None: x0 = max(x0, xmin)
        if xmax is not None: x1 = min(x1, xmax)
        if ymin is not None: y0 = max(y0, ymin)
        c.save()
        c.rectangle(x0, y0, x1 - x0, y1 - y0); c.clip()
        for ang in ([angle, -angle] if cross else [angle]):
            a = math.radians(ang)
            dx, dy = math.cos(a), math.sin(a)
            nx, ny = -dy, dx
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            R = math.hypot(x1 - x0, y1 - y0)
            k = -R
            while k < R:
                px, py = cx + nx * k, cy + ny * k
                da = math.radians(self.r.uniform(-4, 4))
                ex, ey = math.cos(a + da), math.sin(a + da)
                if self.r.random() < 0.88:
                    if self.r.random() < 0.3:
                        cut = self.r.uniform(-R * 0.3, R * 0.3)   # a stroke that stops short
                        seg = [(px - ex * R, py - ey * R), (px + ex * cut, py + ey * cut)]
                    else:
                        seg = [(px - ex * R, py - ey * R), (px + ex * R, py + ey * R)]
                    self.line(seg, w=w * self.r.uniform(0.75, 1.2), col=col or self.ink, amp=0.4)
                k += gap * self.r.uniform(0.7, 1.3)
        c.restore()

    def dot(self, x, y, r=1.6, col=None):
        c = self.c
        c.arc(x, y, r, 0, 6.2832)
        c.set_source_rgb(*(col or self.ink)); c.fill()

    def circle(self, x, y, r, w=1.2, fill=None, n=40):
        pts = [(x + r * math.cos(t * 6.2832 / n), y + r * math.sin(t * 6.2832 / n)) for t in range(n)]
        return self.shape(pts, fill=fill, w=w)

    @staticmethod
    def surf(pts, x):
        """y of an outline (left to right) at x."""
        best = None
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if min(x0, x1) <= x <= max(x0, x1) and x1 != x0:
                y = y0 + (y1 - y0) * (x - x0) / (x1 - x0)
                best = y if best is None else min(best, y)
        return best if best is not None else pts[0][1]

    # ---- architecture ------------------------------------------------
    def crenels(self, x0, x1, y, mw=5.0, mh=4.5, kind="square"):
        """Returns an outline (left to right) of merlons along the top edge at y."""
        pts = []
        n = max(1, int(round((x1 - x0) / (mw * 2))))
        step = (x1 - x0) / (2 * n - 1) if n > 1 else (x1 - x0)
        if n == 1:
            return [(x0, y - mh), (x1, y - mh)]
        x = x0
        for i in range(2 * n - 1):
            xa, xb = x, x + step
            if i % 2 == 0:
                if kind == "swallow":
                    m = (xa + xb) / 2
                    pts += [(xa, y - mh), (m, y - mh * 0.45), (xb, y - mh)]
                elif kind == "round":
                    m = (xa + xb) / 2
                    pts += [(xa, y - mh * 0.6), (m, y - mh * 1.1), (xb, y - mh * 0.6)]
                else:
                    pts += [(xa, y - mh), (xb, y - mh)]
            else:
                pts += [(xa, y), (xb, y)]
            x = xb
        return pts

    def tower(self, x, yg, w, h, top="crenel", shade=True, windows=1, round_=False, merlon="square",
              batter=0.0, roof_h=None, fill="paper", slits=True, corbel=False):
        """Tower centred on x, standing on yg, body height h."""
        x0, x1 = x - w / 2, x + w / 2
        yt = yg - h
        bb = batter * w
        body = [(x0 - bb, yg), (x0, yt), (x1, yt), (x1 + bb, yg)]
        if top == "crenel":
            mw = max(2.6, w / 7)
            outline = [(x0 - bb, yg), (x0, yt)] + self.crenels(x0, x1, yt, mw=mw, mh=mw * 0.95, kind=merlon) + [(x1, yt), (x1 + bb, yg)]
        else:
            outline = body
        hatch = None
        if shade:
            if round_:
                hatch = dict(angle=90, gap=2.4, w=0.6, xmin=x + w * 0.18)
            else:
                hatch = dict(angle=62, gap=3.0, w=0.6, xmin=x + w * 0.12)
        self.shape(outline, fill=fill, hatch=hatch, grounded=True)
        if corbel and top == "crenel":
            cy = yt + max(3, w * 0.12)
            self.shape([(x0 - 1.8, cy), (x0 - 1.8, yt), (x1 + 1.8, yt), (x1 + 1.8, cy)])
            k = x0
            while k < x1:
                self.line([(k, cy), (k, cy + 2.5)], w=0.6)
                k += 3.2
        if round_:
            # curved courses
            for f in (0.35, 0.7):
                yy = yt + (yg - yt) * f
                self.line([(x0 + 1, yy), (x, yy + w * 0.08), (x1 - 1, yy)], w=0.55, col=SEPIA)
        if top == "cone":
            rh = roof_h or w * 1.1
            self.shape([(x0 - 1.5, yt), (x, yt - rh), (x1 + 1.5, yt)], hatch=dict(angle=70, gap=2.6, w=0.6, xmin=x))
        elif top == "flat":
            self.line([(x0 - 1.2, yt), (x1 + 1.2, yt)], w=1.6)
        elif top == "dome":
            self.dome(x, yt, w / 2)
        elif top == "pyramid":
            rh = roof_h or w * 0.5
            self.shape([(x0 - 1, yt), (x, yt - rh), (x1 + 1, yt)], hatch=dict(angle=70, gap=2.6, w=0.6, xmin=x))
        # windows / arrow slits
        if slits and windows:
            for i in range(windows):
                yy = yt + (yg - yt) * (0.28 + 0.38 * i / max(1, windows - 1 if windows > 1 else 1))
                if h > 10:
                    self.line([(x - w * 0.08, yy), (x - w * 0.08, yy + min(7, h * 0.12))], w=1.1)
        return yt

    def wall(self, x0, x1, yg, h, crenel=True, shade=False, gate=False, merlon="square", y1=None, fill="paper"):
        """Curtain wall; y1 lets the right end sit at another ground level."""
        yg1 = yg if y1 is None else y1
        yt0, yt1 = yg - h, yg1 - h
        if crenel:
            n = max(2, int(abs(x1 - x0) / 9))
            top = []
            mw = (x1 - x0) / (2 * n - 1)
            for i in range(2 * n - 1):
                xa = x0 + i * mw; xb = xa + mw
                ya = yt0 + (yt1 - yt0) * (xa - x0) / (x1 - x0)
                yb = yt0 + (yt1 - yt0) * (xb - x0) / (x1 - x0)
                if i % 2 == 0:
                    mh = 3.6
                    if merlon == "swallow":
                        top += [(xa, ya - mh), ((xa + xb) / 2, (ya + yb) / 2 - mh * 0.4), (xb, yb - mh)]
                    elif merlon == "round":
                        top += [(xa, ya - mh * .5), ((xa + xb) / 2, (ya + yb) / 2 - mh * 1.1), (xb, yb - mh * .5)]
                    else:
                        top += [(xa, ya - mh), (xb, yb - mh)]
                else:
                    top += [(xa, ya), (xb, yb)]
            pts = [(x0, yg), (x0, yt0)] + top + [(x1, yt1), (x1, yg1)]
        else:
            pts = [(x0, yg), (x0, yt0), (x1, yt1), (x1, yg1)]
        self.shape(pts, fill=fill, hatch=dict(angle=60, gap=4.5, w=0.5) if shade else None, grounded=True)
        # coursing
        for k in range(1, 3):
            f = k / 3
            self.line([(x0 + 1, yg - h * f), (x1 - 1, yg1 - h * f)], w=0.45, col=SEPIA, amp=0.3)
        if gate:
            gx = (x0 + x1) / 2
            gw = min(10, (x1 - x0) * 0.3); gh = h * 0.6
            ygx = yg + (yg1 - yg) * 0.5
            self.arch_open(gx, ygx, gw, gh)

    def arch_open(self, x, yg, w, h, fill=INK):
        n = 12
        pts = [(x - w / 2, yg), (x - w / 2, yg - h + w / 2)]
        for i in range(n + 1):
            a = math.pi + math.pi * i / n
            pts.append((x + w / 2 * math.cos(a), yg - h + w / 2 + w / 2 * math.sin(a)))
        pts.append((x + w / 2, yg))
        self.shape(pts, fill=fill, w=0.8)

    def pointed_arch(self, x, yg, w, h, fill=INK):
        pts = [(x - w / 2, yg), (x - w / 2, yg - h * 0.62), (x - w * 0.2, yg - h * 0.92), (x, yg - h),
               (x + w * 0.2, yg - h * 0.92), (x + w / 2, yg - h * 0.62), (x + w / 2, yg)]
        self.shape(pts, fill=fill, w=0.8)

    def dome(self, cx, yb, r, onion=False, finial=None, drum=0, drum_w=None, shade=True, ribs=0, fill="paper"):
        if drum:
            dw = drum_w or r
            self.shape([(cx - dw, yb), (cx - dw, yb - drum), (cx + dw, yb - drum), (cx + dw, yb)],
                       fill=fill, hatch=dict(angle=90, gap=2.6, w=0.5, xmin=cx + dw * 0.3) if shade else None)
            for i in range(-2, 3):
                if drum > 7:
                    self.line([(cx + i * dw / 2.6, yb - drum * 0.25), (cx + i * dw / 2.6, yb - drum * 0.7)], w=0.9)
            yb -= drum
        n = 24
        pts = []
        for i in range(n + 1):
            a = math.pi + math.pi * i / n
            if onion:
                t = i / n
                xx = cx + r * math.cos(a) * (1.12 - 0.12 * abs(math.cos(a)))
                yy = yb + r * 1.25 * math.sin(a) - (r * 0.35 * (math.sin(math.pi * t) ** 6))
            else:
                xx, yy = cx + r * math.cos(a), yb + r * math.sin(a)
            pts.append((xx, yy))
        if onion:
            pts.insert(len(pts) // 2 + 1, (cx, yb - r * 1.6))
            pts = [p for p in pts]
        top = min(p[1] for p in pts)
        self.shape(pts + [(cx + r, yb)], fill=fill,
                   hatch=dict(angle=80, gap=2.4, w=0.55, xmin=cx + r * 0.25) if shade else None)
        for k in range(ribs):
            f = -1 + 2 * (k + 1) / (ribs + 1)
            self.line([(cx + r * f, yb), (cx + r * f * 0.55, yb - r * 0.75), (cx, top + 0.5)], w=0.5, col=SEPIA)
        if finial == "cross":
            self.line([(cx, top), (cx, top - 9)], w=1.2)
            self.line([(cx - 3, top - 6), (cx + 3, top - 6)], w=1.2)
        elif finial == "crescent":
            self.line([(cx, top), (cx, top - 5)], w=1.0)
            c = self.c
            c.arc(cx, top - 8, 3, 0, 6.28); c.set_source_rgb(*self.ink); c.fill()
            c.arc(cx + 1.4, top - 8.6, 2.6, 0, 6.28)
            if isinstance(self.paper, cairo.Pattern):
                c.set_source(self.paper)
            else:
                c.set_source_rgb(*self.paper)
            c.fill()
        elif finial == "ball":
            self.line([(cx, top), (cx, top - 4)], w=1.0); self.dot(cx, top - 5.5, 1.8)
        return top

    def minaret(self, x, yg, w, h, style="square"):
        """square (Syrian), round (Mamluk), pencil (Ottoman)."""
        if style == "square":
            yt = self.tower(x, yg, w, h, top=None, shade=True, windows=0, slits=False)
            self.line([(x - w / 2 - 1.5, yg - h * 0.62), (x + w / 2 + 1.5, yg - h * 0.62)], w=1.0)
            # gallery and lantern
            self.shape([(x - w / 2 - 2, yt), (x - w / 2 - 2, yt - 2.5), (x + w / 2 + 2, yt - 2.5), (x + w / 2 + 2, yt)])
            self.tower(x, yt - 2.5, w * 0.62, w * 0.9, top=None, windows=0, slits=False, shade=False)
            self.dome(x, yt - 2.5 - w * 0.9, w * 0.38, finial="crescent", shade=False)
        elif style == "round":
            yt = self.tower(x, yg, w, h * 0.45, top=None, windows=0, slits=False)
            self.shape([(x - w / 2 - 2, yt), (x - w / 2 - 2, yt - 2), (x + w / 2 + 2, yt - 2), (x + w / 2 + 2, yt)])
            y2 = self.tower(x, yt - 2, w * 0.78, h * 0.3, top=None, windows=0, slits=False, round_=True)
            self.shape([(x - w / 2 - 1, y2), (x - w / 2 - 1, y2 - 2), (x + w / 2 + 1, y2 - 2), (x + w / 2 + 1, y2)])
            y3 = self.tower(x, y2 - 2, w * 0.5, h * 0.16, top=None, windows=0, slits=False, shade=False)
            self.dome(x, y3, w * 0.34, onion=True, finial="crescent", shade=False)
        else:  # pencil
            yt = self.tower(x, yg, w, h, top=None, windows=0, slits=False, round_=True)
            self.shape([(x - w / 2 - 2, yg - h * 0.7), (x - w / 2 - 2, yg - h * 0.7 - 2), (x + w / 2 + 2, yg - h * 0.7 - 2), (x + w / 2 + 2, yg - h * 0.7)])
            self.shape([(x - w / 2 - 0.5, yt), (x, yt - w * 2.6), (x + w / 2 + 0.5, yt)], hatch=dict(angle=90, gap=2.0, w=0.5, xmin=x))
            self.line([(x, yt - w * 2.6), (x, yt - w * 2.6 - 5)], w=1.0)

    def gable(self, x0, x1, yt, h, shade=True):
        m = (x0 + x1) / 2
        self.shape([(x0 - 1.5, yt), (m, yt - h), (x1 + 1.5, yt)],
                   hatch=dict(angle=70, gap=2.8, w=0.55, xmin=m) if shade else None)

    def house(self, x, yg, w, h, roof="flat"):
        self.shape([(x - w / 2, yg), (x - w / 2, yg - h), (x + w / 2, yg - h), (x + w / 2, yg)], grounded=True)
        if roof == "gable":
            self.gable(x - w / 2, x + w / 2, yg - h, h * 0.55)
        elif roof == "flat":
            self.line([(x - w / 2 - 1, yg - h), (x + w / 2 + 1, yg - h)], w=1.4)
        elif roof == "dome":
            self.dome(x, yg - h, w * 0.32, shade=False)
        self.line([(x - w * 0.12, yg - h * 0.55), (x - w * 0.12, yg - h * 0.3)], w=1.2)

    def church(self, x, yg, w, h, style="gothic", tower="left", spire=True):
        """Latin church seen side-on: nave, gabled roof, apse and a tower."""
        x0, x1 = x - w / 2, x + w / 2
        self.shape([(x0, yg), (x0, yg - h), (x1, yg - h), (x1, yg)], hatch=dict(angle=60, gap=4, w=0.45, xmin=x + w * 0.2), grounded=True)
        self.gable(x0, x1, yg - h, h * (0.55 if style == "gothic" else 0.38))
        for i in range(3):
            wx = x0 + w * (0.3 + 0.2 * i)
            (self.pointed_arch if style == "gothic" else self.arch_open)(wx, yg - h * 0.25, w * 0.07, h * 0.45)
        tx = x0 - w * 0.08 if tower == "left" else x1 + w * 0.08
        tw = w * 0.26
        th = h * 1.75
        yt = self.tower(tx, yg, tw, th, top=None, windows=0, slits=False)
        self.pointed_arch(tx, yt + th * 0.35, tw * 0.35, th * 0.22) if style == "gothic" else self.arch_open(tx, yt + th * 0.35, tw * 0.35, th * 0.2)
        if spire:
            sh = tw * (2.2 if style == "gothic" else 0.8)
            self.shape([(tx - tw / 2 - 1, yt), (tx, yt - sh), (tx + tw / 2 + 1, yt)], hatch=dict(angle=90, gap=2.2, w=0.5, xmin=tx))
            self.line([(tx, yt - sh), (tx, yt - sh - 8)], w=1.2)
            self.line([(tx - 3, yt - sh - 5), (tx + 3, yt - sh - 5)], w=1.2)

    def facade(self, x, yg, w, h, towers=True, rose=True):
        """Gothic cathedral west front (Famagusta, Nicosia, Tortosa)."""
        x0, x1 = x - w / 2, x + w / 2
        tw = w * 0.24
        self.shape([(x0 + tw, yg), (x0 + tw, yg - h), (x, yg - h - h * 0.38), (x1 - tw, yg - h), (x1 - tw, yg)],
                   hatch=dict(angle=60, gap=3.6, w=0.45, xmin=x + w * 0.05), grounded=True)
        for tx in (x0 + tw / 2, x1 - tw / 2):
            th = h * (1.18 if towers else 1.0)
            yt = self.tower(tx, yg, tw, th, top="flat" if towers else "crenel", windows=0, slits=False)
            for k in range(2):
                self.pointed_arch(tx, yt + th * (0.42 + 0.3 * k), tw * 0.36, th * 0.22)
        for i, f in enumerate((-0.17, 0, 0.17)):
            self.pointed_arch(x + w * f, yg, w * 0.11, h * 0.42)
        if rose:
            self.circle(x, yg - h * 0.7, w * 0.08, w=1.0)
            self.dot(x, yg - h * 0.7, 1.4)

    def hill(self, x0, x1, yg, h, peak=0.5, steep=1.0, hatch=True, cliffs=False, fill="paper", seed=None):
        """Tolkien-style hill: an outline with short shading strokes down the right slope."""
        r = random.Random(seed) if seed is not None else self.r
        n = 30
        pts = [(x0, yg)]
        px = x0 + (x1 - x0) * peak
        for i in range(1, n):
            t = i / n
            xx = x0 + (x1 - x0) * t
            if xx <= px:
                u = (xx - x0) / (px - x0)
                yy = yg - h * (math.sin(u * math.pi / 2) ** steep)
            else:
                u = (x1 - xx) / (x1 - px)
                yy = yg - h * (math.sin(u * math.pi / 2) ** steep)
            yy += r.uniform(-0.6, 0.6) if cliffs else 0
            pts.append((xx, yy))
        pts.append((x1, yg))
        q = self.shape(pts, fill=fill, stroke=False, terrain=True)
        self.line(pts[:-0] if False else pts, w=1.5)
        if hatch:
            # dense short strokes down the shaded right slope, a few on the lit side
            m = 80
            for k in range(m):
                t = k / m
                xx = px + (x1 - px) * t
                yy = self.surf(pts, xx)
                depth = yg - yy
                if depth < 4:
                    continue
                L = depth * r.uniform(0.28, 0.5) * (1 - 0.5 * t)
                self.line([(xx + 0.5, yy + 1.8), (xx - L * 0.45, yy + 1.8 + L)], w=0.55, col=SEPIA, amp=0.15)
            for k in range(int(m * 0.25)):
                xx = x0 + (px - x0) * r.uniform(0.15, 0.9)
                yy = self.surf(pts, xx)
                depth = yg - yy
                if depth < 6:
                    continue
                L = depth * r.uniform(0.08, 0.18)
                self.line([(xx + 2, yy + 3), (xx + 2 - L * 0.4, yy + 3 + L)], w=0.45, col=SEPIA, amp=0.1)
        return pts

    def crag(self, x0, x1, yg, h, peaks=3, seed=None):
        r = random.Random(seed) if seed is not None else self.r
        pts = [(x0, yg)]
        n = peaks * 2 + 1
        for i in range(1, n):
            t = i / n
            xx = x0 + (x1 - x0) * t
            yy = yg - h * (0.55 + 0.45 * (i % 2)) * (math.sin(t * math.pi) ** 0.5) * r.uniform(0.85, 1.0)
            pts.append((xx, yy))
        pts.append((x1, yg))
        self.shape(pts, hatch=dict(angle=70, gap=2.6, w=0.55, xmin=(x0 + x1) / 2 - (x1 - x0) * 0.08), terrain=True)
        for i in range(1, n, 2):
            xa, ya = pts[i]
            for j in range(3):
                xx = xa + r.uniform(2, 14)
                self.line([(xx, ya + 4 + j * 9), (xx - 2, ya + 12 + j * 9)], w=0.6, col=SEPIA)
        for i in range(1, n - 1, 2):
            xx, yy = pts[i + 1]
            self.line([(xx, yy + 1), (xx - 3, yg - 2)], w=0.6, col=SEPIA)
        return pts

    def sea(self, x0, x1, y, rows=3, gap=5.5, col=None):
        for k in range(rows):
            yy = y + k * gap
            xx = x0 + (k % 2) * 6
            while xx < x1 - 10:
                L = self.r.uniform(10, 20)
                pts = [(xx + t, yy + 1.2 * math.sin(t / L * math.pi * 2)) for t in range(0, int(L) + 1, 2)]
                self.line(pts, w=0.6, col=col or SEA, amp=0.15)
                xx += L + self.r.uniform(5, 10)

    def ground(self, x0, x1, y):
        self.supports.append(([(x0, y), (x1, y), (x1, y + 30), (x0, y + 30)], "t"))
        self.line([(x0, y), (x1, y)], w=1.0)
        for k in range(int((x1 - x0) / 9)):
            xx = x0 + k * 9 + self.r.uniform(0, 5)
            self.line([(xx, y + 3), (xx + 4, y + 3)], w=0.5, col=SEPIA, amp=0.1)

    def palm(self, x, yg, h):
        g = self.support_below(x, yg)
        yg = g - 1.5 if g is not None else yg
        self.line([(x, yg), (x + 2, yg - h * 0.5), (x + 1, yg - h)], w=1.3)
        for a in (-150, -120, -90, -60, -30, -170, -10):
            r = h * 0.38
            ex = x + 1 + r * math.cos(math.radians(a)); ey = yg - h + r * math.sin(math.radians(a)) + r * 0.45
            self.line([(x + 1, yg - h), ((x + 1 + ex) / 2, (yg - h + ey) / 2 - 2.5), (ex, ey)], w=0.9)

    def cypress(self, x, yg, h):
        g = self.support_below(x, yg)
        yg = g - 1.5 if g is not None else yg
        w = h * 0.22
        pts = [(x, yg - h)] + [(x + w / 2 * math.sin(t / 10 * math.pi) * 1.0, yg - h + h * t / 10) for t in range(1, 10)] + \
              [(x + w * 0.2, yg), (x - w * 0.2, yg)] + [(x - w / 2 * math.sin(t / 10 * math.pi), yg - h + h * t / 10) for t in range(9, 0, -1)]
        self.shape(pts, hatch=dict(angle=80, gap=1.8, w=0.5, xmin=x))

    def flag(self, x, yt, w=10, h=6, col=None, fill="paper"):
        self.line([(x, yt), (x, yt - h - 6)], w=1.0)
        self.shape([(x, yt - h - 6), (x + w, yt - h - 3.5), (x, yt - 6)], fill=fill if col is None else col, w=0.9)

    def ship(self, x, y, s=1.0, sail=True):
        """Small galley or round ship, waterline at y."""
        L = 40 * s
        hull = [(x - L / 2, y - 6 * s), (x - L / 2 + 6 * s, y), (x + L / 2 - 6 * s, y), (x + L / 2, y - 7 * s),
                (x + L / 2 - 2 * s, y - 5 * s), (x - L / 2 + 2 * s, y - 5 * s)]
        self.shape(hull, hatch=dict(angle=70, gap=2.0, w=0.5))
        if sail:
            self.line([(x, y - 5 * s), (x, y - 30 * s)], w=1.0)
            self.shape([(x - 11 * s, y - 27 * s), (x + 11 * s, y - 27 * s), (x + 9 * s, y - 11 * s), (x - 9 * s, y - 11 * s)], w=0.9)
            self.line([(x, y - 26 * s), (x, y - 12 * s)], w=0.7, col=GULES)
            self.line([(x - 9.5 * s, y - 19 * s), (x + 9.5 * s, y - 19 * s)], w=0.7, col=GULES)


def new_surface(W, H, bg=PAPER):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, int(W), int(H))
    c = cairo.Context(s)
    c.set_source_rgb(*bg); c.paint()
    return s, c
