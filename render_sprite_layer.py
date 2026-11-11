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
from sprite_geometry import sheet_anchor, inset_geometry
from sprite_catalog import BASE, ROOT, placements, atlas_placements



def review_placements(year, show_all_variants=False):
    """Review-only artwork is displayable even when production or technical approval fails."""
    path = BASE / f'placements-review-{year}.geojson'
    if not path.exists():
        raise FileNotFoundError(f'No draft review placements for {year}: {path}')
    data = json.loads(path.read_text())
    result = []
    for feature in data['features']:
        p = feature['properties']
        if not p.get('approval_for_review_placement'):
            continue
        if not (show_all_variants or p.get('default_visible', False)):
            continue
        rel = Path(p['asset_path']).relative_to('data/sprites')
        image = BASE / rel
        if not image.is_file():
            raise FileNotFoundError(f'Review-placement image is missing: {image}')
        result.append(dict(
            id=feature['id'],
            site_id=p['site_id'],
            name=p['name'] + ' [REVIEW ONLY]',
            asset=str(rel),
            coordinates=feature['geometry']['coordinates'],
            map_region=p.get('map_region', 'main'),
            display_width_units=p.get('display_width_units', 512),
            anchor_normalized=p.get('anchor_normalized', [0.5, 0.95]),
            period_1180_eligible=(p.get('depiction_year') == 1180),
            review_only=True,
        ))
    return result


def render(year=1180, atlas=False, review=False, all_review_variants=False):
    catalog=json.loads((BASE/'catalog.json').read_text())
    if review and atlas:
        raise ValueError('Review-only layer cannot use the mixed-period atlas selector')
    chosen=(review_placements(year, all_review_variants) if review
            else atlas_placements(catalog) if atlas else placements(catalog,year))
    suffix=(f'review-{year}' if review else 'atlas' if atlas else str(year)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{frame.W}" height="{frame.H}" viewBox="0 0 {frame.W} {frame.H}">',
         '<title>'+('DRAFT REVIEW ONLY ' if review else 'Provisional ')+('multi-period atlas' if atlas else 'circa-'+str(year))+' sprite layer; repaint review required</title>']
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
    for region in ('aegean','delta'):
        _,_,_,_,_,w,h,bx,by=inset_geometry(region)
        draw.rectangle((bx*scale,by*scale,(bx+w)*scale,(by+h)*scale),outline='#a7a090',width=2)
        draw.text((bx*scale+5,by*scale+5),region,fill='#30251e')
    for e in sorted(chosen,key=lambda e:-e['coordinates'][1]):
        px,py=sheet_anchor(e)
        im=Image.open(BASE/e['asset']).convert('RGBA')
        width=e['display_width_units']; height=width*im.height/im.width
        ax,ay=e['anchor_normalized']; x=px-ax*width;y=py-ay*height
        encoded=base64.b64encode((BASE/e['asset']).read_bytes()).decode('ascii')
        svg.append(f'<image id="{escape(e["id"])}" x="{x:.3f}" y="{y:.3f}" width="{width}" height="{height:.3f}" href="data:image/png;base64,{encoded}"><title>{escape(e["name"])}</title></image>')
        if not e['period_1180_eligible']:
            svg.append(f'<text x="{px:.3f}" y="{py+40:.3f}" font-family="serif" font-size="32" text-anchor="middle" fill="#315b9a">{escape(e["name"])}</text>')
        thumb=im.resize((round(width*scale),round(height*scale)),Image.Resampling.LANCZOS)
        preview.paste(thumb,(round(x*scale),round(y*scale)),thumb)
        draw.ellipse((px*scale-2,py*scale-2,px*scale+2,py*scale+2),fill='#a03333')
        draw.text((px*scale+5,py*scale+5),e['name'],fill='#30251e')
    svg.append('</svg>')
    (ROOT/f'previews/sprite-layer-{suffix}.svg').write_text('\n'.join(svg)+'\n')
    # Crop diagnostic to relevant mainland area; retain full-sheet SVG above.
    box=preview.getbbox()
    if chosen:
        xs=[];ys=[]
        for e in chosen:
            x,y=sheet_anchor(e);xs.append(x*scale);ys.append(y*scale)
        box=(max(0,int(min(xs)-400)),max(0,int(min(ys)-350)),min(preview.width,int(max(xs)+400)),min(preview.height,int(max(ys)+150)))
    preview=preview.crop(box)
    ImageDraw.Draw(preview).text((15,15),f'{suffix}: provisional placement review / grid only / red dots = anchors',fill='#30251e')
    preview.save(ROOT/f'previews/sprite-placement-{suffix}.jpg',quality=93)
    print('Rendered',len(chosen),'sprites; mainland and inset projections match atlas layout')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year',type=int,default=1180)
    parser.add_argument('--atlas',action='store_true',help='Include dated later sites in the multi-period atlas view')
    parser.add_argument('--review',action='store_true',help='Render review-only drafts despite production or technical QA holds')
    parser.add_argument('--all-review-variants',action='store_true',help='For --review: also render hidden duplicate site variants; expect overlaps')
    args=parser.parse_args()
    render(args.year,atlas=args.atlas,review=args.review,all_review_variants=args.all_review_variants)
