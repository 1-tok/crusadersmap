#!/usr/bin/env python3
"""Place the 14 approved Nile vertical-bank paintings along the real Nile centreline.

Art: data/sprites/nile-vertical-banks-2026-11-21/ (PNG originals, SHA-256 checked
against the manifest). Each sprite is half a river: land on one side, painted water
on the other, ending in a ragged cut edge through mid-stream. Left-bank-named art has
its water on the right; right-bank-named art has its water on the left. Scenes are
painted looking north (top = north), so left-bank art goes on the west bank and
right-bank art on the east bank.

Fit: rigid only. A sprite is translated, never rotated, mirrored, sheared, warped or
repainted; all sprites share one uniform scale. Its cut water edge is matched against
the real centreline; the sprite is accepted only where the centreline stays within
TOL_M of that edge after the best single translation. Straight, angled and meandering
edges therefore land only on reaches whose shape they actually follow. Where nothing
fits, the stretch is left empty and recorded.

Review only. Not production approved.
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import median_filter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import place_nile_valley_review_sprites as V  # noqa: E402
import place_nile_joined_painted_strip as J  # noqa: E402

ART = ROOT / "data/sprites/nile-vertical-banks-2026-11-21"
OUT = ROOT / "reports/nile-vertical-banks-fit"
S = 5.0              # metres per sprite pixel, one uniform scale for all 14
TOL_M = 300.0        # real centreline must stay this close to the sprite's cut water edge
STEP_M = 250.0       # slide down the course by this much when a sprite does not fit
HOLD_M = 4000.0      # hold out around owner-approved city/monument anchors
GAP_FILL_M = 160.0   # hairline underlay width hiding the join between the two banks
WATER_RGB = (46, 142, 160)


def load_assets():
    man = json.loads((ART / "manifest.json").read_text())
    assets = []
    for a in man["assets"]:
        p = ART / a["path"]
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        assert sha == a["sha256"], f"checksum mismatch {a['path']}"
        arr = np.array(Image.open(p).convert("RGBA"))
        water_right = a["art_water_side"] == "right"
        alpha = arr[..., 3] > 128
        r_, g_, b_ = (arr[..., i].astype(int) for i in range(3))
        teal = alpha & (b_ > r_ + 15) & (g_ > r_ + 5)
        edge = np.full(arr.shape[0], np.nan)
        for y in range(arr.shape[0]):
            xs = np.where(alpha[y])[0]
            if len(xs) > 5:
                e = xs.max() if water_right else xs.min()
                k = -4 if water_right else 4          # a few px inside the cut edge
                if 0 <= e + k < arr.shape[1] and teal[y, e + k]:
                    edge[y] = e                       # only rows that really end in water
        idx = np.arange(len(edge))
        good = ~np.isnan(edge)
        edge = np.interp(idx, idx[good], edge[good])
        edge = median_filter(edge, size=31, mode="nearest")
        assets.append({"id": a["id"], "type": a["type"], "bank": a["bank"], "arr": arr,
                       "edge": edge, "h": arr.shape[0], "w": arr.shape[1],
                       "side": "west" if a["bank"] == "left" else "east",
                       "alpha_ratio": float(alpha.mean())})
    return assets


def try_fit(asset, y_top, ys, xs):
    rows = np.arange(asset["h"])
    Y = y_top - (rows + 0.5) * S
    X = np.interp(Y, ys, xs)
    d = X - (asset["edge"] + 0.5) * S
    off = (d.max() + d.min()) / 2
    err = (d.max() - d.min()) / 2
    return off, err


def place_run(assets, run, side, usage, anchors_m):
    ys, xs = run[::-1, 1], run[::-1, 0]
    y_top, y_bot = run[0, 1], run[-1, 1]
    cand = [a for a in assets if a["side"] == side]
    placed, y, prev = [], y_top, None
    while True:
        last = placed[-1]["asset"]["id"] if placed else None
        order = sorted(cand, key=lambda a: (a["id"] == last, usage[a["id"]], -a["h"]))
        hit = None
        for a in order:
            if y - a["h"] * S < y_bot:
                continue
            off, err = try_fit(a, y, ys, xs)
            cx, cy = off + a["w"] * S / 2, y - a["h"] * S / 2
            if err > TOL_M:
                continue
            if any(math.hypot(cx - ax, cy - ay) < HOLD_M for ax, ay in anchors_m.values()):
                continue
            hit = (a, off, err)
            break
        if hit is None:
            y -= STEP_M
            if y - 1000 < y_bot:
                break
            continue
        a, off, err = hit
        usage[a["id"]] += 1
        contiguous = prev is not None and abs(prev - y) < 1.0
        placed.append({"asset": a, "off": float(off), "ytop": float(y), "err": float(err),
                       "contiguous_with_previous": bool(contiguous)})
        y -= a["h"] * S
        prev = y
    return placed


def render(placed, channels, window, px_m, line=False):
    x0, y0, x1, y1 = window
    W, H = int((x1 - x0) / px_m), int((y1 - y0) / px_m)
    canvas = Image.new("RGB", (W, H), (232, 214, 170))
    d = ImageDraw.Draw(canvas)
    wpx = max(1, round(GAP_FILL_M / px_m))
    for p in placed:
        a = p["asset"]
        ymid = [p["ytop"], p["ytop"] - a["h"] * S]
        for ln in channels:
            pts = [(x, y) for x, y in ln.coords if ymid[1] <= y <= ymid[0]]
            if len(pts) > 1:
                d.line([((x - x0) / px_m, (y1 - y) / px_m) for x, y in pts], fill=WATER_RGB, width=wpx)
    f = S / px_m
    for p in placed:
        a = p["asset"]
        im = Image.fromarray(a["arr"], "RGBA")
        tw, th = max(1, round(im.width * f)), max(1, round(im.height * f))
        px, py = (p["off"] - x0) / px_m, (y1 - p["ytop"]) / px_m
        if px > W or py > H or px + tw < 0 or py + th < 0:
            continue
        t = im.resize((tw, th), Image.LANCZOS)
        canvas.paste(t, (round(px), round(py)), t)
    if line:
        d = ImageDraw.Draw(canvas)
        for ln in channels:
            d.line([((x - x0) / px_m, (y1 - y) / px_m) for x, y in ln.coords], fill=(220, 30, 120), width=1)
    return canvas


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assets = load_assets()
    J.MAX_SLOPE = 2.0           # candidate window; the fit tolerance decides what actually lands
    channels = V.channel_pieces_m()
    anchors_m = {k: V.FWD.transform(*v) for k, v in J.ANCHORS.items()}
    usage = Counter()
    placed, course_stats = [], []
    for ci, ln in enumerate(channels):
        pts, runs = J.runs_for(ln)
        n0 = len(placed)
        for run in runs:
            for side in ("west", "east"):
                for p in place_run(assets, run, side, usage, anchors_m):
                    p["course"] = ci
                    placed.append(p)
        course_stats.append({"course": ci, "length_km": round(ln.length / 1000, 1),
                             "north_south_km": round(abs(pts[0, 1] - pts[-1, 1]) / 1000, 1),
                             "candidate_runs": len(runs), "sprites_placed": len(placed) - n0})

    x0, y0 = V.FWD.transform(V.LON0, V.LAT0)
    x1, y1 = V.FWD.transform(V.LON1, V.LAT1)
    render(placed, channels, (x0, y0, x1, y1), 120.0).save(OUT / "valley-overview.png")

    # Native-density detail crops (5 m/px, 16 km square), centred on a representative placement
    # of each tall type and on the densest stretch.
    picks = {}
    for p in placed:
        a = p["asset"]
        if a["h"] > 1000 and a["id"] not in picks:
            picks[a["id"]] = p
    dens = Counter((round((p["ytop"]) / 16000), p["course"]) for p in placed)
    best = max(dens, key=dens.get)
    for p in placed:
        if (round(p["ytop"] / 16000), p["course"]) == best:
            picks["densest_reach"] = p
            break
    made = []
    for name, p in picks.items():
        a = p["asset"]
        cx, cy = p["off"] + a["w"] * S / 2, p["ytop"] - a["h"] * S / 2
        win = (cx - 8000, cy - 8000, cx + 8000, cy + 8000)
        tag = name.replace("_", "-")[:40]
        render(placed, channels, win, S).save(OUT / f"detail-{tag}.png")
        render(placed, channels, win, S, line=True).save(OUT / f"detail-{tag}-with-true-centreline.png")
        made.append(tag)

    rows = []
    for p in placed:
        a = p["asset"]
        cx, cy = p["off"] + a["w"] * S / 2, p["ytop"] - a["h"] * S / 2
        lon, lat = V.INV.transform(cx, cy)
        rows.append({"asset": a["id"], "type": a["type"], "map_side": a["side"], "course": p["course"],
                     "centre_lonlat": [round(lon, 4), round(lat, 4)],
                     "size_m": [round(a["w"] * S), round(a["h"] * S)],
                     "retained_alpha_ratio": round(a["alpha_ratio"], 3),
                     "clipped": False, "fit_error_m": round(p["err"], 1),
                     "joined_to_previous_sprite": p["contiguous_with_previous"]})
    errs = [r["fit_error_m"] for r in rows]
    (OUT / "manifest.json").write_text(json.dumps({
        "status": "review_only_not_production_approved",
        "art_dir": str(ART.relative_to(ROOT)), "checksums_verified": True, "assets": len(assets),
        "metres_per_sprite_px": S, "tolerance_m": TOL_M, "hold_out_m": HOLD_M,
        "fit": "rigid translation only; no rotation, mirror, shear, warp or clipping; one uniform scale",
        "left_bank_art": "west bank (water on right, scene painted looking north)",
        "right_bank_art": "east bank (water on left)",
        "usage": dict(usage), "courses": course_stats,
        "fit_error_m": {"median": round(float(np.median(errs)), 1), "max": round(max(errs), 1)} if errs else None,
        "placements": rows,
        "not_checked": ["farmland/desert edge and floodplain mask", "adjacent-sprite seam appearance",
                        "overlap with Cairo/Giza/Saqqara paintings beyond the 4 km hold-out",
                        "12 bend variants (PNGs not yet in repo)"],
        "limitations": ["Natural Earth Nile gap near 27.2-28.8 N not bridged",
                        "east-west reaches (more than 63 degrees from north-south) are left empty",
                        "water width narrows where the small 290 px tiles are used"],
        "detail_crops": made,
    }, indent=2))
    print(json.dumps(course_stats, indent=1))
    print("placed", len(placed), "usage", dict(usage))
    if errs:
        print("fit err median %.0f max %.0f" % (np.median(errs), max(errs)))


if __name__ == "__main__":
    main()
