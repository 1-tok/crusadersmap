#!/usr/bin/env python3
"""Geographic *review* proof of staged island paintings, not final raster georegistration.

Original 47 coastline-registered art remain in the production renderer. This script
selects one non-superseded candidate per unrepresented island, uses a small visual
stamp pinned at a documented center, and puts replacement art in a comparison
sheet. No review stamp is written to assets/islands.json.
"""
import json, re, csv, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "island-review-2026-11-15"
OUT.mkdir(parents=True, exist_ok=True)
read = lambda p: json.loads((ROOT / p).read_text())
active = read("assets/islands.json")
records = read("data/manifests/ISLAND-BATCHES-25-31-RECONCILIATION-2026-11-15.json")["entries"]
markers = read("data/sprites/review/island-batches-25-31-pins-2026-11-15.geojson")["features"]
processing = read("data/sprites/automated-intake/processing-report.json")["results"]
batch3 = read("data/sprites/greek-islands/batch-03/placement_manifest.json")["sprites"]
def clean(v): return re.sub(r"[^a-z0-9]", "", v.lower())
active_names = {clean(r["name"]) for r in active}
pins = {clean(f["properties"]["island"]): f["geometry"]["coordinates"] for f in markers}
source_by_id = {}
# Processing report's 'duplicate' entries intentionally omit their asset path.
# The canonical intake-review index preserves the original imported file.
review_index = read("data/sprites/automated-intake/intake-review-summary.json")
for item in review_index.get("unclassified_category_hints", []):
    if item.get("asset"):
        source_by_id[item["id"]] = ROOT / "data/sprites" / item["asset"]
for entry in processing:
    for piece in entry.get("pieces", []):
        if piece.get("asset"):
            source_by_id[piece["id"]] = ROOT / "data/sprites" / piece["asset"]
selected = {}
replacements = []
for r in records:
    path = source_by_id.get(r["intake_id"])
    item = dict(island=r["island"], path=path, anchor=pins.get(clean(r["island"])),
                intake_id=r["intake_id"], source_batch=r["batch"])
    if clean(r["island"]) in active_names: replacements.append(item)
    else: selected[clean(r["island"])] = item
for r in batch3:
    key = clean(r["name"])
    if key in active_names or key in selected: continue
    selected[key] = dict(island=r["name"],path=ROOT/r["path"],
                         anchor=r.get("candidate_anchor_lonlat"),
                         source_batch=3,intake_id=r["id"])
# Earlier concept/draft records remain in a separate review-only queue; sources are
# not automatically preferred over later selected artwork.
queue = read("reports/greek-islands-review-2026-11-12/deduplicated-review-queue.json")["deduplicated_review_queue"]
def simplify(v):
    v = re.sub(r"^\d+[_-]", "", v)
    v = re.sub(r"[-_](draft|concept)$", "", v, flags=re.I)
    v = re.sub(r"-[0-9a-f]{12}$", "", v)
    return v
for rec in queue:
    if rec["source"] != "zip_intake" and rec["source"] != "batch_extracted": continue
    name = simplify(rec["name"])
    key = clean(name)
    if key in selected or key in active_names or "sheet" in key or "unassigned" in key: continue
    source = rec["path"].split(":")[0] if ":" in rec["path"] else rec["path"]
    if ":" in rec["path"]: continue # ZIP member has no independent renderable path
    path = ROOT / source
    if path.exists(): selected[key] = dict(island=name,path=path,anchor=None,source_batch="earlier",intake_id=None)

# Two region proofs. Fixed geographic long/lat frames are legible rather than
# pretending that artwork image dimensions are registered island footprints.
frames = {
  "aegean": (21.0, 34.2, 30.5, 41.6),
  "ionian": (18.5, 35.2, 24.2, 41.5),
}
font = ImageFont.load_default()
results = []
def panel(region, bounds):
    W,H=4000,3100
    west,south,east,north=bounds
    im=Image.new("RGB",(W,H),(66,164,191))
    d=ImageDraw.Draw(im)
    def project(lon,lat): return (int((lon-west)/(east-west)*(W-160)+80),int((north-lat)/(north-south)*(H-160)+80))
    for lon in range(int(west)+1,int(east)+1):
        x,_=project(lon,south);d.line((x,0,x,H),fill=(94,179,196),width=2)
    for lat in range(int(south)+1,int(north)+1):
        _,y=project(west,lat);d.line((0,y,W,y),fill=(94,179,196),width=2)
    # Existing registered footprint outlines and native assets serve as
    # geographic context. They are not displaced by provisional paintings.
    for a in active:
        x0,y1=project(a["w"],a["s"]);x1,y0=project(a["e"],a["n"])
        if x1<0 or x0>W or y1<0 or y0>H: continue
        xa,ya=max(0,x0),max(0,y0)
        # Historical active overlay; retain longitude/latitude footprint.
        old = ROOT / "assets" / "islands" / a["file"]
        if old.is_file() and x1>x0 and y1>y0 and x1-x0<3000 and y1-y0<3000:
            try:
                base=Image.open(old).convert("RGBA")
                base=base.resize((max(2,x1-x0),max(2,y1-y0)),Image.Resampling.LANCZOS)
                im.paste(base,(x0,y0),base)
            except Exception:
                d.rectangle((xa,ya,min(W-1,x1),min(H-1,y1)),outline=(239,227,177),width=3)
        else:
            d.rectangle((xa,ya,min(W-1,x1),min(H-1,y1)),outline=(239,227,177),width=3)
        px,py=project((a["w"]+a["e"])/2,(a["s"]+a["n"])/2)
        d.text((px+5,py),a["name"],fill=(255,255,255),font=font,stroke_width=2,stroke_fill=(27,73,91))
    eligible=[]
    for a in selected.values():
        if not a["anchor"]: continue
        # Overlapping inset bounds must not draw one island twice.
        # Assign all Aegean/Saronic/Peloponnesian islands east of 21E to
        # the Aegean proof; draw western Ionian islands only on Ionian.
        lon,lat=a["anchor"]
        designated = "ionian" if lon < 21.0 else "aegean"
        if region != designated: continue
        x,y=project(*a["anchor"])
        if not (40<x<W-40 and 40<y<H-40): continue
        eligible.append((a,x,y))
    # Paint a modest floating artwork thumbnail at the marker. Every thumbnail
    # is linked to the location via a line; it MUST NOT be treated as a coast mask.
    eligible.sort(key=lambda x:(x[2],x[1]))
    placed_rects=[]
    for a,x,y in eligible:
        path=a["path"]
        if not path or not path.is_file():
            results.append(dict(island=a["island"],region=region,status="missing_png_binary",path=str(path)))
            continue
        try:
            sprite=Image.open(path).convert("RGBA")
            sprite.thumbnail((178,146),Image.Resampling.LANCZOS)
        except Exception as exc:
            results.append(dict(island=a["island"],region=region,status="unreadable_png",error=str(exc)));continue
        tw,th=sprite.size
        # choose first feasible local card among alternating offsets
        choices=[(x+25,y-145),(x-205,y-145),(x+25,y+20),(x-205,y+20),(x-90,y-190)]
        def overlap(rect):return any(rect[0]<b[2]+6 and rect[2]>b[0]-6 and rect[1]<b[3]+6 and rect[3]>b[1]-6 for b in placed_rects)
        card=None
        for cx,cy in choices:
            rect=(max(4,min(W-tw-8,cx)),max(25,min(H-th-22,cy)),0,0)
            rect=(rect[0],rect[1],rect[0]+tw+6,rect[1]+th+18)
            if not overlap(rect):card=rect;break
        if card is None:
            cx,cy=choices[0];cx=max(4,min(W-tw-8,cx));cy=max(25,min(H-th-22,cy));card=(cx,cy,cx+tw+6,cy+th+18)
        placed_rects.append(card)
        d.line((x,y,(card[0]+card[2])//2,(card[1]+card[3])//2),fill=(251,226,151),width=3)
        d.ellipse((x-7,y-7,x+7,y+7),fill=(255,242,185),outline=(33,53,69),width=2)
        d.rectangle(card,fill=(244,235,212),outline=(54,56,57),width=3)
        im.paste(sprite,(card[0]+3,card[1]+3),sprite)
        d.text((card[0]+4,card[3]-14),a["island"][:26],fill=(27,38,44),font=font)
        results.append(dict(island=a["island"],region=region,status="review_thumbnail_pinned_not_georegistered",path=str(path.relative_to(ROOT)),anchor=a["anchor"]))
    d.rectangle((0,0,W,42),fill=(20,49,70))
    d.text((20,14),region.upper()+" — island ARTWORK REVIEW (thumbnail/leader-line positions; NOT coastline-registered)",fill="white",font=font)
    out=OUT/(region+"-island-artwork-review.jpg")
    im.save(out,quality=89)
    return len(eligible)
counts={k:panel(k,v) for k,v in frames.items()}
# Contact sheet for the previously represented islands: new art MUST NOT
# be stacked atop their existing geographic overlays.
contact=Image.new("RGB",(1400,max(280,((len(replacements)+3)//4)*240)),(236,232,219))
cd=ImageDraw.Draw(contact)
for i,a in enumerate(replacements):
    x=(i%4)*350;y=(i//4)*240
    if a["path"] and a["path"].is_file():
        try:
            s=Image.open(a["path"]).convert("RGBA");s.thumbnail((320,195))
            contact.paste(s,(x+10,y+5),s)
        except Exception:pass
    cd.text((x+12,y+205),a["island"]+" — alternative, not active",fill=(27,36,41),font=font)
contact.save(OUT/"island-replacement-comparison.jpg",quality=89)
summary={"legacy_active":len(active),"newer_candidate_records":len(records),
"newer_replacements_held":len(replacements),"selected_unrepresented_subjects":len(selected),
"review_thumbnails":sum(x["status"]=="review_thumbnail_pinned_not_georegistered" for x in results),
"missing_png":[x for x in results if x["status"]=="missing_png_binary"],
"region_candidate_counts":counts,
"not_rendered_subjects":[x["island"] for x in selected.values() if not x["anchor"]],
"results":results,"note":"Review stamps are not coast-mask placements. Existing active renderer unmodified."}
(OUT/"render-audit.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps({k:v for k,v in summary.items() if k not in ("results","not_rendered_subjects","missing_png")},indent=2))
