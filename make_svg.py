import sys, time
ed = sys.argv[2]
from build_stage2 import *
t = time.time()
surf = cairo.SVGSurface(f"print/ink-{ed}.svg", W, H)
try:
    surf.set_document_unit(cairo.SVGUnit.PX)
except Exception as e:
    print("unit", e)
surf.set_fallback_resolution(72, 72)
draw_ink2(ed, surf=surf, scale=1.0)
surf.finish()
print("ink svg", round(time.time() - t), "s")
