#!/usr/bin/env python3
"""Fit the eight joined painted Nile tiles to the real Natural Earth Nile centreline.

Art: data/sprites/nile-joins-batch-02/nile_joins_01..08.png (660 px wide, joined
edge to edge into one 660x2443 strip, top = north, painted water + both banks).

Fit method: rigid placement. Each tile is only translated, never sheared, bent,
rotated, mirrored or repainted (one uniform scale for all). A tile is placed only
where the real centreline stays inside its painted channel (TOL_M).

Review only. Not production approved.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from shapely.geometry import LineString

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import place_nile_valley_review_sprites as V  # noqa: E402

TILES = sorted((ROOT / "data/sprites/nile-joins-batch-02").glob("nile_joins_0*.png"))
OUT = ROOT / "reports/nile-joined-painted-fit"
S = 7.8                  # metres per sprite pixel (painted river ~114 px = ~890 m)
STEP = 50.0              # centreline sampling, metres
MAX_SLOPE = 1.0          # |dx/dy| limit = 45 degrees from north-south
MIN_RUN_M = 4000.0
CHUNK_ROWS = 3000
TOL_M = 450.0           # real centreline must stay inside the painted channel (half river width)
HOLD_M = 4000.0          # hold out around owner-approved city/monument anchors
ANCHORS = {"Cairo": (31.24, 30.04), "Giza": (31.1325, 29.9792), "Saqqara": (31.216, 29.871)}


def load_strip():
    ims = [np.array(Image.open(f).convert("RGBA")) for f in TILES]
    heights = [i.shape[0] for i in ims]
    return np.concatenate(ims, 0), heights


def painted_centres(strip):
    r, g, b, a = (strip[..., i].astype(int) for i in range(4))
    water = (a > 200) & (b > r + 40) & (b > g + 5)
    c = np.full(strip.shape[0], np.nan)
    for y in range(strip.shape[0]):
        xs = np.where(water[y])[0]
        if len(xs) > 20:
            c[y] = np.median(xs)
    idx = np.arange(len(c))
    good = ~np.isnan(c)
    c = np.interp(idx, idx[good], c[good])
    k = 15
    pad = np.pad(c, k, mode="edge")
    return np.convolve(pad, np.ones(2 * k + 1) / (2 * k + 1), mode="valid")


def runs_for(piece):
    """North-to-south runs where the river heads within 45 degrees of south."""
    n = max(2, int(piece.length // STEP))
    pts = np.array([piece.interpolate(i / n, normalized=True).coords[0] for i in range(n + 1)])
    if pts[-1, 1] > pts[0, 1]:
        pts = pts[::-1]
    w = 20  # +-1 km window
    ok = np.zeros(len(pts), bool)
    for i in range(len(pts)):
        a, b = pts[max(i - w, 0)], pts[min(i + w, len(pts) - 1)]
        dy = a[1] - b[1]
        ok[i] = dy > 0 and abs(b[0] - a[0]) <= MAX_SLOPE * dy
    runs, i = [], 0
    while i < len(pts):
        if not ok[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(pts) and ok[j + 1]:
            j += 1
        seg = pts[i:j + 1]
        keep = [0]
        for k in range(1, len(seg)):
            if seg[k, 1] < seg[keep[-1], 1] - 1e-6:
                keep.append(k)
        seg = seg[keep]
        if seg[0, 1] - seg[-1, 1] >= MIN_RUN_M:
            runs.append(seg)
        i = j + 1
    return pts, runs


def build_chunks(strip, centres, runs, heights):
    """Rigid placement: every tile keeps its exact painted shape and is only translated.

    Tiles are laid down the river in order 1..8, 1..8. A tile is accepted only where
    the real centreline stays within TOL_M of the tile's own painted river centre
    after the best single translation. Otherwise the search slides 600 m further down
    the course and retries the same tile, so tiles are never sheared or bent.
    """
    tile_tops = np.concatenate([[0], np.cumsum(heights)])
    anchors_m = {k: V.FWD.transform(*v) for k, v in ANCHORS.items()}
    chunks, records, rejected = [], [], 0
    for run in runs:
        ys, xs = run[::-1, 1], run[::-1, 0]
        y_top, y_bot = run[0, 1], run[-1, 1]
        t, y, prev_off = 0, y_top, None
        while True:
            h = heights[t % 8]
            if y - h * S < y_bot:
                break
            r0 = int(tile_tops[t % 8])
            rows = np.arange(h)
            Y = y - (rows + 0.5) * S
            X = np.interp(Y, ys, xs)
            d = X - centres[r0:r0 + h] * S
            off = (d.max() + d.min()) / 2
            err = (d.max() - d.min()) / 2
            cx, cy = off + 330 * S, y - h * S / 2
            near = any(math.hypot(cx - ax, cy - ay) < HOLD_M for ax, ay in anchors_m.values())
            if err > TOL_M or near:
                y -= 600.0
                rejected += 1
                continue
            tile = strip[r0:r0 + h]
            chunks.append({"img": tile, "xorig": float(off), "ytop": float(y), "w": tile.shape[1]})
            lon_a, lat_a = V.INV.transform(cx, y)
            records.append({"tile": t % 8 + 1, "centre_lonlat": [round(lon_a, 4), round(lat_a, 4)],
                            "fit_error_m": round(float(err), 1),
                            "seam_step_px": None if prev_off is None or abs(prev_y - y) > 1 else
                            round(float((off - prev_off) / S), 1)})
            prev_off, prev_y = off, y - h * S
            y -= h * S
            t += 1
    return chunks, records, rejected


def render(chunks, channels, window, px_m, line=False):
    x0, y0, x1, y1 = window
    W, H = int((x1 - x0) / px_m), int((y1 - y0) / px_m)
    canvas = Image.new("RGB", (W, H), (232, 214, 170))
    f = S / px_m
    for c in chunks:
        im = Image.fromarray(c["img"], "RGBA")
        tw, th = max(1, round(im.width * f)), max(1, round(im.height * f))
        px = (c["xorig"] - x0) / px_m
        py = (y1 - c["ytop"]) / px_m
        if px > W or py > H or px + tw < 0 or py + th < 0:
            continue
        t = im.resize((tw, th), Image.LANCZOS)
        canvas.paste(t, (round(px), round(py)), t)
    if line:
        from PIL import ImageDraw
        d = ImageDraw.Draw(canvas)
        for ln in channels:
            d.line([((x - x0) / px_m, (y1 - y) / px_m) for x, y in ln.coords], fill=(220, 30, 120), width=1)
    return canvas


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    strip, heights = load_strip()
    assert strip.shape[:2] == (2443, 660), strip.shape
    centres = painted_centres(strip)
    channels = V.channel_pieces_m()
    all_chunks, all_records, bend_gaps, held_all = [], [], [], []
    for ci, ln in enumerate(channels):
        pts, runs = runs_for(ln)
        covered = sum(r[0, 1] - r[-1, 1] for r in runs)
        total_ns = abs(pts[0, 1] - pts[-1, 1])
        bend_gaps.append({"course": ci, "length_km": round(ln.length / 1000, 1),
                          "north_south_km": round(total_ns / 1000, 1),
                          "fitted_north_south_km": round(covered / 1000, 1), "runs": len(runs)})
        ch, rec, rej = build_chunks(strip, centres, runs, heights)
        all_chunks += ch
        all_records += [{"course": ci, **r} for r in rec]
        held_all.append({"course": ci, "retry_slides": rej})
        bend_gaps[-1]["tiles_placed"] = len(ch)
        bend_gaps[-1]["tiles_km"] = round(len(ch) * 2.38, 1)

    x0, y0 = V.FWD.transform(V.LON0, V.LAT0)
    x1, y1 = V.FWD.transform(V.LON1, V.LAT1)
    render(all_chunks, channels, (x0, y0, x1, y1), 120.0).save(OUT / "valley-overview.png")

    # Native-density detail crops (7.8 m/px, 20 km square) with and without the true centreline.
    details = {"giza_saqqara_reach": (31.19, 29.62), "minya_reach": (30.80, 28.40),
               "asyut_reach": (31.20, 27.20), "qena_bend": (32.55, 26.10), "luxor_reach": (32.65, 25.60)}
    made = []
    for name, (lon, lat) in details.items():
        cx, cy = V.FWD.transform(lon, lat)
        win = (cx - 10000, cy - 10000, cx + 10000, cy + 10000)
        render(all_chunks, channels, win, S).save(OUT / f"detail-{name}.png")
        render(all_chunks, channels, win, S, line=True).save(OUT / f"detail-{name}-with-true-centreline.png")
        made.append(name)

    (OUT / "manifest.json").write_text(json.dumps({
        "status": "review_only_not_production_approved",
        "art": [str(p.relative_to(ROOT)) for p in TILES],
        "art_note": "eight joined painted Nile tiles, exact files, unmodified; strip 660x2443 px",
        "fit": "rigid whole-tile translation only; no shear, rotation, mirror or per-row shifting; uniform scale only",
        "metres_per_sprite_px": S, "painted_river_px_median": 114,
        "max_slope_from_north_south": "45 degrees", "bend_gaps_note":
            "stretches where the river runs more than 45 degrees from north-south are left unfilled",
        "courses": bend_gaps, "placed_runs": all_records, "search_stats": held_all, "tolerance_m": TOL_M,
        "anchors_held_out_m": HOLD_M,
        "limitations": [
            "strip repeats every 2443 rows; tile 8 -> tile 1 seam is not an authored join",
            "Natural Earth Nile gap near 27.2-28.8 N not bridged",
            "bank art is not clipped to farmland or desert edge",
            "geographic seam and historical accuracy not certified"],
        "detail_crops": made,
    }, indent=2))
    print(json.dumps(bend_gaps, indent=1))
    print("runs", len(all_records), "chunks", len(all_chunks), "held", len(held_all))


if __name__ == "__main__":
    main()
