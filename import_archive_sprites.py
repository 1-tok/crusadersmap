"""Package recovered ZIP sprites without changing any archived originals.

The original ZIP has already been safely extracted under data/sprites/archive-1180.
Requires Pillow, NumPy and SciPy. No image generation or repainting is performed.
"""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from sprite_catalog import BASE, ROOT, write, qa

ARCHIVE=BASE/'archive-1180'
ALIASES={'krak_des_chevaliers':'krak-des-chevaliers','montreal_shobak':'montreal-shobak',
         'chateau_pelerin':'chateau-pelerin'}
FLAGS={
 'krak-des-chevaliers':['Concentric defenses may include later phases; not certified for 1180.'],
 'belvoir':['Standalone plan differs from the researched v2; gate, roofs, towers and 1180 construction phase need repaint review.'],
 'kerak':['Long ridge composition is interpretive; review Frankish fabric versus later additions.'],
 'montreal-shobak':['Terraced hill, gate approach and upper works are interpretive; exclude later fabric on repaint.'],
 'montfort':['Main Teutonic castle began in the 1220s; never place in 1180. Full depicted phase is unverified.'],
 'chateau-pelerin':['Templar castle begun in 1218; never place in 1180. Generic hilltop image is not an accurate coastal fortress plan.'],
 'tortosa':['Image has generic river-bridge/fortress motifs; coastal Templar urban layout and cathedral are not established. Repaint required.'],
 'caesarea':['Do not treat Louis IX walls of 1251 as 1180 fabric. Harbor, standing antique arcade and walls need phase-specific repaint.'],
 'sidon':['Review any offshore fortification against the later 13th-century sea castle; 1180 site eligibility does not validate all structures.'],
}


def build():
    original=json.loads((ARCHIVE/'manifest.json').read_text())
    by_slug={e['slug']:e for e in original['sprites']}
    files=sorted((ARCHIVE/'sprites').rglob('*.png'))
    entries=[]
    preview=Image.new('RGB',(1200,230*len(files)),'#eee9dc');draw=ImageDraw.Draw(preview)
    (ARCHIVE/'clean').mkdir(exist_ok=True)
    for i,path in enumerate(files):
        primary=path.parent.name=='primary'
        name=path.stem
        slug=re.sub(r'^(CRS-\d+_|VAR_)','',name)
        slug=re.sub(r'_(sheet|16up)$','',slug)
        original_entry=by_slug[slug]
        site=ALIASES.get(slug,slug)
        ident='archive-'+name.lower().replace('_','-')
        with Image.open(path) as source:
            assert source.mode=='RGBA',path
            a=np.array(source)
        before=int(np.count_nonzero(a[:,:,3]))
        a[a[:,:,3]<16]=0
        labels,_=ndimage.label(a[:,:,3]>0);sizes=np.bincount(labels.ravel())
        keep=sizes>=20;keep[0]=False;a[~keep[labels]]=0;a[a[:,:,3]==0]=0
        im=Image.fromarray(a);bbox=im.getbbox();assert bbox,path
        clipped=any((bbox[0]==0,bbox[1]==0,bbox[2]==im.width,bbox[3]==im.height))
        im=im.crop(bbox);out=Image.new('RGBA',(im.width+16,im.height+16));out.paste(im,(8,8))
        target=ARCHIVE/'clean'/f'{ident}.png';out.save(target)
        later=site in ('montfort','chateau-pelerin')
        notes=[original_entry['notes'],*FLAGS.get(site,[])]
        if not primary:notes.append('Sheet crop: review cut boundaries and detached neighboring artwork; no geometry restored by padding.')
        entries.append(dict(id=ident,site_id=site,name=original_entry['name'],
            category='castle' if original_entry['category'] in ('castle','castle_town') else 'city',
            asset=target.relative_to(BASE).as_posix(),
            source=dict(path=path.relative_to(BASE).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                        archive_manifest_id=original_entry['id'],identity_basis='Original archive manifest and filename; artistic identification remains provisional'),
            archive_original_entry=original_entry,variant='archive-primary' if primary else 'archive-sheet-alternate',
            selection_priority=25 if primary else 5,display_width_units=512,
            anchor_normalized=[.5,(out.height-8)/out.height],technical_qa=qa(target),
            extraction_qa=dict(source_nonzero_alpha=before,cleaned_nonzero_alpha=int(np.count_nonzero(a[:,:,3])),
                alpha_floor=16,minimum_component_pixels=20,source_crop_touches_content=clipped,
                visual_review='reviewed-light-and-dark; clipping/architecture flags retained'),
            availability=dict(from_year=1226 if site=='montfort' else 1218 if later else 1180,
                through_year=1271 if site=='montfort' else 1291 if later else 1180,
                basis='Later-period provisional art window; start is construction commencement, not completion' if later else 'Circa-1180 provisional art'),
            approval=dict(status='approved-provisional-later-period' if later else 'approved-provisional',
                provisional_map_use=True,repaint_later=True,authority='User archive recovery and approval request, 2026-11-08',
                historical_accuracy_certified=False),
            historical=dict(target_year=None if later else 1180,requires_historical_review=True,requires_repaint_review=True,
                accuracy='unverified-archive-artistic-interpretation',notes=notes,
                references=['https://hadashot.iaa.org.il/report_detail_eng.aspx?id=13'] if site=='caesarea' else [])))
        thumb=out.copy();thumb.thumbnail((560,195))
        for col,color in enumerate(['#eee9dc','#253544']):
            x=col*600;y=i*230;draw.rectangle((x,y,x+599,y+229),fill=color)
            preview.paste(thumb,(x+20,y+28),thumb);draw.text((x+10,y+5),ident,fill='black' if col==0 else 'white')
    write(ARCHIVE/'imported.json',dict(schema_version=1,original_manifest='manifest.json',assets=entries))
    preview.save(ROOT/'previews/archive-sprite-qa.jpg',quality=92)
    members=[]
    for p in sorted(ARCHIVE.rglob('*')):
        if p.is_file() and p.parts[len(ARCHIVE.parts)] not in ('clean','imported.json','member-hashes.json'):
            members.append(dict(path=p.relative_to(ARCHIVE).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    write(ARCHIVE/'member-hashes.json',dict(original_zip_sha256='6867d4c3a98a20066fe0bf24e470138e3a0213ba667a654a7a346233a8da7872',members=members))
    print(f'Preserved {len(members)} original archive members; packaged {len(entries)} sprite records')


if __name__=='__main__':build()
