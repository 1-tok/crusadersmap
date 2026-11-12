"""Regression tests for year-gated, deduplicated review-only sprite selection."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import render_sprite_layer


def entry(id_, site, year, visible=True, geometry=True, approved=True):
    return {
        "type": "Feature",
        "id": id_,
        "geometry": {"type": "Point", "coordinates": [35.3, 32.1]} if geometry else None,
        "properties": {
            "site_id": site,
            "name": id_,
            "asset_path": f"data/sprites/qa/{id_}.png",
            "depiction_year": year,
            "approval_for_review_placement": approved,
            "default_visible": visible,
            "period_1180_eligible": year in (None, 1180),
        },
    }


class ReviewSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        (self.base / "qa").mkdir()
        features = [
            entry("darbsak", "darbsak", 1180),
            entry("darbsak-alt", "darbsak", 1180),
            entry("chlemoutsi", "chlemoutsi", 1250),
            entry("older-church", "older-church", None),
            entry("missing-geometry", "missing", 1180, geometry=False),
            entry("not-approved", "not-approved", 1180, approved=False),
        ]
        for feature in features:
            (self.base / "qa" / (feature["id"] + ".png")).write_bytes(b"fake-png")
        (self.base / "placements-review-1180.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": features})
        )
        self.patcher = patch.object(render_sprite_layer, "BASE", self.base)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)

    def test_excludes_mismatched_year_and_null_geometry(self):
        chosen = render_sprite_layer.review_placements(1180)
        ids = {x["id"] for x in chosen}
        self.assertEqual(ids, {"darbsak", "older-church"})

    def test_all_variants_keeps_both_but_still_gates_year(self):
        chosen = render_sprite_layer.review_placements(1180, True)
        ids = {x["id"] for x in chosen}
        self.assertEqual(ids, {"darbsak", "darbsak-alt", "older-church"})


if __name__ == "__main__":
    unittest.main()
