"""Package desert, road and schematic hydrology artwork. Pillow, NumPy, SciPy required."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
R=Path(__file__).resolve().parent;B=R/'data/landscape-assets'
def weighted_center(weights):
 return float((np.arange(len(weights))*weights).sum()/max(float(weights.sum()),1))

def build():
 p=B/'manifest.json';m=json.loads(p.read_text());preview=Image.new('RGB',(1400,9*390));draw=ImageDraw.Draw(preview);features=[]
 for i,e in enumerate(m['assets']):
  src=B/e['source'];original=Image.open(src).convert('RGBA');a=np.array(original);before=int(np.count_nonzero(a[:,:,3]));a[a[:,:,3]<16]=0;lab,n=ndimage.label(a[:,:,3]>0);sizes=np.bincount(lab.ravel());keep=sizes>=20;keep[0]=False;a[~keep[lab]]=0;a[a[:,:,3]==0]=0;im=Image.fromarray(a);bbox=im.getbbox();assert bbox;im=im.crop(bbox)
  longest=e['target_long_edge_px'];pad=round(longest*.025);ratio=(longest-2*pad)/max(im.size);im=im.resize((max(1,round(im.width*ratio)),max(1,round(im.height*ratio))),Image.Resampling.LANCZOS);out=Image.new('RGBA',(im.width+2*pad,im.height+2*pad));out.paste(im,(pad,pad));file=B/e['file'];out.save(file);alpha=np.array(out)[:,:,3];assert not alpha[:pad].any() and not alpha[-pad:].any() and not alpha[:,:pad].any() and not alpha[:,-pad:].any()
  e.update(dimensions_px=list(out.size),source_dimensions_px=list(original.size),source_trim_xyxy=list(bbox),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),anchor_normalized=[.5,.5] if e['category'] in ['lake','river','road'] else [weighted_center(alpha[out.height-pad-5:out.height-pad,:].sum(axis=0))/out.width,(out.height-pad)/out.height],technical_validation={'mode':'RGBA','padding_px':pad,'source_nonzero_alpha':before,'cleaned_source_nonzero_alpha':int(np.count_nonzero(a[:,:,3])),'alpha_floor':16,'minimum_component_pixels':20})
  if e['category']=='road':e['connection_hints_normalized']={'left':[pad/out.width,weighted_center(alpha[:,pad:pad+5].sum(axis=1))/out.height],'right':[(out.width-pad)/out.width,weighted_center(alpha[:,out.width-pad-5:out.width-pad].sum(axis=1))/out.height],'status':'approximate centerline hints; inspect bends and endpoint elevations before joining'}
  if e['category']=='river':e['connection_hints_normalized']={'north':[weighted_center(alpha[pad:pad+5,:].sum(axis=0))/out.width,pad/out.height],'south':[weighted_center(alpha[out.height-pad-5:out.height-pad,:].sum(axis=0))/out.width,(out.height-pad)/out.height],'status':'approximate; inspect actual channel center at each end'}
  for col,color in enumerate(['#eee4cc','#253544']):
   x=col*700;y=i*390;draw.rectangle((x,y,x+699,y+389),fill=color);thumb=out.copy();thumb.thumbnail((650,335));preview.paste(thumb,(x+(700-thumb.width)//2,y+40),thumb);draw.text((x+18,y+12),e['name'],fill='black' if col==0 else 'white')
  coord=e['placement']['context_anchor_lonlat'];features.append({'type':'Feature','geometry':{'type':'Point','coordinates':coord} if coord else None,'properties':{'id':e['id'],'asset':'data/landscape-assets/'+e['file'],'orientation':e['orientation'],'placement_status':'context-anchor-only-review-required' if coord else 'route-alignment-unassigned','approval':e['approval'],'historical_accuracy_certified':False}})
 m['status']='packaged-technical-validation-passed';p.write_text(json.dumps(m,indent=2)+'\n');(B/'placements.geojson').write_text(json.dumps({'type':'FeatureCollection','scope':'Context anchors and unassigned road segments, not approved geographic geometry','features':features},indent=2)+'\n');preview.save(R/'previews/desert-water-road-assets.jpg',quality=94);assert len(m['assets'])==9;print('Packaged nine RGBA assets; padding and dimensions checked')
if __name__=='__main__':build()
