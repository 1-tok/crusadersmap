"""Render measured Nile Delta waterway vertices, never synthetic straight branches.

Hydrography review uses OSM modern river/canal lines as geographic geometry.
This module does NOT establish the medieval age of canals. Ancient channels
and the Tinnis route must be historically georeferenced before being promoted.
"""
import json
import math
from pathlib import Path
from collections import Counter
from shapely.geometry import shape, box, LineString
from shapely.ops import unary_union
import cairo

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/"reports/nile-delta-hydrography-review-2026-11-17/delta-osm-waterways.geojson"
OUTPUT = ROOT/"reports/nile-delta-hydrography-review-2026-11-17/renderer-validation.json"
FEATURES = None
_last = {}

def load():
    global FEATURES
    if FEATURES is None:
        if not SOURCE.is_file():
            raise FileNotFoundError("Real Nile waterways not fetched. Run tools/fetch_nile_delta_waterways.py first.")
        j=json.loads(SOURCE.read_text())
        if j.get("type")!="FeatureCollection" or not j.get("metadata",{}).get("no_synthetic_meander_or_split"):
            raise ValueError("Missing sourced waterway network provenance")
        FEATURES=[(shape(f["geometry"]),f["properties"]) for f in j["features"]]
        if sum(p.get("waterway")=="river" for _,p in FEATURES)<2:
            raise ValueError("No independently mapped river network")
    return FEATURES

def _lines(geometry):
    if geometry.is_empty:
        return
    if geometry.geom_type=="LineString":
        if len(geometry.coords)>1:
            yield geometry
    elif hasattr(geometry,"geoms"):
        for item in geometry.geoms:
            yield from _lines(item)

def draw(c, reg, land, lakes, edition):
    """Draw in map region pixels; authentic geometry is clipped to land."""
    global _last
    land_clip=land
    for lake in lakes:
        if lake.intersects(land_clip):
            land_clip=land_clip.difference(lake)
    focus=reg.bbox_ll(pad=.05)
    features=load()
    count=Counter();segments=0;vertices=0;twisty=0
    c.save()
    try:
        # Geographic land polygon clipping ensures river ends at real shoreline.
        c.new_path()
        polys=land_clip.geoms if hasattr(land_clip,"geoms") else [land_clip]
        for poly in polys:
            if poly.geom_type!="Polygon":
                continue
            image=reg.geom_px(poly)
            for ring in [image.exterior]+list(image.interiors):
                pts=list(ring.coords)
                if len(pts)<4:continue
                c.move_to(*pts[0])
                for pt in pts[1:]:c.line_to(*pt)
                c.close_path()
        c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
        c.clip()
        for geom,props in sorted(features,key=lambda x:{"canal":0,"stream":1,"river":2}.get(x[1].get("waterway"),0)):
            if not geom.intersects(focus):
                continue
            kind=props.get("waterway")
            if kind not in ("river","stream","canal"):
                continue
            cut=geom.intersection(focus)
            for line in _lines(cut):
                pts=[reg.ll_px(float(x),float(y)) for x,y in line.coords]
                if len(pts)<2:continue
                width={"river":5.4,"stream":1.6,"canal":1.3}[kind]
                if kind=="river":
                    rgb=(.22,.55,.69) if edition=="colour" else (.24,.35,.45)
                    opacity=.95
                elif kind=="stream":
                    rgb=(.27,.59,.67) if edition=="colour" else (.29,.38,.47)
                    opacity=.80
                else:
                    rgb=(.31,.61,.65) if edition=="colour" else (.35,.41,.47)
                    opacity=.55
                c.new_path();c.move_to(*pts[0])
                for pt in pts[1:]:c.line_to(*pt)
                c.set_line_width(width);c.set_line_cap(cairo.LINE_CAP_ROUND)
                c.set_line_join(cairo.LINE_JOIN_ROUND)
                c.set_source_rgba(*rgb,opacity)
                c.stroke()
                segments+=1;vertices+=len(pts);count[kind]+=1
                for i in range(1,len(pts)-1):
                    x0,y0=pts[i-1];x1,y1=pts[i];x2,y2=pts[i+1]
                    a=(x1-x0,y1-y0);b=(x2-x1,y2-y1)
                    if abs(a[0]*b[1]-a[1]*b[0])>2.5:
                        twisty+=1
    finally:
        c.restore()
    if not count["river"] or vertices<20:
        raise AssertionError("Delta actual waterway geometry too sparse for finished atlas")
    _last={"status":"mapped_geographic_network_review","segment_count":segments,
           "vertex_count":vertices,"curvature_observations":twisty,
           "rendered_by_kind":dict(count),"source_file":str(SOURCE.relative_to(ROOT)),
           "historical_accuracy_certified":False,
           "synthetic_main_branches_drawn":False,
           "coastline_clipped":True}
    return _last

def save_report():
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    if not _last:
        raise AssertionError("Delta hydrography was not rendered")
    OUTPUT.write_text(json.dumps(_last,indent=2)+"\n")
