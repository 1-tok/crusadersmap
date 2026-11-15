#!/usr/bin/env python3
"""Fail closed if Canaan diagnostic masks are mistaken for sprite placements.

Run after tools/build_canaan_coastal_masks.py; standard library only.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/manifests/canaan-coastal-mask-review"
MANIFEST = ROOT / "data/manifests/CANAAN-COASTAL-BATCH37-39-REVIEW-QUEUE-2026-11-13.json"
REGIONS = ("acre_carmel", "sharon_jaffa", "ashkelon_gaza")

def assert_polygon(coords):
    if not isinstance(coords, list) or not coords:
        raise ValueError("Missing polygon rings")
    for ring in coords:
        if len(ring) < 4 or ring[0] != ring[-1]:
            raise ValueError("Unclosed / undersized polygon")
        for point in ring:
            if len(point) < 2 or not (-180 <= point[0] <= 180 and -90 <= point[1] <= 90):
                raise ValueError("Invalid lon/lat in mask")

def main():
    report = json.loads((BASE / "mask-build-report.json").read_text())
    assert report["sprite_placement_authorized"] is False
    assert report["sprite_water_replacement_authorized"] is False
    assert report["medieval_shoreline_certified"] is False
    assert report["coastline_orientation_certified"] is False
    rows = {x["region"]: x for x in report["windows"]}
    assert set(rows) == set(REGIONS)
    for region in REGIONS:
        doc = json.loads((BASE / (region + "-land-mask.geojson")).read_text())
        assert doc["type"] == "FeatureCollection"
        assert len(doc["features"]) == 1
        feature = doc["features"][0]
        assert feature["properties"]["not_sprite_footprint"] is True
        assert feature["properties"]["production_approved"] is False
        geometry = feature["geometry"]
        if geometry["type"] == "Polygon":
            assert_polygon(geometry["coordinates"])
        elif geometry["type"] == "MultiPolygon":
            for poly in geometry["coordinates"]:
                assert_polygon(poly)
        else:
            raise ValueError("Unexpected mask geometry")
        assert rows[region]["sprite_geometry"] is None
        assert rows[region]["placement_status"] == "hold_visual_alignment"
    m = json.loads(MANIFEST.read_text())
    assert len(m["assets"]) == 12
    for asset in m["assets"]:
        assert asset["geometry"] is None, asset["id"]
        assert asset["production_approved"] is False, asset["id"]
        assert asset["print_approved"] is False, asset["id"]
        assert asset["approval_for_review_placement"] is False, asset["id"]
        assert set(asset["diagnostic_mask_regions"]).issubset(REGIONS)
        if asset["id"].startswith("39-"):
            assert asset["restriction"] == "water_restricted_hold", asset["id"]
    print("PASS: 3 geographic diagnostic masks; 12 assets held; all Batch 39 water holds intact")

if __name__ == "__main__":
    main()
