#!/usr/bin/env python3
"""Install artwork extracted from the Nile sprite sheets into the map build.

Input: assets/sprites/incoming/nile_delta_upstream_terrain_sprites_2026-11-17.zip
Output: data/sprites/nile-ecology-2026-11-17/{sprites,manifest.json}
No interpolation of river positions; the river sheet is purely art texture.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import zipfile
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
ZIP=ROOT/"assets/sprites/incoming/nile_delta_upstream_terrain_sprites_2026-11-17.zip"
OUT=ROOT/"data/sprites/nile-ecology-2026-11-17"
REPORT=ROOT/"reports/nile-delta-terrain-review-2026-11-17/painted-pack-intake.json"
CATEGORIES={"delta_farm","nile_farm_upstream","delta_marsh","river_decor_reference"}

def main():
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    if not ZIP.exists():
        REPORT.write_text(json.dumps({
            "status":"awaiting_binary_artwork_upload",
            "expected_zip":str(ZIP.relative_to(ROOT)),
            "expected_png_count":80,
            "production_approved":False,
            "note":"Never claim new paintings are rendered until ZIP is installed"
        },indent=2)+"\n")
        print("NILE PACK: no source zip; retaining currently approved existing sprites")
        return False
    with zipfile.ZipFile(ZIP) as archive:
        manifest=json.loads(archive.read("manifest.json"))
        entries=manifest["assets"]
        if len(entries)!=80:
            raise AssertionError("Nile artwork archive missing generated cutouts")
        seen=set()
        OUT.mkdir(parents=True,exist_ok=True)
        (OUT/"sprites").mkdir(exist_ok=True)
        for entry in entries:
            name=entry["file"]
            if not name.startswith("sprites/") or ".." in name or name in seen:
                raise ValueError("Unsafe or duplicated Nile sprite filename")
            seen.add(name)
            if entry["class"] not in CATEGORIES:
                raise ValueError("Unexpected terrain category")
            data=archive.read(name)
            if hashlib.sha256(data).hexdigest()!=entry["sha256"]:
                raise AssertionError("Sprite SHA mismatch: "+name)
            dest=OUT/name
            dest.write_bytes(data)
            with Image.open(dest) as image:
                if image.mode!="RGBA" or not image.getextrema()[3][0]<255:
                    raise AssertionError("Expected transparent RGBA sprite: "+name)
        (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    result={"status":"installed_for_geographic_review","source_zip":str(ZIP.relative_to(ROOT)),
            "installed":len(entries),"categories":{k:sum(x["class"]==k for x in entries) for k in sorted(CATEGORIES)},
            "print_approved":False}
    REPORT.write_text(json.dumps(result,indent=2)+"\n")
    print("NILE PACK",result)
    return True

if __name__=="__main__":
    main()
