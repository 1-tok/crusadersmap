"""Validate land-only underlay contributions from the actual geographic render.

The continuous base colour wash is not treated as a proof of texture coverage.
This checks that the review underpaint ran in all three geographic frames and
did not colour any masked sea/lake pixels.
"""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
report = ROOT / "out" / "underlay-coverage-report.json"
r = json.loads(report.read_text(encoding="utf-8"))
assert r["enabled"], "Coverage-focused build did not enable land underlays"
assert r["status"] == "provisional_underlay_visual_review"
assert set(r["regions"]) == {"main", "aegean", "delta"}, r["regions"]
for region, counts in r["regions"].items():
    interior = counts["land_interior_pixels"]
    painted = counts["underlay_eligible_pixels"]
    modified = counts["visually_changed_pixels"]
    assert interior > 0, f"{region}: land mask unexpectedly empty"
    assert painted == interior, f"{region}: some eligible land lacks underpaint"
    assert modified > 0, f"{region}: underlay texture did not change any pixels"
    assert modified <= painted, f"{region}: painted outside the masked interior"
    assert counts["water_pixels_painted"] == 0, f"{region}: water was modified"
    assert counts["interior_underlay_fraction"] == 1.0
for path in r["sources"].values():
    assert (ROOT / path).is_file(), f"Missing retained texture: {path}"
print("Coverage underlay check passed in main, Aegean and Delta; "
      "land-interior underpaint confirmed, no sea/lake edits. "
      "Visual and print QA remain open.")
