#!/usr/bin/env python3
"""Restore original approved vertical Nile bank PNGs from text-only split-Base64 ZIP.

Precedent: data/sprites/nile-joins-batch-02/encoded and
tools/render_nile_eight_fixed_print_preview.py.
No map placement, no recompression or substitutions.
"""
from __future__ import annotations
import base64,hashlib,json,zipfile
from io import BytesIO
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"data/sprites/nile-vertical-banks-2026-11-21"
ENC=TARGET/"encoded"

def main():
    metadata=json.loads((ENC/"manifest.json").read_text())
    assert metadata["format"]=="base64-split-zip"
    assert metadata["parts"]==118
    encoded="".join((ENC/f"part-{i:03d}.b64").read_text() for i in range(metadata["parts"]))
    raw=base64.b64decode(encoded,validate=True)
    assert len(raw)==metadata["zip_bytes"],"Encoded ZIP length changed"
    assert hashlib.sha256(raw).hexdigest()==metadata["zip_sha256"],"Encoded ZIP SHA mismatch"
    manifest_path=TARGET/"manifest.json"
    manifest=json.loads(manifest_path.read_text())
    expected={x["path"]:x for x in manifest["assets"]}
    assert len(expected)==14
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        files={Path(name).name:name for name in archive.namelist() if name.lower().endswith(".png")}
        assert set(files)==set(expected),"Exact PNG set does not match approved manifest"
        for name, asset in expected.items():
            data=archive.read(files[name])
            assert hashlib.sha256(data).hexdigest()==asset["sha256"],f"PNG checksum mismatch: {name}"
            assert hashlib.sha256(data).hexdigest()==metadata["file_sha256"][name]
            assert data[:8]==bytes.fromhex("89504e470d0a1a0a")
            width=int.from_bytes(data[16:20],"big")
            height=int.from_bytes(data[20:24],"big")
            assert [width,height]==asset["dimensions_px"],f"PNG dimensions differ: {name}"
            (TARGET/name).write_bytes(data)
            asset["binary_status"]="reconstructed_verified_exact_original"
    manifest["status"]="14_png_binaries_restored_from_encoded_text_review_only"
    manifest["production_map_status"]="NOT_PLACED"
    manifest["binary_status"]="all 14 exact bytes reconstructed from split Base64 ZIP"
    manifest_path.write_text(json.dumps(manifest,indent=2)+"\n")
    print("Successfully restored exact 14 PNGs from", metadata["parts"],"text pieces")
    print("Production sprite placement remains disabled.")

if __name__=="__main__":
    main()
