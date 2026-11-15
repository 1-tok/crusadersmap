"""Tests for non-authoritative sprite intake review reporting."""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from summarize_sprite_intake import build_summary, suggested_categories


class SpriteReviewIntakeTests(unittest.TestCase):
    def test_hints_do_not_claim_verified_identity(self):
        self.assertEqual(suggested_categories("nile_delta_orchard_fields"), ["farmland"])
        self.assertEqual(suggested_categories("castle_port"), ["castle", "port"])
        self.assertEqual(suggested_categories("unknown_subject"), [])

    def test_summary_preserves_reviews_and_inputs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "data/sprites/automated-intake"
            base.mkdir(parents=True)
            manifest = {"schema_version": 1, "assets": [
                {"id": "INTAKE-one", "name": "coastal_city", "asset": "a.png",
                 "category": "unclassified", "approval": {"status": "repaint_required"},
                 "geographic_placement_ready": False, "review_flags": ["southern_pov_unverified"]},
                {"id": "INTAKE-two", "name": "generic_farmland", "asset": "b.png",
                 "category": "farmland", "approval": {"status": "provisional"},
                 "geographic_placement_ready": False, "review_flags": []},
            ]}
            report = {"results": [{"source": "some.png"}], "registered": 1,
                      "duplicates": 0, "errors": 0}
            (base / "manifest.json").write_text(json.dumps(manifest))
            (base / "processing-report.json").write_text(json.dumps(report))
            before = (base / "manifest.json").read_bytes()
            summary, markdown = build_summary(root)
            self.assertEqual(summary["intake_assets_total"], 2)
            self.assertEqual(summary["unclassified_count"], 1)
            self.assertEqual(summary["missing_geographic_placement"], 2)
            self.assertEqual(summary["approval_states"]["repaint_required"], 1)
            self.assertEqual(summary["unclassified_category_hints"][0]["candidate_categories"], ["city"])
            self.assertIn("not classification", markdown)
            self.assertEqual(before, (base / "manifest.json").read_bytes())
            second, text = build_summary(root)
            self.assertEqual(summary, second)
            self.assertEqual(markdown, text)


if __name__ == "__main__":
    unittest.main()
