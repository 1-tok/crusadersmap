#!/usr/bin/env python3
"""Extract the ten owner-selected Levantine city sprites from pinned incoming ZIPs.

Only the known two archives are admitted; never infer locations by nearby
pixels or auto-flip imagery. The canonical source catalogue is preserved.
This selects generated review-map sprites after build_sprite_assets.py.
"""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
INCOMING = ROOT / "out/coastal-sheet-source"  # archived before assets/sprites is recreated
OUT = ROOT / "assets/sprites"
REGISTRY = ROOT / "assets/sprites.json"
REPORT = ROOT / "reports/rebuild-2026-11-12/coastal-sheet-city-activation.json"
BATCHES = {
    "southern": "e2a628da5c98aa0e6c08a9b8349d7abe0d92a35308c9ba7e792f75fc82606dc1",
    "northern": "8e5a4f7c543f27bfa231f46ac5ec2e534749b62c4e946ddee0619f87b89e29dd",
}
EXPECTED = {
    "southern": {"ascalon", "jaffa", "caesarea", "acre", "tyre"},
    "northern": {"sidon", "byblos", "batroun", "tripoli", "latakia"},
}

def main() -> None:
    records = json.loads(REGISTRY.read_text(encoding="utf-8"))
    by_site = {}
    for rec in records:
        by_site.setdefault(rec["site"], []).append(rec)
    results = []
    for batch, digest in BATCHES.items():
        filename = "crusader_" + batch + "_coast_ACTUAL_spritesheet.zip"
        archive = INCOMING / filename
        if not archive.is_file():
            raise FileNotFoundError("missing owner-uploaded sheet: " + str(archive))
        if hashlib.sha256(archive.read_bytes()).hexdigest() != digest:
            raise ValueError(filename + ": archive checksum differs from approved sheet")
        with zipfile.ZipFile(archive) as z:
            man_name = "crusader_" + batch + "_coast_ACTUAL_spritesheet_manifest.json"
            sheet_name = "crusader_" + batch + "_coast_ACTUAL_spritesheet.png"
            manifest = json.loads(z.read(man_name))
            if manifest.get("sheet") != sheet_name or manifest.get("batch") != batch:
                raise ValueError("wrong sheet/manifest pairing: " + batch)
            if {r["site"] for r in manifest["sprites"]} != EXPECTED[batch]:
                raise ValueError("site manifest mismatch in " + batch)
            sheet = Image.open(io.BytesIO(z.read(sheet_name)))
            if sheet.format != "PNG" or sheet.size != tuple(manifest["sheet_size"]):
                raise ValueError("invalid sheet image dimensions")
            sheet = sheet.convert("RGBA")
            for item in manifest["sprites"]:
                site = item["site"]
                matches = by_site.get(site, [])
                if len(matches) != 1:
                    raise ValueError(site + ": expected one existing geographic site, got " + str(len(matches)))
                rec = matches[0]
                # Existing canonical geographic anchors override approximate ZIP coordinates.
                if rec["region"] != item["region"] or abs(rec["lon"] - item["lon"]) > 0.035 or abs(rec["lat"] - item["lat"]) > 0.035:
                    raise ValueError(site + ": ZIP coordinates conflict with canonical atlas position")
                x,y,w,h = item["sheet_pixel_bbox"]
                if min(x,y) < 0 or min(w,h) < 64 or x+w > sheet.width or y+h > sheet.height:
                    raise ValueError(site + ": invalid sheet bounding box")
                image = sheet.crop((x,y,x+w,y+h))
                alpha = image.getchannel("A")
                if not alpha.getbbox():
                    raise ValueError(site + ": empty transparent cutout")
                dest_name = "coastal-2026-11-16-" + site + "-west-ns.png"
                image.save(OUT/dest_name, optimize=True)
                previous = rec["variant"]
                rec.update({
                    "file": dest_name, "w": w, "h": h,
                    "source": "owner-approved-coastal-sheet-2026-11-16",
                    "variant": "assets/sprites/incoming/" + filename + "#" + site,
                    "review": True,
                    "year": 1228 if site == "sidon" else None,
                    "historical_accuracy_certified": False,
                    "coastline_geographic_qa_pending": True,
                })
                results.append({
                    "site": site, "region": rec["region"],
                    "lon": rec["lon"], "lat": rec["lat"],
                    "from_archive": filename, "bbox": [x,y,w,h],
                    "rendered_asset": dest_name, "previous_primary": previous,
                    "historical_phase_note": ("Sidon Sea Castle is post-1227; do not use for 1180-specific exports."
                                              if site == "sidon" else None),
                    "status": "selected_for_cumulative_map_review",
                })
    if len(results) != 10:
        raise RuntimeError("expected exactly ten selected coastal sprites")
    REGISTRY.write_text(json.dumps(records,indent=1)+"\n",encoding="utf-8")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps({
        "source": "owner-uploaded pinned sprite ZIPs",
        "selected_count": len(results),
        "selection": results,
        "canonical_catalog_untouched": True,
        "visual_coast_fit_certified": False,
        "approved_unchanged": ["beirut","constantinople","ayas","dead_sea"],
    },indent=2)+"\n",encoding="utf-8")
    print("Selected",len(results),"coastal replacements from two uploaded sheets")

if __name__ == "__main__":
    main()
