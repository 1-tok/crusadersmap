"""Generate a repeatable sprite review overlap and map-frame audit.

This diagnostic reports *possible* bounding-box overlap, not bad art.
Use after rendering the review-only overlay, never to approve production sprites.
"""
import argparse
import json
from collections import Counter
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PIL import Image
import frame
from sprite_geometry import sheet_anchor
from render_sprite_layer import review_placements
from sprite_catalog import BASE, ROOT


def audit(year):
    chosen = review_placements(year)
    boxes = []
    for e in chosen:
        px, py = sheet_anchor(e)
        asset = BASE / e["asset"]
        with Image.open(asset) as im:
            width = e["display_width_units"]
            height = width * im.height / im.width
        ax, ay = e["anchor_normalized"]
        box = (px - ax * width, py - ay * height, px + (1 - ax) * width,
               py + (1 - ay) * height)
        clipped = (box[0] < 0 or box[1] < 0 or box[2] > frame.W
                   or box[3] > frame.H)
        boxes.append({"id": e["id"], "site_id": e["site_id"],
                      "region": e.get("map_region", "main"),
                      "asset": e["asset"], "bbox_sheet_px": [round(z, 1) for z in box],
                      "outside_sheet": clipped})
    intersections = []
    for i, a in enumerate(boxes):
        for b in boxes[i+1:]:
            if a["region"] != b["region"]:
                continue
            x0 = max(a["bbox_sheet_px"][0], b["bbox_sheet_px"][0])
            y0 = max(a["bbox_sheet_px"][1], b["bbox_sheet_px"][1])
            x1 = min(a["bbox_sheet_px"][2], b["bbox_sheet_px"][2])
            y1 = min(a["bbox_sheet_px"][3], b["bbox_sheet_px"][3])
            if x0 < x1 and y0 < y1:
                intersections.append({
                    "a": a["id"], "b": b["id"],
                    "intersection_px2": round((x1-x0)*(y1-y0)),
                    "same_site": a["site_id"] == b["site_id"],
                })
    result = {"year": year, "review_only": True,
              "render_selection_count": len(boxes),
              "region_counts": dict(Counter(x["region"] for x in boxes)),
              "outside_sheet_count": sum(x["outside_sheet"] for x in boxes),
              "possible_bbox_collisions": len(intersections),
              "limitations": [
                  "Bounding-box intersections are warnings; RGBA shapes may not touch.",
                  "This is not a finished combined atlas map; it audits sprite layer only.",
                  "Geographically unanchored generic assets remain unplaced.",
                  "Historical, coastal, label, 300-dpi and printer QA remain open."
              ],
              "placements": boxes,
              "intersections": intersections}
    dest = ROOT / "previews"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"review-placement-audit-{year}.json").write_text(
        json.dumps(result, indent=2) + "\n")
    lines = [
        f"# Review sprite audit — {year}", "",
        f"Selected located review sprites: **{len(boxes)}**",
        f"Potential bounding-box intersections: **{len(intersections)}**",
        f"Sprite bounds outside sheet: **{result['outside_sheet_count']}**",
        "", "These are diagnostic warnings, not proof of a visible collision or final map integration.",
        "", "## Regions",
    ]
    lines.extend(f"- {k}: {v}" for k, v in sorted(result["region_counts"].items()))
    lines.extend(["", "## Highest-overlap candidates"])
    for x in sorted(intersections, key=lambda t: -t["intersection_px2"])[:25]:
        lines.append(f"- {x['a']} × {x['b']} — {x['intersection_px2']:,} bounding-box px²")
    (dest / f"review-placement-audit-{year}.md").write_text("\n".join(lines) + "\n")
    print(json.dumps({k: result[k] for k in (
        "year", "render_selection_count", "region_counts",
        "outside_sheet_count", "possible_bbox_collisions")}, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=1180)
    args = parser.parse_args()
    audit(args.year)
