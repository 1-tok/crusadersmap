#!/usr/bin/env python3
"""Side-by-side QA for six unused Greek coastal candidate PNGs.

Does not promote any artwork to the atlas. The existing map registry and
historical placement anchors are preserved.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/greece-coastal-six-review-2026-11-17"
INTAKE = ROOT / "data/sprites/automated-intake/png"
ROWS = [
 ("chania","chania-kydonia-1180-south-to-north-review-v1-4d95cc2ab0bd.png","Sea to north behind city; verify harbor mouth"),
 ("rethymno","rethymno-1180-south-to-north-review-v1-99b78959b807.png","Sea to north behind city"),
 ("heraklion","candia-chandax-heraklion-1180-south-to-north-review-v1-7dbc28850010.png","Candia north harbor, phase-correct fortification"),
 ("rhodes","rhodes-1180-byzantine-south-view-review-v1-229c7d80569c.png","Historical twin-harbor topology; local eastern/northern shore"),
 ("monemvasia","monemvasia-1180-byzantine-south-view-review-v1-215b93402da7.png","Island rock, surrounding sea, landward causeway"),
 ("chios","chios-1180-byzantine-south-view-review-v1-e08fe1f9fa4c.png","Chios town on eastern coast; port to east"),
]
def panel(canvas,path,x,y,label):
    w,h=470,310
    d=ImageDraw.Draw(canvas)
    d.rectangle((x,y,x+w-2,y+h-2),outline=(101,93,77),width=2)
    d.text((x+12,y+12),label,fill=(38,37,30))
    if not path.is_file():
        d.text((x+12,y+55),"MISSING SOURCE - HOLD",fill=(165,48,37))
        return {"present":False}
    with Image.open(path) as src:
        if src.format != "PNG":
            raise ValueError(f"Expected PNG: {path}")
        im=src.convert("RGBA")
        extrema=im.getchannel("A").getextrema()
        source_size=list(im.size)
    im.thumbnail((w-24,h-60),Image.Resampling.LANCZOS)
    bg=Image.new("RGBA",im.size,(228,239,237,255))
    bg.alpha_composite(im)
    canvas.paste(bg.convert("RGB"),(x+(w-im.width)//2,y+46+(h-58-im.height)//2))
    return {"present":True,"dimensions":source_size,"alpha_extrema":list(extrema),
            "transparent_background":extrema[0]==0}
def main():
    registry={r["site"]:r for r in json.loads((ROOT/"assets/sprites.json").read_text())}
    OUT.mkdir(parents=True,exist_ok=True)
    w,h,gap=470,310,16
    canvas=Image.new("RGB",(2*w+3*gap,len(ROWS)*(h+gap)+gap),(248,243,233))
    entries=[]
    for idx,(site,filename,expected) in enumerate(ROWS):
        y=gap+idx*(h+gap)
        selected=registry[site]
        old=ROOT/selected["variant"]
        new=INTAKE/filename
        base=panel(canvas,old,gap,y,site.upper()+" / SELECTED ORIGINAL")
        candidate=panel(canvas,new,w+2*gap,y,site.upper()+" / INTAKE ALTERNATIVE")
        entries.append({
            "site":site,
            "anchor_lon_lat":[selected["lon"],selected["lat"]],
            "selected_original":selected["variant"],
            "alternate_intake_png":new.relative_to(ROOT).as_posix(),
            "old_png":base,"new_png":candidate,
            "expected_water_geometry":expected,
            "map_preview_approved":False,
            "required_checks":["viewpoint","shoreline_side","azure_match","water_mask",
                               "historic_phase","alpha_footprint","map_scale_overlap"]
        })
    contact=OUT/"six-greek-cities-original-versus-candidate.jpg"
    canvas.save(contact,quality=91)
    report={"purpose":"Review six existing Greek coastal candidate sprites",
            "map_production_changed":False,
            "contact_sheet":contact.relative_to(ROOT).as_posix(),
            "note":"Individual PNG comparison is not map-scale coast QA.",
            "entries":entries}
    (OUT/"intake-candidate-qa.json").write_text(json.dumps(report,indent=2)+"\n")
    print("Six Greek city candidates:",sum(x["new_png"]["present"] for x in entries),"present")
if __name__=="__main__":
    main()
