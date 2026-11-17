#!/usr/bin/env python3
"""EGYPT-ONLY painted Nile corridor proof (no full-atlas modifications).

Reads the COMMITTED current atlas JPEG and georeferenced Nile centerlines,
enlarges the inset 2.4x in isolation, then re-paints water, banks, irrigated
plots, palms, rural villages and symbolic medieval lateen-sail traffic.

Geographic rule: source centerline vertices are unchanged. Exaggeration is
perpendicular to river course only: water width, farming fringe, boat scale.
This is an illustrated settlement/landscape review, NOT a cadastral survey.
"""
from __future__ import annotations
import json
import math
import random
from pathlib import Path
from collections import Counter
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PIL import Image, ImageDraw, ImageFont
import cairo
from shapely.geometry import LineString, box
from rough import Region
import frame as FR
from terrain import RIVERS
from tools.render_nile_delta_waterways import load as load_delta

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/egypt-inset-corridor-review-2026-11-17"
SOURCE=ROOT/"reports/rebuild-2026-11-12/outremer-current-composite.jpg"
ZOOM=2.2
ATLAS_CROP_SCALE=0.30
REG=Region.from_lonlat(FR.INSETS["delta"]["proj"],FR.INSETS["delta"]["ext"],4800)
BOX=(190,13760-REG.h)
FIELDS=((0.31,0.46,0.22),(0.43,0.57,0.27),(0.61,0.61,0.31),
        (0.75,0.64,0.37),(0.46,0.56,0.32),(0.57,0.54,0.27),
        (0.35,0.52,0.35),(0.71,0.55,0.29))
RND=random.Random(20261117)

def bounds():
    x,y=BOX
    return tuple(round(v*ATLAS_CROP_SCALE) for v in
        (x,y,x+REG.w,y+REG.h))

def projected(lon,lat):
    x,y=REG.ll_px(lon,lat)
    return x*ATLAS_CROP_SCALE*ZOOM,y*ATLAS_CROP_SCALE*ZOOM

def lines(g):
    if g.is_empty:return
    if g.geom_type=="LineString":
        if len(g.coords)>1:yield g
    elif hasattr(g,"geoms"):
        for ch in g.geoms:yield from lines(ch)

def source_paths():
    # Southern valley uses Natural Earth. Northern Delta uses mapped modern
    # river vertices with medieval age explicitly NOT asserted.
    lower=box(29.3,27.7,33.1,30.10)
    for idx,g in enumerate(RIVERS):
        if g.intersects(lower):
            for segment in lines(g.intersection(lower)):
                if len(segment.coords)>=2:
                    yield "valley",f"NE-{idx}",segment
    for geom,props in load_delta():
        if props.get("waterway")!="river":continue
        # Do not duplicate lower Natural Earth Nile: OSM north of Cairo.
        for line in lines(geom.intersection(box(29.75,30.075,32.50,31.65))):
            yield "delta",str(props.get("id","OSM")),line

def coordinates(line):
    return [projected(float(x),float(y)) for x,y in line.coords]

def random_val(a,b):
    return RND.uniform(a,b)

def paint(c,rgba):
    c.set_source_rgba(*rgba)

def stroke(c,points,width,color,cap=cairo.LINE_CAP_ROUND):
    if len(points)<2:return
    c.new_path();c.move_to(*points[0])
    for point in points[1:]:c.line_to(*point)
    c.set_line_join(cairo.LINE_JOIN_ROUND);c.set_line_cap(cap)
    c.set_line_width(width);paint(c,color);c.stroke()

def field(c,x,y,angle,w,h,color,rng):
    c.save();c.translate(x,y);c.rotate(angle)
    points=[(-w/2,-h/2),(.48*w,-.47*h),(.52*w,.52*h),(-.49*w,.49*h)]
    c.move_to(*points[0])
    for p in points[1:]:c.line_to(*p)
    c.close_path();paint(c,(*color,.92));c.fill_preserve()
    c.set_line_width(1.6);paint(c,(.35,.32,.16,.65));c.stroke()
    c.save();c.move_to(*points[0])
    for p in points[1:]:c.line_to(*p)
    c.close_path();c.clip()
    for d in range(-10,11):
        k=d*4.3
        if abs(k)>h*.46:continue
        c.move_to(-w*.55,k);c.line_to(w*.55,k+random_val(-1,1))
        c.set_line_width(.95 if d%3 else 1.6)
        paint(c,(.93,.84,.52,.35));c.stroke()
    c.restore();c.restore()

def palm(c,x,y,s,rng):
    # compact painted crown with trunk, no oversized mountain silhouette
    c.save();c.translate(x,y)
    stroke(c,[(0,0),(-2*s,-16*s)],2.3*s,(.42,.27,.13,.88))
    for k in range(9):
        th=(k/9)*math.tau
        a=(-2*s,-17*s)
        b=(a[0]+math.cos(th)*10*s,a[1]+math.sin(th)*6*s)
        stroke(c,[a,((a[0]+b[0])*.5,a[1]-4*s),b],2.4*s,
               (.19+.04*(k%3),.35+.045*(k%2),.17,.93))
    c.restore()

def boats(c,x,y,angle,s,rng):
    # Illustrated generic medieval Nile craft. Vessel type/date provisional.
    c.save();c.translate(x,y);c.rotate(angle)
    c.new_path();c.move_to(-18*s,0)
    c.curve_to(-11*s,8*s,11*s,8*s,20*s,0)
    c.curve_to(11*s,-6*s,-12*s,-6*s,-18*s,0)
    paint(c,(.33,.18,.075,1));c.fill_preserve()
    c.set_line_width(1.6*s);paint(c,(.11,.11,.08,.9));c.stroke()
    stroke(c,[(0,1*s),(0,-29*s)],1.8*s,(.29,.17,.09,1))
    # One triangular tan sail and a dark-painted boom.
    c.new_path();c.move_to(-1*s,-29*s);c.line_to(-2*s,-5*s)
    c.line_to(16*s,-9*s);c.close_path()
    paint(c,(.95,.86,.62,.93));c.fill_preserve()
    c.set_line_width(.75*s);paint(c,(.42,.3,.18,.9));c.stroke()
    stroke(c,[(-2*s,-6*s),(17*s,-8*s)],1.0*s,(.38,.26,.12,.9))
    c.restore()

def village(c,x,y,scale,rng):
    # Tiny mud-brick courtyard cluster, 12th-16th century suggestive
    c.save();c.translate(x,y)
    c.set_source_rgba(.32,.31,.21,.20)
    c.rectangle(-35*scale,11*scale,70*scale,10*scale);c.fill()
    for i in range(7):
        xx=(-32+(i%4)*16+random_val(-3,3))*scale
        yy=(-13+(i//4)*17+random_val(-2,3))*scale
        ww=random_val(9,16)*scale;hh=random_val(11,19)*scale
        paint(c,(.74,.51,.28,.96))
        c.rectangle(xx,yy,ww,hh);c.fill()
        paint(c,(.91,.73,.45,.93))
        c.rectangle(xx-1*scale,yy-3*scale,ww+1.5*scale,5*scale);c.fill()
        paint(c,(.28,.20,.14,1))
        c.rectangle(xx+ww*.39,yy+hh*.60,2.2*scale,hh*.34);c.fill()
    c.restore()

def out_segment(c, line, path_kind, fid, used, qa):
    pixel_path=LineString(coordinates(line))
    if pixel_path.length<12:return
    qa["segments"][path_kind]+=1
    lat0=(line.bounds[1]+line.bounds[3])*.5
    width=23 if path_kind=="valley" else 20
    # Spline vertices exactly represent source geometry. The Cairo overlap
    # area remains in shared source coordinates without invented connectors.
    pts=list(pixel_path.coords)
    # Defer all water to one connected pass after farmland; prevents a
    # field or a later river segment obscuring a previously painted craft.
    qa["_water"].append((pts,width))
    interval=42 if path_kind=="valley" else 62
    distance=26+random_val(0,18)
    while distance<pixel_path.length-18:
        at=pixel_path.interpolate(distance)
        p=pixel_path.interpolate(max(0,distance-5))
        q=pixel_path.interpolate(min(pixel_path.length,distance+5))
        dx=q.x-p.x;dy=q.y-p.y
        n=math.hypot(dx,dy)
        if n<1:distance+=interval;continue
        nx=-dy/n;ny=dx/n
        angle=math.atan2(dy,dx)
        for side in (-1,1):
            # Narrow Nile Valley vs broad Delta fields, both strongly enlarged.
            bands=(36,63,91) if path_kind=="valley" else (35,69,104,139)
            for band,offset in enumerate(bands):
                if RND.random()<(0.90 if path_kind=="valley" else 0.67):
                    xx=at.x+side*nx*(offset+random_val(-6,7))
                    yy=at.y+side*ny*(offset+random_val(-7,7))
                    if xx<30 or yy<30 or xx>qa["width"]-30 or yy>qa["height"]-30:continue
                    # Natural crop fields are not location-of-specific-farm claims.
                    key=(round(xx/28),round(yy/28))
                    if key not in used["field"]:
                        used["field"].add(key)
                        field(c,xx,yy,angle,
                              random_val(31,58),random_val(22,36),
                              FIELDS[RND.randrange(len(FIELDS))],RND)
                        qa["fields"]+=1
                        if RND.random()<.19 and band<2:
                            palm(c,xx+random_val(-9,9),yy-4,
                                 random_val(.75,1.10),RND)
                            qa["palms"]+=1
        if qa["boats"]<45 and RND.random()<.34:
            key=(round(at.x/85),round(at.y/85))
            if key not in used["boat"]:
                used["boat"].add(key)
                qa["_boats"].append((at.x,at.y,angle,random_val(.84,1.20)))
                qa["boats"]+=1
        if qa["villages"]<29 and RND.random()<.22:
            offset=115 if path_kind=="valley" else 175
            side=1 if RND.random()>.5 else -1
            xx=at.x+nx*side*offset;yy=at.y+ny*side*offset
            key=(round(xx/115),round(yy/115))
            if key not in used["village"] and 25<xx<qa["width"]-40 and 25<yy<qa["height"]-40:
                used["village"].add(key)
                qa["_villages"].append((xx,yy,random_val(.85,1.23)))
                qa["villages"]+=1
        distance+=interval*random_val(.83,1.14)

def main():
    if not SOURCE.is_file():
        raise FileNotFoundError(SOURCE)
    full=Image.open(SOURCE).convert("RGB")
    x0,y0,x1,y1=bounds()
    if (x1-x0)<600 or (y1-y0)<450:
        raise AssertionError("Egypt source inset crop is too small")
    raw=full.crop((x0,y0,x1,y1))
    width=round(raw.width*ZOOM);height=round(raw.height*ZOOM)
    base=raw.resize((width,height),Image.Resampling.LANCZOS)
    surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,width,height)
    c=cairo.Context(surface)
    used={"field":set(),"boat":set(),"village":set()}
    qa={"status":"enlarged_egypt_only_illustrated_proof","width":width,"height":height,
        "source_composite":str(SOURCE.relative_to(ROOT)),
        "source_river_geometry":"Natural Earth upstream plus OSM modern Delta river reference",
        "no_new_geographic_river_nodes":True,
        "river_width_exaggerated_for_legibility":True,
        "settlements_and_traffic":"generic symbolic historical reconstruction, not verified exact sites or ship inventories",
        "source_crs":"Lambert conformal conic Egypt inset; projection locations unchanged",
        "segments":Counter(),"fields":0,"palms":0,"boats":0,"villages":0,
        "_water":[],"_boats":[],"_villages":[]}
    # Paint independent water and shores first; farmland parcels, boats and
    # villages are all source-line fitted, with deliberate size exaggeration.
    for category,fid,line in source_paths():
        out_segment(c,line,category,fid,used,qa)
    # Draw entire river source network together over painted field banks;
    # preserve exact line vertices; then make boats and hamlets legible.
    for pts,width in qa.pop("_water"):
        stroke(c,pts,width+13,(.39,.35,.18,.76))
        stroke(c,pts,width+7,(.80,.65,.33,.83))
        stroke(c,pts,width,(.20,.49,.61,.98))
        stroke(c,pts,max(2,width*.27),(.29,.61,.70,.38))
    for xx,yy,size in qa.pop("_villages"):
        village(c,xx,yy,size,RND)
    for xx,yy,angle,size in qa.pop("_boats"):
        boats(c,xx,yy,angle,size,RND)
    qa["layer_order"]="fields > connected Nile water > villages and boats"
    if qa["fields"]<120 or qa["boats"]<8 or qa["villages"]<8:
        raise AssertionError("Egypt inset proof too sparse: "+str(qa))
    surface.flush()
    buf=bytes(surface.get_data())
    rgba=Image.frombuffer("RGBA",(width,height),buf,"raw","BGRA",0,1).copy()
    bg=Image.alpha_composite(base.convert("RGBA"),rgba).convert("RGB")
    OUT.mkdir(parents=True,exist_ok=True)
    proof=OUT/"egypt-inset-illustrated-river-proof.jpg"
    bg.save(proof,quality=94,subsampling=0)
    # Separate crops demonstrate field furrows and traffic at their intended size.
    for name,point in (
        ("valley", (31.35,28.85)),
        ("cairo", (31.18,30.08)),
        ("delta", (31.12,31.12))
    ):
        px,py=projected(*point)
        span=min(620,width*.43)
        left=max(0,min(width-round(span),round(px-span/2)))
        top=max(0,min(height-round(span*.73),round(py-span*.365)))
        crop=bg.crop((left,top,left+round(span),top+round(span*.73)))
        crop.save(OUT/f"egypt-{name}-detail.jpg",quality=94)
    qa["segments"]=dict(qa["segments"])
    qa["source_crop_pixels"]=[x0,y0,x1,y1]
    qa["proof_image"]=str(proof.relative_to(ROOT))
    qa["geographic_seam_verified"]=False
    qa["historical_field_boundaries_verified"]=False
    qa["production_approved"]=False
    (OUT/"egypt-inset-proof-qa.json").write_text(json.dumps(qa,indent=2)+"\n")
    print("EGYPT PROOF",json.dumps(qa))
if __name__=="__main__":main()
