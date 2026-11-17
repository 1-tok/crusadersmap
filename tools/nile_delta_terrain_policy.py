"""Nile Delta terrain-class policy: narrowly allow flat landcover.

These are editorial classifications inferred from asset names/manifest roles,
NOT visual certifications. Unknown or mixed-class sprites are held for review.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLAT_FARMS = ("river-floodplain-fields",)
FLAT_DRY = ("flat-desert-pavement", "flat-desert-sand-sheet", "salt-flat")
FLAT_DUNES = ()  # dune paintings often contain raised relief
DELTA_GENERIC = ("delta",)  # irrigation shaduf, visually unverified
DELTA_GENERIC_FILES = ("irrigation-shaduf-10c8d38fd3df.png",)
WETLAND_IDS = ("t06-a12", "t06-a13", "t06-b01", "t06-b02")
BANNED_TERMS = ("hill", "mountain", "ridge", "escarpment", "badlands", "cliff",
                "buttress", "upland", "foothill", "karst", "rocky")

def audit():
    manifest = json.loads((ROOT/"data/sprites/terrain-batch06/manifest.json").read_text())
    sprites = {a["id"]:a for a in manifest["assets"]}
    for asset_id in WETLAND_IDS:
        if sprites[asset_id]["terrain_class"] != "wetland":
            raise AssertionError("Misclassified wetland: "+asset_id)
    generic = json.loads((ROOT/"assets/generic2.json").read_text())
    delta_generic = [x for x in generic if x.get("cls") == "delta"]
    for x in delta_generic:
        if x.get("file") not in DELTA_GENERIC_FILES:
            raise AssertionError("Unreviewed Delta generic selected: "+str(x.get("file")))
    dry = json.loads((ROOT/"data/sprites/terrain-batch05/manifest.json").read_text())
    return {
        "scope":"Delta inset only; non-Delta landscape classifications unchanged",
        "classification_basis":"filename/role/manifest metadata; individual pixels not yet inspected",
        "flat_farm_allowlist":list(FLAT_FARMS),
        "flat_desert_allowlist":list(FLAT_DRY),
        "flat_dune_allowlist":[],
        "delta_generic_allowlist":[x["file"] for x in delta_generic],
        "wetland_allowlist":[{"id":k,"file":sprites[k]["file"]} for k in WETLAND_IDS],
        "blocked_mixed_or_relief":sorted(set((
            "badlands-tall-massif","escarpment-tall-deep","dune-field-deep",
            "gravel-wasteland-deep","steppe-basin-deep",
            "eroded-badlands","desert-escarpment","rocky-desert",
            "rocky_upland","mountain","hill","peak",
            "C_FLAT (unverified mixed source CSV set)","C_WASTE",
            "generic2 green, arid, scrub and patch pools in Delta inset"
        ))),
        "terrain_batch05_assets":[{"id":a["id"],"suggested_class":(
            "wetland_provisional" if "reed" in a["id"] else
            "agriculture_provisional" if any(z in a["id"] for z in ("farms","cultivated","terrace")) else
            "relief_or_unknown_hold"
        )} for a in dry["assets"]],
        "terrain_batch06_count_by_original_class":_counts(manifest["assets"]),
        "visual_review_still_required":True,
        "production_approved":False
    }

def _counts(assets):
    out={}
    for a in assets:
        x=a.get("terrain_class","unclassified")
        out[x]=out.get(x,0)+1
    return out

def save(path="reports/nile-delta-terrain-review-2026-11-17/classification-audit.json"):
    obj=audit()
    dest=ROOT/path
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(obj,indent=2)+"\n")
    return obj

if __name__=="__main__":
    save()
