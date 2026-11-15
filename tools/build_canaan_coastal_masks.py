#!/usr/bin/env python3
"""Generate diagnostic Canaan coastal land masks; never approve sprite placement.

Run from the repository root:
    python3 tools/build_canaan_coastal_masks.py
Requires shapely. Uses repo Natural Earth geometry rather than painted water.
Outputs review-only GeoJSON and a QA summary; it does not modify renderer assets.
"""
import json
from pathlib import Path
from shapely.geometry import shape, box, mapping
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data/manifests/canaan-coastal-mask-review"
WINDOWS = {
    # Broad diagnostic study extents (WGS84 west,south,east,north).
    # NOT per-sprite footprints or evidence of placement.
    "acre_carmel": [34.75, 32.55, 35.30, 33.15],
    "sharon_jaffa": [34.55, 31.95, 35.10, 32.60],
    "ashkelon_gaza": [34.15, 31.25, 34.85, 32.00],
}
def geometry(filename):
    data = json.loads((ROOT / "data" / filename).read_text(encoding="utf-8"))
    return [shape(f["geometry"]) for f in data["features"]]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    land = geometry("ne_10m_land.geojson") + geometry("ne_10m_minor_islands.geojson")
    lakes = geometry("ne_10m_lakes.geojson")
    report = {
        "schema_version": 1, "purpose": "diagnostic coastline land masks only",
        "source_land": ["data/ne_10m_land.geojson", "data/ne_10m_minor_islands.geojson"],
        "source_lakes": "data/ne_10m_lakes.geojson",
        "medieval_shoreline_certified": False,
        "coastline_orientation_certified": False,
        "sprite_placement_authorized": False,
        "sprite_water_replacement_authorized": False,
        "windows": [],
    }
    for key, bounds in WINDOWS.items():
        frame = box(*bounds)
        local_land = unary_union([g.intersection(frame) for g in land if g.intersects(frame)])
        local_lakes = unary_union([g.intersection(frame) for g in lakes if g.intersects(frame)])
        mask = local_land.difference(local_lakes)
        if mask.is_empty or not mask.is_valid:
            raise ValueError(f"Invalid or empty land mask: {key}")
        feature = {
            "type": "FeatureCollection",
            "features": [{"type": "Feature", "geometry": mapping(mask), "properties": {
                "region": key, "status": "diagnostic_only", "not_sprite_footprint": True,
                "requires_historical_shoreline_review": True,
                "requires_south_oblique_sprite_orientation_review": True,
                "production_approved": False,
            }}],
        }
        dest = OUT / f"{key}-land-mask.geojson"
        dest.write_text(json.dumps(feature, indent=2) + "\n", encoding="utf-8")
        report["windows"].append({"region": key, "study_bbox_wgs84": bounds,
          "output": str(dest.relative_to(ROOT)), "land_mask_area_degrees2": round(mask.area, 7),
          "sprite_geometry": None, "placement_status": "hold_visual_alignment"})
    (OUT / "mask-build-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("Wrote three diagnostic land masks; no sprite placement or approval granted.")

if __name__ == "__main__":
    main()
