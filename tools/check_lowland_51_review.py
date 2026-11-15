"""Fail map builds on unsafe or unverifiable lowland review placement."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
D = ROOT / "reports/lowland-review-2026-11-15"
audit = json.loads((D / "lowland-51-image-qa-and-regions.json").read_text())
placement = json.loads((D / "lowland-51-placement-review.json").read_text())
records = audit["records"]
assert len(records) == 51
assert audit["summary"]["total"] == 51
assert audit["summary"]["binary_present"] == 51, "One or more canonical PNG assets are missing"
assert len({r["id"] for r in records}) == 51
assert all(r["sha256"] and r["alpha_bbox"] and r["assigned_review_region"] in r["source_region_hints"] for r in records)
assert all(r["review_zone_bbox_wgs84"] for r in records)
assert not audit["human_visual_and_historical_approval"]
assert placement["total_cutouts_inspected"] == 51
assert placement["geographic_review_regions_assigned"] == 51
assert placement["eligible_dry_only"] == sum(r["preview_eligible"] for r in records)
assert placement["geographically_drawn_for_review"] + placement["eligible_held_for_no_anchor"] == placement["eligible_dry_only"]
assert placement["other_sources_held"] + placement["eligible_dry_only"] == 51

eligible = {r["id"] for r in records if r["preview_eligible"]}
placements = placement["rendered"]
assert {r["id"] for r in placements} == eligible
byid = {r["id"]: r for r in records}
seen = set()
for item in placements:
    assert item["id"] not in seen
    seen.add(item["id"])
    orig = byid[item["id"]]
    assert orig["source_group"] in ("07", "09")
    assert orig["preview_eligible"] and orig["valid_png_rgba_preview"]
    assert item["canonical_asset"] == orig["canonical_asset"]
    assert item["region"] == orig["assigned_review_region"]
    assert item["frame"] == orig["frame"]
    if item["status"] == "drawn_provisional_geographic_review":
        lo, lat, hi, hi_lat = orig["review_zone_bbox_wgs84"]
        x, y = item["generic_landcover_review_anchor_lonlat"]
        assert lo <= x <= hi and lat <= y <= hi_lat
        assert item["clip"] == "atlas_land_polygon_minus_lakes"
        assert item["layer"].startswith("underlay_below_")
    else:
        assert item["status"] == "held_no_safe_near_coast_fertile_land"
assert (D / "lowland-51-contact-sheet.jpg").is_file()
print("LOWLAND-51 REVIEW QA PASSED:", json.dumps(placement, indent=2)[:900])
