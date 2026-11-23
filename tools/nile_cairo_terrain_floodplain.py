#!/usr/bin/env python3
"""Terrain-derived Nile floodplain for the Cairo–Giza review window.

Source: committed terrarium-encoded elevation tiles in data/tiles/ (zoom 7,
256 px, z_x_y.png). Method: a cell is floodplain when it lies within MAX_DIST_M
of the Natural Earth channel, sits no more than MAX_HEIGHT_M above the elevation
of its nearest channel point, and is connected to the channel through such cells.

This is an elevation-derived review mask, NOT a cadastral or historical
floodplain. Zoom 7 gives roughly 0.5 km ground resolution, which is coarse for
bank-edge work; the review and QA metrics record that. Cells without a committed
tile are marked unknown and are never classified as farmland.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from scipy.spatial import cKDTree

from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[1]
TILE_DIR = ROOT / "data" / "tiles"
ZOOM = 7
MAX_HEIGHT_M = 8.0
MAX_DIST_M = 8000.0  # review choice; a 15 km limit admitted desert plain (about 1,400 km2)
CELL_M = 250.0

PROJ = "+proj=lcc +lat_1=29.9 +lat_2=30.5 +lat_0=30.2 +lon_0=31.2 +datum=WGS84 +units=m"
FWD = Transformer.from_crs("EPSG:4326", PROJ, always_xy=True)
INV = Transformer.from_crs(PROJ, "EPSG:4326", always_xy=True)


def _tile_pixel(lon, lat):
    n = 2 ** ZOOM
    x = (lon + 180.0) / 360.0 * n * 256
    lat_r = math.radians(lat)
    y = (1.0 - math.asinh(math.tan(lat_r)) / math.pi) / 2.0 * n * 256
    return x, y


class Dem:
    """Lazily loaded terrarium tiles keyed by (x, y) tile index."""

    def __init__(self):
        self.tiles = {}

    def _tile(self, tx, ty):
        key = (tx, ty)
        if key not in self.tiles:
            p = TILE_DIR / f"{ZOOM}_{tx}_{ty}.png"
            if p.exists():
                a = np.asarray(Image.open(p).convert("RGB")).astype(np.float64)
                self.tiles[key] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
            else:
                self.tiles[key] = None
        return self.tiles[key]

    def sample(self, lon, lat):
        """Elevation in metres at lon/lat, or NaN where no tile is committed."""
        px, py = _tile_pixel(lon, lat)
        tx, ty = int(px // 256), int(py // 256)
        t = self._tile(tx, ty)
        if t is None:
            return float("nan")
        ix, iy = int(px % 256), int(py % 256)
        return float(t[min(max(iy, 0), 255), min(max(ix, 0), 255)])


def build(window_m, channel_points_m):
    """Return (mask, valid, elevation, grid) for the projected review window.

    mask: boolean floodplain cells; valid: cells with committed elevation data.
    grid: (x0, y1, cell_m, nx, ny) so the caller can map cells to pixels.
    """
    x0, y0, x1, y1 = window_m
    nx = int(math.ceil((x1 - x0) / CELL_M))
    ny = int(math.ceil((y1 - y0) / CELL_M))
    xs = x0 + (np.arange(nx) + 0.5) * CELL_M
    ys = y1 - (np.arange(ny) + 0.5) * CELL_M  # row 0 is north
    gx, gy = np.meshgrid(xs, ys)
    lon, lat = INV.transform(gx.ravel(), gy.ravel())

    dem = Dem()
    elev = np.array([dem.sample(a, b) for a, b in zip(lon, lat)]).reshape(ny, nx)
    valid = ~np.isnan(elev)

    # Channel reference elevation: sample the DEM at every channel point.
    cx = np.array([p[0] for p in channel_points_m])
    cy = np.array([p[1] for p in channel_points_m])
    clon, clat = INV.transform(cx, cy)
    cz = np.array([dem.sample(a, b) for a, b in zip(clon, clat)])
    ok = ~np.isnan(cz)
    tree = cKDTree(np.column_stack([cx[ok], cy[ok]]))
    dist, idx = tree.query(np.column_stack([gx.ravel(), gy.ravel()]))
    ref = cz[ok][idx].reshape(ny, nx)
    dist = dist.reshape(ny, nx)
    height = elev - ref

    candidate = valid & (height <= MAX_HEIGHT_M) & (dist <= MAX_DIST_M)
    # Close pixel gaps and open thin spurs, so edges read as ground rather than noise.
    candidate = ndimage.binary_closing(candidate, iterations=2)
    candidate = ndimage.binary_opening(candidate, iterations=1)
    labels, _ = ndimage.label(candidate)
    touching = set(np.unique(labels[(dist <= 2 * CELL_M) & candidate]).tolist()) - {0}
    mask = np.isin(labels, list(touching))

    grid = (x0, y1, CELL_M, nx, ny)
    return mask, valid, elev, height, grid


def qa(mask, valid, height, grid):
    x0, y1, cell, nx, ny = grid
    cell_km2 = (cell / 1000.0) ** 2
    inside = valid.sum()
    return {
        "cells_window": int(nx * ny),
        "cells_with_committed_elevation": int(inside),
        "unknown_fraction_of_window": round(1 - inside / (nx * ny), 4),
        "floodplain_cells": int(mask.sum()),
        "floodplain_area_km2": round(mask.sum() * cell_km2, 1),
        "median_height_above_channel_m": round(float(np.nanmedian(height[mask])), 2) if mask.any() else None,
        "max_height_above_channel_m": round(float(np.nanmax(height[mask])), 2) if mask.any() else None,
        "thresholds": {"max_height_m": MAX_HEIGHT_M, "max_distance_m": MAX_DIST_M, "cell_m": CELL_M},
        "zoom": ZOOM,
        "status": "elevation_derived_review_mask_not_certified",
    }


def write_outputs(out_dir: Path, mask, valid, grid, metrics):
    out_dir.mkdir(parents=True, exist_ok=True)
    img = np.zeros(mask.shape + (3,), dtype=np.uint8)
    img[valid] = (60, 60, 60)
    img[mask] = (167, 189, 134)
    Image.fromarray(img).save(out_dir / "floodplain-mask.png")
    (out_dir / "floodplain-qa.json").write_text(json.dumps(metrics, indent=2))
    x0, y1, cell, nx, ny = grid
    (out_dir / "floodplain-grid.json").write_text(json.dumps(
        {"x0": x0, "y1": y1, "cell_m": cell, "nx": nx, "ny": ny, "proj": PROJ}, indent=2))
    np.save(out_dir / "floodplain-mask.npy", mask)
