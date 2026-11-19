#!/usr/bin/env python3
"""Full-length experimental Nile shoreline reconstruction ON THE REAL ATLAS.

This is a separate review JPG, not a replacement of the production composite.
Zero rotation/mirroring of cutouts. Real Natural Earth/OSM waterway geometry
controls river masking; never connect arbitrary point samples with straight
lines. Coastline morphology is illustrative, not a reconstruction of medieval
land use or historical Nile channel widths.

Uses installed repository Nile-ecology cutouts (not the 29 approval-batch
binaries which are not yet in the repository). Protects previously painted
four-panel Nile source by avoiding its production footprint.
"""
from __future__ import annotations
import json, math, random, sys
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy.ndimage import distance_transform_edt
from shapely.geometry import box

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
SOURCE=ROOT/"reports/rebuild-2026-11-12/outremer-current-composite.jpg"
PACK=ROOT/"data/sprites/nile-ecology-2026-11-17"
OUT=ROOT/"reports/nile-full-corridor-review"
APPROVED_PAINTING=ROOT/"reports/rebuild-2026-11-12/nile-painted-production-placement.json"

ZONES=[
    ("DELTA",30.80,31.68,"delta_marsh"),
    ("SOUTHERN DELTA",30.12,30.80,"delta_farm"),
    ("CAIRO / GIZA",29.70,30.12,"delta_farm"),
    ("MIDDLE EGYPT",27.70,29.70,"nile_farm_upstream"),
    ("UPPER EGYPT",26.30,27.70,"nile_farm_upstream"),
    ("THEBES",25.31,26.30,"nile_farm_upstream")
]
ZONE_RGB=[(82,136,82),(93,141,79),(151,157,83),(132,149,79),(142,138,77),(157,143,77)]
ZONE_DECOR=[(56,116,66),(98,140,63),(154,143,74),(116,130,66),(145,119,62),(157,111,56)]

def _lines(g):
    if g.is_empty:return
    if g.geom_type=="LineString":
        if len(g.coords)>1:yield g
    elif hasattr(g,"geoms"):
        for p in g.geoms:
            yield from _lines(p)

def zone(lat):
    for i,(name,lo,hi,cls) in enumerate(ZONES):
        if lo<=lat<hi:return i
    return None

def main():
    import frame as FR
    from rough import Region
    from terrain import RIVERS
    from tools.render_nile_delta_waterways import load as delta_waterways

    if not SOURCE.exists():
        raise FileNotFoundError("Actual atlas must render before shoreline experiment")
    atlas=Image.open(SOURCE).convert("RGB")
    scale=atlas.width/float(FR.W)
    reg=Region.from_lonlat(FR.INSETS["delta"]["proj"],FR.INSETS["delta"]["ext"],3500)
    bx,by=190,13760-reg.h
    rect=(round(bx*scale),round(by*scale),
          round((bx+reg.w)*scale),round((by+reg.h)*scale))
    before=atlas.crop(rect).convert("RGB")
    W,H=before.size
    if W<800 or H<1100:
        raise AssertionError("Full Nile proof requires actual map-scale Egypt crop")

    # Approximate physical envelope of the already-approved original painting.
    p=json.loads(APPROVED_PAINTING.read_text())
    xpaint,ypaint=p["native_egypt_inset_pixel_xy"]
    pw,ph=p["drawn_dimensions_px"]
    protected=(
      int((xpaint-50)*scale),int((ypaint-50)*scale),
      int((xpaint+pw+50)*scale),int((ypaint+ph+50)*scale)
    )
    protected_mask=np.zeros((H,W),dtype=bool)
    px0,py0,px1,py1=protected
    protected_mask[max(0,py0):min(H,py1),max(0,px0):min(W,px1)]=True

    focus=box(29.5,25.31,33.2,31.68)
    lines=[]
    for geom in RIVERS:
        if geom.intersects(focus):
            lines.extend(_lines(geom.intersection(focus)))
    for geom,meta in delta_waterways():
        if meta.get("waterway")=="river" and geom.intersects(focus):
            lines.extend(_lines(geom.intersection(focus)))
    river_mask=Image.new("L",(W,H),0)
    water_draw=ImageDraw.Draw(river_mask)
    anchors=[]
    for g in lines:
        points=[]
        step=max(1,round(g.length/.005))
        for k in range(step+1):
            lon,lat=g.interpolate(k/step,normalized=True).coords[0]
            xx,yy=reg.ll_px(lon,lat)
            xx=round(xx*scale);yy=round(yy*scale)
            points.append((xx,yy))
            if zone(lat) is not None and 12<=xx<W-12 and 12<=yy<H-12:
                anchors.append((lon,lat,xx,yy))
        if len(points)>1:
            water_draw.line(points,fill=255,width=9,joint="curve")
    if not anchors:
        raise AssertionError("No sourced Nile coordinates in expanded inset")
    channel=np.asarray(river_mask)>0
    distances=distance_transform_edt(~channel)
    ys,xs=np.indices((H,W))
    latitude_grid=np.empty((H,),dtype=float)
    for y in range(H):
        mid_lon,lat=reg.inv.transform(reg.x0+(reg.x1-reg.x0)*.45,
                    reg.y1-(y/scale)/reg.h*(reg.y1-reg.y0))
        latitude_grid[y]=lat
    # Layered, regionally distinct floodplain washes are strictly buffered
    # off the sourced centerlines and protected original panels.
    rng=np.random.default_rng(118020261118)
    n=rng.random((H,W))
    rings=np.zeros((H,W,4),dtype=np.uint8)
    for k,(_,lo,hi,_) in enumerate(ZONES):
        zone_mask=(latitude_grid[:,None]>=lo)&(latitude_grid[:,None]<hi)
        # Contrasting channel-bank widths: broad marsh Delta, narrow Thebes.
        widths=[40,31,18,25,20,14]
        width=widths[k]
        near=(distances>5)&(distances<width)&zone_mask&~protected_mask
        # Reduce the cultivated green close to the west of Giza; preserve desert plateau.
        if k==2:
            near &= (xs>W*.27)
        base=np.array(ZONE_RGB[k],dtype=float)
        variation=(n-.5)*32
        for channel_i in range(3):
            rings[:,:,channel_i][near]=np.clip(base[channel_i]+variation[near],0,255).astype(np.uint8)
        # Spatial falloff softens the desert/oasis transition.
        alpha=np.clip((width-distances)*3.3,0,96)
        rings[:,:,3][near]=alpha[near].astype(np.uint8)

    after=before.convert("RGBA")
    after.alpha_composite(Image.fromarray(rings,"RGBA"))

    # Subtle micro-shoreline treatment, not new watercourse segments:
    # individual reeds, orchard dots, silty strips and sandy banks.
    details=Image.new("RGBA",(W,H),(0,0,0,0))
    dd=ImageDraw.Draw(details)
    count_shore=Counter()
    for k,(_,lo,hi,_) in enumerate(ZONES):
        candidates=np.argwhere(
            (latitude_grid[:,None]>=lo)&(latitude_grid[:,None]<hi)
            &(distances>7)&(distances<([34,25,17,24,18,14][k]))
            &~protected_mask)
        if len(candidates)==0:continue
        indices=rng.choice(len(candidates),size=min(len(candidates),[3400,2200,800,2800,1700,1100][k]),replace=False)
        for row in candidates[indices]:
            y,x=map(int,row)
            if k==0:
                # Wetland reed clusters
                length=int(rng.integers(2,8))
                dd.line((x,y,x+int(rng.integers(-2,3)),y-length),
                        fill=(62,104,61,int(rng.integers(85,175))),width=1)
            elif k in (1,3):
                # Staggered orchard palms, field-bank vegetation and furrows
                radius=int(rng.integers(1,4))
                dd.ellipse((x-radius,y-radius,x+radius,y+radius),
                           fill=(*ZONE_DECOR[k],int(rng.integers(55,135))))
            elif k==2:
                # Cairo plateau: silt-brown/yellow edges
                dd.line((x,y,x+int(rng.integers(2,7)),y),
                        fill=(157,124,63,int(rng.integers(75,150))),width=2)
            else:
                # Upper Egypt dry reeds and sparse cultivated margins
                radius=int(rng.integers(1,3))
                dd.ellipse((x-radius,y-radius,x+radius,y+radius),
                           fill=(*ZONE_DECOR[k],int(rng.integers(55,150))))
            count_shore[ZONES[k][0]]+=1
    after.alpha_composite(details)

    manifest=json.loads((PACK/"manifest.json").read_text())
    pools={}
    for e in manifest["assets"]:
        if e["class"] in ("delta_farm","nile_farm_upstream","delta_marsh"):
            filename=PACK/e["file"]
            if filename.exists():
                pools.setdefault(e["class"],[]).append((filename,e["id"]))
    if any(len(pools.get(cls,[]))<12 for cls in ("delta_farm","nile_farm_upstream","delta_marsh")):
        raise AssertionError("Required diversified source ecology PNGs not installed")

    occupancy=np.zeros((H,W),dtype=bool)
    placements=[]
    counts=Counter()
    rng2=random.Random(11802026)
    # Build successive real-centerline shoreline scenes all the way from
    # Delta to Thebes. The existing approved painting footprint stays untouched.
    targets=np.arange(25.40,31.58,.075)
    for ti,goal in enumerate(targets):
        matches=[pt for pt in anchors if abs(pt[1]-goal)<.028 and
                29.7<pt[0]<33.1]
        if not matches:continue
        # Favor the main inland flow for Upper Egypt, and multiple mapped
        # distributaries for the northern Delta; do not draw invented joins.
        if goal<30.12:
            matches.sort(key=lambda a:abs(a[1]-goal)+abs(a[0]-31.2)*.011)
            sample=matches[0]
        else:
            sample=matches[(ti*17)%len(matches)]
        lon,lat,cx,cy=sample
        z=zone(lat)
        if z is None:continue
        cls=ZONES[z][3]
        for side in ("west","east"):
            bank_entries=pools[cls]
            # Cycle through all sources rather than repeating same stamps.
            name_id=(ti*7+(side=="east")*13)%len(bank_entries)
            file,sprite_id=bank_entries[name_id]
            spr=Image.open(file).convert("RGBA")
            target_width=([104,112,81,91,86,75][z])+((ti*19)%17)-8
            hh=max(1,round(spr.height*target_width/spr.width))
            spr=spr.resize((target_width,hh),Image.Resampling.LANCZOS)
            alpha=np.asarray(spr.getchannel("A"))>40
            # In map projection longitude E corresponds to x-right for all zones.
            found=None
            for margin in range(19,170,9):
                x0=cx-target_width//2+(-margin if side=="west" else margin)
                y0=cy-hh//2+(ti%3-1)*6
                if x0<4 or y0<4 or x0+target_width>W-4 or y0+hh>H-4:
                    continue
                sl=np.s_[y0:y0+hh,x0:x0+target_width]
                river_pixels=channel[sl]
                if np.any(alpha&river_pixels):continue
                if np.any(alpha&protected_mask[sl]):continue
                if np.any(alpha&occupancy[sl]):continue
                found=(x0,y0)
                occupancy[sl] |= alpha
                break
            if found:
                after.alpha_composite(spr,found)
                placements.append({
                  "asset":sprite_id,"source":file.relative_to(ROOT).as_posix(),
                  "zone":ZONES[z][0],"side":side,
                  "river_anchor_lonlat":[round(lon,5),round(lat,5)],
                  "xy_preview_px":list(found),"width_preview_px":target_width,
                  "rotation_degrees":0,"mirror":False,
                  "nonuniform_scaling":False,"river_overlap_pixels":0,
                  "approved_panel_overlap_pixels":0
                })
                counts[ZONES[z][0]]+=1
    # More than the prior experiment's sixteen cutouts, distributed by zone.
    if len(placements)<48:
        raise AssertionError("Nile full-corridor varied review too sparse: %s" % len(placements))
    if counts["THEBES"]<2 or counts["MIDDLE EGYPT"]<8 or counts["SOUTHERN DELTA"]<3:
        raise AssertionError("Some Nile zones lack bank-art coverage: "+str(counts))
    gap,banner=20,66
    visual=Image.new("RGB",(2*W+gap*3,H+gap*2+banner),(246,238,218))
    visual.paste(before,(gap,gap+banner))
    visual.paste(after.convert("RGB"),(W+2*gap,gap+banner))
    title=ImageDraw.Draw(visual)
    title.text((gap,18),"LEFT  |  ACTUAL EXISTING ATLAS",fill=(45,43,36))
    title.text((W+2*gap,18),"RIGHT  |  VARIED NILOTIC SHORELINE REBUILD — REVIEW",fill=(45,43,36))
    OUT.mkdir(parents=True,exist_ok=True)
    final=OUT/"nile-delta-to-thebes-varied-shorelines-before-after.jpg"
    visual.save(final,quality=92)
    # Review must show the ACTUAL complete print-map layout, not an invented
    # atlas concept. Paste this experimental Egypt inset into a copy of the
    # repository-rendered atlas. The committed production composite stays intact.
    full_print_review=atlas.copy()
    full_print_review.paste(after.convert("RGB"),(rect[0],rect[1]))
    full_print_file=OUT/"outremer-print-canvas-nile-review.jpg"
    full_print_review.save(full_print_file,quality=93,subsampling=0)
    if full_print_review.size != atlas.size:
        raise AssertionError("Print-canvas review dimensions changed")
    # A clean full-map view is inadequate for checking small sprite placement.
    # Generate an explicit review proof with markers ON the actual composed
    # print canvas and separate 2x Egypt crops. Do not modify source PNGs.
    locator=full_print_review.copy()
    ld=ImageDraw.Draw(locator)
    numbered=after.convert("RGB").copy()
    nd=ImageDraw.Draw(numbered)
    bounds=[]
    for idx,p in enumerate(placements,1):
        px,py=p["xy_preview_px"]
        pw=p["width_preview_px"]
        with Image.open(ROOT/p["source"]) as original:
            ph=max(1,round(original.height*pw/original.width))
        left,top,right,bottom=px,py,px+pw,py+ph
        bounds.append([left,top,right,bottom])
        # Draw boxes on a separate diagnostic, not on the clean print review.
        color=(166,28,24) if p["side"]=="west" else (22,67,152)
        nd.rectangle((left,top,right,bottom),outline=color,width=3)
        lx=max(0,min(W-31,left))
        ly=max(0,min(H-20,top-20))
        nd.rectangle((lx,ly,lx+31,ly+19),fill=(255,251,226),outline=color,width=2)
        nd.text((lx+4,ly+3),str(idx),fill=color)
        gx,gy=rect[0]+lx,rect[1]+ly
        ld.rectangle((gx,gy,gx+31,gy+19),fill=(255,251,226),outline=color,width=2)
        ld.text((gx+4,gy+3),str(idx),fill=color)
    marked=OUT/"outremer-print-canvas-nile-50-cutout-locators.jpg"
    locator.save(marked,quality=96,subsampling=0)
    detailed=OUT/"nile-50-cutouts-actual-placement-numbered-2x.jpg"
    numbered.resize((W*2,H*2),Image.Resampling.LANCZOS).save(detailed,quality=96,subsampling=0)
    # Untouched sprite compositions at 2x to show their real visual size.
    clean_detail=OUT/"nile-50-cutouts-clean-egypt-2x.jpg"
    after.convert("RGB").resize((W*2,H*2),Image.Resampling.LANCZOS).save(
        clean_detail,quality=96,subsampling=0)
    # Prove that all labels correspond to existing committed source PNGs.
    for p in placements:
        if not (ROOT/p["source"]).is_file():
            raise AssertionError("Missing placed Nile cutout: "+p["source"])
    if len(bounds)!=len(placements):
        raise AssertionError("Nile sprite locator count mismatch")
    report={
      "status":"map_scale_experiment_only_not_production_approved",
      "source_atlas":SOURCE.relative_to(ROOT).as_posix(),
      "preview":final.relative_to(ROOT).as_posix(),
      "full_print_canvas_preview":full_print_file.relative_to(ROOT).as_posix(),
      "numbered_print_canvas":marked.relative_to(ROOT).as_posix(),
      "numbered_nile_detail_2x":detailed.relative_to(ROOT).as_posix(),
      "clean_nile_detail_2x":clean_detail.relative_to(ROOT).as_posix(),
      "visible_placement_locator_count":len(bounds),
      "print_canvas_preview_size_px":list(atlas.size),
      "print_layout_source":"existing 0.30-scale actual atlas; not a replacement print master",
      "river_source":"Natural Earth centerlines and mapped OSM Delta waterway lines",
      "approved_four_panel_painting_untouched":True,
      "new_29_png_user_approved_batch_integrated":False,
      "why_not":"approved 29 PNGs remain in conversation archive, not in GitHub repo",
      "applied_source_batch":PACK.relative_to(ROOT).as_posix(),
      "river_sprite_policy":"no raw river-bearing PNG overlay until exact-water geo-fit",
      "opaque_land_pixels_over_river":0,
      "rotation_degrees":0,"mirrored":False,
      "nonuniform_stretch":False,
      "total_bank_cutouts":len(placements),
      "bank_cutouts_per_zone":dict(counts),
      "shoreline_microdetail_per_zone":dict(count_shore),
      "styles":["marsh-reeds","delta-orchards","silt-cairo","cultivated-ribbon","dry-crop-grove","theban-desert-edge"],
      "site_sprites_pending_binary_intake":True,
      "placement_records":placements
    }
    (OUT/"nile-delta-to-thebes-variant-qa.json").write_text(json.dumps(report,indent=2)+"\n")
    print("NILE FULL-LENGTH SHORELINE PROOF",json.dumps({
       "placements":len(placements),"zones":dict(counts),
       "microdetails":dict(count_shore),"file":str(final)}))

if __name__=="__main__":main()
