"""Render an editable first placement proof. Existing print outputs are untouched.
Requires Pillow, pyproj. This intentionally overlays the current preview; native
terrain suppression and final label ordering remain production integration work.
"""
from pathlib import Path
import ast,json,hashlib
from PIL import Image,ImageDraw
from build_terrain_placements import project
R=Path(__file__).resolve().parent;B=R/'data/terrain'

def build():
 manifest=json.loads((B/'manifest.json').read_text());assets={e['id']:e for e in manifest['assets']}
 plan=json.loads((B/'render-plan.json').read_text());im=Image.open(R/'previews/crusader-stage3c-colour.jpg').convert('RGBA');scale=im.width/10800;layer=Image.new('RGBA',im.size);boxes=[];svg=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 10800 14400">'];report=[]
 # Use source place anchors for a conservative overlap review, not automatic relocation.
 tree=ast.parse((R/'places.py').read_text());places=[]
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PLACES' for t in node.targets):places=ast.literal_eval(node.value)
 for i,row in enumerate(plan['instances'],1):
  e=assets[row['asset_id']];f=B/e['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==e['sha256'];src=Image.open(f).convert('RGBA');x,y=project(row['region'],*row['coordinates']);width=row['width_sheet_px'];height=width*src.height/src.width;ax,ay=e['anchor_normalized'];left=x-ax*width;top=y-ay*height;rect=[left,top,left+width,top+height]
  assert min(left,top)>=0 and rect[2]<=10800 and rect[3]<=14400
  hits=[]
  for p in places:
   if p[0]!=row['region']:continue
   px,py=project(p[0],p[3],p[4])
   if left-65<px<rect[2]+65 and top-65<py<rect[3]+65:hits.append(p[7])
  thumb=src.resize((round(width*scale),round(height*scale)),Image.Resampling.LANCZOS);layer.alpha_composite(thumb,(round(left*scale),round(top*scale)));boxes.append((i,rect));svg.append(f'<image x="{left:.3f}" y="{top:.3f}" width="{width}" height="{height:.3f}" xlink:href="../data/terrain/{e["file"]}"/>')
  report.append(dict(instance=i,asset_id=e['id'],sheet_bounds=rect,nearby_place_anchors_for_review=hits,placement_status='visual-proof-only-geographic-and-label-review-required'))
 proof=Image.alpha_composite(im,layer).convert('RGB');proof.save(R/'previews/terrain-map-proof.jpg',quality=94)
 marked=proof.copy();d=ImageDraw.Draw(marked)
 for i,(l,t,r,b) in boxes:
  box=tuple(round(v*scale) for v in (l,t,r,b));d.rectangle(box,outline='#ad251d',width=2);d.text((box[0]+3,box[1]+3),str(i),fill='#ad251d')
 marked.save(R/'previews/terrain-map-proof-markup.jpg',quality=94);svg.append('</svg>');(R/'previews/terrain-proof-overlay.svg').write_text('\n'.join(svg)+'\n');(B/'render-proof-report.json').write_text(json.dumps({'asset_count':len(assets),'instance_count':len(report),'scope':'Review proof only; original terrain remains under overlay. Place hit test is an approximate anchor-box warning, not complete label collision analysis.','instances':report},indent=2)+'\n');print('Rendered',len(report),'instances; review flags:',sum(bool(e['nearby_place_anchors_for_review']) for e in report))
if __name__=='__main__':build()
