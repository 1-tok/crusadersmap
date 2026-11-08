"""Inventory all sprites, project placement points, and mark the current map preview.
Requires Pillow and pyproj. Approval is for artwork/placement planning, not historical certification.
"""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
import frame
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'data/sprites'

def build():
 old=json.loads((BASE/'manifest.json').read_text())['sprites']
 new=json.loads((BASE/'historical-1180/manifest.json').read_text())['assets']
 preferred={e['legacy_sprite_id']:e['id'] for e in new}
 preferred['CAST-001']='CAST-001-STANDALONE'
 features=[]
 for e in old:
  ident=e['id'];p=e['placement'];lon,lat=p['longitude'],p['latitude']
  path='data/sprites/'+e['asset'];group='CAST-001' if ident=='CAST-001-STANDALONE' else ident
  features.append(feature(ident,e['name'],group,path,lon,lat,e['anchor_normalized'],512,e['dimensions_px'],preferred.get(group,group)==ident,'legacy-artistic-interpretation'))
 for e in new:
  lon,lat=e.get('proposed_placement_coordinates',e['coordinates'])
  features.append(feature(e['id'],e['id'].split('-1180')[0].title(),e['legacy_sprite_id'],'data/sprites/historical-1180/'+e['file'],lon,lat,e['anchor_normalized'],e['display_width_units'],e['dimensions_px'],True,'period-informed-specialist-review-pending'))
 out={'type':'FeatureCollection','coordinate_system':'EPSG:4326; longitude,latitude','sheet':{'width':frame.W,'height':frame.H,'projection':frame.PROJ,'pixel_origin':'upper-left'},'approval':{'status':'approved-for-map-artwork-and-placement-planning','authority':'User request: Commit all sprites to repo, markup location for placement on map and approve','historical_certification':False,'approved_scope':'All 14 assets retained; eight preferred site variants selected. Positions and widths are placement instructions; final collision-aware composition is pending.'},'features':features}
 (BASE/'placements.geojson').write_text(json.dumps(out,indent=2)+'\n')
 im=Image.open(ROOT/'previews/crusader-stage3c-colour.jpg').convert('RGB');w,h=im.size;scale=w/frame.W
 board=Image.new('RGB',(w+650,h),(246,240,224));board.paste(im,(0,0));d=ImageDraw.Draw(board)
 font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
 small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
 d.text((w+24,30),'APPROVED SPRITE PLACEMENT',font=font,fill='#6b2219')
 d.text((w+24,70),'Eight sites; 14 retained sprite variants',font=small,fill='black')
 chosen=[f for f in features if f['properties']['preferred']]
 for i,f in enumerate(chosen,1):
  p=f['properties'];x,y=p['sheet_anchor_px'];x*=scale;y*=scale
  d.ellipse((x-18,y-18,x+18,y+18),fill='#a22220',outline='white',width=3)
  d.text((x-7,y-13),str(i),font=font,fill='white')
  yy=130+(i-1)*145;d.text((w+24,yy),f"{i}. {p['name']}",font=font,fill='black')
  lon,lat=f['geometry']['coordinates'];d.text((w+24,yy+35),f'{lon:.3f} E, {lat:.3f} N',font=small,fill='black')
  d.text((w+24,yy+65),f"Width: {p['display_width_sheet_px']} sheet pixels",font=small,fill='black')
  d.text((w+24,yy+95),p['sprite_id'],font=small,fill='#6b2219')
 d.text((w+24,1360),'Markers show ground anchors, not city extents.',font=small,fill='black')
 d.text((w+24,1400),'Artwork approved; historical flags preserved.',font=small,fill='black')
 d.text((w+24,1440),'Tripoli marker uses the coastal al-Mina anchor.',font=small,fill='black')
 board.save(ROOT/'previews/sprite-placement-markup.jpg',quality=94)
 assert len(features)==14 and len(chosen)==8
 print('Checked 14 sprite files and hashes; marked 8 preferred site anchors')

def feature(ident,name,group,path,lon,lat,anchor,width,dimensions,preferred,history):
 file=ROOT/path;im=Image.open(file);assert list(im.size)==dimensions and im.mode=='RGBA'
 x,y=frame.to_px(lon,lat);height=width*im.height/im.width
 return {'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},'properties':{'sprite_id':ident,'name':name,'site_group':group,'asset':path,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'region':'main','preferred':preferred,'approval':'approved-for-map-artwork-and-placement-planning','historical_review':history,'coordinates_verified':False,'anchor_normalized':anchor,'sheet_anchor_px':[round(x,3),round(y,3)],'display_width_sheet_px':width,'display_height_sheet_px':round(height,3),'top_left_sheet_px':[round(x-anchor[0]*width,3),round(y-anchor[1]*height,3)],'placement_notes':'Geographic ground anchor. Keep one preferred variant per site. Avoid label collisions; use leader lines if moved. Tripoli uses proposed coastal al-Mina coordinate.' if group=='CITY-004' else 'Approximate source coordinate; ground anchor, not surveyed site boundary. Avoid label collisions; use leader lines if moved.'}}

if __name__=='__main__':build()
