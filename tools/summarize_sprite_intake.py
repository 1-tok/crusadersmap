#!/usr/bin/env python3
"""Generate review-only intake status and non-authoritative category hints.

This does not edit the asset manifest, change any approval, or invent a site.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import re
from pathlib import Path

# Evidence is lexical only; multiple matches remain ambiguous.
KEYWORDS = {
    "castle": {"castle", "citadel", "fortress", "keep"},
    "fortification": {"fortification", "fortified", "watchtower", "bastion"},
    "church": {"church", "cathedral", "chapel"},
    "mosque": {"mosque"},
    "monastery": {"monastery", "monastic", "abbey"},
    "village": {"village", "hamlet"},
    "city": {"city"},
    "town": {"town"},
    "port": {"port", "harbor", "harbour", "quay"},
    "island": {"island", "islet"},
    "mountain": {"mountain", "mountains"},
    "farmland": {"farmland", "farm", "farms", "orchard", "vineyard", "fields", "grain", "olive"},
    "river": {"river", "stream"},
    "marsh": {"marsh", "wetland"},
    "bridge": {"bridge"},
    "road": {"road"},
    "terrain": {"terrain", "scrub", "steppe", "desert", "valley", "foothills", "uplands", "lowlands", "dunes", "rocky", "ridge", "ridges", "escarpment"},
    "coastal_underlay": {"shoreline", "beach", "sandbank", "tidal"},
    "rectangular_underlay": {"underlay", "underlays"},
}


def suggested_categories(name: str) -> list[str]:
    tokens = set(re.findall(r"[a-z]+", name.lower()))
    return sorted(category for category, words in KEYWORDS.items() if tokens & words)


def build_summary(root: Path) -> tuple[dict, str]:
    base = root / "data/sprites/automated-intake"
    registry = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    report = json.loads((base / "processing-report.json").read_text(encoding="utf-8"))
    assets = registry["assets"]
    if not isinstance(assets, list) or not isinstance(report.get("results"), list):
        raise ValueError("intake manifest/report has unexpected structure")

    categories = Counter(str(a.get("category", "unclassified")) for a in assets)
    approvals = Counter(str(a.get("approval", {}).get("status", "unknown")) for a in assets)
    hints = []
    for item in assets:
        if item.get("category", "unclassified") != "unclassified":
            continue
        matches = suggested_categories(str(item.get("name", "")))
        hints.append({
            "id": item["id"],
            "name": item.get("name", ""),
            "asset": item.get("asset", ""),
            "candidate_categories": matches,
            "status": "hint_only_not_classified",
            "review_flags": item.get("review_flags", []),
        })
    hints.sort(key=lambda x: (x["name"], x["id"]))
    blocked = sum(not bool(a.get("geographic_placement_ready")) for a in assets)
    summary = {
        "schema_version": 1,
        "purpose": "Review queue only: no category, date, historical, or geographic approval is changed",
        "intake_assets_total": len(assets),
        "intake_report": {
            "processed_sources": len(report["results"]),
            "newly_registered_this_run": report.get("registered", 0),
            "duplicates_this_run": report.get("duplicates", 0),
            "errors_this_run": report.get("errors", 0),
        },
        "categories": dict(sorted(categories.items())),
        "approval_states": dict(sorted(approvals.items())),
        "missing_geographic_placement": blocked,
        "unclassified_count": len(hints),
        "unclassified_category_hints": hints,
    }
    lines = [
        "# Sprite intake — review summary", "",
        "Generated from the current automated intake registry. Category hints are **not classification**.",
        "Historical accuracy, viewpoint, coastline, coordinates, and print approval remain separate QA gates.",
        "",
        f"- Registered intake artworks: **{len(assets)}**",
        f"- Unclassified artworks: **{len(hints)}**",
        f"- Without verified intake geography: **{blocked}**",
        f"- Sources processed this run: **{len(report['results'])}**",
        f"- New registrations this run: **{report.get('registered', 0)}**",
        f"- Duplicate pixels this run: **{report.get('duplicates', 0)}**",
        f"- Intake errors this run: **{report.get('errors', 0)}**",
        "",
        "## Classification review sample (first 30 alphabetically)",
        "",
        "| Sprite | Candidate categories (filename clue only) |",
        "| --- | --- |",
    ]
    for item in hints[:30]:
        name = str(item["name"]).replace("|", "/").replace("\n", " ")
        categories_text = ", ".join(item["candidate_categories"]) or "none"
        lines.append(f"| {name} | {categories_text} |")
    lines += [
        "", f"Full review queue: {len(hints)} entries in intake-review-summary.json.",
        "Do not apply candidate labels or assign coordinates without checking source imagery and site evidence.",
        "",
    ]
    return summary, "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    summary, markdown = build_summary(root)
    output = root / "data/sprites/automated-intake"
    output.mkdir(parents=True, exist_ok=True)
    (output / "intake-review-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (output / "intake-review-summary.md").write_text(markdown, encoding="utf-8")
    print(markdown)


if __name__ == "__main__":
    main()
