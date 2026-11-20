#!/usr/bin/env python3
"""Audit original Nile paintings at map pixel scale. Does NOT place field sprites.

Fails closed on missing originals. Results are a review/contact sheet and a
candidate inventory only; do not pretend that cartographic correctness is
guaranteed by line-buffer clipping.
"""
from pathlib import Path
import json, hashlib, sys
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BANK=ROOT/"data/sprites/nile-painted-upright-2026-11-17"
CORRIDOR=ROOT/"data/sprites/nile-painted-modular-2026-11-17-v2"
OUT=ROOT/"reports/nile-original-print-scale-audit"
ATLAS=ROOT/"reports/rebuild-2026-11-12/outremer-current-composite.jpg"

def main():
    bank=json.loads((BANK/"manifest.json").read_text())
    corridor=json.loads((CORRIDOR/"manifest.json").read_text())
    atlas=Image.open(ATLAS)
    assert atlas.size==(3240,4320),f"Unexpected existing print-preview dimensions {atlas.size}"
    assert len(bank["assets"])==4 and len(corridor["assets"])==4
    entries=[]
    originals=[]
    for spec in bank["assets"]:
        source=BANK/spec["name"]
        assert source.is_file(),f"Missing original approved artwork: {source}"
        im=Image.open(source).convert("RGBA")
        bbox=im.getchannel("A").getbbox()
        assert bbox, f"Empty source painting {source}"
        entries.append({"name":spec["name"],"type":"original_painted_bank",
            "source":source.relative_to(ROOT).as_posix(),"image_px":list(im.size),
            "painted_bbox_px":list(bbox),"painted_fraction":round(
                (bbox[2]-bbox[0])*(bbox[3]-bbox[1])/(im.width*im.height),4),
            "sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "render_status":"source_intact_not_placed",
            "fit_status":"requires_measured_alluvial_polygon_and_landmark_collision_test"})
        originals.append((spec["name"],im))
    for spec in corridor["assets"]:
        source=CORRIDOR/spec["path"]
        assert source.is_file(),f"Missing original corridor panel: {source}"
        im=Image.open(source).convert("RGBA")
        entries.append({"name":spec["id"],"type":"approved_existing_corridor_panel",
            "source":source.relative_to(ROOT).as_posix(),"image_px":list(im.size),
            "sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
            "render_status":"preserve_existing_placement_do_not_duplicate",
            "fit_status":"prior fit candidate, not Cairo extension certified"})
    # Full-resolution source inspection contact sheet: original sprites are NOT
    # shrunk to 29px or clipped down to a few visible pixels.
    cellw,cellh=650,470
    gallery=Image.new("RGB",(cellw*2,cellh*2),(245,237,220))
    d=ImageDraw.Draw(gallery)
    for i,(name,im) in enumerate(originals):
        x=(i%2)*cellw;y=(i//2)*cellh
        d.rectangle((x+7,y+7,x+cellw-7,y+cellh-7),outline=(125,104,76),width=2)
        show=im.copy()
        show.thumbnail((cellw-42,cellh-73),Image.Resampling.LANCZOS)
        gallery.paste(show,(x+(cellw-show.width)//2,y+38+(cellh-65-show.height)//2),show)
        d.text((x+18,y+15),name,fill=(42,38,32))
    OUT.mkdir(parents=True,exist_ok=True)
    galleryfile=OUT/"original-four-painted-nile-bank-sprites-contact.jpg"
    gallery.save(galleryfile,quality=95)
    qa={"status":"source_scale_audit_only_no_unverified_placement",
        "production_canvas_unchanged":True,
        "previous_29px_derived_field_pilot_rejected":True,
        "no_procedural_field_sprites_used":True,
        "source_sprite_count":len(originals),
        "original_bank_sprites_verified":len(originals),
        "existing_corridor_panels_verified":len(corridor["assets"]),
        "atlas_preview_resolution":list(atlas.size),
        "contact_sheet":galleryfile.relative_to(ROOT).as_posix(),
        "next_gate":"Fit candidate paintings to mapped floodplain polygon with minimum 80% original visible painted pixels; reject any crossing river, desert, city, monument, or label and compare visual size against Cairo structures.",
        "missing_prerequisite":"No validated Cairo alluvial polygon or original-painting real-world footprint exists in the inspected manifests.",
        "assets":entries}
    (OUT/"audit.json").write_text(json.dumps(qa,indent=2)+"\n")
    print("ORIGINAL NILE ART VERIFIED",len(originals),"CORRIDOR PANELS",len(corridor["assets"]))
    print("NO NEW PLACEMENT ACCEPTED without floodplain/site footprint QA")

if __name__=="__main__":main()
