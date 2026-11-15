"""Inspect all 51 actual canonical lowland PNGs and assign conservative geographic REVIEW regions.

PNG byte/alpha/color checks are automated screening, not human historical
or shoreline approval. Land-only candidates are preview-renderable; mixed
water or coast-dependent imagery remains held for individually fitted geometry.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/manifests/LOWLAND-51-CANONICAL-PLACEMENT-AUDIT-2026-11-15.json"
OUT = ROOT / "reports/lowland-review-2026-11-15"
AUDIT = OUT / "lowland-51-image-qa-and-regions.json"
CONTACT = OUT / "lowland-51-contact-sheet.jpg"

REGIONS = {
    "Nile Delta": {"frame": "delta", "bbox": [29.9, 30.20, 32.2, 31.55], "land": "Nile Delta floodplain"},
    "Greek lowlands": {"frame": "aegean", "bbox": [21.0, 36.8, 24.5, 39.5], "land": "Peloponnese and Greek cultivated lowlands"},
    "Cyprus": {"frame": "main", "bbox": [32.3, 34.6, 34.45, 35.45], "land": "Cyprus interior/coastal cultivated plain"},
    "Cilicia": {"frame": "main", "bbox": [34.3, 36.5, 35.95, 37.35], "land": "Cilician coastal alluvium"},
    "Levantine coastal fields": {"frame": "main", "bbox": [34.5, 31.5, 35.85, 34.9], "land": "Levantine littoral farms"},
}
CHOOSE = {
    "06": ["Nile Delta"],
    "07": ["Cyprus", "Cilicia", "Greek lowlands", "Levantine coastal fields"],
    "08": ["Nile Delta", "Greek lowlands", "Levantine coastal fields"],
    "09": ["Levantine coastal fields", "Cyprus", "Cilicia"],
}


def inspect_one(item, group_index):
    group = item["source_group"]
    selected = CHOOSE[group][group_index % len(CHOOSE[group])]
    path = ROOT / item["canonical_asset"]
    result = {
        "id": item["intake_id"], "source_group": group,
        "canonical_asset": item["canonical_asset"],
        "original_source": item["source_png"],
        "source_region_hints": item["candidate_regions"],
        "assigned_review_region": selected,
        "review_zone_bbox_wgs84": REGIONS[selected]["bbox"],
        "frame": REGIONS[selected]["frame"],
        "georeferencing": "region_polygon_only_not_fixed_site_coordinate",
        "png_present": path.is_file(),
        "preview_eligible": False,
        "render_status": "held",
    }
    if selected not in item["candidate_regions"]:
        raise AssertionError(f"Candidate region not present in registered hints: {item['canonical_asset']}")
    if not path.is_file():
        result["hold_reason"] = "canonical_binary_missing"
        return result, None
    result["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        with Image.open(path) as original:
            result["png_format"] = original.format
            result["native_mode"] = original.mode
            result["native_size"] = list(original.size)
            image = original.convert("RGBA")
    except Exception as exc:
        result["hold_reason"] = "png_decode_failed"
        result["error"] = str(exc)
        return result, None
    a = np.asarray(image, np.uint8)
    alpha = a[..., 3]
    visible = alpha >= 128
    has_visible = bool(np.any(visible))
    bbox = image.getchannel("A").getbbox()
    result["alpha_bbox"] = list(bbox) if bbox else None
    result["transparent_fraction"] = round(float((alpha <= 8).mean()), 5)
    result["visible_fraction"] = round(float(visible.mean()), 5)
    edges = np.concatenate((alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1]))
    result["opaque_boundary_fraction"] = round(float((edges > 128).mean()), 5)
    result["native_alpha_channel"] = ("A" in result["native_mode"] or result["native_mode"] == "P" and "transparency" in original.info) if result["native_mode"] != "RGBA" else True
    # Conservative cyan/blue detection on visibly painted pixels. This is a
    # hold heuristic, not a visual conclusion that blue equals sea.
    rgb = a[..., :3].astype(np.float32)
    rr, gg, bb = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    blue = (bb > rr * 1.24) & (bb >= gg * 0.94) & (bb > 95) & ((bb - rr) > 22)
    teal = (gg > rr * 1.32) & (bb > rr * 1.20) & (gg > 115) & (bb > 105)
    wet = (blue | teal) & visible
    result["blue_teal_visible_fraction"] = round(float(wet.sum() / max(1, visible.sum())), 5)
    result["valid_png_rgba_preview"] = (
        result["png_format"] == "PNG" and "A" in result["native_mode"]
        and min(image.size) >= 64 and has_visible
        and result["transparent_fraction"] >= .01
        and result["opaque_boundary_fraction"] <= .12
    )
    # Group 07 is the only source named as generic land-only cutouts. Mixed
    # Delta/shoreline groups cannot auto-pass even if the pixel heuristic
    # fails to detect painted water. Group 07 stays PROVISIONAL.
    result["preview_eligible"] = (
        group == "07" and result["valid_png_rgba_preview"]
        and result["blue_teal_visible_fraction"] <= 0.035
    )
    if result["preview_eligible"]:
        result["hold_reason"] = None
        result["render_status"] = "region_clipped_preview_only"
        result["approval"] = "provisional_underpaint_only"
    elif not result["valid_png_rgba_preview"]:
        result["hold_reason"] = "alpha_or_native_png_quality"
    elif group in ("06", "08", "09"):
        result["hold_reason"] = "mixed_water_coast_or_hydrology_requires_visual_placement"
    else:
        result["hold_reason"] = "blue_teal_content_needs_visual_water_review"
    return result, image


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    source = json.loads(SOURCE.read_text(encoding="utf-8"))["assets"]
    assert len(source) == 51, "Source register count changed: reconcile before placement"
    items, thumbs = [], []
    idx = Counter()
    for item in source:
        group = item["source_group"]
        rec, image = inspect_one(item, idx[group])
        idx[group] += 1
        items.append(rec)
        thumbs.append(image)
    cw, ch = 260, 220
    page = Image.new("RGB", (6 * cw, 9 * ch), (45, 46, 43))
    draw = ImageDraw.Draw(page)
    for index, (record, im) in enumerate(zip(items, thumbs)):
        ox, oy = (index % 6) * cw, (index // 6) * ch
        if im:
            thumb = im.copy()
            thumb.thumbnail((cw - 20, ch - 55), Image.Resampling.LANCZOS)
            x = ox + (cw - thumb.width) // 2
            y = oy + 5 + (ch - 55 - thumb.height) // 2
            page.paste(thumb, (x, y), thumb.getchannel("A"))
        tag = f"{index+1:02d} G{record['source_group']} {record['assigned_review_region']}"
        status = "PREVIEW" if record["preview_eligible"] else "HOLD"
        draw.text((ox + 8, oy + ch - 42), tag[:37], fill=(240, 238, 219))
        draw.text((ox + 8, oy + ch - 23), f"{status} / {record.get('blue_teal_visible_fraction','?')} blue", fill=(182, 218, 186) if status == "PREVIEW" else (241, 177, 155))
    page.save(CONTACT, quality=87)
    c = Counter(x["source_group"] for x in items if x["preview_eligible"])
    reasons = Counter(x["hold_reason"] or "preview_provisional" for x in items)
    out = {
        "schema_version": 1, "date": "2026-11-15",
        "source_register": str(SOURCE.relative_to(ROOT)),
        "all_51_binaries_inspected": True,
        "qa_type": "actual_png_decode_alpha_color_and_boundary_automated_screening",
        "human_visual_and_historical_approval": False,
        "coastline_preview_policy": "land polygon clipping REQUIRED for every accepted candidate; no seaward pixels",
        "layering": "under coastline ink, below all town/fortress/industry sprites, roads and labels",
        "candidate_regions": REGIONS,
        "summary": {
            "total": len(items),
            "binary_present": sum(x["png_present"] for x in items),
            "preview_eligible": sum(x["preview_eligible"] for x in items),
            "held": sum(not x["preview_eligible"] for x in items),
            "eligible_by_group": dict(c),
            "hold_reasons": dict(reasons),
        },
        "records": items,
    }
    AUDIT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("LOWLAND-51 AUDIT", json.dumps(out["summary"], indent=2))
    return out


if __name__ == "__main__":
    run()
