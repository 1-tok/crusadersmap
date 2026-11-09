"""Join the period gazetteer to approved artwork without treating variants as sites."""
import json,re,unicodedata
from pathlib import Path
from collections import Counter
R=Path(__file__).resolve().parent

def norm(s):
 return re.sub('[^a-z0-9]','',unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower())

def build():
 c=json.loads((R/'data/sprites/catalog.json').read_text());h=json.loads((R/'data/manifests/crusader-period/site-history.json').read_text())
 name_counts=Counter(n for row in h['sites'] for n in {norm(row[k]) for k in ('name','modern_name','alternate_name','title')} if n)
 rows=[]
 for s in h['sites']:
  names={norm(s[k]) for k in ('name','modern_name','alternate_name','title') if norm(s[k]) and name_counts[norm(s[k])]==1}
  matched=[]
  for a in c['assets']:
   an={norm(x) for x in [a['site_id'],a['name'],a.get('historical_name','')]+a.get('alternate_names',[])}-{''}
   if names & an or (s['mark'].startswith('P:') and s['mark']==a.get('repo_place_id')):
    if a.get('asset'):matched.append(a)
  approved=[a for a in matched if a.get('approval',{}).get('provisional_map_use') and a.get('geographic_placement_ready') and a.get('technical_qa',{}).get('status')=='pass']
  status='outside-period-reference' if not s['in_scope'] else 'approved-provisional-art' if approved else 'art-needs-placement-review' if matched else 'needs-art-or-symbol-decision'
  rows.append(dict(id=s['id'],site=s['modern_name'],region=s['region'],status=status,asset_ids=[a['id'] for a in matched],occupation=s['occupation'],sieges=s['siege_label'],history_review_required=s['review_required']))
 result=dict(as_of='2026-11-08',scope='147 source gazetteer records; natural and religious markers may need symbols rather than buildings',counts=dict(Counter(e['status'] for e in rows)),catalog_asset_variants=len(c['assets']),catalog_unique_sites=len({e['site_id'] for e in c['assets'] if e.get('asset')}),sites=rows)
 d=R/'data/manifests';(d/'project-sprite-progress.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
 lines=['# Project sprite progress — 2026-11-08','','Crusader Period · 1095–1291. Artwork is provisional; technical approval is not historical certification. Counts are sites, not image variants. This snapshot joins the saved catalog and all 147 source gazetteer records; terrain assets are a separate inventory.','',f"Catalog: {result['catalog_asset_variants']} asset/variant records across {result['catalog_unique_sites']} sites.",'', '| Source-site status | Count |','|---|---|']
 lines += [f'| {k} | {v} |' for k,v in result['counts'].items()]
 lines += ['','## Project chats checked','','- **Add Crusader fortress sprites**: Period map and fortress coverage. Six new Cyprus and Egypt sprites and the recovered Beaufort and Toron cutouts are approved provisionally.','- **Crusader Cities**: Athens correction and double-size Constantinople backed up; Constantinople approved as a placeholder with high-priority replacement flag. Galata/Sykai, Chrysopolis and Chalcedon have approved detail sprites.','- **Crusader terrain**: latest observed update reports six new desert pieces and placement coverage in progress. Their site count is not added to settlement coverage.','','City-only review before this fortress batch: 95 candidates, 32 placement-ready, 1 awaiting geolocation, 62 needing artwork. Six batch04 drafts remain on audit hold. These city counts use a narrower candidate set than the table below.','','## Site-by-site coverage','','| ID | Site | Region | Artwork status | History review |','|---|---|---|---|---|']
 lines += [f"| {e['id']} | {e['site']} | {e['region']} | {e['status']} | {'required' if e['history_review_required'] else 'selected phases reviewed'} |" for e in rows]
 lines += ['','## New releases','', 'Cyprus and Egypt: Nicosia, Kyrenia, St Hilarion, St Catherine’s, Giza and Wadi El Natrun. Mount Amel: Beaufort and Toron. All eight passed compositing QA and have sourced placement points. Historical repaint flags remain active.','', '## Next queue','','Prioritize the mainland gaps: Safed (choose early or 1240s phase), Ajloun (begun 1184; exclude from 1180), Gaza, Bethlehem, Nablus, Tiberias, Banias, Damascus, Latakia and Cilician strongholds. Later constructions need dates in their titles. Natural/sacred markers need an explicit symbol decision rather than automatically generating castles.','', 'Source histories remain selective: 39 sites have recorded siege/campaign entries; 129 histories retain review flags. No siege recorded is not proof none occurred. Rebuild with `python3 build_project_sprite_progress.py`.']
 (d/'PROJECT-SPRITE-PROGRESS.md').write_text('\n'.join(lines)+'\n');print(result['counts'])
if __name__=='__main__':build()
