import io
import hashlib
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from PIL import Image
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from sprite_zip_intake import extract_archives
from sprite_intake import process


class ZipIntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.incoming = self.root / "assets/sprites/incoming"
        self.incoming.mkdir(parents=True)
        (self.root / "data/sprites").mkdir(parents=True)

    def png(self):
        im = Image.new("RGBA", (90, 90), (0, 0, 0, 0))
        for x in range(10, 80):
            for y in range(10, 80):
                im.putpixel((x, y), (180, 130, 80, 255))
        bio = io.BytesIO()
        im.save(bio, format="PNG")
        return bio.getvalue()

    def make_zip(self, name, members):
        with zipfile.ZipFile(self.incoming / name, "w") as z:
            for path, content in members.items():
                z.writestr(path, content)

    def test_zip_process_repeat_and_duplicate(self):
        source = self.png()
        self.make_zip("batch.zip", {
            "batch/castle.png": source,
            "batch/castle.json": json.dumps({"category":"castle","subject":"Unknown castle","status":"provisional"}),
            "README.md": "source notes",
        })
        report = extract_archives(self.root)
        self.assertEqual(report["extracted"], 1)
        first = process(self.root)
        self.assertEqual(first["registered"], 1)
        self.assertTrue((self.root / "data/sprites/automated-intake/placements-review.geojson").exists())
        self.assertEqual(extract_archives(self.root)["errors"], [])
        self.assertEqual(process(self.root)["registered"], 0)
        records = json.loads((self.root / "data/sprites/automated-intake/manifest.json").read_text())["assets"]
        self.assertIsNone(records[0]["coordinates"])
        self.assertFalse(records[0]["historical_accuracy_certified"])

    def test_quarantine_python_source_without_rejecting_safe_png(self):
        source = self.png()
        self.make_zip("location_underlays.zip", {
            "underlays/terrain.png": source,
            "build_location_underlays.py": "print('must never run')",
            "generated/underlay_syrian_steppe.svg": '<svg onload="alert(1)"/>',
            "manifest.json": '{"category":"terrain"}',
        })
        report = extract_archives(self.root)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["extracted"], 1)
        self.assertEqual(len(report["warnings"]), 2)
        self.assertEqual({e["member"] for e in report["warnings"]},
                         {"build_location_underlays.py", "generated/underlay_syrian_steppe.svg"})
        self.assertFalse((self.root / "assets/sprites/incoming/_zip_extract/location_underlays/build_location_underlays.py").exists())
        self.assertFalse((self.root / "assets/sprites/incoming/_zip_extract/location_underlays/generated/underlay_syrian_steppe.svg").exists())
        self.assertTrue((self.root / "assets/sprites/incoming/_zip_extract/location_underlays/underlays/terrain.png").exists())

    def test_master_sheets_skipped_when_individual_cutouts_exist(self):
        source = self.png()
        self.make_zip("november_lowland.zip", {
            "masters/10_nile_delta_floodplain_MASTER.png": source,
            "png/delta_01.png": source,
            "png/delta_01.json": json.dumps({
                "category": "terrain_transition",
                "subject": "Nile Delta lowland cutout",
                "status": "provisional",
                "map_region": "delta",
                "orientation": "south"
            }),
        })
        result = extract_archives(self.root)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["extracted"], 1)
        self.assertTrue(any("master sheet skipped" in v["warning"]
                            for v in result["warnings"]))
        self.assertFalse((self.incoming / "_zip_extract/november_lowland/masters/10_nile_delta_floodplain_MASTER.png").exists())
        self.assertTrue((self.incoming / "_zip_extract/november_lowland/png/delta_01.png").exists())
        outcome = process(self.root)
        self.assertEqual(outcome["registered"], 1)

    def test_skip_non_png_source_archive(self):
        self.make_zip("non_sprite_underlays.zip", {
            "build_location_underlays.py": "print('not permitted')",
            "generated/underlay_nile_delta.svg": '<svg/>',
            "README.md": "vector source only",
        })
        report = extract_archives(self.root)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["extracted"], 0)
        self.assertTrue(any("no PNG sprites" in x["warning"] for x in report["warnings"]))
        self.assertFalse((self.root / "assets/sprites/incoming/_zip_extract/non_sprite_underlays").exists())

    def test_corrected_root_archive_rejects_wrong_digest(self):
        archive = self.root / "crusader_lowlands_13nov_remaining_51_REGION_QA.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("cutout.png", self.png())
        report = extract_archives(self.root)
        self.assertEqual(report["extracted"], 0)
        self.assertEqual(len(report["errors"]), 1)
        self.assertIn("hash mismatch", report["errors"][0]["error"])
        self.assertFalse((self.incoming / "_zip_extract/crusader_lowlands_13nov_remaining_51_REGION_QA/cutout.png").exists())

    def test_reject_mismatched_canaan_root_archive(self):
        archive = self.root / "crusader_canaan_batch38_complete.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("b38_01_acre_carmel_foothills.png", self.png())
        report = extract_archives(self.root)
        self.assertEqual(report["extracted"], 0)
        self.assertEqual(len(report["errors"]), 1)
        self.assertIn("Git blob mismatch", report["errors"][0]["error"])
        self.assertFalse((self.incoming / "_zip_extract/crusader_canaan_batch38_complete/b38_01_acre_carmel_foothills.png").exists())

    def test_pinned_root_zip_recovers_and_rejects_tampering(self):
        name = "Greek_Islands_12A_part1_RETRY.zip"
        source = self.png()
        archive = self.root / name
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("island.png", source)
        payload = archive.read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(payload)).encode("ascii")
                            + b"\0" + payload).hexdigest()
        audit = self.root / "data/manifests/ROOT-ZIP-RECOVERY-2026-11-13.json"
        audit.parent.mkdir(parents=True, exist_ok=True)
        audit.write_text(json.dumps({"root_archives": [{"path": name, "blob_sha": blob}]}))
        first = extract_archives(self.root)
        self.assertEqual(first["errors"], [])
        self.assertEqual(first["extracted"], 1)
        with zipfile.ZipFile(archive, "w") as z:
            z.writestr("island.png", source + b"x")
        second = extract_archives(self.root)
        self.assertEqual(second["extracted"], 0)
        self.assertEqual(len(second["errors"]), 1)
        self.assertIn("root recovery ZIP Git blob mismatch", second["errors"][0]["error"])

    def test_reject_traversal(self):
        self.make_zip("unsafe.zip", {"../outside.png": self.png()})
        self.assertEqual(len(extract_archives(self.root)["errors"]), 1)
        self.assertFalse((self.root / "outside.png").exists())

    def test_reject_too_many(self):
        self.make_zip("huge.zip", {f"{i}.png": b"x" for i in range(251)})
        self.assertEqual(len(extract_archives(self.root)["errors"]), 1)

    def test_idempotent_separate_archives_dedup(self):
        source = self.png()
        self.make_zip("a.zip", {"a.png": source})
        self.make_zip("b.zip", {"b.png": source})
        self.assertEqual(extract_archives(self.root)["extracted"], 2)
        result = process(self.root)
        self.assertEqual(result["registered"], 1)
        self.assertEqual(result["duplicates"], 1)


if __name__ == "__main__":
    unittest.main()
