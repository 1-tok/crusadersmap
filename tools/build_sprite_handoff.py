#!/usr/bin/env python3
"""Build the Crusader Map asset ledger and an all-artwork review gallery.

Read-only for source manifests and PNGs. Outputs review artifacts, not atlas
placement approval or historical certification. Standard library only.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SPRITES = DATA / "sprites"
MANIFESTS = DATA / "manifests"
PREVIEWS = ROOT / "previews"

def load(relative):
    path = ROOT / relative
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (ValueError, UnicodeDecodeError):
        return None

def png_path(path, base="data/sprites"):
    if not path:
        return None
    p = str(path).replace("\\", "/")
    if p.startswith("data/"):
        return p
    return str(Path(base) / p)

def review_record(source, identifier, label, path, kind, *, geographic=None,
                  region=None, layer=None, note="", status="review-library"):
    rel = png_path(path, "data/terrain" if source == "mountain-terrain" else "data/sprites")
    actual = ROOT / rel if rel else None
    return dict(
        source=source, id=str(identifier), label=str(label or identifier),
        path=rel, file_exists=bool(actual and actual.is_file()),
        kind=kind, region=region, layer=layer,
        geometry=geographic, status=status,
        note=note, production_approved=False,
    )

def collect():
    records = []
    proposals = load("data/manifests/SPRITE-UNPLACED-PLACEMENT-PROPOSALS-2026-11-12.json")
    proposals = {x["asset_id"]: x for x in (proposals or {}).get("assets", [])}
    intake = load("data/sprites/automated-intake/manifest.json") or {}
    for a in intake.get("assets", []):
        p = proposals.get(a["id"], {})
        original = p.get("classification", "unclassified")
        kind = "source-master" if original == "source-master" else original
        status = ("source-reference-only" if kind == "source-master" else
                  "review-gallery-and-map-candidate" if p.get("site_id") else
                  "geographic-registration-required")
        records.append(review_record(
            "automated-intake", a["id"], a.get("name"), a.get("asset"), kind,
            geographic=p.get("anchor_candidate_lonlat"), region=p.get("frame"),
            layer=p.get("proposed_layer"),
            status=status, note=p.get("qa_hold", "No geographic location certified")))
        records[-1]["placement_proposal"] = p.get("suggested_regions", [])
        records[-1]["matched_site_id"] = p.get("site_id")
        records[-1]["historical_review_required"] = True
        records[-1]["technical_qa"] = a.get("technical_qa", {}).get("status")
    # Existing located layers: preserve all review alternatives in the gallery;
    # the compositor selects one compatible variant for any one site/year.
    for source, file in (
        ("base-1180", "data/sprites/placements-1180.geojson"),
        ("review-multi-period", "data/sprites/placements-review.geojson"),
        ("review-1180", "data/sprites/placements-review-1180.geojson"),
        ("review-1250", "data/sprites/placements-review-1250.geojson"),
        ("review-1245", "data/sprites/placements-review-1245.geojson"),
    ):
        obj = load(file) or {}
        for feature in obj.get("features", []):
            prop = feature.get("properties", {})
            asset = prop.get("asset_path") or prop.get("asset")
            coords = (feature.get("geometry") or {}).get("coordinates")
            records.append(review_record(
                source, feature.get("id", prop.get("site_id")), prop.get("name"),
                asset, "named-site", geographic=coords,
                region=prop.get("map_region", "main"),
                layer=prop.get("placement_view", "atlas"),
                status="review-position-record",
                note="Preserve phase gates; do not draw multiple variants per site"))
            records[-1]["depiction_year"] = prop.get("depiction_year", prop.get("year"))
            records[-1]["matched_site_id"] = prop.get("site_catalog_id", prop.get("site_id"))
    terrain = load("data/terrain/manifest.json") or {}
    for a in terrain.get("assets", []):
        hint = a.get("placement", {})
        records.append(review_record(
            "mountain-terrain", a["id"], a.get("name"), a.get("file"),
            "mountain-stamp", geographic=hint.get("suggested_anchor_lonlat"),
            region=hint.get("region"), layer="terrain-under-settlements",
            status="regional-review-candidate",
            note="Position on actual mountain corridor, not necessarily at label anchor"))
    t06 = load("data/sprites/terrain-batch06/manifest.json") or {}
    for a in t06.get("assets", []):
        records.append(review_record(
            "terrain-batch06", a["id"], a.get("name"), a.get("file"),
            "terrain-cutout", layer="terrain-under-settlements",
            status="regional-review-candidate",
            note=a.get("region_hint", "Align hydrology and natural landform")))
    rural = load("data/sprites/rural-landscapes/rural_landscape_placement_manifest.json") or {}
    for a in rural.get("sprites", []):
        place = a.get("placement", {})
        records.append(review_record(
            "rural-landscapes", a["id"], a.get("description"), a.get("png_path"),
            "rural-landscape", geographic=place.get("center_lonlat"),
            region=place.get("region"), layer="rural-under-labels",
            status="needs-placement-review",
            note=place.get("review_note", "") or "Check rural landscape footprint"))
    islands = load("data/sprites/greek-islands/placement_manifest.json") or {}
    for a in islands.get("assets", []):
        records.append(review_record(
            "greek-island-overlays", a["id"], a.get("name"),
            a.get("asset_path"), "island-footprint",
            region="aegean", layer="coastline-projected-overlay",
            status="needs-coastline-registration",
            note="Warp using render_bbox_wgs84, not center point placement"))
            # Additional Greek island batches must be discovered by the
            # repository inventory; do not assume the original twelve are all.
    # Final safety net: capture every PNG physically present in the repository,
    # including old archive/city/castle/island batches not referenced above.
    # Physical discovery is review-library inclusion, NEVER automatic map approval.
    known = {x["path"] for x in records if x.get("path")}
    for folder in (SPRITES, DATA / "terrain"):
        if not folder.is_dir():
            continue
        for file in sorted(folder.rglob("*.png")):
            relative = file.relative_to(ROOT).as_posix()
            if relative in known:
                continue
            name = file.stem.lower()
            source = str(file.parent.relative_to(ROOT))
            reference = any(word in name for word in (
                "source_sheet", "original_sheet", "sprite_sheet", "atlas_sheet",
                "contact_sheet", "collage", "combined_sheet"))
            status = "source-reference-only" if reference else "unindexed-review-only"
            records.append(review_record(
                "filesystem-discovery", relative, file.stem, relative,
                "source-master" if reference else "unindexed-artwork",
                status=status,
                note="Discovered on disk without a matched placement record. "
                     "Keep in gallery; must resolve provenance, date and region before use."))
            records[-1]["source_folder"] = source
            known.add(relative)
    return records

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="Exit nonzero when referenced files are absent")
    args = parser.parse_args()
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    PREVIEWS.mkdir(parents=True, exist_ok=True)
    records = collect()
    counts = dict(Counter(r["source"] for r in records))
    unique = {r["path"] for r in records if r["path"]}
    missing = [r for r in records if r["path"] and not r["file_exists"]]
    sources_only = [r for r in records if r["kind"] == "source-master"]
    unlocated = [r for r in records if r["source"] == "automated-intake"
                 and not r["geometry"] and r["kind"] != "source-master"]
    result = {
        "schema_version": 1,
        "purpose": "Review-library coverage; not proof of map rendering",
        "counts_by_source": counts, "record_count": len(records),
        "unique_referenced_file_count": len(unique),
        "missing_referenced_file_count": len(missing),
        "missing_referenced_files": sorted({r["path"] for r in missing}),
        "intake_unlocated_count": len(unlocated),
        "source_master_count": len(sources_only),
        "rules": [
            "All individual PNGs, including unapproved assets, must be accessible in review gallery.",
            "A map usage is not achieved by merely listing an asset in a manifest.",
            "Source sheets are review references, not placeable artwork.",
            "No arbitrary lon/lat for generics; choose empty land polygons and respect environment.",
            "Aegean islands use coastline registration; do not attach their PNG to a town point.",
            "Preserve period restrictions and one primary variant per named site.",
            "Labels, roads and verified hydrography must remain legible above terrain.",
        ],
        "records": records,
    }
    dest = MANIFESTS / "CLAUDE-BUILD-IMAGE-LEDGER.json"
    dest.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    styles = """body{font:15px system-ui,sans-serif;background:#e9e2d3;color:#2e2a23;margin:24px}
    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px}
    article{background:#fffaf0;padding:12px;border:1px solid #c7bbaa;border-radius:6px}
    img{max-width:100%;width:100%;height:145px;object-fit:contain;background:repeating-conic-gradient(#ddd 0% 25%,white 0% 50%) 50%/18px 18px}
    small{display:block;overflow-wrap:anywhere;color:#665b4c}.tag{font-size:12px;font-weight:bold}
    .missing{background:#ffd5ce}.source{opacity:.72}"""
    cards = []
    for a in records:
        cls = "source" if a["kind"] == "source-master" else ("missing" if not a["file_exists"] else "")
        url = "../" + (a["path"] or "")
        remote_path = "https://raw.githubusercontent.com/1-tok/crusadersmap/main/" + (a["path"] or "")
        github_page = "https://github.com/1-tok/crusadersmap/blob/main/" + (a["path"] or "")
        img = (f'<img loading="lazy" src="{escape(url, quote=True)}" '
               f'onerror="this.onerror=null;this.src=&#39;{escape(remote_path, quote=True)}&#39;" '
               f'alt="">'
               if a["file_exists"] else '<div>FILE MISSING</div>')
        cards.append(f'<article class="{cls}">{img}<strong>{escape(a["label"])}</strong>'
                     f'<small>{escape(a["source"])} · {escape(a["kind"])}</small>'
                     f'<small>{escape(a["status"])}</small>'
                     f'<small><a href="{escape(github_page, quote=True)}">Open image in GitHub</a></small>'
                     f'<small>{escape(a["path"] or "NO FILE")}</small></article>')
    html = ('<!doctype html><html><head><meta charset="utf-8">'
            '<title>Crusader Map — all-sprite review gallery</title><style>'+styles+
            '</style></head><body><h1>Crusader Map — all-artwork review</h1>'
            '<p>Includes duplicates, source reference sheets, provisional and unapproved art. '
            'No row proves geographic map placement.</p>'
            f'<p>{len(records)} manifest references · {len(unique)} unique file paths · '
            f'{len(missing)} broken references · {len(unlocated)} intake assets without coordinates.</p>'
            '<div class="grid">'+ "".join(cards)+'</div></body></html>')
    (PREVIEWS / "claude-all-sprites-review.html").write_text(html, encoding="utf-8")
    print(f"Records={len(records)} paths={len(unique)} missing={len(missing)} "
          f"intake_unlocated={len(unlocated)}")
    if missing and args.strict:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
