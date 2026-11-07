import sys, time, gc, os
ed = sys.argv[2]
Q = int(sys.argv[3]) if len(sys.argv) > 3 else 62
from build_stage2 import *
from PIL import Image
Image.MAX_IMAGE_PIXELS = None
t = time.time()
base = np.asarray(Image.open(f"print/base-{ed}.jpg").convert("RGB")).copy()
surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
draw_ink2(ed, surf=surf, scale=1.0, mode="pic")
surf.flush()
print("pic", round(time.time() - t), flush=True)
a = np.ndarray((H, W, 4), np.uint8, surf.get_data())
for y0 in range(0, H, 400):
    blk = a[y0:y0 + 400].astype(np.float32)
    al = blk[..., 3:4] / 255
    base[y0:y0 + 400] = np.clip(blk[..., [2, 1, 0]] + base[y0:y0 + 400].astype(np.float32) * (1 - al), 0, 255).astype(np.uint8)
del a, surf; gc.collect()
Image.fromarray(base).save(f"print/pic-{ed}.jpg", quality=Q, dpi=(300, 300), optimize=True)
print("jpg", os.path.getsize(f"print/pic-{ed}.jpg") / 1e6, "MB", flush=True)
del base; gc.collect()
ts = cairo.SVGSurface(f"print/text-{ed}.svg", W, H)
try:
    ts.set_document_unit(cairo.SVGUnit.PX)
except Exception:
    pass
draw_ink2(ed, surf=ts, scale=1.0, mode="text")
ts.finish()
print("text svg", os.path.getsize(f"print/text-{ed}.svg") / 1e6, "MB", round(time.time() - t), flush=True)
