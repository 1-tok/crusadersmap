import re, sys, base64, os
import numpy as np
from shapely.geometry import LineString
ed = sys.argv[1]
s = open(f"print/text-{ed}.svg", encoding="utf-8").read()


def flatten(d):
    toks = re.findall(r"[MLCZ]|-?\d+\.?\d*(?:e-?\d+)?", d)
    subs, cur, i, p = [], None, 0, None
    while i < len(toks):
        t = toks[i]
        if t == "M":
            cur = [(float(toks[i + 1]), float(toks[i + 2]))]; subs.append([cur, False]); p = cur[0]; i += 3
        elif t == "L":
            p = (float(toks[i + 1]), float(toks[i + 2])); cur.append(p); i += 3
        elif t == "C":
            x1, y1, x2, y2, x3, y3 = map(float, toks[i + 1:i + 7])
            tt = np.linspace(0, 1, 7)[1:]
            for u in tt:
                a = (1 - u) ** 3; b = 3 * u * (1 - u) ** 2; c = 3 * u * u * (1 - u); e = u ** 3
                cur.append((a * p[0] + b * x1 + c * x2 + e * x3, a * p[1] + b * y1 + c * y2 + e * y3))
            p = (x3, y3); i += 7
        elif t == "Z":
            subs[-1][1] = True; i += 1
        else:
            i += 1
    return subs


def simp(pts, closed, eps):
    if len(pts) < 3:
        return pts
    ls = LineString(pts + ([pts[0]] if closed else []))
    out = list(ls.simplify(eps, preserve_topology=False).coords)
    if closed and len(out) > 1:
        out = out[:-1]
    return out


def fmt(v):
    v = round(v * 2) / 2
    return str(int(v)) if v == int(v) else str(v)


def path_d(subs, eps):
    parts = []
    for pts, closed in subs:
        q = simp(pts, closed, eps)
        if len(q) < 2 + (1 if closed else 0) - 1:
            continue
        parts.append("M" + " ".join(f"{fmt(x)} {fmt(y)}" for x, y in q) + ("Z" if closed else ""))
    return "".join(parts)


fills, strokes = {}, {}
for m in re.finditer(r"<path([^>]*?) d=\"([^\"]*)\"", s):
    attrs, d = m.group(1), m.group(2)
    subs = flatten(d)
    if "stroke=" in attrs and 'fill="none"' in attrs:
        w = float(re.search(r'stroke-width="([\d.]+)"', attrs).group(1))
        col = re.search(r'stroke="([^"]+)"', attrs).group(1)
        op = re.search(r'stroke-opacity="([\d.]+)"', attrs).group(1)
        key = (col, op, max(1, round(w)))
        strokes.setdefault(key, []).append(path_d(subs, 0.5))
    else:
        col = re.search(r'fill="(rgb[^"]+)"', attrs).group(1)
        op = re.search(r'fill-opacity="([\d.]+)"', attrs)
        key = (col, op.group(1) if op else "1")
        fills.setdefault(key, []).append(path_d(subs, 0.3))

vec = []
for (col, op, w), ds in sorted(strokes.items(), key=lambda k: -k[0][2]):
    vec.append(f'<path fill="none" stroke="{col}" stroke-opacity="{op}" stroke-width="{w}" stroke-linecap="round" stroke-linejoin="round" d="{"".join(ds)}"/>')
for (col, op), ds in fills.items():
    vec.append(f'<path fill="{col}" fill-opacity="{op}" fill-rule="nonzero" d="{"".join(ds)}"/>')
vec = "\n".join(vec)
b64 = base64.b64encode(open(f"print/pic-{ed}.jpg", "rb").read()).decode()
out = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="36in" height="48in" viewBox="0 0 10800 14400">\n'
       f'<g id="map-picture"><image x="0" y="0" width="10800" height="14400" preserveAspectRatio="none" xlink:href="data:image/jpeg;base64,{b64}"/></g>\n'
       f'<g id="lettering-outlines">\n{vec}\n</g>\n</svg>\n')
fn = f"print/Outremer-36x48-printify-{ed}.svg"
open(fn, "w", encoding="utf-8").write(out)
print("elements", len(strokes) + len(fills), "vector MB", round(len(vec) / 1e6, 2), "total MiB", round(os.path.getsize(fn) / 2**20, 2))
