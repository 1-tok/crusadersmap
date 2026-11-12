"""Summarize actual composed artwork usage, including transient ZIP imports."""
from collections import Counter
from pathlib import Path
import json,csv

R=Path(__file__).resolve().parents[1]
report=R/"reports/rebuild-2026-11-12"
report.mkdir(parents=True,exist_ok=True)
u=json.loads((R/"out/usage.json").read_text())
pl=json.loads((R/"out/placement_log.json").read_text())
g=json.loads((R/"assets/generic2.json").read_text())
spr=json.loads((R/"assets/sprites.json").read_text())
active=[e for e in pl if e.get("status")=="shown"]
hidden=[e for e in pl if e.get("status")!="shown"]
generic_drawn=u.get("generic",{})
used_g2=[e for e in g if e.get("file") and generic_drawn.get(e["file"],0)>0]
zip_source=[e for e in g if e["src"].startswith("zip:")]
zip_drawn=[e for e in zip_source if generic_drawn.get(e["file"],0)>0]
used_art=set(e.get("sprite") for e in active if e.get("sprite"))
named=[e for e in spr if e.get("variant") in used_art]
result={
 "scope":"Multi-period Crusader atlas 1095–1571 (not a strict 1180 reconstruction)",
 "status":"renderer usage evidence; no separate human visual/period certification",
 "named_art_selected_in_repo":len(spr),
 "named_art_drawn":len(named),
 "named_sites_shown":len([e for e in active if e.get("kind")=="place"]),
 "hidden_items":len(hidden),
 "hidden_names":[e.get("name") for e in hidden],
 "generic_pool_records":len(g),
 "generic_distinct_used":len(used_g2),
 "generic_total_instances":sum(generic_drawn.values()),
 "recent_zip_generic_eligible":len(zip_source),
 "recent_zip_generic_distinct_used":len(zip_drawn),
 "recent_zip_generic_total_instances":sum(generic_drawn.get(e["file"],0) for e in zip_drawn),
 "recent_zip_generic_used_by_category":dict(Counter(e["cls"] for e in zip_drawn)),
 "terrain_distinct_used":len(u.get("terrain",{})),
 "terrain_total_instances":sum(u.get("terrain",{}).values()),
 "island_overlays_used":len(u.get("islands",{})),
 "ship_instances":len(u.get("ships",[])),
 "notes":["Unused source sheets and older variants should not be forced onto map",
          "No geographic accuracy guarantee for generic land sprites",
          "Coastal orientation holds remain in coastal-city-orientation-audit.json"]
}
(report/"sprite-utilization-report.json").write_text(json.dumps(result,indent=2)+"\n")
with (report/"recent-zip-usage.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["source","file","class","instances"])
    w.writeheader()
    for e in zip_source:
        w.writerow({"source":e["src"],"file":e["file"],"class":e["cls"],"instances":generic_drawn.get(e["file"],0)})
print("UTILIZATION",json.dumps(result,indent=2))
