import sys, time, gc
ed = sys.argv[2]
from build_stage2 import *
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
t = time.time()
small = np.load(f"print/base-{ed}-0.8.npy")
base = np.empty((H, W, 3), np.uint8)
hs_, ws_ = small.shape[:2]
step = 1200
for y0 in range(0, H, step):
    y1 = min(H, y0 + step)
    sy0 = max(0, int(y0 * hs_ / H) - 4); sy1 = min(hs_, int(np.ceil(y1 * hs_ / H)) + 4)
    strip = Image.fromarray(small[sy0:sy1]).resize((W, int(round((sy1 - sy0) * H / hs_))), Image.BICUBIC)
    off = int(round(y0 - sy0 * H / hs_))
    base[y0:y1] = np.asarray(strip)[off:off + (y1 - y0)]
del small; gc.collect()
g = grade_jerusalem(base, 1.0, ed)
base[JY:JY + g.shape[0], JX:JX + g.shape[1]] = np.clip(g, 0, 255).astype(np.uint8)
del g
Image.fromarray(base).save(f"print/base-{ed}.jpg", quality=88, dpi=(300, 300))
print("base", round(time.time() - t), flush=True)
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
draw_ink2(ed, surf=surf, scale=1.0)
surf.flush()
print("ink", round(time.time() - t), flush=True)
a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
for y0 in range(0, H, 400):
    blk = a[y0:y0 + 400].astype(np.float32)
    al = blk[..., 3:4] / 255
    rgb = blk[..., [2, 1, 0]]
    base[y0:y0 + 400] = np.clip(rgb + base[y0:y0 + 400].astype(np.float32) * (1 - al), 0, 255).astype(np.uint8)
del a, surf; gc.collect()
Image.fromarray(base).save(f"print/Outremer-36x48-300dpi-{ed}.jpg", quality=92, dpi=(300, 300), subsampling=0)
print("done", round(time.time() - t), flush=True)
