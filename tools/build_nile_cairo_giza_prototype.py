#!/usr/bin/env python3
"""Cairo–Giza Nile prototype: terrain-derived farmland, desert underlay, sprites.

Review output only. Nothing here changes the production atlas, the approved
manifests, or any committed sprite. Inputs:
  - Natural Earth 10m channel centrelines (Ismailiya Canal excluded)
  - zoom-7 terrarium elevation tiles in data/tiles/ (farmland mask)
  - RUL-01 desert underlay, edge-matched, from the underlay manifest
  - committed upright bank sprites and the 1180 Giza and Cairo paintings
Every placement is review-only; the manifest keeps production status unapproved.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import shapely
from PIL import Image, ImageDraw, ImageFont
from pyproj import Transformer
from shapely.geometry import LineString, Point, box
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import nile_cairo_terrain_floodplain as TF  # noqa: E402

OUT = ROOT / "reports" / "nile-cairo-giza-prototype"
RIVERS = ROOT / "data" / "ne_10m_rivers_lake_centerlines.geojson"
UPRIGHT = ROOT / "data" / "sprites" / "nile-painted-upright-2026-11-17"
UNDERLAY_FILE = ROOT / "assets/terrain/large_area/rect_underlays_04/desert_sand_edge_matched.png"
UNDERLAY_ID = "RUL-01"
UNDERLAY_TILE_REVIEW_PX = 800
LANDMARK_1180 = {
    "giza": ROOT / "assets/sprites/giza-1180-v1.png",
    "cairo": ROOT / "assets/sprites/cairo-1180-v1.png",
}

PROJ = TF.PROJ
FWD = Transformer.from_crs("EPSG:4326", PROJ, always_xy=True)
INV = Transformer.from_crs(PROJ, "EPSG:4326", always_xy=True)

# West edge set east of 30.94 E, the first committed elevation tile column.
LON0, LON1, LAT0, LAT1 = 30.96, 31.70, 29.70, 30.35
PX_M = 60.0  # 60 m per review pixel

# Desert reserves: farmland and sprites are kept out of these areas.
GIZA_WEST_RULE = (30.0, 29.90, 31.18, 30.08)  # lon_max, lat0, lat1 (from field-stretch QA)
MONUMENT_RESERVES = [
    {"name": "Giza pyramid plateau", "lonlat": (31.1325, 29.9792), "radius_m": 3000.0,
     "source": "owner manifest 05_giza_pyramids_sphinx anchor; radius is a review choice"},
    {"name": "Saqqara step pyramid", "lonlat": (31.216, 29.871), "radius_m": 2000.0,
     "source": "owner manifest 06_saqqara_step_pyramid anchor; radius is a review choice"},
    {"name": "Valley of the Kings", "lonlat": (32.60, 25.74), "radius_m": 3000.0,
     "source": "owner manifest 13_valley_of_kings_tombs anchor; outside review window",
     "drawn_in_window": False},
]

ANCHORS = {
    "al-Qahira / Cairo": (31.24, 30.04),
    "Pyramids of Giza": (31.1325, 29.9792),
    "Saqqara step pyramid": (31.216, 29.871),
}

BASE_DESERT = (232, 214, 170)
FERTILE = (167, 189, 134)
WATER = (46, 96, 140)
INK = (58, 42, 24)

BANK_OFFSET_M = 5200.0
RIVER_CLEAR_M = 900.0
MONUMENT_CLEAR_M = 4000.0
UPRIGHT_W_M = 4500.0
CITY_W_M = 3200.0
GIZA_W_M = 3600.0


def to_m(lon, lat):
    return FWD.transform(lon, lat)


def window_m():
    x0, y0 = to_m(LON0, LAT0)
    x1, y1 = to_m(LON1, LAT1)
    return x0, y0, x1, y1


def load_channel():
    data = json.loads(RIVERS.read_text())
    main, dist = [], []
    wx0, wy0, wx1, wy1 = window_m()
    win = box(wx0, wy0, wx1, wy1)
    for f in data["features"]:
        name = f["properties"].get("name")
        if name not in ("Nile", "Rosetta Branch", "Damietta Branch"):
            continue  # Ismailiya Canal and other modern cuts are excluded
        g = f["geometry"]
        parts = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        for p in parts:
            ln = LineString([to_m(lon, lat) for lon, lat in p])
            clipped = ln.intersection(win)
            if clipped.is_empty:
                continue
            pieces = [clipped] if clipped.geom_type == "LineString" else list(clipped.geoms)
            for piece in pieces:
                if piece.geom_type == "LineString" and piece.length >= 1000:
                    (main if name == "Nile" else dist).append(piece)
    return main, dist


def sample_points(lines, step=250.0):
    pts = []
    for ln in lines:
        n = max(2, int(ln.length // step))
        for i in range(n + 1):
            p = ln.interpolate(i / n, normalized=True)
            pts.append((p.x, p.y))
    return pts


def perpendicular_point(line, s, offset):
    p = line.interpolate(s)
    a = line.interpolate(max(s - 50, 0))
    b = line.interpolate(min(s + 50, line.length))
    dx, dy = b.x - a.x, b.y - a.y
    n = math.hypot(dx, dy) or 1.0
    return p.x + (-dy / n) * offset, p.y + (dx / n) * offset


def exclusion_geometry():
    parts = []
    lon_max, lat0, lat1 = GIZA_WEST_RULE[2], GIZA_WEST_RULE[1], GIZA_WEST_RULE[3]
    x0, y0 = to_m(LON0 - 0.2, lat0)
    x1, y1 = to_m(lon_max, lat1)
    parts.append(box(x0, y0, x1, y1))
    for r in MONUMENT_RESERVES:
        if not r.get("drawn_in_window", True):
            continue
        cx, cy = to_m(*r["lonlat"])
        parts.append(Point(cx, cy).buffer(r["radius_m"], quad_segs=24))
    return unary_union(parts)


def tile_underlay(W, H):
    src = Image.open(UNDERLAY_FILE).convert("RGB")
    tw = UNDERLAY_TILE_REVIEW_PX
    th = round(tw * src.size[1] / src.size[0])
    tile = src.resize((tw, th), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H))
    for y in range(0, H, th):
        for x in range(0, W, tw):
            canvas.paste(tile, (x, y))
    return canvas


def farmland_cells_in_reserves(mask, grid, excl):
    x0, y1, cell, nx, ny = grid
    xs = x0 + (np.arange(nx) + 0.5) * cell
    ys = y1 - (np.arange(ny) + 0.5) * cell
    gx, gy = np.meshgrid(xs, ys)
    inside = shapely.contains_xy(excl, gx, gy)
    return inside


def footprint_on_farmland(mask, grid, fp):
    """Fraction of a sprite footprint's sample points that fall on farmland cells."""
    x0, y1, cell, nx, ny = grid
    minx, miny, maxx, maxy = fp.bounds
    xs = np.linspace(minx, maxx, 12)
    ys = np.linspace(miny, maxy, 12)
    gx, gy = np.meshgrid(xs, ys)
    keep = shapely.contains_xy(fp, gx, gy)
    if not keep.any():
        return 0.0
    cx = np.clip(((gx[keep] - x0) / cell).astype(int), 0, nx - 1)
    cy = np.clip(((y1 - gy[keep]) / cell).astype(int), 0, ny - 1)
    return float(mask[cy, cx].mean())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wx0, wy0, wx1, wy1 = window_m()
    W = int((wx1 - wx0) / PX_M)
    H = int((wy1 - wy0) / PX_M)

    main_lines, dist_lines = load_channel()
    if not main_lines:
        raise SystemExit("No Nile centreline in the review window.")
    main_line = max(main_lines, key=lambda l: l.length)
    channel_pts = sample_points(main_lines + dist_lines)
    channel_geom = unary_union(main_lines + dist_lines)

    mask, valid, elev, height, grid = TF.build((wx0, wy0, wx1, wy1), channel_pts)
    excl = exclusion_geometry()
    excl_cells = farmland_cells_in_reserves(mask, grid, excl)
    farm = mask & ~excl_cells

    metrics = TF.qa(mask, valid, height, grid)
    metrics["farmland_after_reserves_cells"] = int(farm.sum())
    metrics["reserve_cells_removed_from_farmland"] = int((mask & excl_cells).sum())
    TF.write_outputs(OUT / "terrain", mask, valid, grid, metrics)

    canvas = tile_underlay(W, H)
    draw = ImageDraw.Draw(canvas)

    # Farmland: terrain mask after reserves, upsampled from cells to review pixels.
    x0, y1, cell, nx, ny = grid
    # Upsample the cell mask smoothly, then threshold, so edges read as ground not blocks.
    from PIL import ImageFilter
    farm_img = Image.fromarray((farm.astype(np.uint8) * 255)).resize((W, H), Image.BILINEAR)
    farm_img = farm_img.filter(ImageFilter.GaussianBlur(6)).point(lambda v: 255 if v >= 128 else 0)
    green = Image.new("RGB", (W, H), FERTILE)
    canvas.paste(green, (0, 0), farm_img)
    draw = ImageDraw.Draw(canvas)

    def to_px(x, y):
        return (x - wx0) / PX_M, (wy1 - y) / PX_M

    for ln in main_lines + dist_lines:
        pts = [to_px(x, y) for x, y in ln.coords]
        draw.line(pts, fill=WATER, width=max(2, round(900.0 / PX_M)), joint="curve")

    placements = []

    def footprint_for(src_path, centre_m, width_m):
        im = Image.open(src_path).convert("RGBA")
        aspect = im.size[1] / im.size[0]
        cx, cy = centre_m
        fp = box(cx - width_m / 2, cy - width_m * aspect / 2,
                 cx + width_m / 2, cy + width_m * aspect / 2)
        return im, aspect, fp

    def place(fname, src_path, centre_m, width_m, side, label, anchor_name, kind):
        im, aspect, fp = footprint_for(src_path, centre_m, width_m)
        cx, cy = centre_m
        ch = fp.distance(channel_geom)
        mon = min(Point(cx, cy).distance(Point(*to_m(*ANCHORS[k]))) for k in ANCHORS)
        farm_frac = footprint_on_farmland(farm, grid, fp) if kind == "upright" else None
        desert_reserve = bool(fp.intersects(excl))
        # Reserves exist to hold monuments, so only bank scenes are kept out of them.
        accepted = (ch >= RIVER_CLEAR_M)
        if kind == "upright":
            accepted = accepted and mon >= MONUMENT_CLEAR_M and not desert_reserve and farm_frac >= 0.95
        rec = {
            "id": label,
            "file": str(src_path.relative_to(ROOT)),
            "kind": kind,
            "side": side,
            "anchor": anchor_name,
            "centre_lonlat": [round(v, 5) for v in INV.transform(cx, cy)],
            "footprint_m": [round(width_m), round(width_m * aspect)],
            "source_px": list(im.size),
            "channel_clearance_m": round(ch, 1),
            "nearest_monument_m": round(mon, 1),
            "farmland_share_of_footprint": None if farm_frac is None else round(farm_frac, 3),
            "in_desert_reserve": desert_reserve,
            "accepted": bool(accepted),
            "placement_status": "review_placement_only",
        }
        placements.append((rec, fp, im, accepted))

    def upright_ok(fp, cx, cy, accepted_fps):
        if fp.distance(channel_geom) < RIVER_CLEAR_M:
            return False
        if min(Point(cx, cy).distance(Point(*to_m(*ANCHORS[k]))) for k in ANCHORS) < MONUMENT_CLEAR_M:
            return False
        if fp.intersects(excl):
            return False
        if any(fp.intersects(o) for o in accepted_fps):
            return False
        return footprint_on_farmland(farm, grid, fp) >= 0.95

    # Upright bank scenes: search each target station (and nearby stations) for a spot
    # fully on farmland, on the requested bank, clear of the channel and monuments.
    stations = [(0.22, "leftbank_south_a.png", "left"), (0.42, "rightbank_south_a.png", "right"),
                (0.62, "leftbank_south_b.png", "left"), (0.85, "rightbank_south_b.png", "right")]
    accepted_fps = []
    for target, fname, side in stations:
        im, aspect, _ = footprint_for(UPRIGHT / fname, (0, 0), UPRIGHT_W_M)
        sign = 1.0 if side == "left" else -1.0
        found = None
        fracs = sorted(np.arange(0.05, 0.96, 0.01), key=lambda f: abs(f - target))
        for frac in fracs:
            s = main_line.length * frac
            for off in np.arange(3000.0, 6500.0, 250.0):
                cx, cy = perpendicular_point(main_line, s, sign * off)
                _, _, fp = footprint_for(UPRIGHT / fname, (cx, cy), UPRIGHT_W_M)
                if upright_ok(fp, cx, cy, accepted_fps):
                    found = (cx, cy, fp, frac, off)
                    break
            if found:
                break
        if found is None:
            placements.append(({"id": f"upright:{fname}", "accepted": False,
                                "reason": "no farmland-fit station found"}, None, None, False))
            continue
        cx, cy, fp, frac, off = found
        accepted_fps.append(fp)
        place(fname, UPRIGHT / fname, (cx, cy), UPRIGHT_W_M, side,
              f"upright:{fname}", f"channel station {frac:.2f}, offset {off/1000:.2f} km", "upright")

    # Landmarks from the 1180 committed paintings. Giza sits on its reserve by design.
    gx, gy = to_m(*ANCHORS["Pyramids of Giza"])
    place("giza", LANDMARK_1180["giza"], (gx, gy), GIZA_W_M, "west",
          "landmark:giza-1180", "Pyramids of Giza", "landmark")
    # Owner anchor for al-Qahira sits on the channel (see manifest); scene set on the east bank.
    cx0, cy0 = to_m(*ANCHORS["al-Qahira / Cairo"])
    cx1, cy1 = cx0 + 2600.0, cy0
    place("cairo", LANDMARK_1180["cairo"], (cx1, cy1), CITY_W_M, "east",
          "landmark:cairo-1180 (set 2.6 km east of owner anchor)", "al-Qahira / Cairo", "landmark")

    for rec, fp, im, accepted in placements:
        if not accepted:
            continue
        scaled_w = round((fp.bounds[2] - fp.bounds[0]) / PX_M)
        scaled_h = round((fp.bounds[3] - fp.bounds[1]) / PX_M)
        scaled = im.resize((scaled_w, scaled_h), Image.LANCZOS)
        minx, miny, maxx, maxy = fp.bounds
        px = round((minx - wx0) / PX_M)
        py = round((wy1 - maxy) / PX_M)
        canvas.paste(scaled, (px, py), scaled)

    font = ImageFont.load_default()
    for name, (lon, lat) in ANCHORS.items():
        x, y = to_px(*to_m(lon, lat))
        draw.ellipse([x - 5, y - 5, x + 5, y + 5], outline=INK, width=2)
        tw = draw.textlength(name, font=font)
        draw.text((x - 10 - tw, y - 6), name, fill=INK, font=font)

    canvas.save(OUT / "cairo-giza-prototype-review.png")

    manifest = {
        "id": "nile-cairo-giza-prototype",
        "status": "review_prototype_not_promoted",
        "window_lonlat": [LON0, LAT0, LON1, LAT1],
        "projection": PROJ,
        "image_px": [W, H],
        "px_per_metre_inverse": PX_M,
        "desert_underlay": {
            "id": UNDERLAY_ID,
            "file": str(UNDERLAY_FILE.relative_to(ROOT)),
            "tile_review_px": [UNDERLAY_TILE_REVIEW_PX, round(UNDERLAY_TILE_REVIEW_PX * 1024 / 1536)],
            "placement_status": "review_placement_only",
            "print_review": "required_not_approved",
            "source_manifest": "assets/terrain/large_area/manifest_rectangular_underlays_04.json",
        },
        "farmland": {
            "method": "zoom-7 terrarium elevation: within 15 km of channel, <= 8 m above nearest channel point, connected to channel; minus desert reserves",
            "qa": "terrain/floodplain-qa.json",
            "status": "elevation_derived_review_mask_not_certified",
            "desert_exclusions": {
                "giza_west_bank_rule_lonlat": GIZA_WEST_RULE,
                "monument_reserves": MONUMENT_RESERVES,
            },
        },
        "river": {
            "source": "data/ne_10m_rivers_lake_centerlines.geojson",
            "features": ["Nile", "Rosetta Branch", "Damietta Branch"],
            "excluded": ["Ismailiya Canal (modern cut)"],
            "drawn_width_m": 900.0,
        },
        "placements": [rec for rec, _, _, _ in placements],
        "not_placed": [
            "Saqqara and Dahshur paintings: owner manifest binaries not committed",
            "Desert transition sprites: NILE-DESERT-PLACEMENT-NEXT is sequenced after floodplain approval",
            "Valley of the Kings: outside this window; reserve recorded only",
        ],
    }
    (OUT / "placement-manifest.json").write_text(json.dumps(manifest, indent=2))
    acc = sum(1 for r, _, _, a in placements if a)
    print(f"wrote review ({W}x{H}); farmland cells {int(farm.sum())}; placements accepted {acc}/{len(placements)}")


if __name__ == "__main__":
    main()
