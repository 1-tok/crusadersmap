#!/usr/bin/env python3
"""Cairo–Giza geographical placement-zone REVIEW; no sprite painting or placement.

This deliberately replaces the 21-pixel arbitrary bank buffer with a separately
inspectable geographic alluvial *candidate*, bounded by named geographic
control points. It must be visually/geographically approved before any Nile
bank painting is promoted. Outside this polygon is reserved for future desert
sprites. Historical boundaries are NOT certified.
"""
from __future__ import annotations
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
from shapely.geometry import Polygon,Point,box,mapping
from shapely.ops import unary_union
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
OUT=ROOT/"reports/nile-boundary-review"
MAN=ROOT/"data/manifests/NILE-DESERT-PLACEMENT-NEXT.json"
MAP=ROOT/"reports/rebuild-2026-11-12/outremer-current-composite.jpg"

# Lon/lat candidate control points, ordered north->south. This is a proposed
# illustrated alluvial limit, NOT a claimed surveyed historic floodplain.
# Deliberately west of the river but east of the Giza pyramid plateau.
WEST=[
 (31.02,30.24),(31.06,30.20),(31.11,30.14),(31.13,30.10),
 (31.145,30.06),(31.155,30.02),(31.16,29.98),(31.17,29.94),
 (31.18,29.90),(31.19,29.85),(31.19,29.80)
]
EAST=[
 (31.48,30.24),(31.46,30.20),(31.435,30.14),(31.425,30.10),
 (31.405,30.06),(31.395,30.02),(31.38,29.98),(31.37,29.94),
 (31.36,29.90),(31.35,29.85),(31.34,29.80)
]
BOUNDS=(30.85,29.77,31.63,30.29) # review window only
WEST_PYRAMID=(31.1325,29.9792)   # approximate Giza monument exclusion anchor
SAQQARA=(31.216,29.871)          # approximate monument exclusion anchor

def linework(geom):
    if geom.is_empty:return
    if geom.geom_type=="LineString":
        if len(geom.coords)>1:yield geom
    elif hasattr(geom,"geoms"):
        for g in geom.geoms:yield from linework(g)

def main():
    import frame as FR
    from rough import Region
    from terrain import RIVERS
    from tools.render_nile_delta_waterways import load as delta
    atlas=Image.open(MAP).convert("RGB")
    assert atlas.size==(3240,4320),"Unexpected print-preview dimensions"
    full=Region.from_lonlat(FR.INSETS["delta"]["proj"],FR.INSETS["delta"]["ext"],3500)
    ratio=atlas.width/FR.W
    offset=(190*ratio,(13760-full.h)*ratio)
    def xy(lon,lat):
        x,y=full.ll_px(lon,lat)
        return round(x*ratio+offset[0]),round(y*ratio+offset[1])
    perimeter=Polygon(WEST+list(reversed(EAST)))
    assert perimeter.is_valid and perimeter.area>.001,"Invalid tentative floodplain polygon"
    roi=box(*BOUNDS)
    flood=perimeter.intersection(roi)
    assert not flood.is_empty
    # Preserve Giza plateau and key western monument exclusion zones until
    # site-footprint review; these are *exclusion points*, not ground-truth polygons.
    protected=[{"name":"Giza pyramid plateau","lonlat":list(WEST_PYRAMID),
                "purpose":"no_automatic_green_fields_or_desert_tile_over_monument"},
               {"name":"Saqqara monuments","lonlat":list(SAQQARA),
                "purpose":"no_automatic_terrain_over_monument"}]
    geom=[]
    water_roi=roi
    for g in RIVERS:
        if g.intersects(water_roi):geom.extend(linework(g.intersection(water_roi)))
    for g,p in delta():
        if p.get("waterway")=="river" and g.intersects(water_roi):
            geom.extend(linework(g.intersection(water_roi)))
    assert geom,"No source-mapped Nile segments intersect the Cairo-Giza review"
    river=unary_union(geom)
    # Water zone is an indicative display/placement exclusion around sourced
    # centerlines (not a verified bank-width survey).
    riverzone=river.buffer(.0012).intersection(roi)
    if hasattr(riverzone,"is_valid"):assert riverzone.is_valid
    west_desert=roi.intersection(box(BOUNDS[0],BOUNDS[1],31.26,BOUNDS[3])).difference(flood.union(riverzone))
    east_desert=roi.intersection(box(31.26,BOUNDS[1],BOUNDS[2],BOUNDS[3])).difference(flood.union(riverzone))
    def feature(name,g,role):
        return {"type":"Feature","properties":{"name":name,"role":role,
            "status":"candidate_requires_geographic_visual_approval",
            "geometry_accuracy":"cartographic_only_not_verified_historic_extent"},
            "geometry":mapping(g)}
    collection={"type":"FeatureCollection","name":"Cairo Giza Nile review zones",
        "crs_note":"EPSG:4326 geographic coordinates",
        "features":[feature("alluvial_candidate",flood,"nile_floodplain"),
                    feature("river_water_reference",riverzone,"river_water"),
                    feature("west_desert_reservation",west_desert,"desert"),
                    feature("east_desert_reservation",east_desert,"desert")]}
    OUT.mkdir(parents=True,exist_ok=True)
    geo=OUT/"cairo-giza-placement-zones.geojson"
    geo.write_text(json.dumps(collection,indent=2)+"\n")
    # Review remains on the ACTUAL 3240x4320 print composition. Make a second,
    # correctly reprojected enlarged detail for inspection rather than growing
    # sprites in the physical print map by an arbitrary factor.
    marked=atlas.convert("RGBA")
    overlay=Image.new("RGBA",marked.size,(0,0,0,0))
    pen=ImageDraw.Draw(overlay)
    colors={"desert":(194,143,71,86),"floodplain":(55,145,71,90),
            "water":(42,122,196,165)}
    def poly_draw(shape,fill,stroke):
        from shapely.geometry import Polygon,MultiPolygon,GeometryCollection
        shapes=list(shape.geoms) if hasattr(shape,"geoms") else [shape]
        for g in shapes:
            if g.geom_type=="Polygon":
                pts=[xy(a,b) for a,b in g.exterior.coords]
                pen.polygon(pts,fill=fill)
                pen.line(pts,fill=stroke,width=3,joint="curve")
                # Holes remove visual fill, preserving the actual base image.
                for hole in g.interiors:
                    pen.polygon([xy(a,b) for a,b in hole.coords],fill=(0,0,0,0))
            elif hasattr(g,"geoms"):
                poly_draw(g,fill,stroke)
    poly_draw(west_desert,colors["desert"],(139,86,28,245))
    poly_draw(east_desert,colors["desert"],(139,86,28,245))
    poly_draw(flood,colors["floodplain"],(34,112,40,250))
    poly_draw(riverzone,colors["water"],(27,77,154,240))
    for item in protected:
        x,y=xy(*item["lonlat"])
        pen.ellipse((x-6,y-6,x+6,y+6),fill=(245,244,229,245),outline=(150,24,33,255),width=3)
    marked.alpha_composite(overlay)
    printed=OUT/"cairo-giza-zone-boundaries-on-print-canvas.jpg"
    marked.convert("RGB").save(printed,quality=94,subsampling=0)
    rx0,ry0=xy(BOUNDS[0],BOUNDS[3]);rx1,ry1=xy(BOUNDS[2],BOUNDS[1])
    rx0=max(0,rx0-24);ry0=max(0,ry0-24);rx1=min(atlas.width,rx1+24);ry1=min(atlas.height,ry1+24)
    crop=marked.convert("RGB").crop((rx0,ry0,rx1,ry1))
    # Zoomed review only: no sprite rescaling or edit of the production map.
    zoom=crop.resize((crop.width*3,crop.height*3),Image.Resampling.LANCZOS)
    d=ImageDraw.Draw(zoom)
    d.rectangle((8,8,min(zoom.width-8,1020),94),fill=(252,248,231))
    d.text((24,18),"CAIRO–GIZA | ZONE BOUNDARY CANDIDATE | 3X REVIEW",fill=(39,40,37))
    d.text((24,44),"GREEN=proposed alluvium  BLUE=mapped river  SAND=desert reservation",fill=(39,40,37))
    d.text((24,68),"NOT verified historical landcover | imagery-only review; no sprite placed",fill=(139,31,32))
    zoomfile=OUT/"cairo-giza-boundary-3x-review.jpg"
    zoom.save(zoomfile,quality=95,subsampling=0)
    # Named placement regions rather than fictional exact sprite anchors.
    q={"status":"desert_sprite_placement_queue_not_activated",
       "sequence":"AFTER approval of Nile floodplain treatment",
       "source_boundary":geo.relative_to(ROOT).as_posix(),
       "items":[
          {"id":"CAIRO-DESERT-WEST","class":"desert_underlay_and_transition",
           "region_feature":"west_desert_reservation","source_assets":"existing_committed_desert_artwork_only",
           "placement_status":"queued_not_placed","restriction":"no overlap Nile alluvium/water/Giza/Saqqara monuments"},
          {"id":"CAIRO-DESERT-EAST","class":"desert_underlay_and_transition",
           "region_feature":"east_desert_reservation","source_assets":"existing_committed_desert_artwork_only",
           "placement_status":"queued_not_placed","restriction":"no overlap Nile alluvium/water/city or fortress sprites"},
          {"id":"CAIRO-DESERT-EDGE","class":"desert_edge_tiles",
           "region_feature":"outside_alluvial_boundary","source_assets":"existing_committed_desert_artwork_only",
           "placement_status":"queued_not_placed","restriction":"seamless edges and preserve all approved landmarks"}
        ],"draw_order":["geographic_water_and_land","nile_floodplain_and_bank_sprites",
           "desert_underlay_tiles_in_desert_regions","cities_fortresses_monuments","labels"],
        "approval_gate":"No automatic desert tile activation until floodplain boundary and Nile artwork pass visual QA"}
    MAN.parent.mkdir(parents=True,exist_ok=True)
    MAN.write_text(json.dumps(q,indent=2)+"\n")
    qa={"status":"candidate_review_only_no_production_change",
        "source_canvas":MAP.relative_to(ROOT).as_posix(),
        "print_preview":printed.relative_to(ROOT).as_posix(),
        "zoomed_boundary_preview":zoomfile.relative_to(ROOT).as_posix(),
        "geographic_zones":geo.relative_to(ROOT).as_posix(),
        "desert_queue":MAN.relative_to(ROOT).as_posix(),
        "zone_types":["river_water","nile_floodplain","desert_west","desert_east"],
        "waterway_source":"existing Natural Earth Nile and OSM modern Delta geometry",
        "floodplain_source":"explicit user-review polygon based on Cairo topography/river neighbourhood; NOT validated against landcover remote sensing",
        "historical_accuracy_certified":False,
        "production_composite_modified":False,"nile_painting_placed":False,
        "desert_sprite_placed":False,
        "approved_painted_nile_panels_untouched":True,
        "no_21px_pixel_buffer":True,"zoom_review_only":3,
        "protected_monument_anchor_points":protected,
        "next_requirements":["verify floodplain banks against source landcover data at map scale",
                             "correct edge around pyramids and urban Cairo",
                             "fit intact original Nile paintings without excess clipping",
                             "activate desert tile queue only after Nile review approval"]}
    (OUT/"placement-zones.json").write_text(json.dumps(qa,indent=2)+"\n")
    print("NILE GEOGRAPHIC ZONES REVIEW",printed,zoomfile,"desert queued:",MAN)

if __name__=="__main__":main()
