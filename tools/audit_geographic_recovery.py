"""Reconcile held automated-intake art against actual map geography.

Read-only audit: does not manufacture geographic coordinates, alter historical
periods, or place water/coast sprites by filename alone. All held named
candidates with existing verified site anchors are matched to rendered
primaries; alternates stay review-only.
"""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import csv,json,math,re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/geographic-recovery-2026-11-12"
OUT.mkdir(parents=True,exist_ok=True)
ledger=json.loads((ROOT/"data/manifests/CLAUDE-BUILD-IMAGE-LEDGER.json").read_text())["records"]
intake=json.loads((ROOT/"data/sprites/automated-intake/manifest.json").read_text())["assets"]
primaries=json.loads((ROOT/"assets/sprites.json").read_text())
recovered={p["asset_path"]:p for p in json.loads((ROOT/"data/sprites/placements-geographic-recovery-1095-1571.json").read_text())["placements"]}
existing={(p["site"],p["variant"]) for p in primaries}
def norm(s):return re.sub("[^a-z0-9]","",(s or "").lower())
def nearby(lon,lat,threshold=0.012):
    return sorted(
      ({"name":p["name"],"site":p["site"],"variant":p["variant"],
        "separation_degrees":round(math.hypot(lon-p["lon"],lat-p["lat"]),6)}
       for p in primaries if math.hypot(lon-p["lon"],lat-p["lat"])<=threshold),
      key=lambda q:q["separation_degrees"])
indexed={r["path"]:r for r in ledger if r.get("source")=="automated-intake"}
rows=[]
for record in intake:
    path="data/sprites/"+record["asset"]
    source=indexed.get(path,{})
    geo=source.get("geometry")
    match=source.get("matched_site_id")
    kind=source.get("kind") or record.get("category","unclassified")
    close=nearby(*geo) if isinstance(geo,(list,tuple)) and len(geo)==2 else []
    if kind=="source-master": decision="reference_source_only"
    elif kind=="island-outline": decision="island_coastline_registration_required"
    elif kind=="sea-coast": decision="coastline_geometry_water_side_qa_required"
    elif kind=="river-marsh": decision="river_or_marsh_alignment_required"
    elif kind=="ships":decision="water_context_and_historic_rig_qa_required"
    elif kind in ("named-candidate","named-site"):
        decision=("sourced_geography_review_placed" if path in recovered else
                  "site_already_rendered_keep_as_alternate" if close else
                  "unlocated_named_historic_site_hold" if not geo else
                  "geolocated_not_rendered_review_needed")
    elif kind in ("religious","generic-fort","generic-town"):
        decision="architectural_generic_or_historic_site_review"
    else:
        decision="see_intake-promotion-decisions_for_generic_usage"
    rows.append({
      "intake_id":record["id"],"name":record["name"],"kind":kind,
      "source_path":path,"ledger_site_id":match or "",
      "ledger_coordinates":geo,"matched_rendered_primary":close[0] if close else None,
      "decision":decision,"period_review":"1095–1571: visual architectural phase not certified",
      "alpha_technical_pass":record.get("technical_qa",{}).get("status")=="pass",
      "production_approved":False})
count=Counter(x["decision"] for x in rows)
named=[x for x in rows if x["kind"]=="named-candidate"]
close=[x for x in named if x["decision"]=="site_already_rendered_keep_as_alternate"]
miss=[x for x in named if x["decision"] not in ("site_already_rendered_keep_as_alternate", "sourced_geography_review_placed")]
report={
 "scope":"226 sprite intake, 1095-1571 multi-period atlas",
 "status":"Provisional geographical reconciliation; no incorrect or duplicate map placements",
 "intake_records":len(rows),
 "primary_named_sprites_selected":len(primaries),
 "site_matched_named_alternates":len(close),
 "newly_sourced_review_castles":sum(x["decision"]=="sourced_geography_review_placed" for x in rows),
 "unmatched_named_candidates":len(miss),
 "water_and_coast_assets_held":sum(x["decision"] in ("coastline_geometry_water_side_qa_required","river_or_marsh_alignment_required") for x in rows),
 "decision_counts":dict(sorted(count.items())),
 "unmatched_named_sites":[{"name":r["name"],"source_path":r["source_path"],"coordinates":r["ledger_coordinates"]} for r in miss],
 "ready_for_unconditional_production_placement":0,
 "notes":[
   "Near matches are conservative coordinate proximity only: confirm identity, site ID and time period visually before selecting an alternate.",
   "Coastal artwork needs real shoreline registration and viewing side verification; rivers need bank tangent/alignment.",
   "Do not treat ledger review coordinates as new verified historic survey points.",
   "No input PNG or existing primary has been deleted or replaced.",
 ],
 "records":rows
}
(OUT/"geographic-reconciliation.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
with (OUT/"held-geographic-placement-queue.csv").open("w",newline="",encoding="utf-8") as f:
    cols=["intake_id","name","kind","source_path","ledger_site_id","ledger_coordinates",
          "matched_rendered_primary","decision","period_review"]
    w=csv.DictWriter(f,fieldnames=cols);w.writeheader()
    for row in rows:
        w.writerow({k:json.dumps(row[k],ensure_ascii=False) if isinstance(row[k],(list,dict)) else row.get(k,"") for k in cols})
md=["# Geographic recovery — 226 intake assets","",
    "Atlas scope: **1095–1571**. Source paintings remain provisional and require historical/coastline review.",
    f"- Named sprites currently selected in renderer: **{len(primaries)}**",
    f"- Intake named candidates coincident with existing map primary: **{len(close)}**",
    f"- Sourced castle candidates in review registry: **{report['newly_sourced_review_castles']}**",
    f"- Remaining named candidates without a map primary or sourced anchor: **{len(miss)}**",
    f"- Shoreline/river assets withheld pending geometric alignment: **{report['water_and_coast_assets_held']}**",
    "- New unconditional production placements: **0** — duplicate and orientation QA take priority.",
    "", "## Decisions", ""]
md.extend(f"- {k}: {v}" for k,v in sorted(count.items()))
md.extend(["","## Named candidates still needing coordinates or primary selection",""])
md.extend(f"- {r['name']}: {r['decision']}" for r in miss)
md.extend(["","## Promotion policy","",
 "Retain all existing primary sprites. New historic site artwork is never located by guesswork.",
 "River/coastal images cannot be scattered until their embedded water edges match the relevant geographic bank or shoreline.",
 "A review overlay can be built once precise coastline and river attachments are recorded.",
 "See `held-geographic-placement-queue.csv` for each intake source and QA status."])
(OUT/"README.md").write_text("\n".join(md)+"\n")
print(json.dumps({k:v for k,v in report.items() if k not in ("records","notes","unmatched_named_sites")},indent=2))
if len(rows)!=226:raise SystemExit("Intake roster changed; cannot certify report without reconciliation")
