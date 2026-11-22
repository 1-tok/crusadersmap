#!/usr/bin/env python3
"""Reconstruct four exact approved Nile PNGs from GitHub text blobs.

Ten smaller originals are already committed as PNGs. Verify all fourteen
against the owner-approved SHA-256 manifest; do not change the map.
"""
import base64, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"data/sprites/nile-vertical-banks-2026-11-21"
LARGE=["leftbank_straight_06_village_shaduf.png","rightbank_straight_06_village_feluccas.png","leftbank_meander_01_rocky_farmland.png","rightbank_meander_01_plateau_fields.png"]
def main():
    p=DIR/"manifest.json"
    doc=json.loads(p.read_text())
    candidates={item["path"]:item for item in doc["assets"]}
    if len(candidates)!=14:
        raise RuntimeError("Unexpected source count")
    for name in LARGE:
        folder=DIR/"text-parts"/name.removesuffix(".png")
        paths=[folder/f"part-{i:03d}.b64" for i in range(10)]
        if not all(q.is_file() for q in paths):
            raise RuntimeError(f"Missing encoded parts for {name}")
        b64="".join(q.read_text() for q in paths)
        raw=base64.b64decode(b64,validate=True)
        if hashlib.sha256(raw).hexdigest()!=candidates[name]["sha256"]:
            raise RuntimeError(f"SHA256 mismatch: {name}")
        if raw[:8]!=bytes.fromhex("89504e470d0a1a0a"):
            raise RuntimeError(f"Invalid PNG: {name}")
        dims=[int.from_bytes(raw[16:20],"big"),int.from_bytes(raw[20:24],"big")]
        if dims!=candidates[name]["dimensions_px"]:
            raise RuntimeError(f"Dimension mismatch: {name}")
        (DIR/name).write_bytes(raw)
    for name,item in candidates.items():
        target=DIR/name
        if not target.is_file():
            raise RuntimeError("Missing original asset: "+name)
        if hashlib.sha256(target.read_bytes()).hexdigest()!=item["sha256"]:
            raise RuntimeError("Final content verification failed: "+name)
        item["binary_status"]="verified_original_png_committed"
    doc["binary_status"]="all 14 original PNG files verified"
    doc["status"]="artwork_approved_binaries_committed_review_only"
    doc["production_map_status"]="NOT_PLACED"
    p.write_text(json.dumps(doc,indent=2)+"\n")
    print("SUCCESS: all 14 original Nile bank sprite PNGs verified and available for Claude")
if __name__=="__main__":
    main()
