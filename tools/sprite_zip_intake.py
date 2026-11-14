#!/usr/bin/env python3
"""Safely expand ZIP batches into the existing sprite intake staging tree.

Never replaces source archives, never extracts to uncontrolled paths, and never
assigns historical identity or map coordinates. Run sprite_intake.py afterward.
"""
from __future__ import annotations

import argparse
import hashlib
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
    report = {"archives": [], "extracted": 0, "errors": [], "warnings": []}
    # The corrected 51-cutout lowlands archive was committed at repository
    # root rather than the normal incoming folder. Import only this verified
    # exceptional root ZIP; do not sweep arbitrary root archives.
    corrected_name = "crusader_lowlands_13nov_remaining_51_REGION_QA.zip"
    corrected_sha256 = "d48c93c2e5ebaf6917412cd36f1ab0305555cc8834652c905816214980902e06"
    # Verified existing Git blobs at repository root. Only these exact three
    # archives are admitted; root is never scanned indiscriminately.
    canaan_git_blobs = {
        "crusader_canaan_coastal_underlays_complete.zip": "b1522884a9b5ca8c94b2396342605861f4940daf",
        "crusader_canaan_batch38_complete.zip": "3b6fddefcf6c638c5468ba23f5e96376811c4cb6",
        "crusader_canaan_coast_batch39_complete.zip": "3c90de2e0ad8594ffce89f2892ecd52590ffb7b1",
    }
    archives = sorted(incoming.glob("*.zip")) if incoming.exists() else []
    corrected_root = root / corrected_name
    if corrected_root.is_file():
        archives.append(corrected_root)
    archives.extend(root / name for name in canaan_git_blobs if (root / name).is_file())
    for archive in archives:
        dest = staging / archive.stem
        extracted = []
        try:
            if archive == corrected_root:
                with archive.open("rb") as source:
                    digest = hashlib.file_digest(source, "sha256").hexdigest()
                if digest != corrected_sha256:
                    raise ValueError("corrected lowlands ZIP hash mismatch; refusing import")
            if archive.name in canaan_git_blobs and archive.parent == root:
                with archive.open("rb") as source:
                    payload = source.read()
                git_blob = hashlib.sha1(
                    b"blob " + str(len(payload)).encode("ascii") + b"\0" + payload
                ).hexdigest()
                if git_blob != canaan_git_blobs[archive.name]:
                    raise ValueError("Canaan coastal ZIP Git blob mismatch; refusing import")
            with zipfile.ZipFile(archive) as z:
                members = [m for m in z.infolist() if not m.is_dir()]
                if not members or len(members) > MAX_FILES:
                    raise ValueError("archive must have between 1 and 250 files")
                total = 0
                planned = []
                seen = set()
                # Source/master sheets are useful references, but should never
                # become standalone map sprites when the ZIP contains cutouts.
                def is_master(member_name):
                    p = PurePosixPath(member_name)
                    stem = p.stem.lower()
                    return (p.parts[0].lower() == "masters"
                            or stem.endswith("_master")
                            or stem.endswith("-master"))
                has_cutouts = any(
                    m.filename.lower().endswith(".png")
                    and not is_master(m.filename)
                    for m in members
                )
                for info in members:
                    name = info.filename
                    p = PurePosixPath(name)
                    mode = info.external_attr >> 16
                    if (name.startswith("/") or "\\" in name or not p.parts
                            or any(part in (".", "..") for part in p.parts)
                            or ":" in p.parts[0] or stat.S_ISLNK(mode)):
                        raise ValueError(f"unsafe archive member: {name!r}")
                    if p.suffix.lower() not in (".png", ".json", ".md", ".csv", ".txt"):
                        # Never unpack executable code, potentially active SVG,
                        # or any unrecognized payload type. Only the strict
                        # allowlist is extracted. Keep a visible warning and
                        # process safe PNGs independently within the archive.
                        report["warnings"].append({
                            "archive": archive.name, "member": name,
                            "warning": "unsupported file quarantined; not extracted or executed"})
                        continue
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
                    if p.suffix.lower() == ".png" and has_cutouts and is_master(name):
                        report["warnings"].append({
                            "archive": archive.name, "member": name,
                            "warning": "source/master sheet skipped; individual cutouts available"})
                        continue
                    if p.suffix.lower() in (".png", ".json"):
                        planned.append((info, relative))
                if not any(p.suffix.lower() == ".png" for _, p in planned):
                    # An unrelated map-underlay/source ZIP is not a sprite
                    # package. Keep it intact and explicitly skip it, rather
                    # than failing the complete intake of valid PNG archives.
                    report["warnings"].append({
                        "archive": archive.name,
                        "warning": "archive contains no PNG sprites; preserved and skipped"})
                    continue
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
