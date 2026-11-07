import sys
ed = sys.argv[2]
from build_stage1 import *
import numpy as np
b = base_for(ed)
np.save(f"print/base-{ed}-{S}.npy", np.clip(b, 0, 255).astype(np.uint8))
print("saved", b.shape)
