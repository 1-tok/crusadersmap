"""Produce a reproducible, REVIEW-ONLY 1180 sprite composite and QA register.

This proof uses the existing full-sheet colour base, not the final ink/label
separation. It does not confer historical, phase, native-DPI, or print approval.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw
import frame
from sprite_geometry import sheet_anchor

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"data/sprites"
PREV=ROOT/"previews"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def normalise(p):
    return str(p).strip().lower().replace(" ", "-")

def select(year=1180, include_review=True):
    standard=read(BASE/f"placements-{year}.geojson")["features"]
    records={}
    held=[]
    for f in standard:
        p=f["properties"]
        if p.get("approval_for_placement") is False or p.get("period_1180_eligible") is False:
            held.append({"id":f.get("id"),"reason":"not approved or period-ineligible"})
            continue
        site=normalise(p["site_id"])
        records.setdefault(site,{"feature":f,"source":"standard"})
    if include_review:
        for f in read(BASE/f"placements-review-{year}.geojson")["features"]:
            p=f["properties"]
            if not (p.get("approval_for_review_placement") and p.get("default_visible")):
                continue
            # Conservative: no implicit date assumptions for a strict 1180 proof.
            if p.get("depiction_year") != year:
                held.append({"id":f.get("id"),"reason":"missing or incompatible depiction_year"})
                continue
            if p.get("period_1180_eligible") is False:
                held.append({"id":f.get("id"),"reason":"1180-ineligible"})
                continue
            site=normalise(p["site_id"])
            # Explicitly-dated review artwork replaces standard artwork at same site.
            records[site]={"feature":f,"source":"review"}
    return list(records.values()),held

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--year",type=int,default=1180)
    ap.add_argument("--width",type=int,default=2700)
    ap.add_argument("--standard-only",action="store_true")
    args=ap.parse_args()
    if args.year != 1180:
        raise SystemExit("This audited proof is intentionally restricted to 1180")
    PREV.mkdir(exist_ok=True)
    source_map=PREV/"crusader-stage3c-colour.jpg"
    if not source_map.is_file():
        raise SystemExit(f"Missing existing colour map base: {source_map}")
    records,held=select(args.year,not args.standard_only)
    scale=args.width/frame.W
    H=round(frame.H*scale)
    with Image.open(source_map) as base:
        page=base.convert("RGBA").resize((args.width,H),Image.Resampling.LANCZOS)
    rendered=[]
    failures=[]
    anchors=[]
    for item in sorted(records,key=lambda r: -r["feature"]["geometry"]["coordinates"][1]):
        f=item["feature"];p=f["properties"]
        asset=p.get("asset_path") if item["source"]=="review" else "data/sprites/"+p["asset"]
        filename=ROOT/asset
        if not filename.is_file():
            failures.append({"id":f.get("id"),"reason":"missing PNG","path":asset})
            continue
        region=p.get("map_region","main")
        try:
            px,py=sheet_anchor({"coordinates":f["geometry"]["coordinates"],"map_region":region})
        except Exception as ex:
            failures.append({"id":f.get("id"),"reason":"projection failure","error":str(ex)})
            continue
        if not (0 <= px < frame.W and 0 <= py < frame.H):
            failures.append({"id":f.get("id"),"reason":"anchor out of sheet"})
            continue
        with Image.open(filename) as src:
            if src.mode != "RGBA":
                failures.append({"id":f.get("id"),"reason":"not RGBA","path":asset})
                continue
            width=(p.get("display_width_units") or 512)*scale
            w=max(1,round(width)); h=max(1,round(w*src.height/src.width))
            im=src.resize((w,h),Image.Resampling.LANCZOS)
        ax,ay=p.get("anchor_normalized",[.5,.95])
        x=round(px*scale-ax*w)
        y=round(py*scale-ay*h)
        # A sprite can cross the frame boundary even if its anchor is within it.
        if x<0 or y<0 or x+w>args.width or y+h>H:
            failures.append({"id":f.get("id"),"reason":"sprite footprint clips sheet","path":asset,
                             "rect":[x,y,x+w,y+h]})
        page.alpha_composite(im,(x,y))
        anchors.append((round(px*scale),round(py*scale)))
        rendered.append({"id":f.get("id"),"name":p.get("name"),
                         "site_id":p.get("site_id"),"asset":asset,
                         "source":item["source"],"anchor_px":[round(px),round(py)],
                         "pixel_footprint":[x,y,x+w,y+h]})
    # Deliberately avoid projecting labels as new proof of phase accuracy.
    name="crusader-1180-integrated-review-proof"
    page.convert("RGB").save(PREV/f"{name}.jpg",quality=91,subsampling=0)
    qa={"purpose":"visual integration proof, not production or print approval",
        "map_source":str(source_map.relative_to(ROOT)),
        "year":1180,"dimensions_px":[args.width,H],
        "selected":len(records),"rendered":len(rendered),
        "held":held,"failures":failures,"rendered_assets":rendered,
        "notes":["Sprites overlay the pre-existing colour base; its lettering is not re-layered above sprites.",
                 "Only explicit 1180 review records are included. Undated records are held.",
                 "Visual reconstruction, political boundary dates, heraldry and print resolution need separate review.",
                 "A selected review variant replaces the standard variant with the same normalized site ID."]}
    (PREV/f"{name}.json").write_text(json.dumps(qa,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"1180 proof: {len(rendered)} images painted, {len(held)} review holds, {len(failures)} QA issues")
    print(PREV/f"{name}.jpg")

if __name__=="__main__":
    main()
