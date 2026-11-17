#!/usr/bin/env python3
"""Activate two submitted Egyptian coast-city PNGs in generated REVIEW map only.

The owner elected to assume coastline-fit validation for a visual proof. This
does NOT assert that historic shoreline geometry or azure grading was measured.
Run after build_sprite_assets.py and other coastal activators. Source PNGs are
copied into out/egypt-review-source before that build deletes assets/sprites/.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "out/egypt-review-source"
WORKING = ROOT / "assets/sprites"
REGISTRY = ROOT / "assets/sprites.json"
REPORT = ROOT / "reports/rebuild-2026-11-12/greece-egypt-review-activation.json"
MANIFEST = ROOT / "data/manifests/coastal-city-batch05-regenerated-2026-11-16.json"
SITES = {"alexandria", "damietta"}
SOURCE_PREFIX = "greece-egypt-review-assumed-coast-2026-11-17"

def main():
    files = {r["city"]: r for r in json.loads(MANIFEST.read_text())["files"]
             if r["city"] in SITES}
    if set(files) != SITES:
        raise RuntimeError("expected exactly Alexandria and Damietta in source manifest")
    records = json.loads(REGISTRY.read_text())
    results = []
    for site in sorted(SITES):
        source = SOURCE_DIR / files[site]["filename"]
        if not source.is_file():
            raise FileNotFoundError(f"{site}: review source not staged: {source}")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        if digest != files[site]["sha256"]:
            raise ValueError(f"{site}: source digest differs from verified batch manifest")
        with Image.open(source) as im:
            if im.format != "PNG" or list(im.size) != files[site]["expected_dimensions"]:
                raise ValueError(f"{site}: PNG dimensions differ from verified batch")
            rgba = im.convert("RGBA")
            alpha_extrema = rgba.getchannel("A").getextrema()
            if alpha_extrema[0] != 0:
                raise ValueError(f"{site}: missing transparent background")
            bbox = rgba.getchannel("A").point(lambda a: 255 if a > 16 else 0).getbbox()
            if not bbox:
                raise ValueError(f"{site}: empty alpha content")
            rgba = rgba.crop(bbox)
            if rgba.width > 900:
                rgba = rgba.resize((900, max(1, round(rgba.height*900/rgba.width))),
                                   Image.Resampling.LANCZOS)
        matches = [r for r in records if r.get("site") == site and r.get("cat") == "city"]
        if len(matches) != 1:
            raise RuntimeError(f"{site}: expected one existing city, found {len(matches)}")
        entry = matches[0]
        if entry["region"] != "delta":
            raise RuntimeError(f"{site}: geographic region unexpectedly changed")
        previous = {k: entry.get(k) for k in ("file", "variant", "w", "h", "source", "lon", "lat")}
        dest = "greece-egypt-review-" + files[site]["filename"]
        rgba.save(WORKING / dest)
        entry.update({
            "file": dest, "w": rgba.width, "h": rgba.height,
            "variant": "assets/sprites/qa_provisional/coastal-batch05-2026-11-16/"
                       + files[site]["filename"],
            "source": SOURCE_PREFIX,
            "review": True,
            "historical_accuracy_certified": False,
            "coastline_geographic_qa_pending": True,
            "map_review_only": True
        })
        results.append({
            "site": site, "region": entry["region"],
            "coordinate_lon_lat": [entry["lon"], entry["lat"]],
            "previous_selected": previous,
            "new_selected": entry["variant"], "working_file": dest,
            "source_sha256": digest, "expected_water_side": files[site]["coastal_orientation"],
            "review_selection": True,
            "coastline_qa": "assumed_passed_at_owner_request_not_measured",
            "azure_color_qa": "not_measured",
            "historical_accuracy": "not_certified",
            "production_approved": False
        })
    REGISTRY.write_text(json.dumps(records, indent=1)+"\n")
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
        "mode": "review_only_owner_assumed_coastline_pass",
        "map_rebuild_required": True,
        "selected_count": len(results),
        "canonical_catalog_modified": False,
        "other_greece_cities_unchanged": True,
        "sites": results
    }, indent=2)+"\n")
    print("Activated two Egyptian coastal city candidates for review map; no production approval")

if __name__ == "__main__":
    main()
