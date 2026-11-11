#!/usr/bin/env python3
"""Safely expand ZIP batches into the existing sprite intake staging tree.

Never replaces source archives, never extracts to uncontrolled paths, and never
assigns historical identity or map coordinates. Run sprite_intake.py afterward.
"""
from __future__ import annotations

import argparse
import json
import stat
import zipfile
from pathlib import Path, PurePosixPath

MAX_FILES = 250
MAX_UNCOMPRESSED = 300 * 1024 * 1024
MAX_MEMBER = 35 * 1024 * 1024
MAX_RATIO = 200

def extract_archives(root: Path) -> dict:
    incoming = root / "assets/sprites/incoming"
    staging = incoming / "_zip_extract"
    report = {"archives": [], "extracted": 0, "errors": []}
    for archive in sorted(incoming.glob("*.zip")) if incoming.exists() else []:
        dest = staging / archive.stem
        extracted = []
        try:
            with zipfile.ZipFile(archive) as z:
                members = [m for m in z.infolist() if not m.is_dir()]
                if not members or len(members) > MAX_FILES:
                    raise ValueError("archive must have between 1 and 250 files")
                total = 0
                planned = []
                seen = set()
                for info in members:
                    name = info.filename
                    p = PurePosixPath(name)
                    mode = info.external_attr >> 16
                    if (name.startswith("/") or "\\" in name or not p.parts
                            or any(part in (".", "..") for part in p.parts)
                            or ":" in p.parts[0] or stat.S_ISLNK(mode)):
                        raise ValueError(f"unsafe archive member: {name!r}")
                    if p.suffix.lower() not in (".png", ".json"):
                        raise ValueError(f"unexpected archive member: {name!r}")
                    if info.file_size > MAX_MEMBER:
                        raise ValueError(f"oversized member: {name!r}")
                    if info.file_size and (info.file_size / max(info.compress_size, 1)) > MAX_RATIO:
                        raise ValueError(f"excessive compression ratio: {name!r}")
                    total += info.file_size
                    if total > MAX_UNCOMPRESSED:
                        raise ValueError("archive exceeds 300 MiB uncompressed")
                    relative = Path(*p.parts)
                    if relative.as_posix().lower() in seen:
                        raise ValueError(f"duplicate member path: {name!r}")
                    seen.add(relative.as_posix().lower())
                    planned.append((info, relative))
                if not any(p.suffix.lower() == ".png" for _, p in planned):
                    raise ValueError("archive contains no PNGs")
                for info, rel in planned:
                    target = dest / rel
                    target.parent.mkdir(parents=True, exist_ok=True)
                    content = z.read(info)
                    if target.exists() and target.read_bytes() != content:
                        raise ValueError(f"existing extracted member differs: {target}")
                    if not target.exists():
                        target.write_bytes(content)
                    extracted.append(target.relative_to(root).as_posix())
            report["archives"].append({"path": archive.relative_to(root).as_posix(), "members": extracted})
            report["extracted"] += sum(x.lower().endswith(".png") for x in extracted)
        except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
            report["errors"].append({"archive": archive.name, "error": str(exc)})
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = extract_archives(args.root.resolve())
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["errors"]))
