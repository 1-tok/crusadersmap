import re, sys, base64
ed = sys.argv[1]
s = open(f"print/ink-{ed}.svg", encoding="utf-8").read()
# trim coordinate precision: 0.1 px at 300 dpi is invisible and halves the file
# round path data only (d="..."); matrices, gradients, clips and opacities keep full precision,
# otherwise scales such as 0.446 truncate to 0.4 and slide fills off their outlines
def _r(m):
    return m.group(0) if False else format(round(float(m.group(0)), 1), "g")
def _d(m):
    return ' d="' + re.sub(r"-?\d+\.\d+", _r, m.group(1)) + '"'
s = re.sub(r' d="([^"]*)"', _d, s)
s = s.replace('fill-opacity="1" ', "").replace('stroke-opacity="1" ', "")
head_end = s.index(">", s.index("<svg")) + 1
head = ('<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="36in" height="48in" viewBox="0 0 10800 14400">')
b64 = base64.b64encode(open(f"print/base-{ed}.jpg", "rb").read()).decode()
img = (f'<g id="base-paper-and-colour-wash"><image x="0" y="0" width="10800" height="14400" preserveAspectRatio="none" '
       f'xlink:href="data:image/jpeg;base64,{b64}"/></g>\n<g id="ink-vector-layer">')
out = head + "\n" + img + s[head_end:].replace("</svg>", "</g></svg>")
open(f"print/Outremer-36x48-layered-{ed}.svg", "w", encoding="utf-8").write(out)
print(len(out) / 1e6, "MB")
