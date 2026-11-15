"""Place QA-screened, generic lowland cutouts in geographic REVIEW regions.

Never assigns historical site coordinates. Candidate anchors are selected
deterministically from the existing land/fertility/near-coast fields, then
the entire PNG is vector-clipped against real land polygons minus lakes.
This is a LOW UNDERLAY layer: cities, fortresses, industry, roads, coastline
ink and lettering are painted later by the established renderer.
"""
from __future__ import annotations
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import math

import cairo
import numpy as np
from PIL import Image
from shapely.geometry import Polygon
from shapely.ops import unary_union

from rough import LAND
from terrain import LAKES_OK

ROOT = Path(__file__).resolve().parents[1]
REVIEW_DIR = ROOT / "reports/lowland-review-2026-11-15"
AUDIT_PATH = REVIEW_DIR / "lowland-51-image-qa-and-regions.json"
PLACEMENT_PATH = REVIEW_DIR / "lowland-51-placement-review.json"
_SURF = {}
_USED = []
_REGION_COUNT = defaultdict(int)


def _load():
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def _surface(path, width):
    key = (path, width)
    if key not in _SURF:
        img = Image.open(ROOT / path).convert("RGBA")
        h = max(1, round(img.height / img.width * width))
        img = img.resize((width, h), Image.Resampling.LANCZOS)
        a = np.asarray(img, np.float32)
        alpha = a[..., 3:4] / 255.0
        premult = np.empty((h, width, 4), dtype=np.uint8)
        premult[..., :3] = (a[..., [2, 1, 0]] * alpha).astype(np.uint8)
        premult[..., 3] = a[..., 3].astype(np.uint8)
        backing = bytearray(premult.tobytes())
        surf = cairo.ImageSurface.create_for_data(backing, cairo.FORMAT_ARGB32, width, h, width * 4)
        _SURF[key] = (surf, backing)
    return _SURF[key][0]


def _clip_real_land(c, reg, mpp):
    bbox = reg.bbox_ll(pad=0.02)
    relevant = [g.intersection(bbox) for g in LAND if g.intersects(bbox)]
    if not relevant:
        raise AssertionError("No land geography intersects the review map")
    solid = unary_union(relevant)
    # Existing atlas waters are authoritative. Do not paint into them.
    lakes = [g for g in LAKES_OK if g.intersects(bbox)]
    if lakes:
        solid = solid.difference(unary_union(lakes))
    solid = solid.simplify(max(.00001, .38 * mpp / 111000.), preserve_topology=True)
    c.new_path()
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    pieces = solid.geoms if hasattr(solid, "geoms") else [solid]
    count = 0
    for p in pieces:
        if p.geom_type != "Polygon" or p.is_empty:
            continue
        transformed = reg.geom_px(p)
        for ring in [transformed.exterior] + list(transformed.interiors):
            coords = list(ring.coords)
            if len(coords) < 4:
                continue
            c.move_to(*coords[0])
            for pt in coords[1:]:
                c.line_to(*pt)
            c.close_path()
            count += 1
    if not count:
        raise AssertionError("No drawable land-mask coastline rings")
    c.clip()


def _pick_anchor(terrain, bbox, seen, seed):
    lo, la, hi, ha = bbox
    ok = (
        terrain.land_l & ~terrain.water_l
        & (terrain.lon >= lo) & (terrain.lon <= hi)
        & (terrain.lat >= la) & (terrain.lat <= ha)
        & (terrain.elev < 430)
        & (terrain.fert > 0.18)
        & (terrain.dland >= 0.1)
        & (terrain.dland < 16)
    )
    ys, xs = np.nonzero(ok)
    if not len(xs):
        return None
    rand = np.random.default_rng(seed)
    choices = rand.permutation(len(xs))
    for i in choices[:min(600, len(choices))]:
        lon = float(terrain.lon[ys[i], xs[i]])
        lat = float(terrain.lat[ys[i], xs[i]])
        # Keep individual review cutouts from stacking on the same farm.
        if all(math.hypot((lon - a) * 111 * math.cos(math.radians(lat)), (lat - b) * 111) > 12 for a, b in seen):
            return lon, lat
    return None


def draw_for_region(c, terrain, reg, region, edition):
    if edition != "colour":
        return
    rows = [x for x in _load()["records"] if x["preview_eligible"] and x["frame"] == region]
    if not rows:
        _REGION_COUNT[region] += 0
        return
    choices = {}
    positions = []
    for row in rows:
        subregion = row["assigned_review_region"]
        seed = int(hashlib.sha256(row["id"].encode()).hexdigest()[:12], 16)
        anchor = _pick_anchor(terrain, row["review_zone_bbox_wgs84"],
                              choices.setdefault(subregion, []), seed)
        if anchor is None:
            _USED.append({
                "id": row["id"], "canonical_asset": row["canonical_asset"],
                "region": subregion, "frame": region,
                "status": "held_no_safe_near_coast_fertile_land",
            })
            continue
        choices[subregion].append(anchor)
        positions.append((row, anchor))
    if not positions:
        return
    c.save()
    try:
        _clip_real_land(c, reg, terrain.mpp)
        # All placements here are underlays BEFORE terrain's mountains,
        # trees, ruins, generic industries, towns, fortresses and labels.
        for item, (lon, lat) in positions:
            x, y = reg.ll_px(lon, lat)
            width = 300 if region == "main" else 250
            surf = _surface(item["canonical_asset"], width)
            c.save()
            c.translate(x - width * .5, y - surf.get_height() * .70)
            c.set_source_surface(surf, 0, 0)
            c.get_source().set_filter(cairo.FILTER_BEST)
            c.paint_with_alpha(0.88)
            c.restore()
            _USED.append({
                "id": item["id"], "canonical_asset": item["canonical_asset"],
                "region": item["assigned_review_region"], "frame": region,
                "generic_landcover_review_anchor_lonlat": [round(lon, 6), round(lat, 6)],
                "anchor_method": "sampled_from_existing_geographic_land_mask_fertility_low_elevation_and_coastal_distance",
                "clip": "atlas_land_polygon_minus_lakes",
                "layer": "underlay_below_terrain_cities_castles_industries_roads_and_labels",
                "status": "drawn_provisional_geographic_review",
            })
            _REGION_COUNT[region] += 1
    finally:
        c.restore()


def save_report():
    audit = _load()
    eligible = {x["id"] for x in audit["records"] if x["preview_eligible"]}
    found = {x["id"] for x in _USED}
    if found != eligible:
        raise AssertionError(f"Not all eligible sources reconciled: {sorted(eligible-found)}")
    drawn = [r for r in _USED if r["status"] == "drawn_provisional_geographic_review"]
    out = {
        "status": "provisional_review_build_only_not_print_approved",
        "input_asset_audit": str(AUDIT_PATH.relative_to(ROOT)),
        "total_cutouts_inspected": 51,
        "geographic_review_regions_assigned": 51,
        "eligible_dry_only": len(eligible),
        "geographically_drawn_for_review": len(drawn),
        "eligible_held_for_no_anchor": len(_USED) - len(drawn),
        "other_sources_held": 51 - len(eligible),
        "layer_order": "lowland cutouts before all other atlas sprite and label rendering",
        "coastal_cutout_policy": "precise vector land-minus-lakes clip; overlap beyond coast is masked, not plotted",
        "placement_approval": "review_only",
        "rendered": _USED,
    }
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    PLACEMENT_PATH.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print("LOWLAND-51 RENDER", json.dumps({k:v for k,v in out.items() if k!="rendered"}, indent=2))
    return out
