"""Audit Greek-island art against active 47 and render enlarged Aegean review.
Preserve unregistered artwork. Never promote by center coordinate or filename.
"""
import csv, hashlib, io, json, os, re, zipfile
from collections import Counter, defaultdict
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import cairo
import frame
import islandart
from rough import Region

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"reports"/"greek-islands-review-2026-11-12"
OUT.mkdir(parents=True,exist_ok=True)
ACT=ROOT/"assets"/"islands.json"
ACTIVE=json.loads(ACT.read_text())
IMAGE_PATH=ROOT/"assets"/"islands"
REG=Region.from_lonlat(frame.INSETS["aegean"]["proj"],frame.INSETS["aegean"]["ext"],4800)

def normal_name(s):
    return re.sub("[^a-z0-9]","",s.lower().replace(" / "," "))
def digest(b):return hashlib.sha256(b).hexdigest()
def evidence(entry):
    # Promotion requires an already established render footprint AND
    # explicit coastline verification. An approximate anchor is insufficient.
    p=entry.get("placement") or {}
    bounds=p.get("render_bbox_wgs84") or entry.get("render_bbox_wgs84")
    verified=(entry.get("coastline_verified") is True or
              entry.get("coastline_match") in ("verified","pass","PASS") or
              (entry.get("qa") or {}).get("coastline_match") in ("verified","pass","PASS"))
    return (isinstance(bounds,list) and len(bounds)==4 and
            all(isinstance(v,(int,float)) for v in bounds) and
            bounds[0]<bounds[2] and bounds[1]<bounds[3] and verified and
            p.get("enabled") is True)

activeNames={normal_name(x["name"]):x["id"] for x in ACTIVE}
activeHashes={}
for x in ACTIVE:
    im=IMAGE_PATH/x["file"]
    if im.exists():activeHashes[digest(im.read_bytes())]=x["id"]
records=[]
hashGroups=defaultdict(list)
def add(path,source,blob=None,descriptor=None):
    try:
        b=blob if blob is not None else (ROOT/path).read_bytes()
        sha=digest(b)
        with Image.open(io.BytesIO(b)) as im:
            if im.format!="PNG":return
            dims=list(im.size)
            alpha=("A" in im.getbands())
        name=(descriptor or {}).get("name") or (descriptor or {}).get("subject") or Path(path).stem
        duplicate=activeHashes.get(sha)
        candidate={"path":str(path),"source":source,"name":name,"sha256":sha,
           "size_px":dims,"has_alpha":alpha,"byte_identical_to_active":duplicate,
           "possible_active_name_collision":activeNames.get(normal_name(name)),
           "coastline_registration_verified":evidence(descriptor or {}),
           "decision":"hold_not_geographically_registered"}
        if duplicate:candidate["decision"]="duplicate_active_binary"
        elif not alpha:candidate["decision"]="hold_requires_transparent_PNG"
        elif candidate["possible_active_name_collision"]:candidate["decision"]="hold_duplicate_island_subject"
        records.append(candidate);hashGroups[sha].append(path)
    except Exception as exc:
        records.append({"path":str(path),"source":source,"decision":"read_or_image_error","error":str(exc)[:160]})

root=ROOT/"data/sprites/greek-islands"
manifestByPath={}
for m in root.glob("batch-*/placement_manifest.json"):
    try:
        obj=json.loads(m.read_text())
        for q in (obj.get("sprites") or obj.get("assets") or []):
            for k in ("path","asset_path"):
                if q.get(k):
                    manifestByPath[q[k]]=q
    except Exception:
        pass
# The 47 active are not considered candidates or duplicated by this scan.
actPaths={x["src"] for x in ACTIVE}
for file in sorted(root.glob("batch-*/*.png"))+sorted(root.glob("batch-*/review-unregistered/*.png")):
    rel=str(file.relative_to(ROOT))
    if rel not in actPaths:
        add(rel,"batch_extracted",descriptor=manifestByPath.get(rel))

# Inspect uploaded ZIPs, including late batches not yet unpacked.
zips=list((ROOT/"assets/sprites/incoming").glob("*greek_islands*.zip"))+list(ROOT.glob("*greek_islands*.zip"))
archiveSeen=set()
for z in sorted(zips):
    try:
        za=digest(z.read_bytes())
        if za in archiveSeen:continue
        archiveSeen.add(za)
        with zipfile.ZipFile(z) as arc:
            for info in arc.infolist():
                if info.is_dir() or not info.filename.lower().endswith(".png"):
                    continue
                if info.file_size>20_000_000:continue
                add(str(z.relative_to(ROOT))+":"+info.filename,"zip_intake",arc.read(info))
    except (OSError,zipfile.BadZipFile) as exc:
        records.append({"path":str(z.relative_to(ROOT)),"decision":"bad_zip","error":str(exc)})
# No promotion without verified per-image bbox, pixel/shore identity and
# an explicit enabled placement record. All late candidates in this audit
# remain available for review and are NOT inserted in assets/islands.json.
newEligible=[x for x in records if x.get("coastline_registration_verified")
             and not x.get("byte_identical_to_active")
             and not x.get("possible_active_name_collision") and x.get("has_alpha")]
counts=dict(Counter(x["decision"] for x in records))
dupes=[{"sha256":sha,"paths":p} for sha,p in hashGroups.items() if len(p)>1]
report={"status":"provisional_review; no automatic approval",
    "active_count":len(ACTIVE),"active_expected_drawn":47,
    "archive_unique_count":len(archiveSeen),"candidate_records":len(records),
    "candidate_decisions":counts,"byte_identical_groups":dupes,
    "eligible_for_geographic_promotion":len(newEligible),
    "promotion_note":"No new island is registered unless transparent PNG identity, coastline shape and explicit geographic bbox are verified; user review authorization alone is insufficient.",
    "records":records}
(OUT/"reconciliation.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
with (OUT/"unplaced-artwork.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=["source","name","path","sha256","decision","possible_active_name_collision","byte_identical_to_active"])
    w.writeheader()
    for x in records:w.writerow({k:x.get(k,"") for k in w.fieldnames})

# Render a full 4800px-wide map-coordinate preview; it is *not* a rescaled
# whole-map JPG. It displays registered island artwork in the exact renderer.
surface=cairo.ImageSurface(cairo.FORMAT_ARGB32,REG.w,REG.h)
ctx=cairo.Context(surface)
ctx.set_source_rgb(.77,.84,.85);ctx.paint()
ctx.set_source_rgba(.34,.45,.48,.25);ctx.set_line_width(1.8)
for lo in range(20,31,2):
    p0=REG.ll_px(lo,35);p1=REG.ll_px(lo,41.5)
    ctx.move_to(*p0);ctx.line_to(*p1);ctx.stroke()
for la in range(35,42):
    p0=REG.ll_px(20,la);p1=REG.ll_px(30,la)
    ctx.move_to(*p0);ctx.line_to(*p1);ctx.stroke()
islandart.USED.clear()
islandart.draw(ctx,REG,"colour","aegean")
surface.write_to_png(str(OUT/"aegean-island-placement-review-4800px.png"))
drawn=set(islandart.USED)
missing=[x for x in ACTIVE if x["id"] not in drawn]
(OUT/"render-audit.json").write_text(json.dumps({
    "source":"islandart.draw() at native 4800px inset width",
    "registered":len(ACTIVE),"rendered":len(drawn),
    "missing":[x["name"] for x in missing],
    "corfu_rendered":("CR-GRI-CORFU" in drawn),
    "corfu_policy":"clip to Aegean inset, keep original bbox and scale",
    "note":"Transparent island overlays on a coordinate graticule; coastline precision and historic art not approved",
},indent=2)+"\n")

# Also show the actual last full-atlas Aegean crop for comparison, but
# do NOT claim it includes the Corfu fix until a later whole-map rebuild.
current=ROOT/"reports/rebuild-2026-11-12/outremer-current-composite.jpg"
if current.exists():
    with Image.open(current) as source:
        scale=source.width/frame.W
        bx,by=190,190
        crop=(int(bx*scale),int(by*scale),
              int((bx+REG.w)*scale),int((by+REG.h)*scale))
        source.crop(crop).save(OUT/"previous-atlas-aegean-crop.jpg",quality=92)
md=["# Greek island completion — enlarged review", "",
    "This build intentionally precedes any new full atlas rebuild.",
    f"- Registered geographic overlays: **{len(ACTIVE)}**",
    f"- Rendered: **{len(drawn)}**",
    f"- Corfu present after clip fix: **{'yes' if 'CR-GRI-CORFU' in drawn else 'no'}**",
    f"- Late PNG/ZIP candidate records checked: **{len(records)}**",
    f"- Source ZIPs deduplicated: **{len(archiveSeen)}**",
    f"- Byte-identical candidate groups: **{len(dupes)}**",
    f"- Geographically verified candidates eligible for promotion: **{len(newEligible)}**",
    "",
    "No unverified island paintings were forced onto real coastlines.",
    "The review PNG shows registered overlays on a projected coordinate graticule, not the complete atlas.",
    "",
    "## Candidate status", ""]
md += [f"- {key}: {num}" for key,num in sorted(counts.items())]
md += ["","## Files",
       "- aegean-island-placement-review-4800px.png — enlarged geographic overlay",
       "- previous-atlas-aegean-crop.jpg — old composite Aegean comparison",
       "- reconciliation.json — inspected candidates and hashes",
       "- unplaced-artwork.csv — per-file QA queue",
       "- render-audit.json — actual renderer count and Corfu status",
       "", "Review artwork remains subject to island identity, coastline geometry, alpha edge and historical-building QA."]
(OUT/"README.md").write_text("\n".join(md)+"\n")
print(json.dumps({"registered":len(ACTIVE),"drawn":len(drawn),"missing":[x["name"] for x in missing],
 "candidate_records":len(records),"archives":len(archiveSeen),"duplicates":len(dupes),"promotion_eligible":len(newEligible)},indent=2))
if len(drawn)!=len(ACTIVE):
    raise SystemExit("Existing registered island was not rendered")
