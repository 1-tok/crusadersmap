#!/usr/bin/env python3
"""Conservative Cairo/Giza Nile-bank sprite placement review on existing atlas.

Use only committed repository PNGs; never repaint, stretch non-uniformly, or
spread fields into desert. Each opaque pixel MUST lie on the mapped bank within
a narrow alluvial buffer, and never on the mapped river. No production changes.
"""
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt
from shapely.geometry import box

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
SOURCE=ROOT/"reports/rebuild-2026-11-12/outremer-current-composite.jpg"
PACK=ROOT/"data/sprites/nile-ecology-2026-11-17"
OUT=ROOT/"reports/nile-cairo-bank-pilot"

def segments(g):
    if g.is_empty:return
    if g.geom_type=="LineString":
        if len(g.coords)>1:yield g
    elif hasattr(g,"geoms"):
        for v in g.geoms:yield from segments(v)

def main():
    import frame as FR
    from rough import Region
    from terrain import RIVERS
    from tools.render_nile_delta_waterways import load as waterways
    atlas=Image.open(SOURCE).convert("RGB")
    scale=atlas.width/float(FR.W)
    reg=Region.from_lonlat(FR.INSETS["delta"]["proj"],FR.INSETS["delta"]["ext"],3500)
    bx,by=190,13760-reg.h
    rect=(round(bx*scale),round(by*scale),
          round((bx+reg.w)*scale),round((by+reg.h)*scale))
    before=atlas.crop(rect).convert("RGBA")
    W,H=before.size
    assert W>800 and H>1100
    focus=box(30.65,29.75,31.65,30.28)
    paths=[]
    for g in RIVERS:
        if g.intersects(focus):paths.extend(segments(g.intersection(focus)))
    for g,meta in waterways():
        if meta.get("waterway")=="river" and g.intersects(focus):
            paths.extend(segments(g.intersection(focus)))
    mask=Image.new("L",(W,H),0)
    drawer=ImageDraw.Draw(mask)
    anchors=[]
    for g in paths:
        pts=[]
        n=max(2,round(g.length/.002))
        for j in range(n+1):
            lon,lat=g.interpolate(j/n,normalized=True).coords[0]
            xx,yy=reg.ll_px(lon,lat)
            x,y=round(xx*scale),round(yy*scale)
            pts.append((x,y))
            if 29.85<=lat<=30.16 and 31.02<=lon<=31.40 and 10<x<W-10 and 10<y<H-10:
                anchors.append((lon,lat,x,y))
        if len(pts)>1:drawer.line(pts,fill=255,width=9,joint="curve")
    assert anchors,"Missing sourced Cairo Nile centerline"
    channel=np.array(mask)>0
    distances=distance_transform_edt(~channel)
    manifest=json.loads((PACK/"manifest.json").read_text())
    assets=[(PACK/e["file"],e["id"]) for e in manifest["assets"]
            if e["class"]=="delta_farm" and (PACK/e["file"]).is_file()]
    assert len(assets)>=4,"Committed Cairo bank artwork missing"
    after=before.copy()
    occupied=np.zeros((H,W),dtype=bool)
    placements=[]
    # Four small cartographic vignettes, two per bank; not broad terrain fills.
    for i,(goal,side) in enumerate(((30.13,"west"),(30.10,"east"),
                                     (29.98,"west"),(29.94,"east"))):
        nearby=[a for a in anchors if abs(a[1]-goal)<.018]
        if not nearby:continue
        lon,lat,cx,cy=min(nearby,key=lambda a:abs(a[1]-goal))
        file,ident=assets[(i*7)%len(assets)]
        im=Image.open(file).convert("RGBA")
        # 29px at existing 0.30 preview resolution; no giant field panels.
        ww=29
        hh=max(1,round(im.height*ww/im.width))
        im=im.resize((ww,hh),Image.Resampling.LANCZOS)
        raw=np.asarray(im).copy()
        alpha=raw[:,:,3]>36
        candidate=None
        for offset in (10,13,16,19,22):
            xx=cx-ww-offset if side=="west" else cx+offset
            yy=cy-hh//2
            if xx<3 or yy<3 or xx+ww>=W-3 or yy+hh>=H-3:continue
            sl=np.s_[yy:yy+hh,xx:xx+ww]
            distance=distances[sl]
            # Clip to alluvial banks: no painted field farther than 21 px
            # from the river centreline, nor any land ink across water.
            eligible=(distance>=5)&(distance<=21)&(~channel[sl])&(~occupied[sl])
            valid=alpha&eligible
            if valid.sum()<25:continue
            clipped=raw.copy()
            clipped[:,:,3][~eligible]=0
            candidate=(xx,yy,clipped,valid)
            break
        if candidate is None:continue
        xx,yy,clipped,valid=candidate
        sl=np.s_[yy:yy+hh,xx:xx+ww]
        occupied[sl]|=valid
        sprite=Image.fromarray(clipped,"RGBA")
        after.alpha_composite(sprite,(xx,yy))
        placements.append({"id":ident,"source":file.relative_to(ROOT).as_posix(),
            "bank":side,"anchor_lonlat":[round(lon,5),round(lat,5)],
            "pixel_xy":[xx,yy],"width_print_preview_px":ww,
            "visible_opaque_pixels":int(valid.sum()),
            "pixels_over_river":0,"pixels_outside_21px_bank_buffer":0,
            "rotated":False,"mirrored":False,"nonuniform_scale":False})
    assert len(placements)>=2,"Insufficient safe Nile-bank placements; no preview accepted"
    OUT.mkdir(parents=True,exist_ok=True)
    full=atlas.copy()
    full.paste(after.convert("RGB"),rect[:2])
    fullpath=OUT/"cairo-giza-nile-pilot-on-existing-print-canvas.jpg"
    full.save(fullpath,quality=94,subsampling=0)
    # Comparison of the relevant Cairo portion at magnified review resolution.
    yy=[p["pixel_xy"][1] for p in placements]
    x0=max(0,min(p["pixel_xy"][0] for p in placements)-90)
    x1=min(W,max(p["pixel_xy"][0] for p in placements)+150)
    y0=max(0,min(yy)-100);y1=min(H,max(yy)+160)
    l=before.crop((x0,y0,x1,y1)).convert("RGB")
    r=after.crop((x0,y0,x1,y1)).convert("RGB")
    proof=Image.new("RGB",(l.width*4+54,l.height*2+76),(247,238,215))
    proof.paste(l.resize((l.width*2,l.height*2)),(12,58))
    proof.paste(r.resize((r.width*2,r.height*2)),(l.width*2+36,58))
    d=ImageDraw.Draw(proof)
    d.text((12,18),"BEFORE: CURRENT CAIRO MAP",fill=(50,43,35))
    d.text((l.width*2+36,18),"AFTER: CLIPPED COMMITTED NILE BANK SPRITES",fill=(50,43,35))
    detail=OUT/"cairo-giza-nile-pilot-before-after-2x.jpg"
    proof.save(detail,quality=96,subsampling=0)
    report={"status":"review_only_pending_print_scale_and_site_collision_approval",
      "source_canvas":SOURCE.relative_to(ROOT).as_posix(),
      "print_canvas":fullpath.relative_to(ROOT).as_posix(),
      "detail_comparison":detail.relative_to(ROOT).as_posix(),
      "assets_committed":True,"no_new_painting":True,
      "production_composite_unchanged":True,"desert_outside_21px_river_buffer_untouched":True,
      "river_water_pixels_untouched":True,"max_sprite_width_preview_px":29,
      "placement_count":len(placements),"placements":placements,
      "caveat":"Only mapped centreline buffer verified; actual historic floodplain boundaries and site collisions require visual review."}
    (OUT/"placement-qa.json").write_text(json.dumps(report,indent=2)+"\n")
    print("NILE CAIRO PILOT",len(placements),fullpath,detail)

if __name__=="__main__":main()
