import numpy as np, frame as FR
from rough import *
r = Region(FR.PROJ, FR.X0, FR.X1, FR.Y0, FR.Y1, PW, PH)
img, land = r.render(7)
img.save("out/rough-main-base.png")
np.save("out/land_q4.npy", land)
d = ImageDraw.Draw(img)
for lo in range(28, 43):
    pts = [r.ll_px(lo, la) for la in np.linspace(26, 40, 60)]
    d.line(pts, fill=(170, 150, 120), width=1)
for la in range(26, 41):
    pts = [r.ll_px(lo, la) for lo in np.linspace(28, 43, 60)]
    d.line(pts, fill=(170, 150, 120), width=1)
    d.text(r.ll_px(31.8, la), f"{la}N", fill=SEP)
img.save("out/rough-main-grid.jpg", quality=80)
print(img.size)
