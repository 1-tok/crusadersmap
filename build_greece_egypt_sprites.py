"""Package preserved Greece/Egypt source paintings without changing painted content."""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'data/sprites/greece-egypt-1180'
def write(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def build(base=BASE):
 BASE=base
 m=json.loads((BASE/'manifest.json').read_text());preview=Image.new('RGB',(1200,330*len(m['assets'])),'#e9e3d8');d=ImageDraw.Draw(preview);hashes=set()
 for i,e in enumerate(m['assets']):
  src=BASE/e['source'];im=Image.open(src);assert im.mode=='RGBA';a=im.getchannel('A');bounds=a.getbbox();assert bounds and a.getextrema()[0]==0
  im=im.crop(bounds);w=1024;pad=26;inner=w-2*pad;im=im.resize((inner,round(im.height*inner/im.width)),Image.Resampling.LANCZOS)
  out=Image.new('RGBA',(w,im.height+pad*2));out.paste(im,(pad,pad));out.save(BASE/e['file'])
  alpha=out.getchannel('A');box=alpha.getbbox();assert min(box[0],box[1],out.width-box[2],out.height-box[3])>=pad
  pixelhash=hashlib.sha256(out.width.to_bytes(4,'big')+out.height.to_bytes(4,'big')+out.tobytes()).hexdigest();assert pixelhash not in hashes;hashes.add(pixelhash)
  e.update(asset_path='data/sprites/'+BASE.name+'/'+e['file'],source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),sha256=hashlib.sha256((BASE/e['file']).read_bytes()).hexdigest(),pixel_sha256=pixelhash,dimensions_px=list(out.size),anchor_normalized=[.5,(out.height-pad)/out.height],visual_footprint=dict(canvas_px=list(out.size),painted_bounds_xyxy=list(box),display_width_atlas_px=512,display_height_atlas_px=512*out.height/out.width,geographic_scale=False),technical_qa=dict(status='pass',mode='RGBA',alpha_extrema=list(alpha.getextrema()),transparent_padding_px=pad),visual_review='reviewed on light and dark; provisional; see repaint_flags')
  thumb=out.copy();thumb.thumbnail((550,285));y=i*330;preview.paste(thumb,(20,y+15),thumb);d.rectangle((600,y,1200,y+330),fill='#17283a');preview.paste(thumb,(620,y+15),thumb);d.text((20,y+310),e['name'],fill='black')
 write(BASE/'manifest.json',m);preview.save(ROOT/('previews/'+BASE.name+'-qa.jpg'),quality=93)
 features=[dict(type='Feature',id=e['id'],geometry=dict(type='Point',coordinates=e['coordinates']),properties={k:e[k] for k in ['site_id','name','asset_path','map_region','map_layers','anchor_normalized','visual_footprint','approval_for_placement','coordinate_evidence','repaint_flags']}) for e in m['assets'] if e['approval_for_placement'] and e['coordinates']]
 write(BASE/'placements-1180.geojson',dict(type='FeatureCollection',coordinate_system='EPSG:4326',note='Route each feature to its map_region: main, aegean or delta. Do not project inset cities through mainland frame.to_px. Any city lacking grounded coordinates is omitted.',features=features))
 print(f'{len(m["assets"])} unique PNGs validated; {len(features)} sourced provisional geographic anchors')
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--batch',default=BASE.name)
 folder=parser.parse_args().batch
 assert folder.startswith('greece-egypt') and '/' not in folder and '..' not in folder
 build(ROOT/'data/sprites'/folder)
