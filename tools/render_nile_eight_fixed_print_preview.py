#!/usr/bin/env python3
"""Render the eight approved joined Nile paintings onto the EXISTING print atlas.

Uses the placement preset from the user-approved interactive print-canvas
review (x=265,y=2790,scale=.52 at 3240x4320). No rotation, mirroring,
nonuniform resize, new atlas illustration, or production-map replacement.

This is a visible placement candidate, not a geographic riverfit certificate.
"""
from __future__ import annotations
import base64
import hashlib
import json
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"reports/rebuild-2026-11-12/outremer-current-composite.jpg"
ENCODED=ROOT/"data/sprites/nile-joins-batch-02/encoded"
TILES=ROOT/"data/sprites/nile-joins-batch-02"
REPORT=ROOT/"reports/nile-joined-eight-fixed"
EXPECTED=(3240,4320)
X,Y,S=265,2790,0.52
CROP=(57,2726,1107,4128)

def main():
    metadata=json.loads((ENCODED/"manifest.json").read_text())
    assert metadata["parts"]==24
    parts=[(ENCODED/f"part-{i:03d}.b64").read_text() for i in range(metadata["parts"])]
    raw=base64.b64decode("".join(parts),validate=True)
    digest=hashlib.sha256(raw).hexdigest()
    assert digest==metadata["original_png_sha256"],"Exact approved Nile PNG checksum mismatch"
    sprite=Image.open(BytesIO(raw)).convert("RGBA")
    assert sprite.size==(660,2443)
    heights=metadata["tile_heights"]
    assert len(heights)==8 and sum(heights)==sprite.height
    TILES.mkdir(parents=True,exist_ok=True)
    splits=[];y=0
    for i,h in enumerate(heights,1):
        p=sprite.crop((0,y,sprite.width,y+h))
        p.save(TILES/f"nile_joins_{i:02}.png")
        splits.append(p)
        y+=h
    joins=[]
    for a,b in zip(splits,splits[1:]):
        result=ImageChops.difference(a.crop((0,a.height-1,a.width,a.height)),
                                     b.crop((0,0,b.width,1))).getbbox()
        joins.append(result is None)
    assert all(joins),"Original sprite joins differ after decoding"

    atlas=Image.open(BASE).convert("RGB")
    assert atlas.size==EXPECTED,f"Print canvas dimensions changed {atlas.size}"
    painted=sprite.resize((round(sprite.width*S),round(sprite.height*S)),
                          Image.Resampling.LANCZOS)
    copy=atlas.convert("RGBA")
    copy.alpha_composite(painted,(X,Y))
    combined=copy.convert("RGB")
    REPORT.mkdir(parents=True,exist_ok=True)
    filename=REPORT/"outremer-print-canvas-nile-eight-placed.jpg"
    combined.save(filename,quality=93,subsampling=0)
    before=atlas.crop(CROP)
    after=combined.crop(CROP)
    margin,header=18,58
    w,h=before.size
    comparison=Image.new("RGB",(2*w+3*margin,h+header+2*margin),(244,232,206))
    comparison.paste(before,(margin,header+margin))
    comparison.paste(after,(w+2*margin,header+margin))
    d=ImageDraw.Draw(comparison)
    d.text((margin,16),"BEFORE — CURRENT ATLAS EGYPT INSET",fill=(51,42,32))
    d.text((w+2*margin,16),"AFTER — 8 ORIGINAL JOINED NILE TILES",fill=(51,42,32))
    detail=REPORT/"egypt-nile-joined-eight-before-after.jpg"
    comparison.save(detail,quality=93)
    qa={
        "status":"visual_review_candidate_not_production_approved",
        "source_atlas":BASE.relative_to(ROOT).as_posix(),
        "source_art":ENCODED.relative_to(ROOT).as_posix(),
        "source_sha256_verified":True,
        "original_png_sha256":digest,
        "tile_count":8,
        "joined_edges_exact":joins,
        "decoded_png_directory":TILES.relative_to(ROOT).as_posix(),
        "placement_at_map_preview_resolution":{"x":X,"y":Y,"uniform_scale":S,
                                            "width":painted.width,"height":painted.height},
        "map_preview_dimensions":list(EXPECTED),
        "full_print_canvas_preview":filename.relative_to(ROOT).as_posix(),
        "detail_comparison":detail.relative_to(ROOT).as_posix(),
        "rotation_degrees":0,"mirrored":False,
        "nonuniform_scale":False,"production_composite_modified":False,
        "limitation":"Placed at the approved interactive preview position; matching the geographic Nile's complete meanders requires further segmented fitting or repainting, not warping."
    }
    (REPORT/"placement-qa.json").write_text(json.dumps(qa,indent=2)+"\n")
    print("PRINT CANVAS NILE EIGHT JPG:",filename)
    print("EXACT PNG HASH:",digest)
    print("JOINS ALL EXACT:",all(joins))

if __name__=="__main__":main()
