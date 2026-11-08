"""Export approved sprites at atlas coordinates as a separate SVG overlay.

Requires Pillow and pyproj. Does not alter the multi-period print editions.
"""
import argparse
import base64
import json
from html import escape
from pathlib import Path
from PIL import Image, ImageDraw
import frame
from sprite_catalog import BASE, ROOT, placements


def render(year=1180):
    catalog=json.loads((BASE/'catalog.json').read_text())
    chosen=placements(catalog,year)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{frame.W}" height="{frame.H}" viewBox="0 0 {frame.W} {frame.H}">',
         '<title>Provisional circa-'+str(year)+' sprite layer; repaint review required</title>']
    # Diagnostic on neutral paper with a geographic grid, not a finished atlas.
    scale=.3
    preview=Image.new('RGB',(int(frame.W*scale),int(frame.H*scale)),'#eee9dc')
    draw=ImageDraw.Draw(preview)
    for lon in range(30,39):
        points=[tuple(v*scale for v in frame.to_px(lon,lat/10)) for lat in range(300,386)]
        draw.line(points,fill='#c8c5ba')
    for lat in range(30,39):
        points=[tuple(v*scale for v in frame.to_px(lon/10,lat)) for lon in range(300,386)]
        draw.line(points,fill='#c8c5ba')
    for e in sorted(chosen,key=lambda e:-e['coordinates'][1]):
        px,py=frame.to_px(*e['coordinates'])
        im=Image.open(BASE/e['asset'])
        width=e['display_width_units']; height=width*im.height/im.width
        ax,ay=e['anchor_normalized']; x=px-ax*width;y=py-ay*height
        encoded=base64.b64encode((BASE/e['asset']).read_bytes()).decode('ascii')
        svg.append(f'<image id="{escape(e["id"])}" x="{x:.3f}" y="{y:.3f}" width="{width}" height="{height:.3f}" href="data:image/png;base64,{encoded}"/>')
        thumb=im.resize((round(width*scale),round(height*scale)),Image.Resampling.LANCZOS)
        preview.paste(thumb,(round(x*scale),round(y*scale)),thumb)
        draw.ellipse((px*scale-2,py*scale-2,px*scale+2,py*scale+2),fill='#a03333')
        draw.text((px*scale+5,py*scale+5),e['name'],fill='#30251e')
    svg.append('</svg>')
    (ROOT/f'previews/sprite-layer-{year}.svg').write_text('\n'.join(svg)+'\n')
    # Crop diagnostic to relevant mainland area; retain full-sheet SVG above.
    box=preview.getbbox()
    if chosen:
        xs=[];ys=[]
        for e in chosen:
            x,y=frame.to_px(*e['coordinates']);xs.append(x*scale);ys.append(y*scale)
        box=(max(0,int(min(xs)-400)),max(0,int(min(ys)-350)),min(preview.width,int(max(xs)+400)),min(preview.height,int(max(ys)+150)))
    preview=preview.crop(box)
    ImageDraw.Draw(preview).text((15,15),f'{year}: provisional placement review / grid only / red dots = anchors',fill='#30251e')
    preview.save(ROOT/f'previews/sprite-placement-{year}.jpg',quality=93)
    print('Rendered',len(chosen),'sprites; self-contained SVG uses atlas frame.py projection')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year',type=int,default=1180)
    render(parser.parse_args().year)
