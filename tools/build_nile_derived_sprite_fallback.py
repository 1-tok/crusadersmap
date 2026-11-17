#!/usr/bin/env python3
"""Deterministic Nile ecology sprite fallback, generated from REPO art only.

The conversation-generated hand-painted PNG ZIP cannot be accessed by GitHub
Actions until the ZIP is uploaded. Generate new *derived* RGBA variations
from the existing committed farmland and wetland artwork so that the Nile
Delta and Valley rebuild can still place diverse legitimate binary sprites.
Prefer the hand-painted pack if its exact uploaded ZIP is present.
Do not misrepresent derived variants as newly painted originals.
"""
from __future__ import annotations
import hashlib
import io
import json
import math
from pathlib import Path
import random
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"data/sprites/nile-ecology-2026-11-17"
ZIP=ROOT/"assets/sprites/incoming/nile_delta_upstream_terrain_sprites_2026-11-17.zip"
REPORT=ROOT/"reports/nile-delta-terrain-review-2026-11-17/derived-art-generation.json"
FARMS=[
    "assets/terrain/river-floodplain-fields.png",
    "assets/terrain/orchard-field-mosaic.png",
    "assets/terrain/levant-farmland.png",
]
MARSH=[
    "data/sprites/terrain-batch06/t06_a12_nile_reed_lily_pool.png",
    "data/sprites/terrain-batch06/t06_a13_delta_broad_reed_mosaic.png",
    "data/sprites/terrain-batch06/t06_b01_delta_marsh_reeds_large.png",
    "data/sprites/terrain-batch06/t06_b02_delta_reed_channels_braided.png",
]
COUNTS=[("delta_farm",27),("nile_farm_upstream",27),
        ("delta_marsh",25),("river_decor_reference",38)]

def variant(source, index, kind):
    rng=random.Random(index*9191+int(hashlib.sha1(kind.encode()).hexdigest()[:8],16))
    src=Image.open(ROOT/source).convert("RGBA")
    bbox=src.getchannel("A").getbbox()
    if bbox:
        src=src.crop(bbox)
    if index%2:
        src=ImageOps.mirror(src)
    if index%3==0:
        src=ImageOps.flip(src)
    # Slightly different crops/shape and tint create repetition-resistant
    # agricultural overlays, not invented historical sites.
    w,h=src.size
    pad=int(min(w,h)*rng.uniform(.0,.055))
    if w>3*pad+10 and h>3*pad+10:
        src=src.crop((pad,0,w-pad,h-max(0,pad//3)))
    scale=rng.uniform(.83,1.12)
    width=int(max(64,min(440,src.width*scale)))
    height=int(max(48,min(300,src.height*width/src.width)))
    src=src.resize((width,height),Image.Resampling.LANCZOS)
    alpha=src.getchannel("A")
    rgb=src.convert("RGB")
    rgb=ImageEnhance.Color(rgb).enhance(rng.uniform(.83,1.25))
    rgb=ImageEnhance.Brightness(rgb).enhance(rng.uniform(.91,1.10))
    rgb=ImageEnhance.Contrast(rgb).enhance(rng.uniform(.91,1.11))
    result=rgb.convert("RGBA")
    result.putalpha(alpha)
    return result

def flat_field_mosaic(index,kind):
    """Original procedural flat PLAN-VIEW fields, no mountains or village roofs.

    Past Nile preview art resembled a carpet of small hills. Use separate
    irregular field polygons, crop rows, thin irrigation ditches and low
    orchard canopies instead. The north-south upstream variant is narrower.
    """
    rng=random.Random(index*17041 + (0 if kind=="delta_farm" else 391))
    upstream=kind=="nile_farm_upstream"
    w,h=(255,300) if upstream else (360,205)
    im=Image.new("RGBA",(w,h),(0,0,0,0))
    dr=ImageDraw.Draw(im,"RGBA")
    mask=Image.new("L",(w,h),0)
    md=ImageDraw.Draw(mask)
    # Irregular feathered landcover boundary, to avoid a tiled rectangle.
    outer=[]
    for p in range(42):
        angle=p*math.tau/42
        jitter=rng.uniform(.86,1.06)
        outer.append((round(w/2+math.cos(angle)*w*.47*jitter),
                      round(h/2+math.sin(angle)*h*.43*jitter)))
    md.polygon(outer,fill=250)
    # Warm irrigated alluvium underneath the fields.
    dr.polygon(outer,fill=(170,158,91,224))
    palettes=[
      (91,133,66),(111,154,79),(141,163,77),(175,156,87),
      (190,163,91),(126,144,67),(113,142,80),(202,180,113),
      (153,172,91),(103,151,93),(191,172,104),(150,136,80)
    ]
    cols=3 if upstream else 4
    rows=5 if upstream else 3
    margin_x=int(w*.10);margin_y=int(h*.11)
    tw=(w-2*margin_x)/cols;th=(h-2*margin_y)/rows
    for row in range(rows):
        for col in range(cols):
            x=margin_x+col*tw
            y=margin_y+row*th
            jx=tw*.13;jy=th*.12
            poly=[
                (int(x+rng.uniform(-jx,jx)),int(y+rng.uniform(-jy,jy))),
                (int(x+tw+rng.uniform(-jx,jx)),int(y+rng.uniform(-jy,jy))),
                (int(x+tw+rng.uniform(-jx,jx)),int(y+th+rng.uniform(-jy,jy))),
                (int(x+rng.uniform(-jx,jx)),int(y+th+rng.uniform(-jy,jy))),
            ]
            color=palettes[(row*cols+col+index*3+rng.randrange(len(palettes)))%len(palettes)]
            dr.polygon(poly,fill=(*color,229),outline=(98,96,62,182),width=2)
            # Alternating sowing directions; short strokes remain inside plot.
            top=poly[0];topright=poly[1];botright=poly[2];botleft=poly[3]
            for j in range(1,7):
                t=j/7
                if (row+col+index)%2:
                    a=(int(top[0]*(1-t)+botleft[0]*t),int(top[1]*(1-t)+botleft[1]*t))
                    b=(int(topright[0]*(1-t)+botright[0]*t),int(topright[1]*(1-t)+botright[1]*t))
                else:
                    a=(int(top[0]*(1-t)+topright[0]*t),int(top[1]*(1-t)+topright[1]*t))
                    b=(int(botleft[0]*(1-t)+botright[0]*t),int(botleft[1]*(1-t)+botright[1]*t))
                rowcol=(min(235,color[0]+26),min(235,color[1]+20),min(210,color[2]+12),155)
                dr.line((a,b),fill=rowcol,width=1 if j%2 else 2)
    # Slender canals trace field boundaries rather than invent major Nile routes.
    if index%3!=0:
        yy=int(h*(.32 + .1*(index%4)))
        pts=[(int(w*.06),yy+7),(int(w*.29),yy+2),(int(w*.56),yy-7),(int(w*.92),yy+4)]
        dr.line(pts,fill=(70,93,71,175),width=6,joint="curve")
        dr.line(pts,fill=(62,125,139,210),width=3,joint="curve")
    # Low orchard canopy viewed from overhead (no hillside silhouette).
    for k in range(15 if upstream else 22):
        x=rng.randrange(margin_x,w-margin_x)
        y=rng.randrange(margin_y,h-margin_y)
        radius=rng.randint(2,5)
        if k%4==0:
            dr.ellipse((x-radius,y-radius,x+radius,y+radius),
                       fill=(57,109,55,192),outline=(97,122,58,140))
        elif k%4==1:
            dr.ellipse((x-radius,y-radius,x+radius,y+radius),
                       fill=(81,121,60,175))
    # Opaque coloured shapes inherit the soft irregular alpha boundary.
    aa=np.asarray(mask.filter(ImageFilter.GaussianBlur(3.0)),dtype=np.uint16)
    image=np.asarray(im,dtype=np.uint16).copy()
    image[...,3]=image[...,3]*aa//255
    return Image.fromarray(image.astype(np.uint8),"RGBA")

def river_variant(index):
    # Transparent actual painted texture fragment, not a map route. The
    # geographic renderer strokes its blue water pixels on precise centerlines.
    rng=random.Random(4000+index)
    w,h=192,136
    a=np.zeros((h,w,4),dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            cx=w/2+13*math.sin(y/28+index*.9)+5*math.sin(y/12+index*.4)
            dist=abs(x-cx)
            half=24+3*math.sin(y/17+index*.7)
            if dist<half:
                depth=max(0,min(1,(half-dist)/9))
                grain=math.sin(x*.16+y*.41+index)*3+rng.random()*7
                a[y,x,0]=int(31+grain+18*(1-depth))
                a[y,x,1]=int(109+grain+8*(1-depth))
                a[y,x,2]=int(155+grain+8*(1-depth))
                a[y,x,3]=int(255*min(1,(half-dist)/3))
    return Image.fromarray(a,"RGBA")

def main():
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    if ZIP.is_file():
        print("NILE: uploaded hand-painted source ZIP exists; skipping derived fallback")
        return
    sprites=OUT/"sprites"
    sprites.mkdir(parents=True,exist_ok=True)
    assetlist=[]
    sources={}
    for kind,count in COUNTS:
        for i in range(1,count+1):
            if kind=="river_decor_reference":
                source="procedural water texture from Nile river class"
                image=river_variant(i)
            elif kind in ("delta_farm","nile_farm_upstream"):
                source="original_procedural_flat_field_mosaic"
                image=flat_field_mosaic(i,kind)
            else:
                collection=MARSH
                source=collection[(i*5+i//len(collection))%len(collection)]
                if not (ROOT/source).is_file():
                    raise FileNotFoundError(source)
                image=variant(source,i,kind)
            rel=f"sprites/{kind}_{i:03d}.png"
            buf=io.BytesIO()
            image.save(buf,format="PNG",optimize=True)
            data=buf.getvalue()
            (OUT/rel).write_bytes(data)
            assetlist.append({
                "id":f"derived_{kind}_{i:03d}",
                "file":rel,"class":kind,
                "source_sheet":source,
                "source_georeferenced":False,
                "generated_from_existing_repo_art":source not in ("original_procedural_flat_field_mosaic","procedural water texture from Nile river class"),
                "flat_planview_no_relief":kind in ("delta_farm","nile_farm_upstream"),
                "sha256":hashlib.sha256(data).hexdigest(),
                "bytes":len(data),"png_size":list(image.size),
                "status":"derived_provisional_map_scale_review"
            })
            sources[source]=sources.get(source,0)+1
    obj={
        "project":"1-tok/crusadersmap",
        "batch":"nile-ecology-derived-2026-11-17",
        "source":"original procedural flat-field drawing, existing repository marsh PNGs and procedural water reference",
        "mode":"REVIEW fallback until original 87 hand-painted PNGs uploaded",
        "cutout_count":len(assetlist),
        "river_integration_rule":"texture only, never georeferenced route; river centerlines come from mapped sources",
        "assets":assetlist,
        "production_approved":False
    }
    (OUT/"manifest.json").write_text(json.dumps(obj,indent=2)+"\n")
    report={"status":"generated_derived_art_and_registered",
       "count":len(assetlist),"counts":{k:n for k,n in COUNTS},
       "source_breakdown":sources,
       "hand_painted_archive_installed":False,"production_approved":False}
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print("NILE DERIVED",json.dumps(report))

if __name__=="__main__":
    main()
