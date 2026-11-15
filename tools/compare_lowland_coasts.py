"""Side-by-side geographic map-scale comparisons for coastal lowland QA.

Uses actual previous and current geographic composites, the same projection
as the renderer, and a 0.30-scale QA raster. Not final print certification.
"""
from __future__ import annotations
from pathlib import Path
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pyproj import Transformer
import frame as FR

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/lowland-review-2026-11-15"
BEFORE = ROOT / "out/coverage-before.jpg"
AFTER = ROOT / "reports/rebuild-2026-11-12/outremer-current-composite.jpg"
S = .30
ZONES = {
    "nile_delta": ("delta", [30.05, 30.30, 32.20, 31.62]),
    "levant_coast": ("main", [34.35, 31.38, 35.60, 34.82]),
    "cyprus": ("main", [32.05, 34.48, 34.50, 35.60]),
    "cilicia": ("main", [33.52, 36.28, 36.00, 37.65]),
    "greek_lowlands": ("aegean", [21.05, 36.75, 24.75, 39.45]),
}


def _inset_projection(name):
    item = FR.INSETS[name]
    projection = Transformer.from_crs("EPSG:4326", item["proj"], always_xy=True)
    l0, a0, l1, a1 = item["ext"]
    xl, _ = projection.transform(l0, a1)
    xr, _ = projection.transform(l1, a1)
    _, ytop = projection.transform((l0+l1)/2, a1)
    _, ybot = projection.transform(l0, a0)
    w = 4800
    h = round(w * (ytop-ybot) / (xr-xl))
    bx, by = (190, 190) if name=="aegean" else (190, 13760-h)
    return projection, (xl, xr, ybot, ytop, w, h, bx, by)


def _px(lon, lat, region):
    if region=="main":
        x, y = FR.to_px(lon, lat)
    else:
        proj, (xl, xr, ybot, ytop, w, h, bx, by) = _inset_projection(region)
        x0, y0 = proj.transform(lon, lat)
        x = bx + (x0-xl)/(xr-xl)*w
        y = by + (ytop-y0)/(ytop-ybot)*h
    return x*S, y*S


def cropbox(region, bbox, size):
    lo, la, hi, ha = bbox
    points = [_px(x, y, region) for x in (lo, hi) for y in (la, ha)]
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    pad = 8
    b = [max(0, math.floor(min(xs)-pad)), max(0, math.floor(min(ys)-pad)),
         min(size[0], math.ceil(max(xs)+pad)), min(size[1], math.ceil(max(ys)+pad))]
    if b[2]<=b[0] or b[3]<=b[1]:
        raise AssertionError(f"Invalid crop region {region}: {b}")
    return tuple(b)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    if not BEFORE.is_file():
        raise FileNotFoundError("Cannot compare without an actual previous composite")
    with Image.open(BEFORE) as source:
        before = source.convert("RGB")
    with Image.open(AFTER) as source:
        after = source.convert("RGB")
    if before.size != after.size:
        raise AssertionError(f"Map-scale mismatch: {before.size} vs {after.size}")
    output = {
        "status": "visual_review_not_print_certified",
        "render_resolution": list(after.size),
        "base_ref": "prior committed geographic composite at workflow checkout",
        "comparison_ref": "new coverage-focused geographic composite",
        "method": "same projected bbox and render scale, before-and-after actual JPG geographic map raster",
        "zones": {},
    }
    for label, (region, bbox) in ZONES.items():
        box = cropbox(region, bbox, after.size)
        b = before.crop(box)
        a = after.crop(box)
        ar1 = np.asarray(b, np.int16)
        ar2 = np.asarray(a, np.int16)
        difference = np.abs(ar1-ar2)
        changed = np.max(difference, axis=2) > 8
        w, h = b.size
        sheet = Image.new("RGB", (2*w, h+34), (239, 234, 214))
        sheet.paste(b, (0, 34))
        sheet.paste(a, (w, 34))
        d = ImageDraw.Draw(sheet)
        d.text((12, 10), f"{label.replace('_',' ').title()} — BEFORE", fill=(29,37,45))
        d.text((w+12, 10), "AFTER — geographically clipped underlays", fill=(29,37,45))
        path = OUT / f"{label}-before-after.jpg"
        sheet.save(path, quality=87, optimize=True)
        output["zones"][label] = {
            "region": region, "study_bbox_wgs84": bbox,
            "map_crop_px": list(box), "qa_crop_size_px": [w,h],
            "pixels_with_difference_over_8": int(changed.sum()),
            "changed_percent": round(float(changed.mean()*100), 2),
            "mean_abs_difference": round(float(difference.mean()), 3),
            "preview_file": str(path.relative_to(ROOT)),
        }
    (OUT / "coastline-map-scale-comparison.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print("COASTAL LOWLAND COMPARISONS",json.dumps({
        k: {"changed_percent":v["changed_percent"],"file":v["preview_file"]}
        for k,v in output["zones"].items()
    },indent=2))


if __name__ == "__main__":
    run()
