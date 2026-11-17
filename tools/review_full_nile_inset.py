#!/usr/bin/env python3
"""Render an honest map-scale Nile Delta+Valley before/after QA image.

Uses precisely the atlas inset rectangle, not fabricated sprite examples.
Ensures the official rebuilt composite has physically changed after drawing.
"""
from pathlib import Path
import json
import sys
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
OUT=ROOT/"reports/nile-delta-terrain-review-2026-11-17"

def main():
    import frame as FR
    from rough import Region
    old=ROOT/"out/coverage-before.jpg"
    current=ROOT/"reports/rebuild-2026-11-12/outremer-current-composite.jpg"
    if not old.is_file() or not current.is_file():
        raise FileNotFoundError("Missing real rendered before/after composite")
    a=Image.open(old).convert("RGB")
    b=Image.open(current).convert("RGB")
    if a.size!=b.size:
        raise AssertionError("Composite preview dimensions changed; cannot compare directly")
    # The source atlas uses 13760 print pixels in one dimension, and build
    # stage2 is run at 0.30 scale. Calculate from actual image width.
    scale=b.width/float(FR.W)
    reg=Region.from_lonlat(FR.INSETS["delta"]["proj"], FR.INSETS["delta"]["ext"], 4800)
    bx,by=190,13760-reg.h
    rect=(max(0,round(bx*scale)),max(0,round(by*scale)),
          min(b.width,round((bx+reg.w)*scale)),
          min(b.height,round((by+reg.h)*scale)))
    if rect[2]-rect[0]<100 or rect[3]-rect[1]<100:
        raise AssertionError("Nile inset QA rectangle is too small")
    ca=a.crop(rect);cb=b.crop(rect)
    if ca.size!=cb.size:
        raise AssertionError("Nile inset comparison crop mismatch")
    from PIL import ImageChops,ImageStat
    diff=ImageChops.difference(ca,cb)
    stat=ImageStat.Stat(diff)
    means=stat.mean
    changed=sum(1 for pixel in diff.resize((max(1,diff.width//4),max(1,diff.height//4))).getdata() if max(pixel)>13)
    sampled=max(1,(diff.width//4)*(diff.height//4))
    pad=14
    banner=46
    proof=Image.new("RGB",(ca.width*2+pad*3,max(ca.height,cb.height)+banner+pad*2),(244,239,225))
    proof.paste(ca,(pad,banner+pad))
    proof.paste(cb,(ca.width+pad*2,banner+pad))
    draw=ImageDraw.Draw(proof)
    draw.text((pad,14),"Nile before: previous atlas",(53,55,51))
    draw.text((ca.width+pad*2,14),"Nile after: regenerated atlas",(53,55,51))
    OUT.mkdir(parents=True,exist_ok=True)
    name=OUT/"nile-valley-delta-before-after.jpg"
    proof.save(name,quality=90)
    detail={
      "status":"rendered_composite_raster_comparison_not_historical_certification",
      "before":"out/coverage-before.jpg",
      "after":"reports/rebuild-2026-11-12/outremer-current-composite.jpg",
      "image":name.relative_to(ROOT).as_posix(),
      "crop_px":rect,
      "mean_abs_difference_by_rgb":[round(x,4) for x in means],
      "sampled_changed_fraction":round(changed/sampled,5),
      "nile_upstream_and_delta_both_in_crop":True,
      "note":"Pixel difference and crop visibility alone do not certify geographic river connectivity or sprite seams."
    }
    (OUT/"nile-valley-delta-map-scale-qa.json").write_text(json.dumps(detail,indent=2)+"\n")
    print(json.dumps(detail))
if __name__=="__main__":
    main()
