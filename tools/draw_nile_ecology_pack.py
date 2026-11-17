"""Painted Nile ecological cutouts placed over geographic land; no rivers invented.

Requires output of tools/install_nile_ecology_pack.py. Fails closed (skips)
when the generated PNG archive is not installed. Independently draws and
clips river texture to sourced Nile lines through the current renderer.
"""
import json
import random
import math
from pathlib import Path
import numpy as np
from shapely.geometry import Point, box
from shapely.ops import unary_union
import cairo
from PIL import Image
from scipy.ndimage import distance_transform_edt
from tools.lowland_51_review_placer import _clip_real_land, _surface

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"data/sprites/nile-ecology-2026-11-17"
OUT=ROOT/"reports/nile-delta-terrain-review-2026-11-17/painted-pack-placement.json"
_surface_buffers=[]
_last={"status":"not_rendered"}
_texture=None

def _manifest():
    file=PACK/"manifest.json"
    if not file.is_file():
        return []
    obj=json.loads(file.read_text())
    entries=obj.get("assets",[])
    if len(entries)<87:
        raise AssertionError("Partially installed Nile ecology pack (needs at least 87 cutouts)")
    for entry in entries:
        if not (PACK/entry["file"]).is_file():
            raise FileNotFoundError("Missing Nile generated PNG "+entry["file"])
    return entries

def _pool(kind):
    return [x for x in _manifest() if x["class"]==kind]

def _choose(candidates,rnd,desired,min_distance_degrees):
    picked=[]
    rnd.shuffle(candidates)
    for lo,la in candidates:
        if len(picked)>=desired:
            break
        if all(math.hypot((lo-x)*math.cos(math.radians(la)),la-y)>min_distance_degrees for x,y in picked):
            picked.append((lo,la))
    return picked

def draw_landcover(c,terrain,reg,edition):
    """Under terrain/rivers and cities; physically clipped to land and lakes."""
    global _last
    _last={"status":"awaiting_generated_sprite_pngs"}
    if edition!="colour":
        return
    entries=_manifest()
    if not entries:
        return
    from terrain import RIVERS
    from shapely.geometry import LineString
    # Real stored Nile trunk is the only source for upstream farm buffers.
    candidates=[g for g in RIVERS if g.intersects(box(28.5,27.6,33.0,30.16))]
    upstream=unary_union(candidates) if candidates else None
    rnd=random.Random(20261117)
    d_farm=[];u_farm=[];marsh=[]
    # Sample the actual latitude/longitude projected terrain grid.
    for iy in range(0,terrain.lh,3):
        for ix in range(0,terrain.lw,3):
            if not terrain.land_l[iy,ix] or terrain.water_l[iy,ix]:
                continue
            lon=float(terrain.lon[iy,ix]);lat=float(terrain.lat[iy,ix])
            if not (27.7<=lat<=31.65):
                continue
            if terrain.dland[iy,ix]<1.2:
                continue
            if 30.07<=lat<=31.43 and (31.16-(lat-30.04)/(31.55-30.04))<=lon<=(31.35+0.75*(lat-30.04)/(31.55-30.04)):
                if lat>=31.08 and terrain.dland[iy,ix]<32:
                    marsh.append((lon,lat))
                elif terrain.fert[iy,ix]>.47:
                    d_farm.append((lon,lat))
            elif upstream is not None and 27.78<=lat<30.07 and 29.5<lon<33.15:
                if Point(lon,lat).distance(upstream)<.09:
                    u_farm.append((lon,lat))
    selected=[
        ("delta_farm",_choose(d_farm,rnd,45,.105),220),
        ("nile_farm_upstream",_choose(u_farm,rnd,35,.095),205),
        ("delta_marsh",_choose(marsh,rnd,19,.115),174),
    ]
    placed=[]
    c.save()
    try:
        _clip_real_land(c,reg,terrain.mpp)
        for kind,positions,base_width in selected:
            pool=[x for x in entries if x["class"]==kind]
            if not pool:
                raise AssertionError("Empty source ecology category "+kind)
            for index,(lo,la) in enumerate(positions):
                art=pool[(index*7+rnd.randrange(len(pool)))%len(pool)]
                path="data/sprites/nile-ecology-2026-11-17/"+art["file"]
                width=round(base_width*rnd.uniform(.84,1.18))
                surf=_surface(path,width)
                px,py=reg.ll_px(lo,la)
                c.save()
                c.translate(px-width*.5,py-surf.get_height()*.68)
                c.set_source_surface(surf,0,0)
                c.get_source().set_filter(cairo.FILTER_BEST)
                c.paint_with_alpha(.82 if kind!="delta_marsh" else .76)
                c.restore()
                placed.append({"class":kind,"asset":art["id"],"lonlat":[round(lo,5),round(la,5)],
                               "width_print_px":width,"coast_clipped":True,
                               "alignment":"ecological_sampling_not_historical_site"})
    finally:
        c.restore()
    counts={kind:sum(x["class"]==kind for x in placed) for kind,_,_ in selected}
    _last={"status":"provisional_generated_paintings_rendered",
           "placed":len(placed),"by_class":counts,
           "geography":"actual coastline and Nile centerline proximity",
           "not_historical_georeferencing_of_individual_paintings":True,
           "river_preset_art_not_accepted_as_waterway_geometry":True,
           "instances":placed}

def _painted_water_pattern():
    """Derive reusable water-only pixels from the generated river paintings.
    
    Water colour is sampled from its source sheet. River curves and seams come
    from real geographic centerlines, NEVER from sprite segment endpoints.
    """
    global _texture
    if _texture is not None:
        return _texture
    entries=_pool("river_decor_reference")
    if not entries:
        return None
    src=np.asarray(Image.open(PACK/entries[2]["file"]).convert("RGBA"),dtype=np.uint8)
    rgb=src[...,:3].astype(np.float32);a=src[...,3]
    # select cool blue river pixels; exclude banks/palms/textured soil
    valid=(a>100)&(rgb[...,2]>rgb[...,0]*1.12)&(rgb[...,2]>rgb[...,1]*1.015)&(rgb[...,2]>72)
    if valid.sum()<250:
        raise AssertionError("River sheet water texture sampling failed")
    # Use nearest sampled water colour for every tile pixel, then blend with
    # local subtle variation without introducing spatially disconnected banks.
    _,indices=distance_transform_edt(~valid,return_indices=True)
    water=rgb[indices[0],indices[1]]
    rgb_im=Image.fromarray(water.astype(np.uint8),"RGB").resize((128,128),Image.Resampling.BICUBIC)
    data=np.asarray(rgb_im,dtype=np.uint8)
    bgra=np.empty((128,128,4),dtype=np.uint8)
    bgra[:,:,:3]=data[:,:,::-1]
    bgra[:,:,3]=255
    backing=bytearray(bgra.tobytes())
    surface=cairo.ImageSurface.create_for_data(backing,cairo.FORMAT_ARGB32,128,128,128*4)
    _surface_buffers.append(backing)
    pattern=cairo.SurfacePattern(surface);pattern.set_extend(cairo.EXTEND_REPEAT)
    _texture=pattern
    return pattern

def stroke_real_rivers(c,reg,river_geometries,width=7.0):
    pattern=_painted_water_pattern()
    if pattern is None:
        return 0
    def lines(g):
        if g.is_empty:return
        if g.geom_type=="LineString":
            yield g
        elif hasattr(g,"geoms"):
            for x in g.geoms:yield from lines(x)
    count=0
    c.save()
    try:
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        c.set_line_join(cairo.LINE_JOIN_ROUND)
        for geom in river_geometries:
            for line in lines(geom):
                pts=[reg.ll_px(float(x),float(y)) for x,y in line.coords]
                if len(pts)<2:continue
                c.new_path();c.move_to(*pts[0])
                for pt in pts[1:]:c.line_to(*pt)
                # Underlying full-width channel has a geographic outline.
                c.set_source_rgba(.15,.39,.52,.74)
                c.set_line_width(width+1.0)
                c.stroke_preserve()
                c.set_source(pattern)
                c.set_line_width(width)
                c.stroke()
                count+=1
    finally:
        c.restore()
    return count

def save_report():
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(_last,indent=2)+"\n")
    return _last
