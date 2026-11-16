"""Conservative coastal-city artwork QA for the current composite.
No horizontal mirroring is performed: this can corrupt landmarks and waterfront geometry.
Lists selected artwork and the expected sea side from a south-looking oblique view.
"""
import csv,json,os
from PIL import Image, ImageDraw
import places as PL
from placer import coastal_sprite_held
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
"chios":"local coast geometry required","monemvasia":"island-separated shore",
# Aegean island settlements are not interchangeable with the island outline.
"naxos":"left / west (Chora western port)",
"naxie":"left / west (Chora western port)",
"candia":"back / north (Heraklion northern harbor)",
"heraklion":"back / north (Heraklion northern harbor)",
"rethymno":"back / north (northern Crete)",
"chania":"back / north (northwestern Crete)",
"canea":"back / north (northwestern Crete)",
"ierapetra":"front / south (southern Crete)",
"sitia":"north / east local coastline review required"}
def norm(s):return "".join(c for c in str(s or "").lower() if c.isalnum())
rows=[]
def render_status(e):
    candidates = [p for p in PL.PLACES if p[0] == e.get("region")
                  and abs(p[3] - e.get("lon", 999)) < 0.08
                  and abs(p[4] - e.get("lat", 999)) < 0.08]
    if not candidates:
        return "no_matching_placed_settlement_review"
    for p in candidates:
        if coastal_sprite_held(p[0], p[5], p[7]):
            return "held_existing_geographic_marker"
    return "painted_sprite_selected_orientation_unverified"

for e in entries:
    key=norm(e.get("site"))
    nm=norm(e.get("name"))
    match=next((v for k,v in EXPECTED.items() if norm(k)==key or norm(k)==nm),None)
    if not match and any(t in (key + nm) for t in ("naxos", "naxie", "candia", "heraklion", "rethymno", "chania", "canea", "ierapetra", "sitia")):
        match = "island waterfront: compare painted water with local projected coastline"
    if not match:continue
    art=ROOT/"assets/sprites"/e["file"]
    rows.append({"site":e["site"],"name":e["name"],"source":e.get("source"),
      "asset":e.get("variant"),"expected_water_side":match,
      "viewpoint":"south looking north; no mirroring in renderer",
      "file_exists":art.is_file(),"render_disposition":render_status(e),
      "visual_water_side_verified":False,
      "qa_status":"requires_visual_coastline_orientation_review",
      "note":"Selected file exists and is not auto-flipped; painted shoreline side requires visual human inspection."})
out=ROOT/"reports/rebuild-2026-11-12";out.mkdir(parents=True,exist_ok=True)
with (out/"coastal-city-orientation-audit.csv").open("w",newline="") as fh:
    wr=csv.DictWriter(fh,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
W,H,COLS = 440,310,4
sheet = Image.new("RGB",(W*COLS,H*((len(rows)+COLS-1)//COLS)),(244,237,223))
draw = ImageDraw.Draw(sheet)
for i,row in enumerate(rows):
    ox,oy=(i%COLS)*W,(i//COLS)*H
    status=row["render_disposition"]
    draw.rectangle((ox+2,oy+2,ox+W-3,oy+H-3),outline=(115,105,89),width=2)
    draw.text((ox+12,oy+8),row["name"][:33],fill=(40,34,27))
    draw.text((ox+12,oy+27),("MARKER HOLD" if status.startswith("held") else "SPRITE / UNVERIFIED"),
              fill=((154,51,36) if status.startswith("held") else (92,64,29)))
    draw.text((ox+12,oy+47),("Water expected: "+row["expected_water_side"])[:61],fill=(48,64,82))
    path=ROOT/row["asset"]
    if not path.is_file():
        path=ROOT/"assets/sprites"/next((e["file"] for e in entries if e["site"]==row["site"]),"")
    if path.is_file():
        with Image.open(path) as src:
            im=src.convert("RGBA")
            im.thumbnail((W-24,H-107),Image.Resampling.LANCZOS)
            bg=Image.new("RGBA",im.size,(224,236,234,255))
            bg.alpha_composite(im)
            sheet.paste(bg.convert("RGB"),(ox+(W-im.width)//2,oy+69+(H-107-im.height)//2))
    draw.text((ox+9,oy+H-28),row["site"][:48],fill=(55,49,39))
sheet.save(out/"coastal-all-cities-actual-art-review.jpg",quality=90)
result={"count":len(rows),"verified":0,
        "marker_holds":sum(r["render_disposition"]=="held_existing_geographic_marker" for r in rows),
        "painted_selected_unverified":sum(r["render_disposition"]=="painted_sprite_selected_orientation_unverified" for r in rows),
        "meaning":"Marker hold is not visual certification; sprite presence is not orientation certification.",
        "contact_sheet":"reports/rebuild-2026-11-12/coastal-all-cities-actual-art-review.jpg",
        "rows":rows}
(out/"coastal-city-orientation-audit.json").write_text(json.dumps(result,indent=2)+"\n")
print("Coastal city QA:",result["count"],"sites;",result["marker_holds"],"marker holds;",
      result["painted_selected_unverified"],"painted but unverified")
