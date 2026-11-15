"""Generate explicitly PROVISIONAL water masks and before/after QA galleries.

Never commits candidates as approved masks; they exist only inside QA build artifacts.
"""
import json, os, glob
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from water_palette import grade_masked_sprite

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets/sprites"
MASKS = SRC / "water-masks"
REPORT = ROOT / "reports/azure-water-qa"
REPORT.mkdir(parents=True, exist_ok=True)
MASKS.mkdir(parents=True, exist_ok=True)


def candidate(im):
    a = np.asarray(im.convert("RGBA"), dtype=np.float32)
    h, w = a.shape[:2]
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    hi = np.max(a[..., :3], axis=2)
    lo = np.min(a[..., :3], axis=2)
    # Guard against recoloring stone, blue roof/shields and pale cloud.
    chroma = hi - lo
    blue = (b > r + 19) & (g > r + 8) & (b >= g - 16) & (chroma > 27)
    lower = np.arange(h)[:, None] > h * .44
    pix = blue & lower & (al > 100)
    # Only contiguous large regions; crop away fine detail and isolated blue roofs.
    labels, n = ndi.label(pix)
    result = np.zeros((h, w), bool)
    for i in range(1, n + 1):
        q = labels == i
        yy, xx = np.where(q)
        if len(xx) < max(160, h * w * .006):
            continue
        # Coastal water typically reaches a lower or lateral edge of artwork.
        if yy.max() < .84 * h and not (xx.min() < .03 * w or xx.max() > .97 * w):
            continue
        result |= q
    result = ndi.binary_opening(result, iterations=2)
    return Image.fromarray(np.uint8(result) * 255, "L")


def main():
    records = json.load(open(ROOT / "assets/sprites.json"))
    selected = []
    candidates = []
    for rec in records:
        path = SRC / rec["file"]
        if not path.is_file():
            continue
        with Image.open(path) as src:
            im = src.convert("RGBA")
        mask = candidate(im)
        amt = float(np.asarray(mask).mean() / 255)
        if amt < .006:
            continue
        mask_path = MASKS / rec["file"]
        mask_path.parent.mkdir(parents=True, exist_ok=True)
        mask.save(mask_path)
        edited = grade_masked_sprite(im, mask)
        selected.append((rec.get("name", rec["file"]), rec["file"], round(amt, 4)))
        if len(candidates) < 24:
            candidates.append((rec.get("name", rec["file"]), im, edited, mask))
    # Single report: this cannot be used as approval for auto-generated masks.
    (REPORT / "provisional-water-mask-report.json").write_text(json.dumps({
        "approval": "PROVISIONAL REVIEW ONLY", "count": len(selected),
        "algorithm": "conservative blue contiguous region near lower/side boundary; false positives possible",
        "sprites": selected}, indent=2))
    cols, cell_w, cell_h = 2, 420, 250
    canvas = Image.new("RGB", (cols * cell_w, max(1, len(candidates)) * cell_h), "#eee5d5")
    d = ImageDraw.Draw(canvas)
    for index, (name, original, washed, mask) in enumerate(candidates):
        for col, im in enumerate((original, washed)):
            im.thumbnail((cell_w - 16, cell_h - 38))
            x = col * cell_w + (cell_w - im.width) // 2
            y = index * cell_h + 26
            canvas.paste(im, (x, y), im)
            d.text((col * cell_w + 8, index * cell_h + 5), (name[:41] + (" — BEFORE" if col == 0 else " — MASKED PREVIEW")), fill="black")
    canvas.save(REPORT / "harbor-sprite-before-after.jpg", quality=88)
    print("provisional mask candidates", len(selected))


if __name__ == "__main__":
    main()
