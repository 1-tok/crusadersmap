"""Mark illustrative family corridors and asset anchors, without changing map rendering."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
from pyproj import Transformer
import frame
R=Path(__file__).resolve().parent;B=R/'data/terrain'
GUIDES=[('palestine-limestone-ridge','Palestine limestone uplands','main',[(35.05,31.50),(35.16,31.85),(35.25,32.20),(35.30,32.60)]),('lebanon-high-massif','Lebanon / Hermon context','main',[(35.86,33.42),(35.90,33.80),(35.91,34.12),(36.10,34.40)]),('taurus-ridge','Taurus range context','main',[(33.90,37.10),(34.75,37.40),(35.60,37.65),(36.10,37.75)]),('pindus-forested-ridge','Pindus range context','aegean',[(20.90,40.00),(21.15,39.70),(21.30,39.50),(21.60,39.10)]),('anatolian-volcanic-massif','Central Anatolia: future map extension','outside_current_frames',[(35.20,38.30),(35.45,38.53),(35.60,38.70)])]
def project(region,lo,la):
 if region=='main':return frame.to_px(lo,la)
 if region!='aegean':return None
 c=frame.INSETS['aegean'];f=Transformer.from_crs('EPSG:4326',c['proj'],always_xy=True);lo0,la0,lo1,la1=c['ext'];xl,_=f.transform(lo0,la1);xr,_=f.transform(lo1,la1);_,top=f.transform((lo0+lo1)/2,la1);_,bottom=f.transform(lo0,la0);w=4800;h=round(w*(top-bottom)/(xr-xl));x,y=f.transform(lo,la);return 190+(x-xl)/(xr-xl)*w,190+(top-y)/(top-bottom)*h

def build():
 p=B/'manifest.json';m=json.loads(p.read_text());features=[];families={g[0]:g for g in GUIDES}
 for e in m['assets']:
  assert hashlib.sha256((B/e['file']).read_bytes()).hexdigest()==e['sha256']
  family=e.get('family',e['id']);g=families[family];lo,la=e['placement']['suggested_anchor_lonlat'];xy=project(g[2],lo,la);width=e['display_width_units'];height=width*e['dimensions_px'][1]/e['dimensions_px'][0];ax,ay=e['anchor_normalized']
  props={'id':e['id'],'asset':'data/terrain/'+e['file'],'family':family,'role':e.get('interlay_role','massif'),'approval':'approved-for-artwork-and-placement-planning','historical_geography_certified':False,'region':g[2],'sheet_anchor_px':list(xy) if xy else None,'top_left_sheet_px':[xy[0]-ax*width,xy[1]-ay*height] if xy else None,'display_width_sheet_px':width,'display_height_sheet_px':height,'anchor_normalized':[ax,ay],'overlap_fraction':[.20,.35],'placement_status':'future-extension-only' if not xy else 'regional-context-anchor-not-individual-stamp-location','notes':'Variants share context anchors; do not stack all at that point. Distribute along reviewed terrain corridors; keep rivers, passes, cities and labels clear.'}
  features.append({'type':'Feature','geometry':{'type':'Point','coordinates':[lo,la]},'properties':props});e['approval']=props['approval'];e['review_status']='technical-checks-passed; visual-review-complete; geographic-accuracy-not-certified'
 for fam,name,region,coords in GUIDES:
  features.append({'type':'Feature','geometry':{'type':'LineString','coordinates':coords},'properties':{'id':'guide-'+fam,'family':fam,'name':name,'region':region,'type':'schematic-family-placement-corridor','approval':'approved-for-placement-planning','geographic_accuracy':'editorial-guide-not-surveyed-ridgeline'}})
 out={'type':'FeatureCollection','approval_authority':'User instruction: add to repo, markup for placement, approve and proceed with next','scope':'Artwork and regional placement planning; not historical/geographic certification or final composition','coordinate_system':'EPSG:4326 longitude,latitude','sheet_px':[frame.W,frame.H],'features':features};(B/'placements.geojson').write_text(json.dumps(out,indent=2)+'\n');p.write_text(json.dumps(m,indent=2)+'\n')
 im=Image.open(R/'previews/crusader-stage3c-colour.jpg').convert('RGB');w,h=im.size;sc=w/frame.W;board=Image.new('RGB',(w+850,h),'#f1e8d2');board.paste(im,(0,0));d=ImageDraw.Draw(board);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',25);small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',20)
 d.text((w+25,30),'TERRAIN PLACEMENT: APPROVED ARTWORK',font=font,fill='#70251e');d.text((w+25,80),str(len(m['assets']))+' pieces / five terrain families',font=small,fill='black')
 for i,(fam,name,region,coords) in enumerate(GUIDES,1):
  yy=160+(i-1)*500;color=['#ab291e','#386d37','#73512b','#315d9c','#76559b'][i-1];d.text((w+25,yy),str(i)+'. '+name,font=font,fill=color)
  ids=[e['id'] for e in m['assets'] if e.get('family',e['id'])==fam]
  for j,ident in enumerate(ids):d.text((w+35,yy+45+j*32),ident,font=small,fill='black')
  d.text((w+35,yy+350),'Outside current frames' if region=='outside_current_frames' else 'Schematic corridor; refine to terrain',font=small,fill=color)
  if region!='outside_current_frames':
   pts=[tuple(v*sc for v in project(region,*c)) for c in coords];d.line(pts,fill=color,width=11)
   for x,y in pts:d.ellipse((x-11,y-11,x+11,y+11),fill=color,outline='white',width=2)
 d.text((w+25,2800),'Not a finished terrain composite.',font=font,fill='#70251e');d.text((w+25,2860),'Distribute variants; preserve valleys and labels.',font=small,fill='black')
 board.save(R/'previews/terrain-placement-markup.jpg',quality=94);assert len(m['assets'])==len({e['id'] for e in m['assets']});print('Approved and marked',len(m['assets']),'assets / five family guides')
if __name__=='__main__':build()
