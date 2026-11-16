"""Generate six-city old/new coastal artwork QA sheet without promoting sprites.

Run: python tools/review_coastal_city_batch05.py
Requires Pillow. All artwork stays QA-provisional until map-scale shoreline QA.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/coastal-city-batch05-regenerated-2026-11-16.json"
REGISTRY = ROOT / "assets/sprites.json"
OUT = ROOT / "reports/coastal-city-batch05-2026-11-16"
NEW_DIR = ROOT / "assets/sprites/qa_provisional/coastal-batch05-2026-11-16"
W, H, MARGIN = 550, 300, 16

def art_panel(canvas, path, x, y, title):
    d = ImageDraw.Draw(canvas)
    d.rectangle((x, y, x+W-2, y+H-2), outline=(100, 92, 76), width=2)
    d.text((x+12, y+10), title[:78], fill=(35, 40, 42))
    if not path.is_file():
        d.text((x+12, y+50), "SOURCE NOT FOUND - HOLD", fill=(150, 45, 34))
        return False
    with Image.open(path) as src:
        im = src.convert("RGBA")
    im.thumbnail((W-24, H-55), Image.Resampling.LANCZOS)
    checker = Image.new("RGBA", im.size, (229, 238, 235, 255))
    checker.alpha_composite(im)
    canvas.paste(checker.convert("RGB"), (x+(W-im.width)//2, y+41+(H-50-im.height)//2))
    return True

def main():
    batch = json.loads(MANIFEST.read_text())
    registry = json.loads(REGISTRY.read_text())
    selected = {entry["site"].lower(): entry for entry in registry if entry.get("cat") == "city"}
    items = batch["files"]
    OUT.mkdir(parents=True, exist_ok=True)
    sheet = Image.new("RGB", (W*2+MARGIN*3, H*len(items)+MARGIN*(len(items)+1)), (247, 243, 234))
    results = []
    for i, row in enumerate(items):
        city = row["city"]
        old = selected.get(city)
        old_path = ROOT / old["variant"] if old else ROOT / "__missing_selected_city__"
        new_path = NEW_DIR / row["filename"]
        y = MARGIN+i*(H+MARGIN)
        old_ok = art_panel(sheet, old_path, MARGIN, y, city.upper()+" / CURRENT SELECTED")
        new_ok = art_panel(sheet, new_path, W+MARGIN*2, y, city.upper()+" / REGENERATED CANDIDATE")
        results.append({
            "site": city,
            "registry_anchor_lon_lat": [old.get("lon"), old.get("lat")] if old else None,
            "current_selected_sprite": old["variant"] if old else None,
            "new_candidate": new_path.relative_to(ROOT).as_posix(),
            "expected_coast_water_side": row["coastal_orientation"],
            "old_asset_present": old_ok,
            "candidate_present": new_ok,
            "status": "hold_for_map_scale_coastline_and_historical_review",
            "selected_for_production": False,
            "checks_required": ["south_oblique_camera", "historical_phase", "harbor_topology",
                                "coast_mask_intersection", "sprite_landward_access",
                                "water_duplicate_overlap", "label_clearance", "final_print_scale"]
        })
    sheet_path = OUT / "old-vs-new-six-city-contact-sheet.jpg"
    sheet.save(sheet_path, quality=91)
    report = {
        "batch": batch["batch"],
        "review_kind": "source_artwork_side_by_side_only",
        "map_scale_fit_certified": False,
        "production_selection_changed": False,
        "review_image": sheet_path.relative_to(ROOT).as_posix(),
        "sites": results
    }
    (OUT / "placement-gate.json").write_text(json.dumps(report, indent=2)+"\n")
    print("Wrote", sheet_path, "and placement-gate.json; no production selections changed")

if __name__ == "__main__":
    main()
