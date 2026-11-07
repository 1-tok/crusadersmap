"""Hand-drawn mountains and hills: open-footed ridge outlines with a soft tonal shadow wash (no base line, no hatching)."""
import math, random
import cairo

INK = (0.17, 0.13, 0.10)
SHADE = (0.36, 0.27, 0.18)


def _jag(r, a, b, n, amp):
    """Wobbly polyline from a to b with n interior points."""
    pts = [a]
    for i in range(1, n + 1):
        t = i / (n + 1)
        x = a[0] + (b[0] - a[0]) * t + r.uniform(-amp, amp) * 0.6
        y = a[1] + (b[1] - a[1]) * t + r.uniform(-amp, amp)
        pts.append((x, y))
    pts.append(b)
    return pts


def _stroke(c, pts, w, alpha=1.0, col=INK):
    c.set_source_rgba(*col, alpha)
    c.set_line_width(w)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.stroke()


def mountain(c, seed, fill, h=48.0, w=80.0, peaks=None):
    """Local coords: ground y=0, centred on x=0, apex up (negative y). Draws in a 80-unit-wide frame."""
    r = random.Random(seed)
    npk = peaks or r.choice((1, 2, 2, 3))
    xs = sorted(r.uniform(-0.26, 0.26) * w + (i - (npk - 1) / 2) * w * (0.30 if npk > 1 else 0) for i in range(npk))
    hs = [h * r.uniform(0.72, 1.0) for _ in xs]
    hs[r.randrange(npk)] = h
    foot_l = (-w / 2 + r.uniform(0, 5), 0.0); foot_r = (w / 2 - r.uniform(0, 5), 0.0)
    apex = [(x, -hh) for x, hh in zip(xs, hs)]
    # valleys between peaks
    nodes = [foot_l]
    for i, a in enumerate(apex):
        nodes.append(a)
        if i + 1 < len(apex):
            b = apex[i + 1]
            vx = (a[0] + b[0]) / 2 + r.uniform(-4, 4)
            vy = -min(hs[i], hs[i + 1]) * r.uniform(0.38, 0.58)
            nodes.append((vx, vy))
    nodes.append(foot_r)
    # the outline: jagged slopes between nodes
    outline = [nodes[0]]
    for a, b in zip(nodes, nodes[1:]):
        L = math.dist(a, b)
        seg = _jag(r, a, b, max(1, int(L / 9)), 1.6)
        outline += seg[1:]
    # soft fill that fades out at the foot, so no base line shows
    g = cairo.LinearGradient(0, -h, 0, 4)
    g.add_color_stop_rgba(0, *fill, 1.0); g.add_color_stop_rgba(0.62, *fill, 0.95); g.add_color_stop_rgba(1, *fill, 0.0)
    c.move_to(*outline[0])
    for p in outline[1:]:
        c.line_to(*p)
    c.close_path()
    c.set_source(g); c.fill()
    # shadow wash on the right-hand face of every peak
    for i, a in enumerate(apex):
        ia = next(k for k, p in enumerate(outline) if p == a)
        nxt = apex[i + 1][0] if i + 1 < len(apex) else foot_r[0]
        # walk the outline down the right side to the valley (or foot)
        face = [outline[ia]]
        k = ia + 1
        while k < len(outline) and outline[k][0] < nxt - 0.5 and (outline[k][1] < -1.0 or k == ia + 1):
            face.append(outline[k]); k += 1
            if i + 1 < len(apex) and outline[k - 1][1] > -hs[i] * 0.2 and False:
                break
        # the fold: a crooked line from the apex running down to near the foot of the face
        bx = face[-1][0] - r.uniform(0.0, 5.0)
        by = min(0.0, face[-1][1] + r.uniform(0, 3))
        mid = (a[0] + (bx - a[0]) * 0.28 + r.uniform(-2, 2), a[1] + (by - a[1]) * 0.5)
        fold = [(a[0], a[1]), (a[0] + r.uniform(-2, 1), a[1] + (by - a[1]) * 0.25), mid, (bx - (bx - a[0]) * 0.3, by - 1)]
        poly = face + [(bx, by)] + fold[::-1][:-0 or None]
        sg = cairo.LinearGradient(0, a[1], 0, 2)
        sg.add_color_stop_rgba(0, *SHADE, 0.50); sg.add_color_stop_rgba(0.7, *SHADE, 0.34); sg.add_color_stop_rgba(1, *SHADE, 0.0)
        c.move_to(*poly[0])
        for p in poly[1:]:
            c.line_to(*p)
        c.close_path()
        c.set_source(sg); c.fill()
        _stroke(c, fold, 0.9, 0.55, SHADE)
        # a few short cracks on the lit face
        for _ in range(r.randint(1, 3)):
            t = r.uniform(0.25, 0.8)
            j = max(1, int(t * ia)) if ia > 1 else 0
            px, py = a[0] - r.uniform(3, 12), a[1] + r.uniform(8, 20)
            _stroke(c, [(px, py), (px - 1.5, py + r.uniform(4, 8))], 0.7, 0.5, SHADE)
    # ridge outline only
    _stroke(c, outline, 1.5)


def hill(c, seed, fill, h=12.0, w=60.0):
    r = random.Random(seed)
    pk = r.uniform(0.38, 0.62)
    pts = []
    n = 14
    for i in range(n + 1):
        t = i / n
        u = t / pk if t < pk else (1 - t) / (1 - pk)
        y = -h * math.sin(u * math.pi / 2) ** 1.1 + r.uniform(-0.4, 0.4)
        pts.append((-w / 2 + w * t, y))
    g = cairo.LinearGradient(0, -h, 0, 3)
    g.add_color_stop_rgba(0, *fill, 1); g.add_color_stop_rgba(0.6, *fill, 0.9); g.add_color_stop_rgba(1, *fill, 0)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.line_to(pts[-1][0], 0); c.line_to(pts[0][0], 0); c.close_path()
    c.set_source(g); c.fill()
    # shadow wash on the right of the crest
    ip = int(pk * n)
    face = pts[ip:] + [(pts[-1][0] - 3, 0), (pts[ip][0] + 2, -h * 0.35)]
    sg = cairo.LinearGradient(0, -h, 0, 2)
    sg.add_color_stop_rgba(0, *SHADE, 0.42); sg.add_color_stop_rgba(1, *SHADE, 0.0)
    c.move_to(*face[0])
    for p in face[1:]:
        c.line_to(*p)
    c.close_path(); c.set_source(sg); c.fill()
    _stroke(c, pts, 1.2)


def _wedge(c, x, y, L, w0, alpha, lean=0.0):
    """A painted ravine: a narrow dark wedge running down from the crest."""
    g = cairo.LinearGradient(0, y, 0, y + L)
    g.add_color_stop_rgba(0, *SHADE, alpha); g.add_color_stop_rgba(1, *SHADE, 0.0)
    c.move_to(x - w0 / 2, y); c.line_to(x + w0 / 2, y); c.line_to(x + lean, y + L); c.close_path()
    c.set_source(g); c.fill()


def massif(c, seed, fill, h=40.0, w=100.0):
    """A long limestone ridge: broad crest with a few summits, shadowed ravines on the right-hand face."""
    r = random.Random(seed)
    n = 16
    summits = [r.uniform(0.18, 0.82) for _ in range(r.choice((1, 2, 2, 3)))]
    crest = []
    wob = 0.0
    for i in range(n + 1):
        t = i / n
        env = math.sin(math.pi * t) ** 0.65
        wob = 0.6 * wob + r.uniform(-0.16, 0.16)
        bump = sum(0.38 * math.exp(-((t - s) / 0.075) ** 2) for s in summits)
        y = -h * env * (0.62 + wob + bump)
        crest.append((-w / 2 + w * t, min(y, -0.5) if 0 < i < n else 0.0))
    # soft fill fading at the foot
    g = cairo.LinearGradient(0, -h * 1.1, 0, 5)
    g.add_color_stop_rgba(0, *fill, 1.0); g.add_color_stop_rgba(0.6, *fill, 0.95); g.add_color_stop_rgba(1, *fill, 0.0)
    c.move_to(*crest[0])
    for p in crest[1:]:
        c.line_to(*p)
    c.line_to(crest[-1][0], 0); c.line_to(crest[0][0], 0); c.close_path()
    c.set_source(g); c.fill()
    # shadow side: right of the highest summit, wash from crest to foot
    top = min(range(n + 1), key=lambda i: crest[i][1])
    face = crest[top:]
    sg = cairo.LinearGradient(0, -h, 0, 4)
    sg.add_color_stop_rgba(0, *SHADE, 0.46); sg.add_color_stop_rgba(0.7, *SHADE, 0.28); sg.add_color_stop_rgba(1, *SHADE, 0.0)
    c.move_to(*face[0])
    for p in face[1:]:
        c.line_to(*p)
    c.line_to(face[-1][0], 0); c.line_to(face[0][0] + 1.5, -h * 0.25); c.close_path()
    c.set_source(sg); c.fill()
    # ravines down both faces, fewer and fainter on the lit side
    for i in range(2, n - 1):
        x, y = crest[i]
        if i >= top and r.random() < 0.8:
            _wedge(c, x, y + 1, -y * r.uniform(0.7, 1.05) + 3, r.uniform(2.4, 4.4), 0.46, lean=r.uniform(-1.5, 1.5))
        elif r.random() < 0.28:
            _wedge(c, x, y + 1, -y * r.uniform(0.5, 0.8) + 2, r.uniform(1.6, 2.6), 0.22, lean=r.uniform(-1.2, 1.2))
    _stroke(c, crest, 1.3)


def mesa(c, seed, fill, h=30.0, w=90.0):
    """Desert mountain: a flat-topped, stepped block with a cliff face in shadow."""
    r = random.Random(seed)
    j = lambda a: r.uniform(-a, a)
    t1 = r.uniform(0.28, 0.38); t2 = r.uniform(0.55, 0.7)
    pts = [(-w / 2, 0), (-w * (0.5 - 0.10) + j(2), -h * 0.42 + j(2)), (-w * 0.40 + j(1.5), -h * 0.52), (-w * 0.34 + j(1.5), -h * 0.94 + j(1.5)),
           (-w * 0.12 + j(2), -h + j(1.5)), (w * 0.16 + j(2), -h * 0.97 + j(1.5)), (w * 0.22 + j(1.5), -h * 0.62),
           (w * 0.30 + j(1.5), -h * 0.58), (w * 0.34 + j(1.5), -h * 0.36), (w * 0.44, -h * 0.30 + j(2)), (w / 2, 0)]
    g = cairo.LinearGradient(0, -h, 0, 5)
    g.add_color_stop_rgba(0, *fill, 1.0); g.add_color_stop_rgba(0.7, *fill, 0.95); g.add_color_stop_rgba(1, *fill, 0.0)
    c.move_to(*pts[0])
    for p in pts[1:]:
        c.line_to(*p)
    c.close_path(); c.set_source(g); c.fill()
    # shadowed cliff on the right
    sg = cairo.LinearGradient(0, -h, 0, 4)
    sg.add_color_stop_rgba(0, 0.42, 0.28, 0.18, 0.50); sg.add_color_stop_rgba(1, 0.42, 0.28, 0.18, 0.05)
    face = pts[4:]
    c.move_to(face[0][0] + w * 0.04, face[0][1] + 1)
    for p in face[1:]:
        c.line_to(*p)
    c.line_to(w / 2, 0); c.line_to(face[0][0] + w * 0.06, -h * 0.1); c.close_path()
    c.set_source(sg); c.fill()
    for k in range(r.randint(3, 6)):
        x = r.uniform(-w * 0.10, w * 0.34)
        _wedge(c, x, -h * 0.9, h * r.uniform(0.5, 0.8), r.uniform(1.8, 3.2), 0.36, lean=r.uniform(-1, 1))
    # strata on the lit side
    for k in range(2):
        y = -h * (0.25 + 0.2 * k)
        _stroke(c, [(-w * 0.34 + k * 3, y), (-w * 0.08, y + r.uniform(-1, 1))], 0.8, 0.4, SHADE)
    _stroke(c, pts, 1.3)
