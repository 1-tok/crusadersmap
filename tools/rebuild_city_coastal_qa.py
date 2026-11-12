"""Conservative coastal-city artwork QA for the current composite.
No horizontal mirroring is performed: this can corrupt landmarks and waterfront geometry.
Lists selected artwork and the expected sea side from a south-looking oblique view.
"""
import csv,json,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
entries=json.loads((ROOT/"assets/sprites.json").read_text())
# At southern camera/looking north: west = image left, east = image right.
EXPECTED={
"acre":"left / west","tyre":"left / west","sidon":"left / west",
"beirut":"left / west","jaffa":"left / west","caesarea":"left / west",
"ascalon":"left / west","ashkelon":"left / west","gaza":"left / west",
"tripoli":"left / west","tartus":"left / west","latakia":"left / west",
"baniyas":"left / west","byblos":"left / west","batroun":"left / west",
"antioch":"not waterfront / river valley","alexandria":"back / north",
"damietta":"river mouth and Mediterranean north","famagusta":"right / east",
"kyrenia":"back / north","limassol":"front / south","paphos":"front-west",
"larnaca":"front-east","rhodes":"local coast geometry required",
"constantinople":"front: Marmara / right: Bosphorus / back: Golden Horn",
"galata-sykai":"front-south: Golden Horn","chrysopolis":"left: Bosphorus",
"chalcedon":"left: Bosphorus / front: Marmara",
"chios":"local coast geometry required","monemvasia":"island-separated shore"}
def norm(s):return "".join(c for c in str(s or "").lower() if c.isalnum())
rows=[]
for e in entries:
    key=norm(e.get("site"))
    nm=norm(e.get("name"))
    match=next((v for k,v in EXPECTED.items() if norm(k)==key or norm(k)==nm),None)
    if not match:continue
    art=ROOT/"assets/sprites"/e["file"]
    rows.append({"site":e["site"],"name":e["name"],"source":e.get("source"),
      "asset":e.get("variant"),"expected_water_side":match,
      "viewpoint":"south looking north; no mirroring in renderer",
      "file_exists":art.is_file(),"visual_water_side_verified":False,
      "qa_status":"requires_visual_coastline_orientation_review",
      "note":"Selected file exists and is not auto-flipped; painted shoreline side requires visual human inspection."})
out=ROOT/"reports/rebuild-2026-11-12";out.mkdir(parents=True,exist_ok=True)
with (out/"coastal-city-orientation-audit.csv").open("w",newline="") as fh:
    wr=csv.DictWriter(fh,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
(out/"coastal-city-orientation-audit.json").write_text(json.dumps({"count":len(rows),"verified":0,"rows":rows},indent=2))
print("Coastal city art entries audited:",len(rows),"visual side QA outstanding")
