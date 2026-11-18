#!/usr/bin/env python3
"""Egypt-only painted bank PNG proof, using genuine binary artwork.

No procedural fields, hill symbols or vector villages. Reads four real
transparent painting PNGs committed under data/sprites/nile-painted-upright...
and places each at an actual Nile centerline anchor without rotation, mirroring
or arbitrary deformation. The existing river is never replaced.
"""
from __future__ import annotations
import hashlib,json,math,random
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from shapely.geometry import LineString
from tools.build_egypt_inset_painted_proof import (
    ROOT,SOURCE,ZOOM,bounds,projected,source_paths,lines,
)
PACK=ROOT/"data/sprites/nile-painted-upright-2026-11-17"
OUT=ROOT/"reports/egypt-nile-real-painted-sprites-review"
ANCHORS=[
    ("leftbank_south_a.png","left",28.23),
    ("rightbank_south_a.png","right",28.23),
    ("leftbank_south_b.png","left",29.00),
    ("rightbank_south_b.png","right",29.00),
]
# Editorial preview scale for a large high-quality Egypt inset (no geographic resize).
BANK_WIDTH=320
WATER_PROTECTION=26

def _river_point_at_lat(geoms,lat):
    """Interpolate the existing Natural Earth Nile through a latitude; no invented bends."""
    matches=[]
    for line in geoms:
        coords=list(line.coords)
        for a,b in zip(coords,coords[1:]):
            if (a[1]<=lat<=b[1] or b[1]<=lat<=a[1]) and abs(b[1]-a[1])>1e-9:
                t=(lat-a[1])/(b[1]-a[1])
                lo=a[0]+t*(b[0]-a[0])
                matches.append((lo,lat))
    if not matches:
        raise AssertionError(f"No existing Nile segment at latitude {lat}")
    # A southern Nile location, away from separate eastern Delta branch records.
    return min(matches,key=lambda p:abs(p[0]-31.1))

def main():
    src=Image.open(SOURCE).convert("RGB")
    x0,y0,x1,y1=bounds()
    region=src.crop((x0,y0,x1,y1))
    width=int(round(region.width*ZOOM))
    height=int(round(region.height*ZOOM))
    if width<2000 or height<1600:raise AssertionError("Unusable Egypt inset")
    before=region.resize((width,height),Image.Resampling.LANCZOS).convert("RGBA")
    paintings=Image.new("RGBA",before.size,(0,0,0,0))
    data=json.loads((PACK/"manifest.json").read_text())
    catalog={a["name"]:a for a in data["assets"]}
    upstream=[g for cat,fid,line in source_paths() if cat=="valley" for g in lines(line)]
    if not upstream:raise AssertionError("Missing Nile Valley geographic source")
    placement=[]
    for name,side,lat in ANCHORS:
        p=PACK/name
        if name not in catalog or not p.is_file():
            raise FileNotFoundError(name)
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        # Main manifest pins original Git blobs, so validate shape and alpha here.
        im=Image.open(p).convert("RGBA")
        if im.getchannel("A").getextrema()[0]!=0:
            raise AssertionError(f"Source PNG must have transparent exterior: {name}")
        im=im.resize((BANK_WIDTH,round(im.height*BANK_WIDTH/im.width)),Image.Resampling.LANCZOS)
        lon,la=_river_point_at_lat(upstream,lat)
        px,py=projected(lon,la)
        # Only move upright. Painting is NOT rotated even if Nile meanders.
        x=round(px-(BANK_WIDTH*.91 if side=="left" else BANK_WIDTH*.09))
        y=round(py-im.height*.5)
        paintings.alpha_composite(im,(x,y))
        placement.append({"asset":name,"side":side,"latitude":lat,
                          "lon":round(lon,6),"river_anchor_px":[round(px,2),round(py,2)],
                          "painting_xy":[x,y],"display_px":list(im.size),
                          "rotation_degrees":0,"mirrored":False,
                          "sha256":actual})
    # Protect ALL mapped waterway paths from being obscured by painted riverbank
    # foliage: a transparent exclusion mask along source river coordinates.
    mask=Image.new("L",(width,height),0);d=ImageDraw.Draw(mask)
    water_segment_count=0
    for category,fid,line in source_paths():
        pts=[projected(float(a),float(b)) for a,b in line.coords]
        if len(pts)<2:continue
        d.line(pts,fill=255,width=WATER_PROTECTION if category=="valley" else 20,joint="curve")
        water_segment_count+=1
    mask=mask.filter(ImageFilter.GaussianBlur(2.0))
    alpha=np.asarray(paintings.getchannel("A"),dtype=np.float32)
    protect=np.asarray(mask,dtype=np.float32)
    protected=np.uint8(np.clip(alpha*(1-protect/255),0,255))
    paintings.putalpha(Image.fromarray(protected,"L"))
    after=Image.alpha_composite(before,paintings).convert("RGB")
    OUT.mkdir(parents=True,exist_ok=True)
    after.save(OUT/"egypt-painted-bank-sprites-trial.jpg",quality=93,subsampling=0)
    # Side by side reveals whether bank sprites are too small or misfit; proof only.
    comp=Image.new("RGB",(before.width*2+60,before.height+74),(238,231,210))
    comp.paste(before.convert("RGB"),(15,50))
    comp.paste(after,(before.width+45,50))
    dd=ImageDraw.Draw(comp);dd.text((15,15),"BEFORE — CURRENT GEOGRAPHIC NILE",fill=(42,44,31))
    dd.text((before.width+45,15),"AFTER — FOUR PAINTED BANK PNGS, UPRIGHT",fill=(42,44,31))
    comp.save(OUT/"egypt-painted-bank-comparison.jpg",quality=90)
    report={
        "status":"painted_sprites_provisional_egypt_only_review",
        "source":"four exact committed RGBA painted PNGs",
        "sprite_count":len(placement),
        "source_geographic_waterway_segments_protected":water_segment_count,
        "sprite_rotation_degrees":0,"mirror_count":0,
        "water_geometry_modified":False,
        "full_map_modified":False,
        "alignment":"real Nile valley centerline intersected at specified latitudes",
        "geographic_seam_certified":False,
        "historical_site_accuracy_certified":False,
        "production_approved":False,
        "placements":placement,
    }
    (OUT/"placement-qa.json").write_text(json.dumps(report,indent=2)+"\n")
    print("EGYPT PAINTED BANK TRIAL:",json.dumps({k:v for k,v in report.items() if k!="placements"}))
if __name__=="__main__":
    main()
