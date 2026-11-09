"""Sourced-anchor detail placement: four sprites, no invented geographic offsets."""
import base64,json
from html import escape
from itertools import combinations
from PIL import Image,ImageDraw,ImageFont
from sprite_catalog import ROOT,BASE,build,placements,write
from sprite_geometry import sheet_anchor

WIDTH,HEIGHT=3000,2600
MAGNIFICATION=60
ORIGIN=(1300,1300)
LANDSCAPE_DIR=BASE/'greece-egypt-1180-bosphorus'


def render_landscape_pairing(city, *, review_water=False):
    """Render landscape layers in back-to-front order using visual offsets."""
    shore=json.loads((LANDSCAPE_DIR/'bosphorus-asian-shore-1180.json').read_text())
    if not shore['approval_for_placement']:
        return
    companions=[shore]
    horn_path=LANDSCAPE_DIR/'golden-horn-north-shore-1180.json'
    if horn_path.exists():
        horn=json.loads(horn_path.read_text())
        if horn['approval_for_placement']:
            companions.append(horn)
    expanded=len(companions)>1
    city_origin=(20,212 if expanded else 22)
    canvas=Image.new('RGBA',(1840,800 if expanded else 610),'#eee9dc')
    water_path=LANDSCAPE_DIR/'bosphorus-water-join-1180.json'
    if water_path.exists():
        water=json.loads(water_path.read_text())
        if water['approval_for_placement'] or review_water:
            companions.insert(0,water)
    layers=[]
    for companion in companions:
        pairing=companion['pairing']
        dx,dy=pairing['companion_top_left_relative_to_city_px']
        layers.append((LANDSCAPE_DIR/companion['asset'],pairing['companion_display_width_px'],
                       (city_origin[0]+dx,city_origin[1]+dy)))
    layers.append((BASE/city['asset'],shore['pairing']['city_display_width_px'],city_origin))
    for path,width,origin in layers:
        with Image.open(path) as sprite:
            height=round(sprite.height*width/sprite.width)
            image=sprite.resize((width,height),Image.Resampling.LANCZOS)
            canvas.alpha_composite(image,origin)
    filename='constantinople-landscape-1180.jpg' if expanded else 'bosphorus-asian-shore-pairing.jpg'
    if review_water:
        filename='constantinople-water-join-review.jpg'
    result=canvas.convert('RGB')
    result.save(ROOT/'previews'/filename,quality=95)
    return result

def detail_point(entry,center):
    x,y=sheet_anchor(entry);cx,cy=sheet_anchor(center)
    return ORIGIN[0]+(x-cx)*MAGNIFICATION,ORIGIN[1]+(y-cy)*MAGNIFICATION

def layout(catalog):
    center=next(e for e in placements(catalog,1180) if e['site_id']=='constantinople')
    chosen=[center]+placements(catalog,1180,view='constantinople-detail')
    rows=[]
    for e in chosen:
        x,y=detail_point(e,center);w=e['display_width_units'];iw,ih=e['technical_qa']['dimensions_px'];h=w*ih/iw
        ax,ay=e['anchor_normalized'];box=(x-ax*w,y-ay*h,x+(1-ax)*w,y+(1-ay)*h)
        assert min(box)>=0 and box[2]<WIDTH and box[3]<HEIGHT,(e['id'],box)
        rows.append((e,(x,y),box))
    for a,b in combinations(rows,2):
        aa,bb=a[2],b[2]
        assert min(aa[2],bb[2])<=max(aa[0],bb[0]) or min(aa[3],bb[3])<=max(aa[1],bb[1]),('sprite-collision',a[0]['id'],b[0]['id'])
    return rows

def main():
    c=build();rows=layout(c)
    render_landscape_pairing(rows[0][0])
    canvas=Image.new('RGB',(WIDTH,HEIGHT),'#eee9dc');d=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',32)
    small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',25)
    d.text((70,45),'CONSTANTINOPLE AND THE OPPOSITE SHORES — circa 1180',font=font,fill='#33281f')
    d.text((70,95),'Geographic anchor diagnostic; grid only. Painted silhouettes are not surveyed city footprints.',font=small,fill='#665a4c')
    d.text((70,135),'Constantinople 1024 px / companions 256 px. Enlarged geography; no shifted anchors.',font=small,fill='#665a4c')
    # Graticule follows the same projection as the Aegean inset, magnified uniformly.
    center=rows[0][0]
    for lat in [40.98,41.00,41.02,41.04]:
        points=[detail_point(dict(map_region='aegean',coordinates=[lon/10000,lat]),center) for lon in range(289400,290501,10)]
        d.line(points,fill='#d6d0c2',width=2)
        _,y=detail_point(dict(map_region='aegean',coordinates=[28.95,lat]),center)
        if 200<y<HEIGHT-100:d.text((50,y+8),f'{lat:.2f} N',font=small,fill='#827665')
    for lon in [28.96,28.98,29.00,29.02,29.04]:
        points=[detail_point(dict(map_region='aegean',coordinates=[lon,lat/10000]),center) for lat in range(409700,410501,10)]
        d.line(points,fill='#d6d0c2',width=2)
    features=[];svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">','<title>Constantinople circa1180 provisional sprite detail overlay; sourced anchors; no coastline reconstruction</title>']
    for e,(x,y),box in rows:
        w,h=box[2]-box[0],box[3]-box[1];im=Image.open(BASE/e['asset']).resize((round(w),round(h)),Image.Resampling.LANCZOS)
        canvas.paste(im,(round(box[0]),round(box[1])),im)
        d.ellipse((x-8,y-8,x+8,y+8),fill='#a13325',outline='white',width=2)
        label=f"{e['name']} — {e['display_width_units']} px"
        d.text((box[0],y+25),label,font=font,fill='#33281f')
        d.text((box[0],y+70),f"{e['latitude']:.6f} N / {e['longitude']:.6f} E",font=small,fill='#665a4c')
        encoded=base64.b64encode((BASE/e['asset']).read_bytes()).decode()
        svg.append(f'<image id="{escape(e["id"])}" x="{box[0]:.3f}" y="{box[1]:.3f}" width="{w}" height="{h}" href="data:image/png;base64,{encoded}"/>')
        features.append(dict(type='Feature',id=e['id'],geometry=dict(type='Point',coordinates=e['coordinates']),properties=dict(site_id=e['site_id'],name=e['name'],asset='data/sprites/'+e['asset'],approval_for_placement=True,approval_status='approved-provisional',period_1180_eligible=True,placement_view='constantinople-detail',map_region='aegean',coordinate_evidence=e['coordinate_evidence'],anchor_normalized=e['anchor_normalized'],detail_anchor_px=[x,y],detail_top_left_px=list(box[:2]),display_width_px=w,display_height_px=h,visual_footprint=e['visual_footprint'],review_required=True,repaint_flags=e.get('repaint_flags',[]),replacement_review=e.get('replacement_review'))))
    d.text((70,HEIGHT-120),'Provisional illustrations: house plans, churches, fort elevations and coastline details remain unverified.',font=small,fill='#665a4c')
    d.text((70,HEIGHT-80),'Chrysopolis coordinate precision: 2000 m. Galata/Sykai point marks the settlement area, not the chain fort.',font=small,fill='#665a4c')
    canvas.save(ROOT/'previews/constantinople-detail-1180.jpg',quality=94)
    svg.append('</svg>');(ROOT/'previews/constantinople-detail-1180.svg').write_text('\n'.join(svg)+'\n')
    write(BASE/'placements-constantinople-detail-1180.geojson',dict(type='FeatureCollection',year=1180,placement_view='constantinople-detail',note='Detail overlay and geographic anchors only; no surveyed medieval footprints or coastline. Do not use detail pixel positions on regional atlas.',detail_canvas=dict(width=WIDTH,height=HEIGHT,geographic_projection='Same LCC as frame.INSETS.aegean',regional_pixel_magnification=MAGNIFICATION,origin_site='constantinople',origin_anchor_px=list(ORIGIN),visual_offsets=False),features=features))
    print('4 sourced anchors; sprite bounding boxes fit without overlap; regional overlay excludes companion sprites')

if __name__=='__main__':main()
