import sys, os
meth = sys.argv[2]; ed = sys.argv[3]
os.environ["SEA_METHOD"] = meth
from build_stage1 import *
from PIL import Image
out = base_for(ed)
np.clip(out, 0, 255)
im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
# a window of open sea and coast between Tyre and Acre, and one off Cyprus
im.crop((int(5500 * S), int(8500 * S), int(7300 * S), int(10000 * S))).save(f"out/sea_{meth}_{ed}.png")
im.crop((int(3600 * S), int(3800 * S), int(5400 * S), int(5300 * S))).save(f"out/sea_{meth}_{ed}_open.png")
print("ok", meth, ed)
