"""Package period-informed sprite candidates. Requires Pillow, NumPy, SciPy.
Original generations are preserved. Fixed display widths implement Jerusalem's 2x request.
"""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw
from scipy import ndimage
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'data/sprites/historical-1180'
def build():
 m=json.loads((BASE/'manifest.json').read_text())
 preview=Image.new('RGB',(1600,1100),'#eee9dc');d=ImageDraw.Draw(preview)
 for i,e in enumerate(m['assets']):
  src=BASE/e['source'];im=Image.open(src).convert('RGBA');a=np.array(im)
  before=int(np.count_nonzero(a[:,:,3]));a[a[:,:,3]<16]=0
  labels,n=ndimage.label(a[:,:,3]>0);sizes=np.bincount(labels.ravel());keep=sizes>=20;keep[0]=False;a[~keep[labels]]=0;a[a[:,:,3]==0]=0
  im=Image.fromarray(a);bbox=im.getbbox();im=im.crop(bbox)
  # Scale painted width with proportional height and an equal percentage margin.
  width=e['output_width_px'];inner=width-2*round(width*.025)
  im=im.resize((inner,round(im.height*inner/im.width)),Image.Resampling.LANCZOS)
  pad=round(width*.025);out=Image.new('RGBA',(width,im.height+2*pad));out.paste(im,(pad,pad))
  out.save(BASE/e['file']);alpha=np.array(out)[:,:,3]
  assert not alpha[:pad].any() and not alpha[-pad:].any() and not alpha[:,:pad].any() and not alpha[:,-pad:].any()
  e.update(dimensions_px=list(out.size),source_dimensions_px=list(Image.open(src).size),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),sha256=hashlib.sha256((BASE/e['file']).read_bytes()).hexdigest(),anchor_normalized=[.5,(out.height-pad)/out.height],technical_validation={'mode':'RGBA','transparent_padding_px':pad,'source_nonzero_alpha':before,'cleaned_source_nonzero_alpha':int(np.count_nonzero(a[:,:,3])),'alpha_floor':16,'minimum_component_pixels':20,'native_detail_increased_by_resizing':False})
  for col,color in enumerate(['#eee9dc','#253544']):
   x=col*800;y=i*550;d.rectangle((x,y,x+799,y+549),fill=color)
   thumb=out.copy();thumb.thumbnail((760,490));preview.paste(thumb,(x+20,y+45),thumb);d.text((x+20,y+15),e['id']+' / '+str(width)+' px',fill='black' if col==0 else 'white')
 (BASE/'manifest.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n');preview.save(ROOT/'previews/historical-batch-01.jpg',quality=94)
 print('Packaged',len(m['assets']),'sprites; Jerusalem width is 2x Belvoir')
if __name__=='__main__':build()
