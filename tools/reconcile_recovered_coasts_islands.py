#!/usr/bin/env python3
"""Reconcile recovered root ZIP art without promoting unverified geographic variants.

Outputs a per-image decision ledger, Greek island and coastal-city comparison
galleries, and a labelled full-map review composite. Existing renderer selections
remain the baseline until coastline, phase and orientation evidence is verified.
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "rebuild-2026-11-12"
OUT.mkdir(parents=True, exist_ok=True)
manifest = json.loads((ROOT / "data/manifests/ROOT-ZIP-RECOVERY-2026-11-13.json").read_text())
intake = json.loads((ROOT / "data/sprites/automated-intake/manifest.json").read_text())
active_islands = json.loads((ROOT / "assets/islands.json").read_text())
active_sites = json.loads((ROOT / "assets/sprites.json").read_text())
report = json.loads((ROOT / "data/sprites/automated-intake/processing-report.json").read_text())

def key(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())

def words(value):
    stop = {"draft", "concept", "review", "historical", "redo", "south", "view",
            "city", "coastal", "sprite", "island", "whole", "v1", "v2", "v3",
            "1180", "1190", "1250", "2026", "11", "13"}
    return {w for w in re.findall(r"[a-z]+", str(value).lower()) if len(w) >= 4 and w not in stop}

# Every imported root ZIP entry has an exact member provenance in the processing report.
archive_categories = {x["path"][:-4]: x["category"] for x in manifest["root_archives"]}
asset_index = {x.get("id"): x for x in intake["assets"]}
source_items = []
for item in report.get("results", []):
    match = re.search(r"/_zip_extract/([^/]+)/", item.get("source", ""))
    if not match or match.group(1) not in archive_categories:
        continue
    group = archive_categories[match.group(1)]
    for p in item.get("pieces", []):
        row = asset_index.get(p.get("id"))
        if p.get("status") == "duplicate":
            source_items.append({"source": item["source"], "category": group,
                                 "status": "duplicate_binary", "asset": None})
        elif row:
            source_items.append({"source": item["source"], "category": group,
                                 "status": p.get("status"), "asset": row})
        else:
            source_items.append({"source": item["source"], "category": group,
                                 "status": "unmatched_intake_id", "asset": None})

island_active = {key(e["name"]): e for e in active_islands}
site_active = {key(e.get("site") or e.get("name")): e for e in active_sites}
all_selected = active_islands + active_sites

def matches(candidate, group):
    target = active_islands if group == "greek_islands" else active_sites
    stem = Path(candidate.get("name", "")).stem
    kw = words(stem)
    found = []
    for e in target:
        subject = e.get("site") or e.get("name") or ""
        token = key(subject)
        if token and token in key(stem):
            found.append(e)
        elif kw and key(stem) in key(subject):
            found.append(e)
        elif kw and len(kw.intersection(words(subject))) >= 1:
            found.append(e)
    return found[:6]

ledgers = []
for entry in source_items:
    art = entry["asset"]
    raw_name = (art or {}).get("name") or Path(entry["source"]).stem
    group = entry["category"]
    linked = matches({"name":raw_name}, group) if art and group != "lowland_terrain" else []
    has_coords = bool(art and art.get("coordinates") and art.get("coordinate_source"))
    approved = bool(art and art.get("approval_for_placement"))
    if entry["status"] == "duplicate_binary":
        disposition = "already_registered_duplicate"
    elif not art:
        disposition = "hold_missing_registry_record"
    elif group == "lowland_terrain":
        disposition = "hold_terrain_geographic_mask_review"
    elif linked:
        disposition = "hold_existing_site_selected_no_unverified_override"
    else:
        disposition = "hold_unmatched_island_or_city_geometry"
    # Do not accept intake coordinates alone as a shoreline footprint.
    if group == "greek_islands" and disposition.startswith("hold_"):
        gate = "verify island outline bbox and medieval construction phase"
    elif group == "coastal_city_revision" and disposition.startswith("hold_"):
        gate = "verify year-specific architecture and water side from south looking north"
    else:
        gate = "verify hydrology and terrain mask before drawing"
    ledgers.append({
        "source": entry["source"], "archive_category": group,
        "name": raw_name, "intake_id": (art or {}).get("id", ""),
        "asset_path": "data/sprites/" + art["asset"] if art and art.get("asset") else "",
        "intake_status": entry["status"],
        "existing_site_candidates": "; ".join(str(e.get("name") or e.get("site")) for e in linked),
        "existing_selected_art": "; ".join(str(e.get("src") or e.get("variant")) for e in linked),
        "has_sourced_coordinates": has_coords,
        "intake_placement_approval": approved,
        "decision": disposition,
        "qa_required": gate,
        "selected_for_review_map": False,
        "historical_certified": False,
        "coastline_verified": False
    })

csv_path = OUT / "recovered-root-sprites-reconciliation.csv"
with csv_path.open("w", newline="", encoding="utf-8") as fp:
    writer = csv.DictWriter(fp, fieldnames=list(ledgers[0]) if ledgers else ["source"])
    writer.writeheader()
    writer.writerows(ledgers)

def load_thumb(path, bounds):
    try:
        with Image.open(path) as im:
            im.thumbnail(bounds, Image.Resampling.LANCZOS)
            result = im.convert("RGBA")
            return result.copy()
    except (OSError, ValueError):
        return None

def build_gallery(group, filename):
    subset = [r for r in ledgers if r["archive_category"] == group and r["asset_path"]]
    w, h, cols = 480, 350, 4
    if not subset:
        return 0
    rows = (len(subset) + cols - 1) // cols
    sheet = Image.new("RGB", (cols*w, rows*h + 62), "#f7f4ed")
    draw = ImageDraw.Draw(sheet)
    draw.text((16, 16), f"{group.replace('_',' ').title()} | recovered draft comparisons | HOLD", fill="#222222")
    for i, record in enumerate(subset):
        x, y = (i % cols) * w, (i // cols) * h + 62
        draw.rectangle((x+5,y+5,x+w-7,y+h-7), outline="#b9b3aa", width=2)
        thumb = load_thumb(ROOT / record["asset_path"], (w-30, h-95))
        if thumb:
            backdrop = Image.new("RGBA", thumb.size, "white")
            backdrop.alpha_composite(thumb)
            sheet.paste(backdrop.convert("RGB"), (x+(w-thumb.width)//2, y+14))
        draw.text((x+13,y+h-65), record["name"][:63], fill="#202020")
        draw.text((x+13,y+h-43), (record["existing_site_candidates"] or "No mapped counterpart")[:60], fill="#555555")
        draw.text((x+13,y+h-21), "PROVISIONAL - NOT SELECTED FOR MAP", fill="#8b3527")
    sheet.save(OUT / filename, optimize=True)
    return len(subset)

island_gallery = build_gallery("greek_islands", "recovered-greek-islands-review.png")
coastal_gallery = build_gallery("coastal_city_revision", "recovered-coastal-cities-review.png")

# The composite preserves the map's current selected variants. A sidecar
# banner explicitly prevents a historical-certification interpretation.
existing = OUT / "outremer-current-composite.jpg"
review_map = OUT / "outremer-recovered-artwork-review.jpg"
map_output = False
if existing.is_file():
    with Image.open(existing) as image:
        base = image.convert("RGB")
    banner = max(76, min(140, base.width // 24))
    canvas = Image.new("RGB", (base.width, base.height + banner), "#f3eee3")
    canvas.paste(base, (0, banner))
    d = ImageDraw.Draw(canvas)
    d.text((22, 15), "CRUSADER MAP | RECOVERED ARTWORK REVIEW", fill="#222222")
    d.text((22, 41), "Current selected map variants retained; 99 recovered PNGs are provisional, not automatically placed.", fill="#7b3024")
    d.text((22, 66), "1180 baseline; later phases gated | compare Greek Islands and coastal-city galleries", fill="#444444")
    canvas.save(review_map, quality=91)
    map_output = True

summary = {
    "status": "review_only_no_unverified_auto_placement",
    "archive_count": len(manifest["root_archives"]),
    "source_piece_records": len(source_items),
    "recovered_new_records": sum(x["asset_path"] != "" for x in ledgers),
    "duplicate_records": sum(x["intake_status"] == "duplicate_binary" for x in ledgers),
    "decisions": dict(Counter(x["decision"] for x in ledgers)),
    "active_island_records_preserved": len(active_islands),
    "active_named_art_records_preserved": len(active_sites),
    "new_named_placements_authorized": 0,
    "island_gallery_items": island_gallery,
    "coastal_gallery_items": coastal_gallery,
    "new_review_composite_created": map_output,
    "outputs": ["recovered-root-sprites-reconciliation.csv",
                "recovered-greek-islands-review.png",
                "recovered-coastal-cities-review.png",
                "outremer-recovered-artwork-review.jpg"],
    "note": "Newly recovered historical redos and whole-island concepts are not enough evidence to replace mapped art. Existing dated selections remain, and every collision is held pending verified architecture, coastline and viewpoint QA."
}
(OUT / "recovered-root-sprites-review-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
