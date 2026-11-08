"""Render reproducible illustrative overlap recipes, not geographic terrain placement."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parent;B=R/'data/terrain'
recipes=[{'name':'Palestine ridge and foothill transitions','pieces':[['palestine-foothills-west',45,300,620],['palestine-limestone-ridge',455,290,700],['palestine-foothills-east',955,320,610],['limestone-valley-gap',610,370,440]]}, {'name':'Lebanon and Taurus: linked massif, saddle and escarpment','pieces':[['lebanon-high-massif',55,700,700],['lebanon-saddle',500,735,630],['taurus-short-peaks',925,740,610],['taurus-cliff-spur',690,760,430]]}, {'name':'Greek woodland chain with open gorge','pieces':[['pindus-forested-ridge',50,1190,690],['greek-short-ridge',900,1170,640],['greek-gorge-gap',555,1260,550],['greek-forested-foothills',160,1200,510]]}]
im=Image.new('RGB',(1650,1400),'#eee4cc');d=ImageDraw.Draw(im);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',26)
for j,recipe in enumerate(recipes):
 d.text((35,20+j*450),recipe['name'],font=font,fill='#493d2f')
 for ident,x,bottom,width in recipe['pieces']:
  p=Image.open(B/'png'/(ident+'.png')).convert('RGBA');p=p.resize((width,round(width*p.height/p.width)),Image.Resampling.LANCZOS);im.paste(p,(x,bottom-p.height),p)
im.save(R/'previews/terrain-interlay-examples.jpg',quality=94)
(B/'interlay-recipes.json').write_text(json.dumps({'canvas_px':[1650,1400],'coordinate_convention':'x left, bottom y, display width; ordered rear to front','purpose':'illustrative overlap examples, not geographically accurate chains','recipes':recipes},indent=2)+'\n')
# Compact individual catalog.
entries=json.loads((B/'manifest.json').read_text())['assets'];sheet=Image.new('RGB',(1500,((len(entries)+2)//3)*230),'#eee4cc');draw=ImageDraw.Draw(sheet)
for i,e in enumerate(entries):
 x=(i%3)*500;y=(i//3)*230;p=Image.open(B/e['file']);p.thumbnail((470,185));sheet.paste(p,(x+15,y+30),p);draw.text((x+12,y+9),e['id'],fill='black')
sheet.save(R/'previews/terrain-catalog.jpg',quality=94)
print('Rendered three interlay examples and',len(entries),'piece catalog')
