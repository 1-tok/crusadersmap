#!/usr/bin/env python3
"""Build evidence-based Dead Sea shoreline QA crop from current actual atlas.

This does not repaint, clip, or modify the approved Dead Sea asset.
"""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"reports/rebuild-2026-11-12/outremer-current-composite.jpg"
OUT=ROOT/"reports/dead-sea-review"
PROJ="+proj=lcc +lat_1=30 +lat_2=36.5 +lat_0=33.2 +lon_0=35.9 +datum=WGS84 +units=m"
BBOX=(35.23,30.97,35.82,31.94)
W,H=10800,14400
X0,X1=-486000,170000
Y0,Y1=-345000,530000

def main():
    if not SOURCE.is_file():
        raise FileNotFoundError("Full atlas missing; cannot fabricate QA result")
    OUT.mkdir(parents=True,exist_ok=True)
    im=Image.open(SOURCE).convert("RGB")
    tr=Transformer.from_crs("EPSG:4326",PROJ,always_xy=True)
    def pixel(lon,lat):
        x,y=tr.transform(lon,lat)
        return ((x-X0)/(X1-X0)*im.width,(Y1-y)/(Y1-Y0)*im.height)
    west,south,east,north=BBOX
    positions=[]
    for i in range(101):
        t=i/100
        positions.extend((pixel(west+(east-west)*t,south),pixel(west+(east-west)*t,north),
             pixel(west,south+(north-south)*t),pixel(east,south+(north-south)*t)))
    bounds=[max(0,int(min(x for x,y in positions))-25),max(0,int(min(y for x,y in positions))-25),
      min(im.width,int(max(x for x,y in positions))+26),min(im.height,int(max(y for x,y in positions))+26)]
    x0,y0,x1,y1=bounds
    if x1-x0<100 or y1-y0<100:raise ValueError("Bad projected Dead Sea window")
    crop=im.crop(tuple(bounds))
    crop.save(OUT/"dead-sea-actual-map-crop.png")
    # Nearest-neighbor enlarges the existing pixels for seam inspection; does not
    # imply more resolution in the original rebuild.
    zoom=crop.resize((crop.width*3,crop.height*3),Image.Resampling.NEAREST)
    zoom.save(OUT/"dead-sea-inspection-3x.png")
    # Annotate river inlet area for focused visual comparison, not accuracy certification.
    annotated=crop.copy()
    draw=ImageDraw.Draw(annotated)
    lon,lat=35.545,31.775
    px,py=pixel(lon,lat)
    cx,cy=round(px-x0),round(py-y0)
    draw.ellipse((cx-9,cy-9,cx+9,cy+9),outline=(230,35,30),width=3)
    draw.line((cx,cy,cx+55,cy-32),fill=(230,35,30),width=3)
    draw.text((cx+60,cy-44),"Jordan inlet QA",fill=(230,35,30),stroke_width=2,stroke_fill=(255,255,255))
    annotated.save(OUT/"dead-sea-jordan-inlet-markup.png")
    qa={
      "source":str(SOURCE.relative_to(ROOT)),
      "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
      "source_px":list(im.size),
      "wgs84_review_bbox":list(BBOX),
      "crop_px":bounds,
      "crop_size_px":list(crop.size),
      "scale_note":"3x inspection is nearest-neighbor, not higher source resolution",
      "approved_dead_sea_sprite_modified":False,
      "legacy_dead_sea_ink_suppression_code":"terrain.py",
      "legacy_ink_suppression_present":"35.30 < pg.centroid.x < 35.67" in (ROOT/"terrain.py").read_text(),
      "river_inlet_reference_lonlat":[35.545,31.775],
      "double_coast_visual_verdict":"requires human inspection",
      "river_connection_visual_verdict":"requires human inspection",
      "print_qa_approved":False
    }
    (OUT/"dead-sea-review-report.json").write_text(json.dumps(qa,indent=2)+"\n")
    print(json.dumps(qa,indent=2))

if __name__=="__main__":main()
