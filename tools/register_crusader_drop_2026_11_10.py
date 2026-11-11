#!/usr/bin/env python3
"""Register 30 imported rural terrain PNG paths, preserving all existing review gates."""
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/sprites/rural-landscapes/rural_landscape_placement_manifest.json"
BASE = ROOT / "data/sprites/rural-landscapes/png"

def register(check=False):
    doc = json.loads(MANIFEST.read_text())
    count = 0
    for item in doc["sprites"]:
        ident = item.get("id", "")
        if not ident.startswith("CSV-"):
            continue
        n = int(ident[4:])
        if not 89 <= n <= 118:
            continue
        path = BASE / (ident + ".png")
        if not path.is_file() or not path.stat().st_size:
            raise SystemExit("Missing/empty PNG: " + str(path))
        item["png_path"] = "data/sprites/rural-landscapes/png/" + ident + ".png"
        item["asset_visual_qa"] = "needs_alpha_edge_and_geography_review"
        item["ready_for_renderer"] = False
        count += 1
    if count != 30:
        raise SystemExit(f"Expected 30 manifest records; got {count}")
    doc["artwork_delivery"] = "files_present_requires_visual_review"
    doc["notes"] = "PNG files staged; alpha, visual and geographic placement reviews remain pending."
    if not check:
        MANIFEST.write_text(json.dumps(doc, indent=2) + "\n")
    print(("Verified" if check else "Registered"), count, "PNG paths; renderer stays disabled.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    register(args.check)
