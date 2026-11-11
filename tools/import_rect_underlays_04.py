#!/usr/bin/env python3
"""Import and verify the four rectangular Crusader Map terrain underlays.

Usage:
  git switch terrain-assets-access-20261110
  python tools/import_rect_underlays_04.py ~/Downloads/crusadersmap_rect_underlays_04_20261110.zip
  git add assets/terrain/large_area/rect_underlays_04
  git commit -m "Add four rectangular Crusader terrain underlays (8 PNGs)"
  git push origin terrain-assets-access-20261110

This does not approve map placement or final 300-DPI print quality.
"""
import hashlib
import pathlib
import struct
import sys
import zipfile

EXPECTED = {
    "canaan_scrub_edge_matched.png": ("73b0c5774484353025779de83bac12504a73b409681ccded7e0eaaeecf95abbc", (1672, 941)),
    "canaan_scrub_opaque.png": ("f36030b42d5307edbdde1c0cc695cfc8a7196069c066f378a63d0199db69d18e", (1672, 941)),
    "desert_sand_edge_matched.png": ("2c69b3239a0f5e41c3268a6a96ac60e7c3ebc54a801a7085b0c1c43ceefaec4c", (1536, 1024)),
    "desert_sand_opaque.png": ("da51a527fabc32a4cc3b9b19951cb94ce7cf33077b296b9b126e9602e301a68d", (1536, 1024)),
    "dry_steppe_edge_matched.png": ("eecf0cd31bc3d42545f6fdda89fec1618d7417271d7cca3a9170d65aeada53f2", (1774, 887)),
    "dry_steppe_opaque.png": ("defa4a9fde46a03afabbcf520b3096e9b42e11e714e18d251d4e358513c2bdd1", (1774, 887)),
    "green_plain_edge_matched.png": ("fb89ed160ffcfa0a0e240455294b6bb6ae30577fa5fd4e9fefe90d089d0f35b8", (1536, 1012)),
    "green_plain_opaque.png": ("43b5de6d3b70f7ea981d8ab1ead2187a5706b866ba19f9972b3336283d238cce", (1536, 1012)),
}
SUBDIR = pathlib.Path("assets/terrain/large_area/rect_underlays_04")

def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python tools/import_rect_underlays_04.py /path/to/crusadersmap_rect_underlays_04_20261110.zip")
    root = pathlib.Path(__file__).resolve().parents[1]
    manifest = root / "assets/terrain/large_area/manifest_rectangular_underlays_04.json"
    if not manifest.exists():
        raise SystemExit("Expected staging manifest missing. Switch to branch terrain-assets-access-20261110.")
    zip_path = pathlib.Path(sys.argv[1]).expanduser().resolve()
    with zipfile.ZipFile(zip_path) as zf:
        checked = {}
        for filename, (want_sha, want_dimensions) in EXPECTED.items():
            member = str(SUBDIR / filename)
            data = zf.read(member)
            digest = hashlib.sha256(data).hexdigest()
            if digest != want_sha:
                raise SystemExit(f"Checksum failure: {filename}\n expected {want_sha}\n got {digest}")
            if not data.startswith(b"\x89PNG\r\n\x1a\n") or data[12:16] != b"IHDR":
                raise SystemExit(f"Not a valid PNG header: {filename}")
            dimensions = struct.unpack(">II", data[16:24])
            if dimensions != want_dimensions:
                raise SystemExit(f"Unexpected PNG size for {filename}: {dimensions} != {want_dimensions}")
            checked[member] = data
    for member, data in checked.items():
        path = root / member
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists() and path.read_bytes() != data:
            raise SystemExit(f"Refusing to overwrite differing existing file: {path}")
        path.write_bytes(data)
        print(f"VERIFIED {member} ({len(data):,} bytes)")
    print(f"Successfully extracted {len(checked)} PNG files; ready for git add/commit.")
    print("QA: placement and 300dpi print approval remain pending.")

if __name__ == "__main__":
    main()
