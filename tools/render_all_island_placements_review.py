#!/usr/bin/env python3
"""Map all non-superseded island candidates for visual approval, not final QA."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/island-review-2026-11-15/all-islands-map"
OUT.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads((ROOT/p).read_text())
old=read("assets/islands.json")
new=read("data/manifests/GREEK-ISLANDS-ALL-ORPHAN-SELECTED-REVIEW-2026-11-15.json")["selected"]
assert len(old)==47 and len(new)==62
assert len({r["subject"].lower() for r in new})==62
frames={"ionian":(18.8,35.5,22.6,40.65),"aegean-north":(22.2,37.45,30.7,41.7),"aegean-south":(22.2,34.25,30.7,37.95)}
W,H=4400,3220
font=ImageFont.load_default()
audit={"selected":62,"previous":47,"drawn":[],"legacy_drawn":[],"missing":[],"image_outputs":[],"mode":"geographic centre artwork draft, not registered coastline or print approval"}
def which(lon,lat):
    return "ionian" if lon<22.2 else "aegean-north" if lat>=37.63 else "aegean-south"
def project(lon,lat,extent):
    w,s,e,n=extent
    return round(60+(lon-w)/(e-w)*(W-120)),round(60+(n-lat)/(n-s)*(H-120))
def land(im,extent):
    try:
        from shapely.geometry import shape,box
        content=read("data/ne_10m_land.geojson")
        area=box(*extent)
        d=ImageDraw.Draw(im)
        def polys(g):
            if g.is_empty:return
            if g.geom_type=="Polygon":yield g
            elif hasattr(g,"geoms"):
                for child in g.geoms:yield from polys(child)
        for feat in content["features"]:
            obj=shape(feat["geometry"])
            if not obj.intersects(area):continue
            for p in polys(obj.intersection(area)):
                xy=[project(x,y,extent) for x,y in p.exterior.coords]
                if len(xy)>2:d.polygon(xy,fill=(194,185,141));d.line(xy,fill=(231,218,171),width=2)
                for hole in p.interiors:
                    xy=[project(x,y,extent) for x,y in hole.coords]
                    if len(xy)>2:d.polygon(xy,fill=(51,155,180))
    except Exception as ex:print("Land outline fallback",ex)
def paste(path,im,xy,maxwidth,maxheight):
    with Image.open(path) as source:art=source.convert("RGBA")
    art.thumbnail((maxwidth,maxheight),Image.Resampling.LANCZOS)
    x,y=xy
    im.paste(art,(int(x-art.width/2),int(y-art.height/2)),art)
    return (int(x-art.width/2),int(y-art.height/2),int(x+art.width/2),int(y+art.height/2))
for region,extent in frames.items():
    im=Image.new("RGB",(W,H),(51,155,180))
    land(im,extent)
    d=ImageDraw.Draw(im)
    for r in old:
        if r["e"]<extent[0] or r["w"]>extent[2] or r["n"]<extent[1] or r["s"]>extent[3]:continue
        path=ROOT/"assets/islands"/r["file"]
        if not path.exists():
            audit["missing"].append({"subject":r["name"],"asset":str(path),"type":"legacy"});continue
        x0,y0=project(r["w"],r["n"],extent)
        x1,y1=project(r["e"],r["s"],extent)
        try:
            with Image.open(path) as src:art=src.convert("RGBA")
            art=art.resize((max(2,x1-x0),max(2,y1-y0)),Image.Resampling.LANCZOS)
            im.paste(art,(x0,y0),art)
            audit["legacy_drawn"].append({"subject":r["name"],"view":region})
        except Exception as ex:audit["missing"].append({"subject":r["name"],"error":str(ex)})
    rects=[]
    for r in new:
        if which(*r["anchor"])!=region:continue
        path=ROOT/r["asset"]
        if not path.is_file():
            audit["missing"].append({"subject":r["subject"],"asset":r["asset"],"type":"new"});continue
        x,y=project(*r["anchor"],extent)
        if not (0<=x<W and 0<=y<H):
            audit["missing"].append({"subject":r["subject"],"error":"outside assigned frame"});continue
        width=148 if r["selection"]=="batch25-31-preferred" else 130 if r["selection"]=="batch03-preferred" else 116
        try:box=paste(path,im,(x,y),width,width)
        except Exception as ex:
            audit["missing"].append({"subject":r["subject"],"error":str(ex)});continue
        collision=sum(box[0]<p[2] and box[2]>p[0] and box[1]<p[3] and box[3]>p[1] for p in rects)
        rects.append(box)
        d.text((box[0],max(42,box[1]-13)),r["subject"][:25],fill="white",font=font,stroke_width=2,stroke_fill=(22,57,75))
        audit["drawn"].append({"subject":r["subject"],"asset":r["asset"],"view":region,"anchor":r["anchor"],"collision_count":collision,"status":"artwork on review map, unregistered silhouette"})
    d.rectangle((0,0,W,39),fill=(28,55,69))
    d.text((14,13),region.upper()+" - ISLAND ART ON MAP FOR APPROVAL (NOT FINAL COASTLINE QA)",fill="white",font=font)
    dest=OUT/(region+"-all-island-sprites-review.jpg")
    im.save(dest,quality=90,optimize=True)
    audit["image_outputs"].append(str(dest.relative_to(ROOT)))
got={r["subject"].lower() for r in audit["drawn"]}
audit["unique_selected_drawn"]=len(got)
audit["remaining_selected"]=[r["subject"] for r in new if r["subject"].lower() not in got]
audit["complete"]=not audit["remaining_selected"]
(OUT/"review-placement-audit.json").write_text(json.dumps(audit,indent=2)+"\n")
(OUT/"README.md").write_text("# Aegean and Ionian painted island map draft\n\n"
    "47 original geographic overlays retained. 62 non-superseded island candidate paintings "
    "selected and assigned to real island centres for provisional visual approval. "
    "They are not yet fitted to exact coastline silhouettes or print approved.\n\n"
    "Selected subjects rendered: "+str(len(got))+"/62. "
    "See review-placement-audit.json for unresolved assets and collisions.\n")
print(json.dumps({"drawn":len(got),"missing":audit["remaining_selected"],"images":audit["image_outputs"]},indent=2))
