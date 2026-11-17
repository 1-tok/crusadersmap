#!/usr/bin/env python3
"""Geographically anchored Nile Delta wetland sprite layer, review only.

Only terrain-batch06 sprites with manifest terrain_class=wetland are used.
Existing coastline/lake vector geometry clips every pixel of each painting.
They render below rivers, cities, fortresses, industry and labels.
"""
import json
from pathlib import Path
import cairo
from tools.lowland_51_review_placer import _clip_real_land, _surface

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/sprites/terrain-batch06/manifest.json"
REPORT = ROOT / "reports/nile-delta-terrain-review-2026-11-17/wetland-placement.json"
# Shoreline-adjacent wetlands and shallow lakes, never urban core.
# Positions are representative terrain-area anchors, not historical site locations.
PLACEMENTS = [
    ("t06-a12", 30.96, 31.43, 165), # central-west northern Delta reed pool
    ("t06-a13", 31.38, 31.44, 185), # northern central mosaic
    ("t06-b01", 31.70, 31.35, 160), # eastern marsh fringe toward Lake Manzala
    ("t06-b02", 31.17, 31.31, 170), # narrow channels between cultivated fields
]
_last = []

def draw(c, terrain, reg, edition):
    global _last
    _last = []
    if edition != "colour":
        return
    data = json.loads(MANIFEST.read_text())
    by_id = {x["id"]: x for x in data["assets"]}
    c.save()
    try:
        _clip_real_land(c, reg, terrain.mpp)
        for ident, lon, lat, width in PLACEMENTS:
            entry = by_id[ident]
            if entry.get("terrain_class") != "wetland":
                raise AssertionError(f"Refusing non-wetland class {ident}")
            file = entry["file"]
            if not (ROOT / file).is_file():
                raise FileNotFoundError(file)
            px, py = reg.ll_px(lon, lat)
            if not (0 <= px < reg.w and 0 <= py < reg.h):
                raise AssertionError(f"Wetland placement outside Delta inset: {ident}")
            surf = _surface(file, width)
            c.save()
            c.translate(px-width*.5, py-surf.get_height()*.65)
            c.set_source_surface(surf, 0, 0)
            c.get_source().set_filter(cairo.FILTER_BEST)
            c.paint_with_alpha(.78)
            c.restore()
            _last.append({
                "id":ident,"terrain_class":"wetland","png":file,
                "lon_lat":[lon,lat],"display_width_px":width,
                "coastline_clip":"land_minus_lakes",
                "status":"rendered_for_review_not_historical_site"
            })
    finally:
        c.restore()

def save_report():
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps({
       "mode":"provisional_rebuild_review",
       "layer":"wetland_above_land_underlay_below_terrain_rivers_and_city_sprites",
       "placed_count":len(_last),"rendered":_last,
       "no_hill_sprite_reclassification":True
    }, indent=2)+"\n")
    return REPORT
