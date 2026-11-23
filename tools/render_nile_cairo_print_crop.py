#!/usr/bin/env python3
"""Cairo print-density crop on the Cairo–Giza prototype pipeline.

The al-Qahira painting (assets/sprites/cairo-1180-v1.png, 900 px wide) is placed
at its native pixel density: the ground footprint is CITY_W_M and the review pixel
is CITY_W_M / 900 metres, so every source pixel maps to one output pixel. The
ground footprint is unchanged (3.2 km), so the city is not scaled up to a size
the valley cannot support.

Writes to reports/nile-cairo-print-crop/. The full-valley outputs are not touched.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import build_nile_cairo_giza_prototype as P  # noqa: E402

P.OUT = ROOT / "reports" / "nile-cairo-print-crop"
P.LON0, P.LON1 = 31.20, 31.33
P.LAT0, P.LAT1 = 29.99, 30.09
P.PX_M = P.CITY_W_M / 900.0  # native pixel density for the 900 px painting

if __name__ == "__main__":
    P.main()
