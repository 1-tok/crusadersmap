#!/usr/bin/env python3
"""Prepare Greece/Egypt painted-city water review: never silently promote artwork."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/greece-egypt-water-review-2026-11-16"
REG = {x["site"]: x for x in json.loads((ROOT / "assets/sprites.json").read_text()) if x.get("cat") == "city"}
PRIORITY = {
    "alexandria": "Mediterranean north; two historic harbor basins",
    "damietta": "Mediterranean north with Nile distributary; do not confuse river with open sea",
    "chania": "Cretan north coast; harbor behind from south-facing camera",
    "rethymno": "Cretan north coast; harbor behind from south-facing camera",
    "heraklion": "Cretan north coast; Candia harbor behind city",
    "rhodes": "Harbor openings follow local peninsula geography",
    "monemvasia": "Island rock and mainland causeway; no detached sea patches",
    "chios": "Eastern Chios town port; local east-coast verification",
    "methoni": "West Peloponnese coastal fortress; local southwest shore",
    "koroni": "Southwest Peloponnese eastern side of Messenian Gulf",
    "thessaloniki": "Thermaic Gulf south of town",
    "corinth": "Inland medieval core; do not invent adjacent maritime waterfront",
    "athens": "Inland urban core; do not paint a sea shoreline at Athens",
    "cairo": "Nile riverfront inland; no marine azure sea",
}
CANDIDATES = {
    "alexandria": "assets/sprites/qa_provisional/coastal-batch05-2026-11-16/alexandria-coastal-city-2026-11-16-review.png",
    "damietta": "assets/sprites/qa_provisional/coastal-batch05-2026-11-16/damietta-coastal-city-2026-11-16-review.png",
}
def thumbnail_tile(canvas, x, y, path, label, width=440, height=280):
    d = ImageDraw.Draw(canvas)
    d.rectangle((x,y,x+width-2,y+height-2), outline=(118,110,90),width=2)
    d.text((x+12,y+12),label[:65],fill=(35,40,46))
    if not path.is_file():
        d.text((x+12,y+55),"FILE MISSING",fill=(158,45,36))
        return False
    with Image.open(path) as src:
        im=src.convert("RGBA")
    im.thumbnail((width-24,height-58),Image.Resampling.LANCZOS)
    surface=Image.new("RGBA",im.size,(224,235,230,255))
    surface.alpha_composite(im)
    canvas.paste(surface.convert("RGB"),(x+(width-im.width)//2,y+48+(height-58-im.height)//2))
    return True

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=[]
    sites=list(PRIORITY)
    w,h,gap=440,280,16
    sheet=Image.new("RGB",(w*2+gap*3,(h+gap)*len(sites)+gap),(248,245,236))
    for i,site in enumerate(sites):
        old=REG.get(site)
        y=gap+i*(h+gap)
        source=ROOT / old["variant"] if old else ROOT / "__missing__"
        candidate=ROOT / CANDIDATES[site] if site in CANDIDATES else ROOT / "__not_submitted__"
        a=thumbnail_tile(sheet,gap,y,source,site.upper()+" / CURRENT SELECTED")
        b=thumbnail_tile(sheet,gap*2+w,y,candidate,site.upper()+" / PROVISIONAL CANDIDATE" if site in CANDIDATES else site.upper()+" / NO NEW PNG SUBMITTED")
        rows.append({
            "site":site,
            "anchor_lon_lat":[old["lon"],old["lat"]] if old else None,
            "existing_asset":old["variant"] if old else None,
            "candidate":CANDIDATES.get(site),
            "existing_png_present":a,"candidate_png_present":b,
            "expected_water_geometry":PRIORITY[site],
            "status":"pending_geographic_mask_and_visual_review" if b else "awaiting_revised_sprite_png",
            "production_approved":False,
            "checks":["historical_phase","water_side_from_south_oblique","map_coast_mask","alpha_seam",
                      "azure_color_difference","harbor_topology","building_on_land","labels_on_top"]
        })
    photo=OUT/"existing-vs-candidate.jpg"
    sheet.save(photo,quality=90)
    report={"scope":"Greece and Egypt existing city art","count":len(rows),
            "status":"staged_review_only","production_changed":False,
            "map_scale_qa_completed":False,"artwork_contact_sheet":photo.relative_to(ROOT).as_posix(),
            "note":"Contact sheet is NOT a geographic composite. Coast-mask QA and human source-image review remain mandatory.",
            "sites":rows}
    (OUT/"placement-gate.json").write_text(json.dumps(report,indent=2)+"\n")
    geo={"type":"FeatureCollection","features":[{
       "type":"Feature","geometry":{"type":"Point","coordinates":r["anchor_lon_lat"]},
       "properties":{"site":r["site"],"selected_sprite":r["existing_asset"],
       "candidate":r["candidate"],"review_only":True,"ready_for_placement":False,
       "water_geometry":r["expected_water_geometry"]}}
       for r in rows if r["anchor_lon_lat"]]}
    (OUT/"review-points.geojson").write_text(json.dumps(geo,indent=2)+"\n")
    print("Staged",len(rows),"cities; candidate PNG present:",sum(r["candidate_png_present"] for r in rows))
if __name__=="__main__":main()
