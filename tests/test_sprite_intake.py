import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from sprite_intake import process

class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "assets/sprites/incoming").mkdir(parents=True)
        (self.root / "data/sprites").mkdir(parents=True)

    def make(self, name="ascalon.png"):
        image = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        for x in range(20, 100):
            for y in range(30, 110):
                image.putpixel((x, y), (180, 80, 30, 255))
        target = self.root / "assets/sprites/incoming" / name
        image.save(target)
        return target

    def test_provisional_and_idempotent(self):
        src = self.make()
        original = src.read_bytes()
        first = process(self.root)
        self.assertEqual(first["registered"], 1)
        e = json.loads((self.root / "data/sprites/automated-intake/manifest.json").read_text())["assets"][0]
        self.assertFalse(e["geographic_placement_ready"])
        self.assertTrue(e["approval"]["provisional_map_use"])
        dest = self.root / "data/sprites" / e["asset"]
        self.assertEqual(dest.read_bytes(), original)
        second = process(self.root)
        self.assertEqual(second["registered"], 0)
        self.assertEqual(len(json.loads((self.root / "data/sprites/automated-intake/manifest.json").read_text())["assets"]), 1)

    def test_declared_sheet_boxes_and_coordinates(self):
        src = self.make("sheet.png")
        metadata = {"sprites": [{"box": [0, 0, 64, 128], "subject": "A", "category": "castle",
                                "coordinates": [35.2, 31.3], "coordinate_source": "editorial", "orientation": "south"},
                               {"box": [64, 0, 128, 128], "subject": "B", "category": "city"}]}
        src.with_suffix(".json").write_text(json.dumps(metadata))
        result = process(self.root)
        self.assertEqual(result["registered"], 2)
        entries = json.loads((self.root / "data/sprites/automated-intake/manifest.json").read_text())["assets"]
        self.assertEqual(sum(bool(e["geographic_placement_ready"]) for e in entries), 1)

    def test_invalid_png_preserved_and_reported(self):
        p = self.root / "assets/sprites/incoming/bad.png"
        p.write_bytes(b"broken")
        self.assertEqual(process(self.root)["errors"], 1)
        self.assertEqual(p.read_bytes(), b"broken")

if __name__ == "__main__":
    unittest.main()
