#!/usr/bin/env python3
"""Reassemble exact PNGs from temporarily committed raw binary parts.

Never treats pixel interpolation / recompression as an acceptable substitute.
Validation is SHA-256 of each full original PNG.
"""
import hashlib
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
STAGING = BASE / ".terrain-staging" / "rect_underlays_04"
OUT = BASE / "assets" / "terrain" / "large_area" / "rect_underlays_04"
FILES = {
    "canaan_scrub_edge_matched.png": (3, 3179469, "73b0c5774484353025779de83bac12504a73b409681ccded7e0eaaeecf95abbc"),
    "canaan_scrub_opaque.png": (3, 3264318, "f36030b42d5307edbdde1c0cc695cfc8a7196069c066f378a63d0199db69d18e"),
    "desert_sand_edge_matched.png": (2, 2620411, "2c69b3239a0f5e41c3268a6a96ac60e7c3ebc54a801a7085b0c1c43ceefaec4c"),
    "desert_sand_opaque.png": (2, 2722342, "da51a527fabc32a4cc3b9b19951cb94ce7cf33077b296b9b126e9602e301a68d"),
    "dry_steppe_edge_matched.png": (3, 3059072, "eecf0cd31bc3d42545f6fdda89fec1618d7417271d7cca3a9170d65aeada53f2"),
    "dry_steppe_opaque.png": (3, 3154977, "defa4a9fde46a03afabbcf520b3096e9b42e11e714e18d251d4e358513c2bdd1"),
    "green_plain_edge_matched.png": (2, 1840299, "fb89ed160ffcfa0a0e240455294b6bb6ae30577fa5fd4e9fefe90d089d0f35b8"),
    "green_plain_opaque.png": (2, 1874467, "43b5de6d3b70f7ea981d8ab1ead2187a5706b866ba19f9972b3336283d238cce")
}

def main():
    if not STAGING.is_dir():
        raise SystemExit("Staging binary parts not found")
    prepared = {}
    for name, (parts, expected_size, expected_hash) in FILES.items():
        blocks = []
        for n in range(parts):
            part = STAGING / f"{name}.part{n:03d}"
            if not part.is_file():
                raise SystemExit(f"Missing part: {part}")
            blocks.append(part.read_bytes())
        data = b"".join(blocks)
        actual_hash = hashlib.sha256(data).hexdigest()
        if len(data) != expected_size or actual_hash != expected_hash:
            raise SystemExit(f"Integrity failure for {name}: {len(data)} bytes / {actual_hash}")
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise SystemExit(f"Invalid PNG signature: {name}")
        prepared[name] = data
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in prepared.items():
        dest = OUT / name
        if dest.exists() and dest.read_bytes() != data:
            raise SystemExit(f"Refusing to overwrite a different PNG: {dest}")
        dest.write_bytes(data)
        print(f"VERIFIED {name}: {len(data)} bytes")
    print(f"SUCCESS: {len(prepared)} source-exact PNGs reassembled.")

if __name__ == "__main__":
    main()
