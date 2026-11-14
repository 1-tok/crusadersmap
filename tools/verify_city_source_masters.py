#!/usr/bin/env python3
"""Check the five original city-sheet masters without importing them as map sprites."""
from __future__ import annotations

import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "data/sprites/city-review-2026-11-10/source_sheets/crusadersmap_five_city_source_sheets_recovery.zip"
EXPECTED_ZIP_SHA256 = "9b2ec7707d3b1800278e035a7cb9ec3c0cc495a970793fbe7c615e3fe11d6c47"
EXPECTED = {
    "source_sheets/batch-07-levant-galilee-source-sheet.png":
        "5c9db1a36d763a6f1b4a7c59543414abd041563c35b061260f2d6b8771c23ddb",
    "source_sheets/batch-08-syria-source-sheet.png":
        "cd3f0a32e31da14cb837d72ebd7acfe0b8f05ca919959fedab4584c10e409c24",
    "source_sheets/batch-09-cilicia-cyprus-source-sheet.png":
        "a07a7b5595525c6b0847f84536480fc2ed424e0bf89c0fd10340822126443dec",
    "source_sheets/batch-10-aegean-1-source-sheet.png":
        "43f28edde3dd51b910652535d57e5bb3cafdf8f6084ad0c8a86f32e00efcfae9",
    "source_sheets/batch-11-aegean-egypt-source-sheet.png":
        "6288e8817577ef1bf1f303d27488810d750d4131bb8fd850f3954275d3534032",
}
ALLOWED_ADDITIONAL = {"README.txt", "source_sheets/recovery-manifest.json"}


def verify(path: Path = ARCHIVE) -> dict:
    result = {"archive": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
              "present": path.is_file(), "checks": [], "errors": []}
    if not path.is_file():
        result["errors"].append("The original binary ZIP has not yet been uploaded.")
        return result
    digest = hashlib.file_digest(path.open("rb"), "sha256").hexdigest()
    if digest != EXPECTED_ZIP_SHA256:
        result["errors"].append(f"Archive checksum mismatch: {digest}")
        return result
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None:
            result["errors"].append("Archive member CRC failed")
        names = set(z.namelist())
        missing = set(EXPECTED) - names
        unexpected = names - set(EXPECTED) - ALLOWED_ADDITIONAL
        if missing:
            result["errors"].append("Missing members: " + ", ".join(sorted(missing)))
        if unexpected:
            result["errors"].append("Unexpected archive members: " + ", ".join(sorted(unexpected)))
        for name, expected_digest in EXPECTED.items():
            if name not in names:
                continue
            content = z.read(name)
            current = hashlib.sha256(content).hexdigest()
            good_png = (content[:8] == bytes.fromhex("89504e470d0a1a0a")
                        and len(content) >= 24
                        and struct.unpack(">II", content[16:24]) == (1254, 1254))
            result["checks"].append({"member": name, "sha256_match": current == expected_digest,
                                     "dimensions_1254x1254": good_png})
            if current != expected_digest:
                result["errors"].append(f"Sheet hash mismatch: {name}")
            if not good_png:
                result["errors"].append(f"PNG signature/dimension mismatch: {name}")
    return result


if __name__ == "__main__":
    report = verify()
    print(json.dumps(report, indent=2))
    if report["errors"]:
        for err in report["errors"]:
            print(f"::error::{err}")
    sys.exit(bool(report["errors"]))
