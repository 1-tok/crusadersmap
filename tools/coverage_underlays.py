"""Geography-clipped painted texture underlays for a coverage-focused REVIEW map.

This does not georegister the 51 held lowland cutouts or certify uncovered
base pixels. It uses the four already-retained edge-matched textures only as
subtle underpaint within the existing land polygons; all water and lakes
remain untouched. Roads, cities, coast ink, labels and water art render later.
"""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import json
import os

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSET_DIR = ROOT / "assets" / "terrain" / "large_area" / "rect_underlays_04"
SOURCES = {
    "desert": "desert_sand_edge_matched.png",
    "steppe": "dry_steppe_edge_matched.png",
    "scrub": "canaan_scrub_edge_matched.png",
    "fertile": "green_plain_edge_matched.png",
}
_CACHE = {}
_COUNTS = defaultdict(lambda: defaultdict(int))
REGION_SHIFT = {"main": (0, 0), "aegean": (173, 91), "delta": (301, 213)}
ENABLED = os.environ.get("CRUSADER_COVERAGE_UNDERLAYS", "review").lower() != "off"


def _texture(kind):
    """Retain hand-painted detail without substituting another area's palette."""
    if kind not in _CACHE:
        path = ASSET_DIR / SOURCES[kind]
        if not path.is_file():
            raise FileNotFoundError(f"Missing retained coverage underlay: {path}")
        src = Image.open(path).convert("RGB").resize((768, 512), Image.Resampling.LANCZOS)
        # Periodic blur: a plain edge-clamped blur breaks an otherwise
        # seam-matched tile at each repeated border.
        wrapped = Image.new("RGB", (src.width * 3, src.height * 3))
        for ty in range(3):
            for tx in range(3):
                wrapped.paste(src, (tx * src.width, ty * src.height))
        soft = wrapped.filter(ImageFilter.GaussianBlur(radius=29)).crop(
            (src.width, src.height, 2 * src.width, 2 * src.height)
        )
        detail = np.asarray(src, np.float32) - np.asarray(soft, np.float32)
        _CACHE[kind] = np.clip(detail, -38, 38)
    return _CACHE[kind]


def _field_chunk(field, width, height, row0, row1):
    """Interpolate known geographic terrain fields at working render resolution."""
    a = np.asarray(field, np.float32)
    img = Image.fromarray(a, mode="F")
    chunk = img.resize(
        (width, row1 - row0), Image.Resampling.BICUBIC,
        box=(0, row0 * a.shape[0] / height, a.shape[1],
             row1 * a.shape[0] / height),
    )
    return np.asarray(chunk, np.float32)


def apply_land_underlay(base_chunk, terrain, region, row0, row1):
    """Apply the underlay below ALL sprite/label passes, never over water.

    terrain.wash() must have just run on the same row stripe and populated
    terrain._ml and terrain._lk at the same working resolution.
    """
    if not ENABLED:
        return
    if region not in REGION_SHIFT:
        raise ValueError(f"Unknown atlas region: {region}")
    h, w = base_chunk.shape[:2]
    if h != row1 - row0 or w != terrain.ws:
        raise ValueError("Coverage underlay stripe does not match terrain wash")
    land = np.asarray(terrain._ml, np.float32)
    lake = np.asarray(terrain._lk, np.float32)
    if land.shape != (h, w) or lake.shape != (h, w):
        raise ValueError("Geographic land/water mask size mismatch")

    # Use the exact rasterized land and lake polygons at the same preview
    # resolution as the geographic wash. The blurred wash's 0.995 threshold
    # previously erased the shoreline pixels; a binary geographic mask clips
    # texture right up to the coast without putting any into the water.
    exact_land = np.asarray(terrain._land_exact, bool)
    exact_lake = np.asarray(terrain._lake_exact, bool)
    if exact_land.shape != (h, w) or exact_lake.shape != (h, w):
        raise ValueError("Exact geographic coastline mask size mismatch")
    inside = exact_land & ~exact_lake
    counts = _COUNTS[region]
    counts["land_interior_pixels"] += int(inside.sum())
    counts["shoreline_land_pixels"] += int(np.count_nonzero(inside & (land < 0.995)))
    counts["sea_or_lake_excluded_pixels"] += int(np.count_nonzero(~inside))
    counts["excluded_boundary_water_pixels"] += int(inside.size - inside.sum())
    if not np.any(inside):
        return

    fertility = np.clip(_field_chunk(terrain.fert, w, terrain.hs, row0, row1), 0, 1)
    desert = np.clip(_field_chunk(terrain.desert, w, terrain.hs, row0, row1), 0, 1)
    desert_weight = np.clip(desert * 1.5, 0, 1)
    fertile_weight = (1 - desert_weight) * np.clip((fertility - .26) / .55, 0, 1)
    remaining = np.maximum(0, 1 - desert_weight - fertile_weight)
    scrub_weight = remaining * (0.70 if region == "main" else 0.40)
    steppe_weight = remaining - scrub_weight
    weights = {
        "desert": desert_weight,
        "fertile": fertile_weight,
        "scrub": scrub_weight,
        "steppe": steppe_weight,
    }

    # Continuous tile phase across stripes prevents horizontal seams. The
    # retained textures were verified edge-matched; colour comes from the
    # existing geographic wash, not an invented satellite colour layer.
    shift_y, shift_x = REGION_SHIFT[region]
    ys = (np.arange(row0, row1, dtype=np.int32) + shift_y) % 512
    xs = (np.arange(w, dtype=np.int32) + shift_x) % 768
    detail = np.zeros_like(base_chunk, dtype=np.float32)
    for kind, weight in weights.items():
        patch = _texture(kind)[ys[:, None], xs[None, :], :]
        detail += patch * weight[..., None]
        counts[f"{kind}_weighted_pixel_equivalents"] += int(weight[inside].sum())

    # This is deliberately a reversible review rendering, not a substitute
    # for visually fitted, high-resolution regional terrain paintings.
    # Feather *within* the exact land boundary: gradual stroke strength for
    # anti-aliased shoreline land pixels, absolutely zero beyond the boundary.
    detail *= (0.82 * (0.48 + 0.52 * np.clip(land, 0, 1)) * (1 - lake))[..., None]
    before = base_chunk[inside].copy()
    excluded_before = base_chunk[~inside].copy()
    base_chunk[inside] = np.clip(base_chunk[inside] + detail[inside], 0, 255)
    counts["underlay_eligible_pixels"] += int(inside.sum())
    counts["visually_changed_pixels"] += int(np.any(
        np.abs(base_chunk[inside] - before) >= 0.5, axis=1
    ).sum())
    # Measure, rather than merely assume, that the excluded shoreline,
    # open sea and lakes are unchanged.
    counts["water_pixels_painted"] += int(np.any(
        base_chunk[~inside] != excluded_before, axis=1
    ).sum())


def write_coverage_report(path="out/underlay-coverage-report.json"):
    out = {
        "status": "provisional_underlay_visual_review",
        "method": "edge-matched retained paintings, exact land-and-lake polygon clipping up to coastline, in-land feathered texture over geographic wash",
        "enabled": ENABLED,
        "workflow": {
            "head_sha": os.environ.get("GITHUB_SHA"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
        },
        "sources": {k: str((ASSET_DIR / v).relative_to(ROOT)) for k, v in SOURCES.items()},
        "notes": [
            "A pixel receiving underpaint is not proof that a visual sprite gap is resolved.",
            "A continuous geographic wash already existed; flat/thin cells can be intentional deserts.",
            "Exact land-mask pixels now receive underpaint through the shoreline; sea and lakes remain unpainted.",
            "Held 51 lowland cutouts, Canaan coastal strips and island replacements were not promoted.",
            "The enlarged green texture requires repaint/print QA; this is review-only.",
            "Per-region paint totals overlap where inset boxes cover the main map.",
        ],
        "regions": {},
    }
    for region, values in sorted(_COUNTS.items()):
        counts = dict(values)
        total = counts.get("land_interior_pixels", 0)
        painted = counts.get("underlay_eligible_pixels", 0)
        counts["interior_underlay_fraction"] = round(painted / total, 6) if total else 0.0
        if ENABLED and (not total or painted != total or counts.get("water_pixels_painted", 0)):
            raise AssertionError(f"Unsafe underlay coverage for {region}: {counts}")
        out["regions"][region] = counts
    if ENABLED and set(out["regions"]) != set(REGION_SHIFT):
        raise AssertionError("Not every geographic atlas region received review underlay")
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
