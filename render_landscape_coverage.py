"""Accepted-artwork map proof with dry-zone coverage and editable water/road placement.
Pillow, NumPy, pyproj required. Preserves print files; geographic/period review remains.
"""
from pathlib import Path
import ast,json,math,random
import numpy as np
from PIL import Image,ImageDraw,ImageChops
from pyproj import Transformer
import frame
from build_terrain_placements import project as oldproject
R=Path(__file__).resolve().parent;B=R/'data/landscape-assets'
def project(region,lon,lat):
 if region!='delta':return oldproject(region,lon,lat)
 c=frame.INSETS['delta'];f=Transformer.from_crs('EPSG:4326',c['proj'],always_xy=True);a,b,cx,d=c['ext'];xl,_=f.transform(a,d);xr,_=f.transform(cx,d);_,top=f.transform((a+cx)/2,d);_,bottom=f.transform(a,b);w=4800;h=round(w*(top-bottom)/(xr-xl));x,y=f.transform(lon,lat);return 190+(x-xl)/(xr-xl)*w,13760-h+(top-y)/(top-bottom)*h

def literal(file,name):
 for n in ast.parse((R/file).read_text()).body:
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id==name for t in n.targets):return ast.literal_eval(n.value)

def build():
 m=json.loads((B/'manifest.json').read_text());assets={e['id']:e for e in m['assets']};basepath=R/'previews/terrain-map-proof.jpg';base=Image.open(basepath if basepath.exists() else R/'previews/crusader-stage3c-colour.jpg').convert('RGBA');w,h=base.size;sc=w/10800
 # Masks limit dry overlays to land-colored regions and protect panels and settlement anchors.
 rgb=np.array(base)[:,:,:3].astype(float);dry=((rgb[:,:,0]>rgb[:,:,1]*1.025)&(rgb[:,:,1]>rgb[:,:,2]*1.08)).astype('uint8')*255;drymask=Image.fromarray(dry);protect=Image.new('L',(w,h),255);pd=ImageDraw.Draw(protect)
 def blocked(rect):pd.rectangle(tuple(round(v*sc) for v in rect),fill=0)
 # main-region copies exclude the two inset rectangles; inset candidate handling below overrides this mask.
 for rect in [(0,0,10800,130),(0,13890,10800,14400),(270,4770,2330,9130),(2680,6730,5430,7770),(8190,10350,10650,13800)]:blocked(rect)
 for p in literal('places.py','PLACES'):
  x,y=project(p[0],p[3],p[4]);blocked((x-110,y-85,x+230,y+110))
 # Preserve dark/red ink in the current raster where possible; this is not full label-layout reconstruction.
 ink=((rgb.min(axis=2)<105)&(rgb.max(axis=2)<155))|((rgb[:,:,0]>rgb[:,:,1]*1.5)&(rgb[:,:,1]<125));mask=np.array(protect);mask[ink]=0;protect=Image.fromarray(mask)
 layer=Image.new('RGBA',(w,h));items=[];rng=random.Random(1180)
 def image_for(ident):
  im=Image.open(B/assets[ident]['file']).convert('RGBA');return im.crop(im.getbbox())
 def stamp(ident,region,coord,width,opacity=.72,kind='dry-zone'):
  x,y=project(region,*coord);src=image_for(ident).rotate(rng.uniform(-7,7),resample=Image.Resampling.BICUBIC,expand=True);ww=max(1,round(width*sc));hh=max(1,round(ww*src.height/src.width));left=round(x*sc-ww/2);top=round(y*sc-hh*.80)
  if left<50*sc or top<100*sc or left+ww>w-50*sc or top+hh>h-150*sc:return
  # Keep main instances outside inset footprints (inset height derived from source layout).
  if region=='main' and (left<4990*sc and (top<4400*sc or top+hh>9350*sc)):return
  patch=src.resize((ww,hh),Image.Resampling.LANCZOS);alpha=patch.getchannel('A');crop=ImageChops.multiply(drymask.crop((left,top,left+ww,top+hh)),protect.crop((left,top,left+ww,top+hh)));alpha=ImageChops.multiply(alpha,crop).point(lambda a:round(a*opacity))
  if alpha.getbbox() is None:return
  patch.putalpha(alpha);layer.alpha_composite(patch,(left,top));items.append(dict(asset_id=ident,region=region,coordinates=coord,width_sheet_px=width,opacity=opacity,kind=kind,pixel_bounds=[left,top,left+ww,top+hh]))
 zones=[('Syrian steppe','main',[36.85,33.9,37.55,35.7],['dry-scrub-steppe','gravel-wasteland','rocky-desert']),('Transjordan','main',[36.10,30.8,37.25,33.4],['gravel-wasteland','eroded-badlands','desert-escarpment']),('Judaean desert','main',[35.30,31.25,35.42,31.75],['rocky-desert','eroded-badlands']),('Araba and southern desert','main',[34.8,30.05,35.45,30.9],['sand-dunes','dune-transition','gravel-wasteland']),('Sinai','delta',[33.1,28.6,34.4,30.9],['sand-dunes','rocky-desert','dune-transition','gravel-wasteland']),('Western Egyptian desert','delta',[29.75,29.2,30.25,30.5],['sand-dunes','gravel-wasteland'])]
 for zone,region,(lo0,la0,lo1,la1),choices in zones:
  lat=la1
  while lat>=la0:
   lon=lo0
   while lon<=lo1:
    coord=[round(lon+rng.uniform(-.05,.05),4),round(lat+rng.uniform(-.025,.025),4)];stamp(rng.choice(choices),region,coord,rng.randrange(620,920),.62,zone);lon+=.32
   lat-=.075
 stamp('salt-flat','main',[35.35,30.90],410,.65,'salt-flat-context')
 stamp('broad-valley-floor','main',[35.55,32.15],300,.8,'valley-context')
 # Oasis is a generic Jericho-area motif; site identity remains unverified.
 def place_box(ident,region,bounds,kind):
  lo0,la0,lo1,la1=bounds;corners=[project(region,lo,la) for lo,la in [(lo0,la0),(lo0,la1),(lo1,la0),(lo1,la1)]];left=round(min(x for x,y in corners)*sc);top=round(min(y for x,y in corners)*sc);right=round(max(x for x,y in corners)*sc);bottom=round(max(y for x,y in corners)*sc);src=image_for(ident).resize((right-left,bottom-top),Image.Resampling.LANCZOS);layer.alpha_composite(src,(left,top));items.append(dict(asset_id=ident,region=region,geographic_fit_bounds=bounds,kind=kind,review='Illustrative fit, aspect ratio and shoreline not certified',pixel_bounds=[left,top,right,bottom]))
 place_box('sea-of-galilee','main',[35.50,32.70,35.66,32.91],'north-up-lake-fit')
 place_box('dead-sea','main',[35.36,31.02,35.61,31.77],'north-up-lake-fit')
 place_box('jordan-river','main',[35.54,31.77,35.58,32.70],'schematic-lower-jordan-fit')
 place_box('palm-oasis','main',[35.40,31.86,35.44,31.89],'generic-oasis-context')
 # Decorative road segments follow selected existing source control-point edges.
 roads=literal('build_stage2.py','ROADS')
 for roadindex in [2,3]:
  road=roads[roadindex]
  for a,b in zip(road,road[1:]):
   x0,y0=project('main',*a);x1,y1=project('main',*b);dx=(x1-x0)*sc;dy=(y1-y0)*sc;length=max(2,round(math.hypot(dx,dy)));src=image_for('road-straight').resize((length,max(2,round(7*sc))),Image.Resampling.LANCZOS);src=src.rotate(-math.degrees(math.atan2(dy,dx)),resample=Image.Resampling.BICUBIC,expand=True);left=round((x0+x1)*sc/2-src.width/2);top=round((y0+y1)*sc/2-src.height/2);layer.alpha_composite(src,(left,top));items.append(dict(asset_id='road-straight',kind='existing-source-road-edge',road_index_zero_based=roadindex,coordinates=[a,b],pixel_bounds=[left,top,left+src.width,top+src.height]))
 layer.save(R/'previews/landscape-coverage-layer.png');proof=Image.alpha_composite(base,layer).convert('RGB');proof.save(R/'previews/map-landscape-coverage.jpg',quality=94)
 markup=proof.copy();d=ImageDraw.Draw(markup)
 for i,e in enumerate(items,1):
  l,t,rr,bb=e['pixel_bounds'];d.rectangle((l,t,rr,bb),outline='#a73024',width=1)
 markup.save(R/'previews/map-landscape-coverage-markup.jpg',quality=94)
 (B/'coverage-plan.json').write_text(json.dumps({'seed':1180,'user_acceptance':'Accept these, place on map, generate more desert and wasteland terrain to cover the whole map','status':'accepted-artwork-geographic-review-required','base_preview':str(basepath.relative_to(R)),'scope':'Broad dry-zone coverage proof on current map. Printed terrain and labels remain below. Masks protect panels, approximate settlement anchors and dark/red ink, not every moved label. No desert cover over Greece or seas. Water fit is illustrative, not georeferenced shoreline certification.','zones':[dict(name=z,region=r,bounds=b,asset_choices=c) for z,r,b,c in zones],'instances':items},indent=2)+'\n');print('Rendered',len(items),'landscape placements')
if __name__=='__main__':build()
