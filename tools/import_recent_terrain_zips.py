"""Stage ecologically identifiable transparent terrain from recent ZIP uploads.
Only generic LAND pieces with a readable type in filename/sidecar are used.
Geographically unique sites, rivers, shorelines, labels and atlas sheets stay
in the unresolved ZIP register. Source ZIPs are never modified.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
from PIL import Image
import hashlib,io,json,re,zipfile

ROOT=Path(__file__).resolve().parents[1]
ASSET=ROOT/"assets"
POOL=ASSET/"generic2"
MAN=ASSET/"generic2.json"
REPORT=ROOT/"reports"/"rebuild-2026-11-12"
REPORT.mkdir(parents=True,exist_ok=True)
POOL.mkdir(parents=True,exist_ok=True)
records=json.loads(MAN.read_text())
known={x["src"] for x in records}
seen=set()
for x in records:
    f=POOL/x.get("file","")
    if f.is_file() and x.get("file"):
        seen.add(hashlib.sha256(f.read_bytes()).hexdigest())
source_zips=[]
for folder in (ROOT,ROOT/"assets/sprites/incoming"):
    for p in folder.glob("*.zip"):
        n=p.name.lower()
        if ("terrain" in n or "farming" in n or "rural" in n
            or "batch34" in n or "batch29" in n):
            source_zips.append(p)
# Avoid duplicate archives uploaded to the repository root and intake folder.
archives={}
for p in source_zips:
    archives.setdefault(hashlib.sha256(p.read_bytes()).hexdigest(),p)
source_zips=list(archives.values())

# Never scatter the image if it depicts a geographically unique feature or
# depends on water alignment / correct onshore-offshore perspective.
FORBIDDEN=("river","water","stream","creek","lake","marsh","reed",
           "canal","bridge","coast","shore","harbour","harbor","port",
           "estuary","sea","ship","castle","fortress","citadel","town",
           "city","abbey","church","mosque","temple","lighthouse",
           "atlas","sheet","contact","preview","source","master",
           "map_frame","rectangular_underlay")
CATS=[
 ("patcha",("desert","dune","sand","badland","wasteland","hamada","salt_flat",
            "dry_scrub","gravel","arid","sinai","steppe","transjordan")),
 ("patchg",("farmland","farm","wheat","grain","field","orchard","vineyard",
            "terrac","garden","lowland","cultivat","pasture","crop")),
 ("patchw",("forest","woodland","wooded","pine","cedar","oak","grove",
            "copse","maquis","scrubland")),
 ("patchd",("mountain","cliff","ridge","rocky","limestone","karst",
            "hill","foothill","escarpment","gorge","plateau"))
]
# Sidecars are used only when they clearly refer to the same PNG stem.
def classify(name, desc):
    base=(Path(name).stem+" "+desc).lower().replace("-","_").replace(" ","_")
    if any(w in base for w in FORBIDDEN):
        return None
    for cls,terms in CATS:
        if any(w in base for w in terms):
            return cls
    return None

outcome=Counter()
skipped=[]
added=[]
for arc in source_zips:
    try:
        z=zipfile.ZipFile(arc)
    except (OSError,zipfile.BadZipFile):
        outcome["bad_zip"]+=1
        continue
    with z:
        files=[f for f in z.infolist() if not f.is_dir()]
        descriptions={}
        for f in files:
            if f.filename.lower().endswith(".json") and f.file_size<50000:
                try:
                    val=json.loads(z.read(f))
                    if isinstance(val,dict):
                        stem=Path(f.filename).stem.lower()
                        descriptions[stem]=" ".join(str(val.get(k,"")) for k in
                            ("subject","name","terrain","category","description","region","type"))
                except (json.JSONDecodeError,ValueError,UnicodeDecodeError):
                    pass
        for f in files:
            if not f.filename.lower().endswith(".png"):
                continue
            key=arc.name+":"+f.filename
            stem=Path(f.filename).stem.lower()
            cls=classify(f.filename,descriptions.get(stem,""))
            if cls is None:
                outcome["not_safe_to_scatter"]+=1
                skipped.append(key)
                continue
            if f.file_size>14000000:
                outcome["large_image_skipped"]+=1
                continue
            try:
                payload=z.read(f)
                sha=hashlib.sha256(payload).hexdigest()
                if sha in seen:
                    outcome["duplicate"]+=1
                    continue
                im=Image.open(io.BytesIO(payload)).convert("RGBA")
                if im.width<90 or im.height<70:
                    outcome["too_small"]+=1
                    continue
                alpha=im.getchannel("A")
                if alpha.getextrema()[0]>20:
                    outcome["no_transparency"]+=1
                    continue
                bb=alpha.point(lambda a: 255 if a>18 else 0).getbbox()
                if not bb:
                    outcome["empty"]+=1
                    continue
                im=im.crop(bb)
                if im.width>1200:
                    im=im.resize((1200,round(im.height*1200/im.width)),Image.Resampling.LANCZOS)
                fname="recent-"+sha[:18]+".png"
                im.save(POOL/fname,optimize=True)
                seen.add(sha)
                records.append({"src":"zip:"+key,"file":fname,"cls":cls,
                       "w":im.width,"h":im.height,"reason":"2026-11-12 ZIP terrain; provisional scatter / ecology and alpha review"})
                outcome["imported"]+=1
                added.append({"file":fname,"class":cls,"source":key})
            except Exception as ex:
                outcome["decode_error"]+=1
                skipped.append(key+" : "+str(ex)[:100])
MAN.write_text(json.dumps(records,indent=1))
(REPORT/"recent-terrain-zip-intake.json").write_text(json.dumps({
 "archives":[str(p.relative_to(ROOT)) for p in source_zips],
 "outcomes":dict(outcome),"imported":added,"skipped_count":len(skipped),
 "skipped_example":skipped[:150],
 "limits":"Only identifiable generic land textures are scattered; unique coasts/rivers/fortresses held for placement QA. Uploaded ZIPs remain unaltered."
},indent=2))
print("Recent ZIP terrain scatter:",dict(outcome),"from",len(source_zips),"unique archives")
