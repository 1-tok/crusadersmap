#!/usr/bin/env python3
"""Import Terrain Batch 05 PNGs from its conversation ZIP into this checkout.

Checks SHA-256 and PNG dimensions against the repository manifest. It never
approves map placement, prints, or unverified historic landcover.
"""
from pathlib import Path
import hashlib
import json
import struct
import sys
import zipfile

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python3 tools/import_terrain_batch05.py /path/to/crusadersmap_terrain_batch05_20261111.zip")
    repo_root = Path(__file__).resolve().parent.parent
    manifest_path = repo_root / "data/sprites/terrain-batch05/manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if len(manifest["assets"]) != 18:
        raise SystemExit("Unexpected manifest count; verify branch first.")
    staged = {}
    with zipfile.ZipFile(Path(sys.argv[1]).expanduser()) as z:
        for entry in manifest["assets"]:
            name = entry["file"]
            blob = z.read(name)
            digest = hashlib.sha256(blob).hexdigest()
            if digest != entry["sha256"]:
                raise SystemExit(f"Checksum mismatch for {name}: {digest}")
            if blob[:8] != b"\x89PNG\r\n\x1a\n" or blob[12:16] != b"IHDR":
                raise SystemExit(f"Invalid PNG header: {name}")
            dims = struct.unpack(">II", blob[16:24])
            if tuple(entry["dimensions_px"]) != dims:
                raise SystemExit(f"Wrong image dimensions: {name}, got {dims}")
            # PNG IHDR colour type 6 is RGBA, i.e. transparency-capable.
            if blob[25] != 6:
                raise SystemExit(f"Sprite is not RGBA: {name}")
            path = repo_root / name
            if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                raise SystemExit(f"Refusing to overwrite changed path: {path}")
            staged[path] = blob
        if z.testzip() is not None:
            raise SystemExit("ZIP integrity failed")
    for path, blob in staged.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(blob)
        print(f"Verified: {path.relative_to(repo_root)}")
    print(f"All {len(staged)} sprites extracted and SHA-256 verified.")
    print("Placement, regional accuracy and print quality remain pending review.")

if __name__ == "__main__":
    main()
