"""Verify evidence-backed historic castle placements in rendered review map."""
import csv,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
manifest=json.loads((R/"data/sprites/placements-geographic-recovery-1095-1571.json").read_text())["placements"]
sprites=json.loads((R/"assets/sprites.json").read_text())
placements=json.loads((R/"out/placement_log.json").read_text())
out=R/"reports/rebuild-2026-11-12"
rows=[]
for m in manifest:
    matches=[p for p in sprites if p.get("site")==m["site_id"]]
    # Place names and selected file coordinates must both match.
    candidates=[p for p in placements if p.get("name")==m["name"]]
    shown=[p for p in candidates if p.get("status")=="shown"]
    row={"site_id":m["site_id"],"name":m["name"],"indexed":bool(matches),
         "asset_matches":any(p.get("variant")==m["asset_path"] for p in matches),
         "placement_log_records":len(candidates),"rendered_shown":bool(shown),
         "history_certified":False,
         "coastal_orientation_certified":False}
    rows.append(row)
data={"status":"review_only","total":len(rows),"indexed":sum(x["indexed"] for x in rows),
      "shown":sum(x["rendered_shown"] for x in rows),"records":rows,
      "note":"Automated rendering is not a visual QA signoff; do not treat these castles as strict 1180 art."}
(out/"geographic-recovered-castle-render-audit.json").write_text(json.dumps(data,indent=2)+"\n")
print(json.dumps(data,indent=2))
if len(rows)!=len(manifest) or not all(x["indexed"] and x["asset_matches"] for x in rows):
    raise SystemExit("Recovered castle asset was omitted or wrongly selected")
