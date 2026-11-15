"""Fail the rebuild if generated terrain-gap classifications disagree.

Low visual texture is not proof that the bottom map layer is exposed.
The separate base-layer-exposure verdict stays unverified until visual QA.
"""
from __future__ import annotations
from pathlib import Path
import csv
import re

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "rebuild-2026-11-12"
with (REPORTS / "terrain-gap-cells.csv").open(newline="", encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))

counts = {"flat": 0, "thin": 0}
for row in rows:
    detail = float(row["detail"])
    expected = "flat" if detail < 12 else "thin" if detail < 16 else "not_flagged"
    assert expected != "not_flagged", f"High-detail cell incorrectly flagged: {row}"
    assert row["detail_class"] == expected, f"Detail class mismatch: {row}"
    assert row["flat"].strip().lower() == str(expected == "flat").lower(), (
        f"Derived flat flag disagrees with the report threshold: {row}"
    )
    assert row["base_layer_exposure"] == "unverified", (
        "Low texture is not proof of underlying base-layer exposure"
    )
    assert "legacy_flat_flag" in row, "Unmodified upstream flag was lost"
    counts[expected] += 1

report = (REPORTS / "terrain-gap-report.md").read_text(encoding="utf-8")
match = re.search(
    r"Whole sheet:\s*(\d+) land cells,\s*(\d+) flat,\s*(\d+) thin",
    report,
)
assert match, "Summary count not found in terrain-gap-report.md"
total, flat, thin = map(int, match.groups())
assert total >= flat + thin, "Flagged cell total exceeds land cells"
assert (flat, thin) == (counts["flat"], counts["thin"]), (
    f"CSV and Markdown summary mismatch: CSV={counts}, MD={(flat, thin)}"
)
print(f"Terrain gap QA OK: {total} land cells, {flat} flat, {thin} thin; "
      "no base-layer visibility inferred from texture")
