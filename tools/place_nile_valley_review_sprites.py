#!/usr/bin/env python3
"""Review placements for the whole Nile valley, Thebes to the Delta head.

Review only. Each placement is labelled with how its farmland was established:
  - terrain_verified: the cell lies in the zoom-7 elevation mask (lat >= 29.54 N)
  - provisional_corridor: no committed elevation; a stated 4 km corridor each side
    of the Natural Earth channel stands in for farmland. Not production-approved.

Sprites: committed upright bank paintings (four, rotated in turn) and the ecology
field tiles (delta_farm and nile_farm_upstream, least-used first). No rotation or
mirroring. The desert underlay is not placed here.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import shapely
import shapely.ops
from PIL import Image, ImageDraw
from shapely.geometry import Point, LineString, box
from shapely.ops import linemerge, unary_union

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import nile_cairo_terrain_floodplain as TF  # noqa: E402
import build_nile_cairo_giza_prototype as P  # noqa: E402

OUT = ROOT / "reports" / "nile-valley-review-placements"
RIVERS = ROOT / "data" / "ne_10m_rivers_lake_centerlines.geojson"
UPRIGHT = ROOT / "data" / "sprites" / "nile-painted-upright-2026-11-17"
ECOLOGY = ROOT / "data" / "sprites" / "nile-ecology-2026-11-17"
UPRIGHT_FILES = ["leftbank_south_a.png", "rightbank_south_a.png",
                 "leftbank_south_b.png", "rightbank_south_b.png"]

LON0, LON1, LAT0, LAT1 = 30.90, 32.95, 24.95, 30.20
PX_M = 120.0
TF.CELL_M = 500.0          # valley-scale mask cell
CORRIDOR_M = 8000.0        # provisional half-width where no elevation is committed
BANK_SPACING_M = 20000.0
BANK_W_M = 4500.0
BANK_OFFSET_M = 5200.0
FIELD_W_M = 2200.0
FIELD_STEP_M = 2250.0
RIVER_CLEAR_M = 900.0
FIELD_GAP_M = 80.0

FWD, INV = P.FWD, P.INV


def channel_pieces_m():
    """Continuous Nile courses inside the window, each traced in its own order.

    Sorting points by latitude folds the river back on itself, so Natural Earth
    segments are clipped to the window and merged. The source has a gap near
    27.2–28.8 N, so the Cairo reach and the southern reach come out as separate pieces.
    """
    data = json.loads(RIVERS.read_text())
    x0, y0 = FWD.transform(LON0, LAT0)
    x1, y1 = FWD.transform(LON1, LAT1)
    win = box(x0, y0, x1, y1)
    pieces = []
    for f in data["features"]:
        if f["properties"].get("name") != "Nile":
            continue
        g = f["geometry"]
        parts = g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]
        for p in parts:
            ln = LineString([FWD.transform(lon, lat) for lon, lat in p])
            clipped = ln.intersection(win)
            if clipped.is_empty:
                continue
            pieces += [clipped] if clipped.geom_type == "LineString" else list(clipped.geoms)
    merged = linemerge(unary_union(pieces))
    parts = [merged] if merged.geom_type == "LineString" else list(merged.geoms)
    return sorted([p for p in parts if p.length >= 2000], key=lambda l: -l.length)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(20261121)
    channels = channel_pieces_m()
    channel_all = unary_union(channels)
    x0, y0 = FWD.transform(LON0, LAT0)
    x1, y1 = FWD.transform(LON1, LAT1)
    W = int((x1 - x0) / PX_M)
    H = int((y1 - y0) / PX_M)

    # Terrain mask where elevation exists; provisional corridor elsewhere.
    pts_m = []
    for ln in channels:
        n = max(2, int(ln.length // 250))
        pts_m += [ln.interpolate(i / n, normalized=True).coords[0] for i in range(n + 1)]
    mask, valid, elev, height, grid = TF.build((x0, y0, x1, y1), pts_m)
    gx0, gy1, cell, nx, ny = grid
    cx = gx0 + (np.arange(nx) + 0.5) * cell
    cy = gy1 - (np.arange(ny) + 0.5) * cell
    CX, CY = np.meshgrid(cx, cy)
    d_chan = np.array(shapely.distance(channel_all, shapely.points(CX.ravel(), CY.ravel()))).reshape(ny, nx)
    corridor = d_chan <= CORRIDOR_M
    verified = mask & valid
    provisional = corridor & ~valid
    farm = verified | provisional

    def share(fp, mask_cells):
        minx, miny, maxx, maxy = fp.bounds
        xs = np.linspace(minx, maxx, 10)
        ys = np.linspace(miny, maxy, 10)
        gx, gy = np.meshgrid(xs, ys)
        keep = shapely.contains_xy(fp, gx, gy)
        if not keep.any():
            return 0.0
        ix = np.clip(((gx[keep] - gx0) / cell).astype(int), 0, nx - 1)
        iy = np.clip(((gy1 - gy[keep]) / cell).astype(int), 0, ny - 1)
        return float(mask_cells[iy, ix].mean())

    bank_imgs = {f: Image.open(UPRIGHT / f).convert("RGBA") for f in UPRIGHT_FILES}
    man = json.loads((ECOLOGY / "manifest.json").read_text())
    pool = [a for a in man["assets"] if a.get("class") in ("delta_farm", "nile_farm_upstream")]
    field_imgs = {a["id"]: (a, Image.open(ECOLOGY / a["file"]).convert("RGBA")) for a in pool}

    placed_fps = []
    bank_records = []
    field_records = []
    used = {}
    k = 0

    # Bank scenes along each continuous course, each scene on the bank named in its filename, every BANK_SPACING_M.
    for channel in channels:
        # Orient each course to flow north (Nile flows south to north). Scenes are painted
        # looking north from the south, so a "left" scene belongs on the left (west) bank.
        if channel.coords[-1][1] < channel.coords[0][1]:
            channel = LineString(list(channel.coords)[::-1])
        total = channel.length
        s = 0.0
        while s < total:
            fname = UPRIGHT_FILES[k % len(UPRIGHT_FILES)]
            side = 1.0 if fname.startswith("leftbank") else -1.0
            im = bank_imgs[fname]
            h_m = BANK_W_M * im.size[1] / im.size[0]
            done = False
            for off in (BANK_OFFSET_M, 4700.0, 5700.0, 4200.0, 6200.0):
                for ds in (0.0, 1500.0, -1500.0):
                    ss = min(max(s + ds, 0), total)
                    p = channel.interpolate(ss)
                    a = channel.interpolate(max(ss - 50, 0))
                    b = channel.interpolate(min(ss + 50, total))
                    dx, dy = b.x - a.x, b.y - a.y
                    nrm = math.hypot(dx, dy) or 1.0
                    cxm = p.x + side * (-dy / nrm) * off
                    cym = p.y + side * (dx / nrm) * off
                    # Scenes are painted looking north: left = west bank, right = east bank.
                    # Where the river bends east-west that rule fails, so skip the station.
                    if (cxm < p.x) != (side > 0):
                        continue
                    nearest = shapely.ops.nearest_points(channel_all, Point(cxm, cym))[0]
                    if (cxm < nearest.x) != (side > 0):
                        continue
                    fp = box(cxm - BANK_W_M / 2, cym - h_m / 2, cxm + BANK_W_M / 2, cym + h_m / 2)
                    if fp.distance(channel_all) < RIVER_CLEAR_M:
                        continue
                    if share(fp, farm) < 0.95:
                        continue
                    if any(fp.intersects(q) for q in placed_fps):
                        continue
                    ver = share(fp, verified) >= 0.95
                    placed_fps.append(fp)
                    bank_records.append({
                        "id": f"bank:{fname}@{k}",
                        "file": f"data/sprites/nile-painted-upright-2026-11-17/{fname}",
                        "centre_lonlat": [round(v, 5) for v in INV.transform(cxm, cym)],
                        "footprint_m": [round(BANK_W_M), round(h_m)],
                        "farmland_basis": "terrain_verified" if ver else "provisional_corridor",
                        "accepted": True,
                        "placement_status": "review_placement_only",
                    })
                    done = True
                    break
                if done:
                    break
            k += 1
            s += BANK_SPACING_M

    # Field tiles across the farmland, least-used tile first.
    gx = x0 + FIELD_W_M / 2
    row = 0
    last = None
    while gx < x1:
        gy = y0 + FIELD_W_M / 2 + (row % 2) * FIELD_STEP_M / 2
        while gy < y1:
            jx = gx + rng.uniform(-0.35, 0.35) * FIELD_STEP_M
            jy = gy + rng.uniform(-0.35, 0.35) * FIELD_STEP_M
            cands = [rng.choice(pool) for _ in range(4)]
            cands = [c for c in cands if c["id"] != last] or pool
            pick = min(cands, key=lambda a: (used.get(a["id"], 0), rng.random()))
            a, im = field_imgs[pick["id"]]
            h_m = FIELD_W_M * im.size[1] / im.size[0]
            fp = box(jx - FIELD_W_M / 2, jy - h_m / 2, jx + FIELD_W_M / 2, jy + h_m / 2)
            if share(fp, farm) >= 1.0 and fp.distance(channel_all) >= FIELD_GAP_M and \
                    not any(fp.intersects(q) for q in placed_fps):
                ver = share(fp, verified) >= 0.95
                placed_fps.append(fp)
                used[a["id"]] = used.get(a["id"], 0) + 1
                last = a["id"]
                field_records.append({
                    "id": a["id"],
                    "centre_lonlat": [round(v, 5) for v in INV.transform(jx, jy)],
                    "footprint_m": [round(FIELD_W_M), round(h_m)],
                    "farmland_basis": "terrain_verified" if ver else "provisional_corridor",
                })
            gy += FIELD_STEP_M
        gx += FIELD_STEP_M
        row += 1

    # Review image
    def to_px(x, y):
        return (x - x0) / PX_M, (y1 - y) / PX_M

    arr = np.zeros((H, W, 3), dtype=np.uint8)
    arr[:] = (232, 214, 170)
    fy, fx = np.indices((H, W))
    mx = x0 + (fx + 0.5) * PX_M
    my = y1 - (fy + 0.5) * PX_M
    ix = np.clip(((mx - gx0) / cell).astype(int), 0, nx - 1)
    iy = np.clip(((gy1 - my) / cell).astype(int), 0, ny - 1)
    arr[farm[iy, ix]] = (167, 189, 134)
    canvas = Image.fromarray(arr)
    draw = ImageDraw.Draw(canvas)
    for ln in channels:
        draw.line([to_px(*c) for c in ln.coords], fill=(46, 96, 140), width=max(2, round(700 / PX_M)))
    for rec in bank_records:
        lon, lat = rec["centre_lonlat"]
        xm, ym = FWD.transform(lon, lat)
        px, py = to_px(xm, ym)
        img = bank_imgs[rec["file"].split("/")[-1]]
        tw = round(BANK_W_M / PX_M)
        th = round(tw * img.size[1] / img.size[0])
        t = img.resize((tw, th), Image.LANCZOS)
        canvas.paste(t, (round(px - tw / 2), round(py - th / 2)), t)
    for rec in field_records:
        lon, lat = rec["centre_lonlat"]
        xm, ym = FWD.transform(lon, lat)
        px, py = to_px(xm, ym)
        a, im = field_imgs[rec["id"]]
        tw = max(1, round(FIELD_W_M / PX_M))
        th = max(1, round(tw * im.size[1] / im.size[0]))
        t = im.resize((tw, th), Image.LANCZOS)
        canvas.paste(t, (round(px - tw / 2), round(py - th / 2)), t)
    canvas.save(OUT / "nile-valley-review.png")

    features = []
    for rec in bank_records + field_records:
        features.append({"type": "Feature",
                         "geometry": {"type": "Point", "coordinates": rec["centre_lonlat"]},
                         "properties": {k2: v for k2, v in rec.items() if k2 != "centre_lonlat"}})
    (OUT / "placements.geojson").write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    manifest = {
        "status": "review_only_not_promoted",
        "window_lonlat": [LON0, LAT0, LON1, LAT1],
        "image_px": [W, H],
        "px_per_metre": PX_M,
        "channel_source": "data/ne_10m_rivers_lake_centerlines.geojson (Nile only; Ismailiya excluded)",
        "channel_pieces": len(channels),
        "channel_gap_note": "Natural Earth Nile has a gap near 27.2–28.8 N; the two courses are not joined",
        "farmland_basis": {
            "terrain_verified": "zoom-7 terrarium mask where committed tiles exist (lat >= ~29.54 N)",
            "provisional_corridor": f"stated {CORRIDOR_M/1000:.0f} km each side of channel where no elevation is committed; not approved",
        },
        "bank_scenes": len(bank_records),
        "bank_scenes_terrain_verified": sum(1 for r in bank_records if r["farmland_basis"] == "terrain_verified"),
        "field_tiles": len(field_records),
        "field_tiles_terrain_verified": sum(1 for r in field_records if r["farmland_basis"] == "terrain_verified"),
        "tile_uses": used,
        "not_placed": ["desert sprites (sequenced after floodplain approval)",
                       "Valley of the Kings and Luxor temple paintings (binaries not committed)"],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(f"pieces {len(channels)}; bank {len(bank_records)} (verified {manifest['bank_scenes_terrain_verified']}); "
          f"fields {len(field_records)} (verified {manifest['field_tiles_terrain_verified']}); image {W}x{H}")


if __name__ == "__main__":
    main()
