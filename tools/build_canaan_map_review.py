#!/usr/bin/env python3
"""Crop the actual atlas to Canaan and build a diagnostic review companion.

Uses the existing assembled atlas JPEG. Does NOT composite unregistered coastal
sprites into the production image or infer footprints from regional study masks.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports/rebuild-2026-11-12/outremer-current-composite.jpg"
OUT = ROOT / "reports/canaan-coastal-review"
MASK = ROOT / "data/manifests/canaan-coastal-mask-review/mask-build-report.json"
MANIFEST = ROOT / "data/manifests/CANAAN-COASTAL-BATCH37-39-REVIEW-QUEUE-2026-11-13.json"
# Geographic study window intentionally covers shoreline and inland context:
BBOX = (33.95, 30.95, 36.20, 33.70) # WGS84 (west,south,east,north)
PROJ = "+proj=lcc +lat_1=30 +lat_2=36.5 +lat_0=33.2 +lon_0=35.9 +datum=WGS84 +units=m"
X0, X1 = -486000, 170000
Y0, Y1 = -345000, 530000
W, H = 10800, 14400

def font(size):
    paths = [ROOT/"fonts"/"DejaVuSans.ttf",Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
    for p in paths:
        if p.exists():
            return ImageFont.truetype(str(p),size)
    return ImageFont.load_default()

def main():
    if not SOURCE.exists():
        raise FileNotFoundError("Actual atlas absent; refusing to substitute illustrative art")
    OUT.mkdir(parents=True, exist_ok=True)
    src = Image.open(SOURCE).convert("RGB")
    transform = Transformer.from_crs("EPSG:4326",PROJ,always_xy=True)
    sx, sy = src.width/W,src.height/H
    def pixel(lon,lat):
        x,y=transform.transform(lon,lat)
        return ((x-X0)/(X1-X0)*W*sx,(Y1-y)/(Y1-Y0)*H*sy)
    coords=[]
    west,south,east,north=BBOX
    for k in range(51):
        t=k/50
        coords.extend([pixel(west+(east-west)*t,south),pixel(west+(east-west)*t,north),
                       pixel(west,south+(north-south)*t),pixel(east,south+(north-south)*t)])
    x0=max(0,int(min(p[0] for p in coords))-20);y0=max(0,int(min(p[1] for p in coords))-20)
    x1=min(src.width,int(max(p[0] for p in coords))+21);y1=min(src.height,int(max(p[1] for p in coords))+21)
    if x1-x0 < 300 or y1-y0 < 300:
        raise RuntimeError(f"Unexpectedly small Canaan crop: {(x0,y0,x1,y1)}")
    crop=src.crop((x0,y0,x1,y1))
    crop.save(OUT/"canaan-current-map.jpg",quality=94,subsampling=0)
    annotated=crop.copy()
    d=ImageDraw.Draw(annotated,"RGBA")
    mask=json.loads(MASK.read_text())
    colors={"acre_carmel":(235,184,46,255),"sharon_jaffa":(88,175,135,255),"ashkelon_gaza":(225,130,99,255)}
    def local(lon,lat):
        x,y=pixel(lon,lat);return (round(x-x0),round(y-y0))
    for entry in mask["windows"]:
        region=entry["region"]
        a,b,c,e=entry["study_bbox_wgs84"]
        points=[local(a,b),local(c,b),local(c,e),local(a,e)]
        col=colors[region]
        d.line(points+[points[0]],fill=col,width=4,joint="curve")
        label=region.replace("_"," / ").title()
        lx,ly=local(a,e)
        d.rounded_rectangle((lx+6,ly+5,lx+260,ly+40),radius=6,fill=(32,38,40,225))
        d.text((lx+13,ly+10),label,font=font(17),fill=(255,255,255,255))
    annotated.save(OUT/"canaan-coastal-mask-review.jpg",quality=94,subsampling=0)
    manifest=json.loads(MANIFEST.read_text())
    records={"source":"reports/rebuild-2026-11-12/outremer-current-composite.jpg",
      "source_dimensions_px":list(src.size),"study_bbox_wgs84":list(BBOX),
      "crop_source_pixel_box":[x0,y0,x1,y1],"image_dimensions_px":list(crop.size),
      "actual_atlas_crop":True,"new_coastal_assets_composited":False,
      "regional_qa_boxes_are_not_sprite_footprints":True,
      "mask_regions":list(colors),
      "coastal_assets_in_manifest":len(manifest["assets"]),
      "coastal_assets_placed_by_this_script":0,
      "print_approved":False,
      "notes":"Actual current atlas crop and diagnostic regional outlines only. Individual candidate PNG fit, orientation and waterline QA remain pending."}
    (OUT/"review-report.json").write_text(json.dumps(records,indent=2)+"\n")
    (OUT/"README.md").write_text(
      "# Canaan geographic map review\n\n"
      "- `canaan-current-map.jpg`: crop of the repository's **actual assembled atlas**.\n"
      "- `canaan-coastal-mask-review.jpg`: same atlas with **regional study window boxes**, not individual PNG masks.\n"
      "- `review-report.json`: source image and crop provenance.\n\n"
      "**No new Batch 37–39 artwork is force-placed**. Water-bearing Batch 39 remains held, "
      "and current coastlines are not certified as historically precise.\n"
    )
    print(json.dumps(records,indent=2))

if __name__=="__main__":
    main()
