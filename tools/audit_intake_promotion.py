"""Non-destructive reconciliation of the 226 technical-PNG intake assets.

This audit NEVER certifies historical accuracy or assigns invented coordinates.
Safe generic artwork stays in the ecological pools. Named/shoreline/river/island
assets remain held until real geographic matching and phase QA are supplied.
Run after the map build so usage counts are measured rather than inferred.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import csv
import json

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports/rebuild-2026-11-12"
OUT.mkdir(parents=True,exist_ok=True)
intake=json.loads((ROOT/"data/sprites/automated-intake/manifest.json").read_text())["assets"]
pool=json.loads((ROOT/"assets/generic2.json").read_text())
usage=json.loads((ROOT/"out/usage.json").read_text())
generic_use=usage.get("generic",{})
pool_by_source={}
for r in pool:
    source=r.get("src","")
    if source.startswith("data/sprites/automated-intake/"):
        pool_by_source[source]=r
SAFE={"green","past","arid","vegg","vegd","vega","rock","ruin",
      "patchg","patchw","patchd","patcha","delta","oasis"}
# These are the only scene types which can be placed from a generic landscape
# pool without allocating a new named historical/geographic site. "town",
# "ships" and architecture fallback require their own rendering contexts.
hold_by_category={"castle":"named_fortification_needs_coordinates_and_phase",
 "fortification":"named_fortification_needs_coordinates_and_phase",
 "landmark":"named_landmark_needs_coordinates_and_phase",
 "monastery":"religious_landmark_needs_coordinates_and_phase",
 "church":"religious_landmark_needs_coordinates_and_phase",
 "bridge":"bridge_needs_river_alignment",
 "port":"port_needs_water_side_and_coordinates",
 "settlement":"settlement_needs_coordinates",
 "village":"settlement_needs_coordinates"}
rows=[]
for r in intake:
    asset="data/sprites/"+r["asset"]
    slot=pool_by_source.get(asset)
    cls=slot.get("cls") if slot else None
    file=slot.get("file","") if slot else ""
    used=generic_use.get(file,0) if file else 0
    if used:
        status="rendered_as_generic"
    elif cls in SAFE:
        status="eligible_generic_not_drawn"
    elif cls=="off":
        status="held_geo_water_or_named_art"
    elif cls and cls.startswith("fb:"):
        status="held_generic_architecture_fallback"
    elif cls=="ship":
        status="ship_pool_needs_water_context"
    elif r.get("category") in hold_by_category:
        status=hold_by_category[r["category"]]
    else:
        status="held_unmatched_or_unclassified"
    rows.append({
       "id":r["id"],"name":r["name"],"category":r.get("category",""),
       "asset":asset,"classification":cls or "",
       "decision":status,"generic_render_instances":used,
       "technical_pass":r.get("technical_qa",{}).get("status")=="pass",
       "historical_certified":bool(r.get("historical_accuracy_certified")),
       "has_verified_coordinates":bool(r.get("coordinates") and r.get("coordinate_source")),
       "placement_approved":bool(r.get("approval_for_placement")),
       "review_note":slot.get("reason","") if slot else "No safe generic class in current map pool",
    })
counts=Counter(r["decision"] for r in rows)
assert len(rows)==226, "Intake manifest changed; verify expected counts"
assert all(r["technical_pass"] for r in rows),"Unexpected failed technical QA"
assert not any(r["placement_approved"] for r in rows), "Placement approvals changed; audit classification"
with (OUT/"intake-promotion-decisions.csv").open("w",newline="",encoding="utf-8") as fh:
    w=csv.DictWriter(fh,fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
summary={
  "scope":"Latest 1095-1571 map render; 226 automated-intake sprites",
  "note":"Technical PNG success does not confer geographic or historical approval. Use actual generic render counts from out/usage.json.",
  "intake_total":len(rows),
  "technical_pass":sum(r["technical_pass"] for r in rows),
  "placement_approved":sum(r["placement_approved"] for r in rows),
  "historical_certified":sum(r["historical_certified"] for r in rows),
  "generic_rendered_distinct":sum(r["decision"]=="rendered_as_generic" for r in rows),
  "generic_rendered_instances":sum(r["generic_render_instances"] for r in rows),
  "generic_eligible_but_unused":sum(r["decision"]=="eligible_generic_not_drawn" for r in rows),
  "status_counts":dict(sorted(counts.items())),
  "holds_keep_originals":True,
  "rendered_sources":[{"name":r["name"],"asset":r["asset"],"times":r["generic_render_instances"]} for r in rows if r["generic_render_instances"]],
  "held_sources":[{"name":r["name"],"asset":r["asset"],"reason":r["decision"]} for r in rows if r["generic_render_instances"]==0],
}
(OUT/"intake-promotion-audit.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
print("INTAKE PROMOTION AUDIT",json.dumps({k:v for k,v in summary.items() if k not in ("held_sources","rendered_sources")},indent=2))
