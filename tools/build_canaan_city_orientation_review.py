#!/usr/bin/env python3
"""Create a four-city Canaan coastal orientation review sheet from actual PNGs.

No mirroring, replacement, or placement authorization. Source art and its
provenance are preserved. Emit per-file sidecar and visible comparison sheet.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/canaan-coastal-review/orientation"
CITIES = [("Acre","acre"),("Caesarea","caesarea"),("Jaffa","jaffa"),("Ashkelon / Ascalon","ascalon")]
PANEL_W, PANEL_H = 780, 680

def font(size):
    for p in [ROOT/"fonts"/"DejaVuSans.ttf",Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]:
        if p.exists():return ImageFont.truetype(str(p),size)
    return ImageFont.load_default()

def actual_image(row):
    candidates=[ROOT/"assets/sprites"/row["file"],ROOT/row["variant"]]
    for p in candidates:
        if p.is_file():return p
    return None

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    all_rows=json.loads((ROOT/"assets/sprites.json").read_text())
    lookup={row.get("site","").lower():row for row in all_rows}
    sheet=Image.new("RGB",(PANEL_W*2,PANEL_H*2),(241,232,210))
    draw=ImageDraw.Draw(sheet)
    records=[]
    for i,(name,key) in enumerate(CITIES):
        row=lookup.get(key)
        if not row:raise RuntimeError("No registered site for "+key)
        p=actual_image(row)
        if p is None:raise RuntimeError("Selected source PNG absent for "+key)
        with Image.open(p) as image:
            source_mode=image.mode
            im=image.convert("RGBA")
            original_size=list(im.size)
            alpha=im.getchannel("A")
            alpha_range=list(alpha.getextrema())
            im.thumbnail((PANEL_W-65,PANEL_H-185),Image.Resampling.LANCZOS)
            backdrop=Image.new("RGBA",im.size,(235,246,249,255))
            backdrop.alpha_composite(im)
            px=(i%2)*PANEL_W+(PANEL_W-im.width)//2
            py=(i//2)*PANEL_H+90+(PANEL_H-185-im.height)//2
            sheet.paste(backdrop.convert("RGB"),(px,py))
        ox=(i%2)*PANEL_W;oy=(i//2)*PANEL_H
        draw.rectangle((ox+5,oy+5,ox+PANEL_W-5,oy+PANEL_H-5),outline=(86,66,47),width=3)
        draw.text((ox+24,oy+20),name+" — ORIENTATION HOLD",font=font(27),fill=(127,38,26))
        draw.text((ox+24,oy+58),"N ↑  |  west / Mediterranean expected generally LEFT",font=font(16),fill=(54,61,66))
        draw.text((ox+24,oy+PANEL_H-80),p.relative_to(ROOT).as_posix(),font=font(15),fill=(55,45,35))
        draw.text((ox+24,oy+PANEL_H-51),"Actual selected PNG — no flip / geographic fitting applied",font=font(15),fill=(127,38,26))
        records.append({"city":name,"site_id":key,"selected_file":p.relative_to(ROOT).as_posix(),
            "source_variant":row.get("variant"),"original_px":original_size,"mode":source_mode,
            "alpha_range":alpha_range,"status":"hold_user_reported_water_orientation",
            "expected_global_water_side":"west/left with harbor-specific exceptions",
            "visually_verified_by_script":False,"coastline_fit_verified":False,
            "production_approved":False,"repaint_or_variant_review_required":True,
            "map_asset_changed":False})
    sheet.save(OUT/"four-city-orientation-selected-art.jpg",quality=94)
    (OUT/"city-orientation-review.json").write_text(json.dumps({"purpose":"selected PNG source evidence for four user-flagged cities; requires manual comparison","production_approved":False,"records":records},indent=2)+"\n")
    (OUT/"README.md").write_text("# Canaan coastal city orientation — selected artwork\n\n"
      "This is a four-panel review of the **actual selected source PNGs**, NOT a "
      "coastline-corrected map or production replacement.\n\n"
      "User-flagged on 2026-11-15: Acre, Caesarea, Jaffa and Ascalon/Ashkelon. "
      "All four are on orientation QA hold. No automatic mirroring. "
      "Compare harbors and coastline sides against south-looking-north view, "
      "and validate exact shoreline footprint before accepting replacement.\n")
    print(json.dumps({"generated":len(records),"image":str(OUT/"four-city-orientation-selected-art.jpg"),"status":"review_only"}))

if __name__=="__main__":main()
