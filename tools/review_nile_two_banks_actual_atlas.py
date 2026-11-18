#!/usr/bin/env python3
"""Review-only Nile experiments on the ACTUAL latest rendered atlas.

Uses the repository's currently available provisional bank PNGs to prove
bank-safe zero-rotation placements. It does NOT substitute these provisional
images for the user's separately approved 29-PNG batch, which must be
ingested independently before production placement. Never edits the atlas.
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import box

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports/rebuild-2026-11-12/outremer-current-composite.jpg"
PACK = ROOT / "data/sprites/nile-ecology-2026-11-17"
OUT = ROOT / "reports/nile-two-bank-target-review"


def _lines(geom):
    if geom.is_empty:
        return
    if geom.geom_type == "LineString":
        if len(geom.coords) > 1:
            yield geom
    elif hasattr(geom, "geoms"):
        for part in geom.geoms:
            yield from _lines(part)


def main():
    import frame as FR
    from rough import Region, RIVERS
    from tools.render_nile_delta_waterways import load as delta_waterways

    if not SOURCE.is_file():
        raise FileNotFoundError("Real rebuilt atlas not available; refusing schematic fallback")
    atlas = Image.open(SOURCE).convert("RGB")
    scale = atlas.width / FR.W
    reg = Region.from_lonlat(FR.INSETS["delta"]["proj"], FR.INSETS["delta"]["ext"], 3500)
    bx, by = 190, 13760-reg.h
    rect = (round(bx*scale), round(by*scale),
            round((bx+reg.w)*scale), round((by+reg.h)*scale))
    if rect[1] < 0 or rect[3] > atlas.height or rect[2] > atlas.width:
        raise AssertionError("Egypt inset outside target atlas: %s" % (rect,))
    before = atlas.crop(rect).convert("RGBA")
    after = before.copy()

    geographic_box = box(29.5, 25.25, 35.2, 31.8)
    river_geoms = []
    for g in RIVERS:
        if g.intersects(geographic_box):
            river_geoms.extend(_lines(g.intersection(geographic_box)))
    for g, properties in delta_waterways():
        if properties.get("waterway") == "river" and g.intersects(geographic_box):
            river_geoms.extend(_lines(g.intersection(geographic_box)))
    centerline_points = []
    mask = Image.new("L", before.size, 0)
    painter = ImageDraw.Draw(mask)
    for g in river_geoms:
        points = []
        step = max(1, int(g.length/.008))
        for k in range(step+1):
            lon, lat = g.interpolate(k/step, normalized=True).coords[0]
            xp, yp = reg.ll_px(lon, lat)
            x = round((bx+xp)*scale-rect[0])
            y = round((by+yp)*scale-rect[1])
            centerline_points.append((lon, lat, x, y))
            points.append((x,y))
        if len(points)>1:
            painter.line(points, fill=255, width=9, joint="curve")
    if not centerline_points:
        raise AssertionError("No geographic Nile linework")

    entries = json.loads((PACK/"manifest.json").read_text())["assets"]
    pool = [(PACK/e["file"], e["class"]) for e in entries
            if e.get("class") in ("nile_farm_upstream", "delta_farm")
            and (PACK/e["file"]).is_file()]
    if len(pool)<2:
        raise AssertionError("Provisional repository bank images missing")
    water = np.asarray(mask)
    latitudes = (25.75,26.6,27.4,28.1,28.9,29.5,30.15,30.75,31.2)
    placements=[]
    for i, lat_goal in enumerate(latitudes):
        possible=[p for p in centerline_points
                  if abs(p[1]-lat_goal)<.08 and
                  29.5 <= p[0] <= 33.0 and
                  10 <= p[2] < before.width-10 and
                  10 <= p[3] < before.height-10]
        if not possible:
            placements.append({"latitude_target":lat_goal,"status":"no_centerline_anchor"})
            continue
        # The Nile is the authority; do not fit a river by rotating a sprite.
        lon,lat,cx,cy=min(possible,key=lambda p:abs(p[1]-lat_goal))
        for side in ("west","east"):
            path, sprite_class = pool[(i*2+(side=="east"))%len(pool)]
            cutout=Image.open(path).convert("RGBA")
            width=82 if lat<30.1 else 94
            height=max(1,round(cutout.height*width/cutout.width))
            cutout=cutout.resize((width,height),Image.Resampling.LANCZOS)
            alpha=np.asarray(cutout.getchannel("A"))>30
            ok=False
            for margin in range(18,210,9):
                x0=cx-width//2+(-margin if side=="west" else margin)
                y0=cy-height//2
                if (x0<4 or y0<4 or
                    x0+width>before.width-4 or y0+height>before.height-4):
                    continue
                if np.any(alpha & (water[y0:y0+height,x0:x0+width]>0)):
                    continue
                after.alpha_composite(cutout,(x0,y0))
                placements.append({
                  "source":str(path.relative_to(ROOT)), "sprite_class":sprite_class,
                  "longitude":round(lon,5),"latitude":round(lat,5),
                  "side":side,"position_px":[x0,y0],
                  "width_px":width,"rotation_degrees":0,"mirrored":False,
                  "nonuniform_deformation":False,"river_overlap_pixels":0,
                  "status":"review_on_real_atlas"})
                ok=True
                break
            if not ok:
                placements.append({"side":side,"latitude_target":lat_goal,
                                   "status":"held_instead_of_crossing_river"})
    successful=[p for p in placements if p["status"]=="review_on_real_atlas"]
    if len(successful)<8:
        raise AssertionError("Bank-safe placements too sparse: %s" % successful)
    # Before and after crops come from the SAME actual atlas at full preview scale.
    gap,banner=18,64
    proof=Image.new("RGB",(before.width*2+3*gap,
                           max(before.height,after.height)+banner+2*gap),
                    (246,239,221))
    proof.paste(before.convert("RGB"),(gap,banner+gap))
    proof.paste(after.convert("RGB"),(before.width+2*gap,banner+gap))
    draw=ImageDraw.Draw(proof)
    draw.text((gap,16),"CURRENT ATLAS — BEFORE",fill=(58,47,32))
    draw.text((before.width+2*gap,16),
              "ACTUAL ATLAS — BANK ART REVIEW (ZERO ROTATION)",fill=(58,47,32))
    OUT.mkdir(parents=True,exist_ok=True)
    image_path=OUT/"nile-both-banks-actual-atlas-before-after.jpg"
    proof.save(image_path,quality=91)
    report={
      "status":"review_not_approved_for_production",
      "source_atlas":SOURCE.relative_to(ROOT).as_posix(),
      "image":image_path.relative_to(ROOT).as_posix(),
      "existing_approved_four_panel_nile_untouched":True,
      "approved_new_29_png_batch_included":False,
      "reason":"29 approved PNGs not available in repository; used existing registered provisional bank cutouts",
      "candidate_placements":len(successful),"placement_audit":placements,
      "rotation_degrees":0,"mirrored":False,
      "sprite_deformation":"uniform_resize_only",
      "river_crossing_rule":"all bank-only candidate opaque pixels rejected when overlapping mapped river centerline buffer",
      "accuracy_limit":"sourced centerline mask; final pixel shoreline and historical placement validation required",
      "target_frame_width":3500,
      "target_frame_latitude_range":[25.3,31.8]
    }
    (OUT/"nile-both-banks-actual-atlas-qa.json").write_text(json.dumps(report,indent=2)+"\n")
    print("Two-bank actual atlas preview:",image_path,"placements:",len(successful))

if __name__=="__main__":
    main()
