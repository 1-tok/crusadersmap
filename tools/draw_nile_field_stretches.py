"""Geo-fitted, highly visible Nile floodplain fields, no invented river paths.

Cultivation is laid out ON BOTH BANKS OF THE EXISTING actual Nile centerlines
(Natural Earth valley / OSM Delta), which gives contiguous painted stretches.
Bank widths are conservative cartographic approximations, NOT cadastral data.
Fields are original flat, plan-view geometric paintings drawn directly as
polygons and crop-row strokes, with gentle warm/cool color alternation.
No shadowed relief, hills, or historical settlement claims.

Two separate controls:
  * upstream: narrowly irrigated ribbons; desert beyond their edges
  * delta: broader cultivated mosaic; reduced density near coast/wetlands
"""
import json
import math
import random
from collections import Counter
from pathlib import Path

import cairo
from shapely.geometry import box, LineString
from tools.lowland_51_review_placer import _clip_real_land

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"reports/nile-delta-terrain-review-2026-11-17/nile-field-stretches-qa.json"

# These are review intervals, not seams in the geographic river geometry.
STRETCHES=(
    ("southern_valley",27.70,28.35),
    ("central_valley",28.35,29.15),
    ("northern_valley",29.15,30.12),
    ("southern_delta",30.12,30.84),
    ("northern_delta",30.84,31.65),
)
# Colors represent greens of planted crops, silt, harvested straw and orchards.
PALETTE=(
    (0.32,0.47,0.22),(0.43,0.55,0.27),(0.52,0.59,0.32),
    (0.61,0.61,0.33),(0.67,0.61,0.38),(0.75,0.65,0.40),
    (0.56,0.52,0.28),(0.47,0.54,0.27),(0.59,0.66,0.39),
    (0.72,0.68,0.46),(0.37,0.50,0.31),(0.69,0.55,0.30),
)
_last={}

def _lines(g):
    if g.is_empty:return
    if g.geom_type=="LineString":
        if len(g.coords)>1:yield g
    elif hasattr(g,"geoms"):
        for part in g.geoms:
            yield from _lines(part)

def _paths(reg):
    from terrain import RIVERS
    from tools.render_nile_delta_waterways import load
    # Include all true upstream Nile centerlines without long invented joins.
    upstream=box(29.45,27.67,33.05,30.102)
    for line in RIVERS:
        if line.intersects(upstream):
            yield "upstream",line.intersection(upstream)
    north=box(29.78,29.98,32.50,31.66)
    for g,p in load():
        if p.get("waterway")=="river" and g.intersects(north):
            yield "delta",g.intersection(north)

def _paint_transition_banks(c, reg):
    """Soft painted floodplain ribbons follow sourced lines, NOT fabricated river art.

    Widths are cartographic approximations. Keep the Giza west bank narrow:
    fields must surrender to the limestone plateau, not carpet the desert.
    These strokes sit beneath the actual river ink and approved PNG panel.
    """
    sections=0
    for category,geom in _paths(reg):
        for source_line in _lines(geom):
            line=LineString([reg.ll_px(x,y) for x,y in source_line.coords])
            if line.length<12:
                continue
            p=0.0
            while p<line.length-1:
                nxt=min(p+15,line.length)
                a=line.interpolate(p)
                b=line.interpolate(nxt)
                middle=line.interpolate((p+nxt)*.5)
                lon,lat=reg.inv.transform(
                    reg.x0+middle.x/reg.w*(reg.x1-reg.x0),
                    reg.y1-middle.y/reg.h*(reg.y1-reg.y0))
                # The bank is a narrow oasis south of Cairo, a broad
                # floodplain in the Delta, with a constrained Giza shoulder.
                if category=="delta":
                    width=105 if lat<30.8 else 142
                else:
                    width=68 if lat<29.8 else 76
                if 29.88<=lat<=30.08 and 31.00<=lon<=31.45:
                    width=37
                # Avoid cutting a hard green stripe at the southern sheet edge.
                south_fade=max(.35,min(1.,(lat-27.70)/.12))
                c.new_path()
                c.move_to(a.x,a.y)
                c.line_to(b.x,b.y)
                c.set_line_cap(cairo.LINE_CAP_ROUND)
                c.set_line_width(width*south_fade)
                c.set_source_rgba(.48,.55,.28,.17 if category=="upstream" else .12)
                c.stroke()
                sections+=1
                p=nxt
    return sections


def _field(c, x,y,angle,length,depth,color,seed):
    rnd=random.Random(seed)
    c.save()
    c.translate(x,y)
    c.rotate(angle)
    # Parcel is intentionally flat and has no top-facing hill silhouette.
    c.new_path()
    j0=rnd.uniform(-1.7,1.7);j1=rnd.uniform(-1.7,1.7)
    points=[(-length*.51+j0,-depth*.49),
            (length*.49+j1,-depth*.47),
            (length*.51-j0,depth*.48),
            (-length*.50-j1,depth*.49)]
    c.move_to(*points[0])
    for pt in points[1:]:c.line_to(*pt)
    c.close_path()
    c.set_source_rgba(*color,.87)
    c.fill_preserve()
    c.set_source_rgba(.34,.36,.21,.50)
    c.set_line_width(1.15)
    c.stroke()
    c.save()
    c.new_path()
    c.move_to(*points[0])
    for pt in points[1:]:c.line_to(*pt)
    c.close_path();c.clip()
    # Furrows and alternating crop rows are visible at 0.30 preview scale.
    mode=rnd.randrange(3)
    if mode==0:
        for v in range(-11,12):
            xx=v*3.8
            if abs(xx)>length*.46:continue
            c.move_to(xx,-depth*.62);c.line_to(xx+2.0,depth*.62)
            c.set_source_rgba(.88,.80,.48,.52)
            c.set_line_width(.95);c.stroke()
    else:
        for v in range(-10,11):
            yy=v*3.6
            if abs(yy)>depth*.45:continue
            c.move_to(-length*.58,yy)
            c.line_to(length*.58,yy+.6)
            c.set_source_rgba(.92,.85,.54,.45 if mode==1 else .29)
            c.set_line_width(1.25);c.stroke()
    c.restore()
    c.restore()

def draw(c,terrain,reg,edition):
    global _last
    if edition!="colour":
        _last={"status":"not_applied_to_monochrome"}
        return
    rnd=random.Random(118020261117)
    rows=[]
    stats=Counter()
    segments=0
    for category,g in _paths(reg):
        for geom in _lines(g):
            line=LineString([reg.ll_px(x,y) for x,y in geom.coords])
            if line.length<13:continue
            segments+=1
            # Avoid a visually tiny palette: 3-5 plots per natural river turn.
            interval=31 if category=="upstream" else 34
            position=rnd.uniform(6,min(25,line.length*.2))
            while position<line.length-5:
                pre=line.interpolate(max(0,position-5))
                post=line.interpolate(min(line.length,position+5))
                dx=post.x-pre.x;dy=post.y-pre.y
                norm=math.hypot(dx,dy)
                if norm<1e-6:
                    position+=interval;continue
                nx=-dy/norm;ny=dx/norm
                tangent=math.atan2(dy,dx)
                spot=line.interpolate(position)
                lon,lat=reg.inv.transform(
                    reg.x0+spot.x/reg.w*(reg.x1-reg.x0),
                    reg.y1-spot.y/reg.h*(reg.y1-reg.y0))
                if not 27.70<=lat<=31.65:
                    position+=interval;continue
                # Broad northern marsh fringe: do not carpet wetlands with farms.
                density=.46 if lat>=31.29 else .83 if category=="delta" else .93
                # South of Cairo a short ribbon follows the alluvial valley.
                # North of Cairo plots may run more widely between branches.
                distances=(20,48) if category=="upstream" else (22,54,84)
                for side in (-1,1):
                    for band,dist in enumerate(distances):
                        if rnd.random()>density*(1-.09*band):continue
                        offset=dist+rnd.uniform(-5,5)
                        x=spot.x+nx*side*offset
                        y=spot.y+ny*side*offset
                        if not (5<x<reg.w-5 and 5<y<reg.h-5):
                            continue
                        # Giza plateau is WEST of the river. Keep mapped
                        # limestone/desert from acquiring invented fields.
                        parcel_lon,parcel_lat=reg.inv.transform(
                            reg.x0+x/reg.w*(reg.x1-reg.x0),
                            reg.y1-y/reg.h*(reg.y1-reg.y0))
                        if (29.90<=parcel_lat<=30.08 and parcel_lon<31.18):
                            continue
                        # These parcels have a flat painted outline, not sprite hills.
                        length=rnd.uniform(26,43) if band==0 else rnd.uniform(29,53)
                        depth=rnd.uniform(18,30) if category=="upstream" else rnd.uniform(20,38)
                        paint=PALETTE[rnd.randrange(len(PALETTE))]
                        rows.append((x,y,tangent,length,depth,paint,rnd.randrange(1_000_000_000),lat,category))
                        for name,lo,hi in STRETCHES:
                            if lo<=lat<hi:
                                stats[name]+=1
                                break
                position+=interval*rnd.uniform(.78,1.23)
    if not rows:
        raise AssertionError("No geofitted Nile farm fields generated")
    c.save()
    try:
        # Exact mapped coastline and lakes, never sea, no overlaid new hills.
        _clip_real_land(c,reg,terrain.mpp)
        painted_bank_sections=_paint_transition_banks(c,reg)
        for x,y,angle,length,depth,color,seed,lat,category in rows:
            _field(c,x,y,angle,length,depth,color,seed)
    finally:
        c.restore()
    if any(stats[name]<12 for name,_,_ in STRETCHES):
        raise AssertionError("Nile stretch lost field coverage: "+str(stats))
    _last={
        "status":"painted_geofitted_floodplain_review",
        "source":"existing Natural Earth Nile trunk and mapped OSM Delta river segments",
        "preview_scale_field_readability":"parcel shapes and crop furrows designed for atlas at 0.30",
        "fields_painted":len(rows),
        "geography_fitted_painted_bank_sections":painted_bank_sections,
        "giza_west_bank_rule":"no parcels west of 31.18 E between 29.90 and 30.08 N; narrowed painted transition",
        "southward_limit":"27.7 N inset edge; Valley of the Kings near 25.7 N is outside this frame",
        "extension_status":"continuous source-aligned visual bank treatment; NOT additional approved original PNG panels",
        "source_geometries":segments,
        "stretches":[{"name":name,"latitude_range":[lo,hi],
                      "painted_fields":stats[name]} for name,lo,hi in STRETCHES],
        "river_centerlines_modified":False,
        "coastline_clip":"land-minus-lakes",
        "width_historical_certification":False,
        "river_seam_certified":False,
        "terrain_style":"flat fields; no relief sprites",
        "rendered_layer":"below existing Nile vector and water texture, below cities and labels",
    }
    return _last

def save_report():
    if not _last:
        raise AssertionError("Nile field stretch drawing did not execute")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(_last,indent=2)+"\n")
