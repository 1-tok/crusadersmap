#!/usr/bin/env python3
"""Review eight MATCHING Nile paintings on the EXISTING Outremer print base.

No invented/repainted map, no rotation, no mirroring, no nonlinear warp.
This review is deliberately separate from the production composite. If
the eight binary PNGs are not yet in GitHub, emit a pending report rather
than pretending they have been placed.

Inputs are the eight extracted images nile_joins_01.png ... _08.png,
660 px wide, totaling 2443 px tall. Adjacent sections must be joined in
their original order. Fitting uses geographically sourced Nile centerlines
to choose one UNIFORM scale and x/y translation for the whole strip.
Do not use this proof as an automatic production placement authorization.
"""
from __future__ import annotations
import json
import base64
from io import BytesIO
import sys
import zipfile
import tempfile
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
from shapely.geometry import box

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
OUT=ROOT/"reports/nile-joined-eight-print-review"
ATLAS=ROOT/"reports/rebuild-2026-11-12/outremer-current-composite.jpg"
INPUT_CANDIDATES=[
    ROOT/"data/sprites/nile-joins-batch-02",
    ROOT/"assets/sprites/incoming/nile-joins-batch-02",
    ROOT/"assets/sprites/incoming/nile_joins_batch_02",
    ROOT/"data/sprites/automated-intake/nile-joins-batch-02",
]
REQUIRED=[f"nile_joins_{i:02d}.png" for i in range(1,9)]

def source_path():
    # Prefer unaltered committed binaries, if already present.
    for directory in INPUT_CANDIDATES:
        if all((directory/f).is_file() for f in REQUIRED):
            return directory
    # A single repository-ready ZIP can also be uploaded to incoming. Extract
    # ONLY the eight named files to a temporary directory in the runner:
    # never overwrite production data or mistake other images for approved art.
    archives=[
        ROOT/"assets/sprites/incoming/nile_joins_batch_02_repo_ready.zip",
        ROOT/"assets/sprites/incoming/nile_joins_batch_02.zip",
    ]
    for archive in archives:
        if not archive.is_file():
            continue
        with zipfile.ZipFile(archive) as z:
            prefix="data/sprites/nile-joins-batch-02/"
            names=z.namelist()
            exact=[prefix+f for f in REQUIRED]
            if not all(n in names for n in exact):
                raise AssertionError("Uploaded Nile ZIP missing one or more exact named tiles")
            if len(names)>40 or sum(z.getinfo(n).file_size for n in exact)>35*1024*1024:
                raise AssertionError("Unexpected oversized or crowded Nile ZIP")
            name_manifest=prefix+"manifest.json"
            manifest=None
            if name_manifest in names:
                manifest=json.loads(z.read(name_manifest))
                if len(manifest.get("tiles",[]))!=8:
                    raise AssertionError("Nile ZIP manifest must enumerate all eight tiles")
            dest=ROOT/"out/nile-batch02-review-input"
            dest.mkdir(parents=True,exist_ok=True)
            for i,n in enumerate(exact):
                blob=z.read(n)
                if manifest is not None:
                    meta=manifest["tiles"][i]
                    if meta.get("file")!=REQUIRED[i] or meta.get("sha256")!=hashlib.sha256(blob).hexdigest():
                        raise AssertionError("Nile ZIP manifest digest mismatch: "+REQUIRED[i])
                (dest/REQUIRED[i]).write_bytes(blob)
            return dest
    # Exact artwork was staged via lossless base64 Git blobs to bypass
    # connector binary upload limits. Decode only inside the review runner,
    # verify the PNG checksum, then split along the original pixel boundaries.
    encoded=ROOT/"data/sprites/nile-joins-batch-02/encoded"
    spec=encoded/"manifest.json"
    if spec.is_file():
        meta=json.loads(spec.read_text())
        count=int(meta["parts"])
        if count!=24 or len(meta["tile_heights"])!=8:
            raise AssertionError("Unexpected encoded Nile tile manifest")
        parts=[encoded/f"part-{i:03d}.b64" for i in range(count)]
        if not all(p.is_file() for p in parts):
            raise FileNotFoundError("Encoded Nile PNG Git blobs incomplete")
        raw=base64.b64decode("".join(p.read_text() for p in parts),validate=True)
        if hashlib.sha256(raw).hexdigest()!=meta["original_png_sha256"]:
            raise AssertionError("Original Nile joined PNG sha256 mismatch")
        strip=Image.open(BytesIO(raw)).convert("RGBA")
        if strip.size!=(meta["width"],meta["height"]):
            raise AssertionError("Original Nile painted strip dimensions mismatch")
        if sum(meta["tile_heights"])!=strip.height:
            raise AssertionError("Nile joined tile heights do not total source")
        target=ROOT/"out/nile-batch02-review-input"
        target.mkdir(parents=True,exist_ok=True)
        y=0
        for name,h in zip(REQUIRED,meta["tile_heights"]):
            strip.crop((0,y,strip.width,y+h)).save(target/name,optimize=False)
            y+=h
        return target
    return None

def river_lines(g):
    if g.is_empty:
        return
    if g.geom_type=="LineString" and len(g.coords)>1:
        yield g
    elif hasattr(g,"geoms"):
        for child in g.geoms:
            yield from river_lines(child)

def report(data):
    OUT.mkdir(parents=True,exist_ok=True)
    path=OUT/"nile-joined-eight-qa.json"
    path.write_text(json.dumps(data,indent=2)+"\n",encoding="utf-8")
    print("NILE EIGHT JOIN REVIEW:",json.dumps({
        k:data[k] for k in ("status","input_files_found","preview") if k in data
    }))
    return data

def main():
    directory=source_path()
    if directory is None:
        return report({
            "status":"waiting_for_exact_eight_png_binaries",
            "input_files_found":False,
            "required_files":REQUIRED,
            "searched_paths":[p.relative_to(ROOT).as_posix() for p in INPUT_CANDIDATES],
            "note":"The ZIP is available in ChatGPT, but its binary PNGs are not in this repository. No approximation rendered.",
            "production_composite_modified":False
        })
    pieces=[Image.open(directory/f).convert("RGBA") for f in REQUIRED]
    if len(set(p.width for p in pieces))!=1:
        raise AssertionError("Nile joining tiles have inconsistent width")
    if len(pieces)!=8 or pieces[0].width<200:
        raise AssertionError("Incomplete eight-sprite Nile corridor")
    widths=[p.width for p in pieces]
    # Verify aligned water at every adjacent boundary, not simply that
    # the textures are similar in average color.
    seam=[]
    for i in range(7):
        a=np.asarray(pieces[i])[-1,:,:].astype(np.int16)
        b=np.asarray(pieces[i+1])[0,:,:].astype(np.int16)
        diff=np.abs(a-b)
        seam.append({"join":[i+1,i+2],
                     "mean_abs_rgba_delta":round(float(diff.mean()),3),
                     "pct_exact_pixels":round(float(np.mean(np.all(a==b,axis=1))),4)})
    total_h=sum(p.height for p in pieces)
    strip=Image.new("RGBA",(pieces[0].width,total_h),(0,0,0,0))
    cursor=0
    for p in pieces:
        strip.alpha_composite(p,(0,cursor))
        cursor+=p.height
    if not ATLAS.is_file():
        raise FileNotFoundError("Actual current print-base atlas is absent")
    import frame as FR
    from rough import Region
    from terrain import RIVERS
    from tools.render_nile_delta_waterways import load as delta_waterways

    original=Image.open(ATLAS).convert("RGB")
    ratio=original.width/float(FR.W)
    region=Region.from_lonlat(
        FR.INSETS["delta"]["proj"],FR.INSETS["delta"]["ext"],3500)
    bx,by=190,13760-region.h
    rect=(round(bx*ratio),round(by*ratio),
          round((bx+region.w)*ratio),round((by+region.h)*ratio))
    region_before=original.crop(rect)
    rw,rh=region_before.size
    # Measured main Nile/Delta line geometry. Never draw a fabricated
    # joining line between disconnected geographic source geometries.
    mask=Image.new("L",(rw,rh),0)
    ink=ImageDraw.Draw(mask)
    bounds=box(29.5,25.3,33.3,31.8)
    geometry=[]
    geometry.extend([g for g in RIVERS if g.intersects(bounds)])
    geometry.extend([g for g,props in delta_waterways()
                     if props.get("waterway")=="river" and g.intersects(bounds)])
    for g in geometry:
        for line in river_lines(g.intersection(bounds)):
            coords=[]
            for lon,lat in line.coords:
                x,y=region.ll_px(float(lon),float(lat))
                coords.append((round(x*ratio),round(y*ratio)))
            if len(coords)>1:
                ink.line(coords,fill=255,width=9,joint="curve")
    realriver=np.asarray(mask)>0
    if not realriver.any():
        raise AssertionError("Real source-mapped Nile geometry not available")
    to_real=distance_transform_edt(~realriver)

    # Blue-only extraction of the painted water inside each tile.
    rgb=np.asarray(strip).astype(np.float32)
    blue=(rgb[:,:,3]>80)&(rgb[:,:,2]>rgb[:,:,0]*1.12)&(rgb[:,:,2]>rgb[:,:,1]*1.035)
    center=[]
    for y in range(12,total_h-12,22):
        xs=np.flatnonzero(blue[max(0,y-5):min(total_h,y+6)].any(axis=0))
        if len(xs)>12:
            center.append((int(np.median(xs)),y))
    if len(center)<30:
        raise AssertionError("Blue river centerline could not be recovered from original sprites")

    # Whole eight-tile sheet is kept intact and upright. Try only uniform
    # overall scale and translation; a real mismatch remains visible.
    fits=[]
    for height_fraction in (0.69,0.74,0.79,0.84,0.89,0.94):
        factor=(rh*height_fraction)/total_h
        target_w=round(strip.width*factor)
        target_h=round(strip.height*factor)
        for top_fraction in (0.04,0.08,0.12,0.16,0.20):
            y0=round(rh*top_fraction)
            if y0+target_h>=rh-5:
                continue
            for x0 in range(5,max(6,rw-target_w-5),18):
                samples=[]
                for x,y in center[::3]:
                    tx=round(x0+x*factor)
                    ty=round(y0+y*factor)
                    if 0<=tx<rw and 0<=ty<rh:
                        samples.append(to_real[ty,tx])
                if len(samples)>20:
                    fits.append((float(np.median(samples)),float(np.percentile(samples,90)),
                                 x0,y0,target_w,target_h,factor))
    if not fits:
        raise AssertionError("Could not register the unrotated painted Nile in the actual Egypt inset")
    fits.sort(key=lambda z:(z[0],z[1]))
    median_miss,p90_miss,x0,y0,w,h,factor=fits[0]
    painted=strip.resize((w,h),Image.Resampling.LANCZOS)

    after=region_before.convert("RGBA")
    after.alpha_composite(painted,(x0,y0))
    full=original.copy()
    full.paste(after.convert("RGB"),(rect[0],rect[1]))
    OUT.mkdir(parents=True,exist_ok=True)
    print_preview=OUT/"outremer-print-map-eight-nile-joins-review.jpg"
    full.save(print_preview,quality=93,subsampling=0)

    margin=20;banner=64
    side=Image.new("RGB",(rw*2+margin*3,rh+banner+2*margin),(247,237,217))
    side.paste(region_before,(margin,margin+banner))
    side.paste(after.convert("RGB"),(rw+margin*2,margin+banner))
    draw=ImageDraw.Draw(side)
    draw.text((margin,20),"ORIGINAL PRINT ATLAS / EGYPT INSET",fill=(49,40,34))
    draw.text((rw+margin*2,20),"EIGHT UPRIGHT PAINTED NILE TILES / TRIAL FIT",fill=(49,40,34))
    compare=OUT/"eight-joined-nile-on-actual-atlas-before-after.jpg"
    side.save(compare,quality=92)
    status=("geographic_review_fit_candidate" if p90_miss<=25
            else "visual_only_geographic_mismatch_repaint_to_fit")
    report({
        "status":status,"input_files_found":True,
        "source_directory":directory.relative_to(ROOT).as_posix(),
        "tile_files":REQUIRED,"piece_dimensions_px":[list(p.size) for p in pieces],
        "join_edges":seam,"rotation_degrees":0,"mirror":False,
        "nonuniform_scaling":False,"tile_sequence_unmodified":True,
        "source_river_pixel_samples":len(center),
        "registration":{"x0":x0,"y0":y0,"w":w,"h":h,
                        "uniform_scale":round(factor,6),
                        "median_distance_from_true_Nile_preview_px":round(median_miss,2),
                        "p90_distance_from_true_Nile_preview_px":round(p90_miss,2)},
        "source_atlas":ATLAS.relative_to(ROOT).as_posix(),
        "preview":print_preview.relative_to(ROOT).as_posix(),
        "comparison":compare.relative_to(ROOT).as_posix(),
        "review_only":True,"production_composite_modified":False,
        "warning":"Whole-strip translation+uniform scale cannot match all true river meanders if shape differs. Repaint individual geography-specific joints rather than rotate or warp."
    })

if __name__=="__main__":main()
