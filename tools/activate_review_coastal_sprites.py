#!/usr/bin/env python3
"""Select accepted Beirut/Tartus azure intake sprites for the geographic REVIEW map.

This changes only generated assets/sprites.json and assets/sprites/*.png during
a build, not canonical production catalogs or original PNGs. The two locations
are existing sourced atlas sites, not invented new coordinates.
"""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSET_BASE = ROOT / "data" / "sprites" / "automated-intake" / "png"
OUTPUT = ROOT / "assets" / "sprites"
REGISTRY = ROOT / "assets" / "sprites.json"
REPORT = ROOT / "reports" / "rebuild-2026-11-12" / "coastal-azure-preview-selection.json"

CHOICES = {
    "beirut": {
        "filename": "beirut-azure-1096-1600-a5c9a2af188e.png",
        "expected_coordinates": (35.505141, 33.896339),
    },
    "tortosa": {
        "filename": "tartus-azure-1096-1600-5056e5143230.png",
        "expected_coordinates": (35.89, 34.89),
    },
}

def main():
    records = json.loads(REGISTRY.read_text(encoding="utf-8"))
    changes = []
    for site, selection in CHOICES.items():
        matches = [r for r in records if r["site"] == site]
        if len(matches) != 1:
            raise RuntimeError(f"{site}: expected exactly one existing named-site record, got {len(matches)}")
        entry = matches[0]
        x, y = selection["expected_coordinates"]
        if abs(entry["lon"] - x) > 0.00001 or abs(entry["lat"] - y) > 0.00001:
            raise RuntimeError(f"{site}: existing coordinates changed, refusing placement")
        source = ASSET_BASE / selection["filename"]
        if not source.is_file():
            raise FileNotFoundError(f"{site}: processed intake image missing: {source}")
        with Image.open(source) as orig:
            if orig.format != "PNG":
                raise ValueError(f"{site}: source must be PNG")
            image = orig.convert("RGBA")
            bbox = image.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox()
            if not bbox:
                raise ValueError(f"{site}: empty source")
            image = image.crop(bbox)
            if image.width > 900:
                image = image.resize((900, max(1, round(900 * image.height / image.width))), Image.Resampling.LANCZOS)
        old = entry["variant"]
        dest_name = "coastal-review-" + selection["filename"]
        OUTPUT.mkdir(parents=True, exist_ok=True)
        image.save(OUTPUT / dest_name)
        entry.update({
            "file": dest_name, "w": image.width, "h": image.height,
            "variant": source.relative_to(ROOT).as_posix(),
            "source": "approved-artwork-geographic-review-only",
            "year": None, "review": True,
            "historical_accuracy_certified": False,
            "coastline_geographic_qa_pending": True,
        })
        changes.append({
            "site_id": site, "name": entry["name"],
            "coordinates": [x, y], "previous_primary": old,
            "review_selected": entry["variant"], "renderer_file": dest_name,
            "status": "visible_in_review_render_pending_visual_approval",
            "coastline_verified": False, "production_approved": False
        })
    REGISTRY.write_text(json.dumps(records, indent=1) + "\n", encoding="utf-8")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "scope": "1096–1600 cumulative master atlas visual review",
        "selection_mode": "review_only_preserve_canonical_catalog",
        "selected": changes
    }, indent=2) + "\n", encoding="utf-8")
    print("Selected reviewed coastal city alternatives for geographic preview:", len(changes))

if __name__ == "__main__":
    main()
