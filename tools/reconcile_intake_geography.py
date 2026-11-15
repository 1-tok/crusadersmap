#!/usr/bin/env python3
"""Reconcile every technical-intake PNG to trusted existing map anchors, without invented points.

Produces a comprehensive ledger and geographically anchored review-only GeoJSON.
Neither result changes production approvals. No map-margin placement is produced.
"""
from __future__ import annotations
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "rebuild-2026-11-12"
OUT.mkdir(parents=True, exist_ok=True)

def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def norm(s):
    return re.sub(r"[^a-z0-9]+", "-", str(s or "").lower()).strip("-")

def starts_subject(stem, alias):
    """Only anchored name at start, optionally preceded by a numeric source index."""
    stem = re.sub(r"^\d+-", "", stem)
    return stem == alias or stem.startswith(alias + "-")

# Explicit distinctions prevent the tempting but false geographic name inferences.
ALIASES = {
    "tartus": "tortosa", "tortosa": "tortosa", "akko": "acre",
    "sur": "tyre", "saidon": "sidon", "antakya": "antioch",
    "kyrenia": "kyrenia", "foca": "phocaea",
}
SHEET = re.compile(r"(?:^|[-_])(?:source[-_]?sheet|contact[-_]?sheet|original[-_]?sheet|sprite[-_]?collection)(?:$|[-_])", re.I)
GENERIC = re.compile(
    r"^(?:b\d+|t\d+|lowland|farming|large|generic|source|batch|original|"
    r"c\d+|a-detailed|\d+-nile|\d+-levant|\d+-greek|\d+-cyprus|"
    r"\d+-mediterranean|\d+-anatolian)"
)
PHASE_WORDS = ("concept", "draft", "repaint", "historical-redo")
BLUEPRINT = ("city", "castle", "fort", "island", "monastery", "harbor", "coastal")

intake = load("data/sprites/automated-intake/placements-review.geojson")["features"]
city_entries = load("assets/sprites.json")
islands = load("assets/islands.json")
site_history = load("data/manifests/crusader-period/site-history.json")["sites"]

# Select longest aliases first; never substring-match a named location inside another word.
city_alias = {}
for city in city_entries:
    token = norm(city.get("site") or city.get("name"))
    if token:
        city_alias[token] = city
    spelled = norm(city.get("name"))
    if spelled:
        city_alias.setdefault(spelled, city)
for site in site_history:
    key = norm(site.get("mark", "").split(":")[-1])
    for alt in (site.get("title"), site.get("name"), site.get("modern_name")):
        alias = norm(alt)
        if not alias or alias in city_alias:
            continue
        city_alias[alias] = {
            "site": key, "name": site.get("title") or site.get("name"),
            "lon": site["coordinates"][0], "lat": site["coordinates"][1],
            "region": site.get("region", "main"),
            "variant": None, "source": "site-history"
        }
for alias, target in ALIASES.items():
    if target in city_alias:
        city_alias[alias] = city_alias[target]

island_alias = {}
for island in islands:
    name = norm(island.get("name"))
    if name:
        island_alias[name] = island
for alias, full in {"kerkyra": "corfu", "ithaki": "ithaca",
                    "leipsoi": "lipsi", "bozcaada": "tenedos",
                    "rheneia": "rhenia"}.items():
    if full in island_alias:
        island_alias[alias] = island_alias[full]

def choose(stem, table):
    candidates = [(len(alias), alias, r) for alias, r in table.items()
                  if len(alias) >= 4 and starts_subject(stem, alias)]
    if not candidates:
        return None
    candidates.sort(key=lambda c: (-c[0], c[1]))
    return candidates[0][1], candidates[0][2]

rows, features = [], []
for feat in intake:
    p = feat["properties"]
    stem = norm(p.get("site_id", ""))
    asset = p.get("asset", "")
    flags = p.get("review_flags", [])
    row = {
        "intake_id": feat.get("id"),
        "name": p.get("site_id"),
        "asset": asset,
        "class": "", "match_site": "", "match_confidence": "",
        "longitude": "", "latitude": "", "placement_source": "",
        "status": "", "reason": "", "production_approved": False,
    }
    if SHEET.search(stem):
        row.update({"class": "source_sheet", "status": "not_drawable",
                    "reason": "master/contact sheet; cutouts must be used instead"})
    elif GENERIC.match(stem):
        row.update({"class": "generic_or_terrain", "status": "regional_pool_review",
                    "reason": "do not assign one arbitrary coordinate; ecology/hydrology-scoped placement"})
    else:
        city = choose(stem, city_alias)
        island = choose(stem, island_alias)
        # Prefer a city when it is a more specific name than the island term.
        selected = "city" if city and (not island or len(city[0]) >= len(island[0])) else ("island" if island else None)
        if selected == "city":
            alias, entry = city
            lon, lat = entry.get("lon"), entry.get("lat")
            if lon is None or lat is None:
                row.update({"class": "named_site", "status": "hold_missing_anchor",
                            "reason": "site matched but no trusted coordinates"})
            else:
                row.update({"class": "named_site", "match_site": entry.get("site", alias),
                            "match_confidence": "existing_named_site_alias",
                            "longitude": lon, "latitude": lat,
                            "placement_source": "assets/sprites.json or site-history.json",
                            "status": "anchored_review_alternate",
                            "reason": "same named site; historical phase and painted coastline still require review"})
        elif selected == "island":
            alias, entry = island
            lon = (entry["w"] + entry["e"]) / 2
            lat = (entry["s"] + entry["n"]) / 2
            row.update({"class": "island", "match_site": entry["name"],
                        "match_confidence": "island_name_and_existing_bbox",
                        "longitude": lon, "latitude": lat,
                        "placement_source": "assets/islands.json existing bounding box",
                        "status": "bbox_center_review_only",
                        "reason": "center of known island bbox is NOT a verified sprite placement or coastline mask"})
        else:
            row.update({"class": "unresolved_named_or_generic", "status": "hold_unmatched",
                        "reason": "no unambiguous existing geographic anchor or regional classification"})
    if "concept" in stem or "draft" in stem or "repaint" in stem:
        row["reason"] += "; source concept/draft/repaint QA required"
    rows.append(row)
    if row["status"] in ("anchored_review_alternate", "bbox_center_review_only"):
        features.append({
            "type": "Feature", "id": row["intake_id"],
            "geometry": {"type": "Point", "coordinates": [row["longitude"], row["latitude"]]},
            "properties": {
                "asset": asset, "site_id": row["match_site"],
                "status": row["status"], "review_only": True,
                "production_approved": False, "coastline_verified": False,
                "draw_on_geographic_map": False,
                "reason": row["reason"], "placement_source": row["placement_source"]
            }
        })

assert len(rows) == len(intake), "every intake sprite must be accounted for"
with (OUT / "intake-geographic-reconciliation.csv").open("w", newline="", encoding="utf-8") as fh:
    writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
(OUT / "intake-geographic-review-candidates.geojson").write_text(
    json.dumps({"type": "FeatureCollection", "features": features}, indent=2) + "\n",
    encoding="utf-8"
)
counts = dict(sorted(Counter(r["status"] for r in rows).items()))
summary = {
    "scope": "1096–1600 master atlas; non-destructive review reconciliation",
    "intake_total": len(rows),
    "matched_geographic_review_candidates": len(features),
    "status_counts": counts,
    "production_placements_changed": 0,
    "map_margin_artwork": 0,
    "note": "Named sites use existing anchors; island candidates use bbox centers for identification only. No candidate is automatically rendered as a second primary.",
    "coastal_azure": [r for r in rows if r["name"] in
                      ("beirut-azure-1096-1600", "tartus-azure-1096-1600")],
    "outputs": [
        "reports/rebuild-2026-11-12/intake-geographic-reconciliation.csv",
        "reports/rebuild-2026-11-12/intake-geographic-review-candidates.geojson",
    ],
}
(OUT / "intake-geographic-reconciliation-summary.json").write_text(
    json.dumps(summary, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(summary, indent=2))
