"""Refresh reviewed city queue against all available catalog variants."""
import json,unicodedata,re
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parent

def key(s):
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
 return re.sub('[^a-z0-9]','',s)

def main():
 p=ROOT/'data/manifests/city-placement-review.json';review=json.loads(p.read_text())
 catalog=json.loads((ROOT/'data/sprites/catalog.json').read_text())
 for e in review['entries']:
  names={key(x) for x in [e['name'],e.get('map_name') or ''] if x}
  matched=[]
  for a in catalog['assets']:
   if not a.get('asset'):continue
   anames={key(x) for x in [a['name'],a['site_id'],a['historical_name']]+a.get('alternate_names',[])}
   mark=e.get('renderer_mark','')
   if names & anames or (mark.startswith('P:') and mark==a.get('repo_place_id')):matched.append(a)
  e['sprite_ids']=[a['id'] for a in matched]
  e['approval_for_new_placement']=any(a['approval_for_placement'] for a in matched)
  e['placement_status']='needs_sprite' if not matched else 'sprite_available' if any(a['geographic_placement_ready'] for a in matched) else 'sprite_available_needs_geolocation'
 review['review_date']='2026-11-08';review['counts']['by_status']=dict(Counter(e['placement_status'] for e in review['entries']))
 p.write_text(json.dumps(review,indent=2,ensure_ascii=False)+'\n')
 lines=['# City sprite placement review','','The atlas spans1095–1571; city artwork and geographic readiness are tracked independently from existing map markers.','',f"{len(review['entries'])} reviewed urban candidates. Status counts: {review['counts']['by_status']}.",'','Greece and Egypt are included; ancient island or urban reference points are not surveyed medieval footprints. Mystras and Mansoura remain excluded from the1180 production queue. Rhodes uses an earlier Byzantine depiction.','']
 for group in dict.fromkeys(e['group'] for e in review['entries']):
  lines += ['## '+group,'','| City / urban site | Sprite status | Provisional1180 placement |','|---|---|---|']
  for e in review['entries']:
   if e['group']==group:lines += [f"| {e['name']} | {e['placement_status'].replace('_',' ')} | {'approved' if e['approval_for_new_placement'] else 'pending artwork / location / phase'} |"]
  lines += ['']
 lines += ['## Placement and review','','Use `../sprites/catalog.json`, `../sprites/placements-1180.geojson` and root `previews/sprite-placement-markup.jpg`. The inset review is in `previews/city-inset-placement-review.jpg`.','', 'All15 newly generated city paintings are in the unified catalog. Damietta is art-approved but has no invented medieval coordinate. Next batch02 contains Patras, Thebes, Rosetta, Tinnis, Bilbeis and a Jaffa variant. Prompts, source PNGs and repaint notes are preserved.','', 'Pelusium/Bilbeis legacy alias conflict remains a separate source-manifest correction; the new Bilbeis sprite uses a documented Bilbeis city point. Tinnis occupation intensity is uncertain. Full per-entry research and uncertainty notes remain in the JSON and sprite manifests.','']
 (p.parent/'CITY-PLACEMENT-REVIEW.md').write_text('\n'.join(lines))
 print(review['counts'])
if __name__=='__main__':main()
