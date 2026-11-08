"""Mark all catalog sprites on the existing atlas. Requires Pillow and pyproj."""
import json
from PIL import Image, ImageDraw, ImageFont
import frame
from sprite_geometry import sheet_anchor, inset_geometry
from sprite_catalog import BASE, ROOT, build, placements, atlas_placements, write


def main():
    catalog=build()
    available=[e for e in catalog['assets'] if e['asset'] and e['geographic_placement_ready']]
    chosen=atlas_placements(catalog)
    selected_1180={e['id'] for e in placements(catalog,1180)}
    selected={e['id'] for e in chosen}
    features=[]
    for e in available:
        x,y=sheet_anchor(e)
        width=e['display_width_units']
        w,h=e['technical_qa']['dimensions_px'];height=width*h/w
        ax,ay=e['anchor_normalized']
        features.append(dict(type='Feature',id=e['id'],geometry=dict(type='Point',coordinates=e['coordinates']),
            properties=dict(sprite_id=e['id'],site_group=e['site_id'],name=e['name'],asset='data/sprites/'+e['asset'],
                sha256=e['technical_qa']['sha256'],preferred=e['id'] in selected,
                preferred_1180=e['id'] in selected_1180,display_title=e['display_title'],construction=e.get('construction'),
                approval=e['approval']['status'],repaint_later=True,historical_accuracy_certified=False,
                replacement_review=e.get('replacement_review'),
                placement_view=e.get('placement_view','atlas'),
                availability=e['availability'],coordinates_surveyed=False,coordinate_source_checked=True,
                coordinate_source=e['coordinate_source'],coordinate_evidence=e['coordinate_evidence'],
                approval_for_placement=e['approval_for_placement'],period_1180_eligible=e['period_1180_eligible'],
                map_layers=e['map_layers'],map_region=e['map_region'],historical_name=e['historical_name'],
                anchor_normalized=e['anchor_normalized'],sheet_anchor_px=[round(x,3),round(y,3)],
                display_width_sheet_px=width,display_height_sheet_px=round(height,3),
                top_left_sheet_px=[round(x-ax*width,3),round(y-ay*height,3)])))
    write(BASE/'placements.geojson',dict(type='FeatureCollection',default_year=1180,
        note='Multi-period inventory: preferred=true selects one image per site, including dated later castles. Use preferred_1180 or placements-1180.geojson for the 1180 snapshot.',
        sheet=dict(width=frame.W,height=frame.H,projection=frame.PROJ,pixel_origin='upper-left'),features=features))
    write(BASE/'placements-atlas.geojson',dict(type='FeatureCollection',
        period_mode='multi-period; construction dates shown in later-site titles',
        features=[f for f in features if f['properties']['preferred']]))
    im=Image.open(ROOT/'previews/crusader-stage3c-colour.jpg').convert('RGB')
    w,h=im.size;scale=w/frame.W
    board=Image.new('RGB',(w+850,max(h,250+len(chosen)*145+330)),(246,240,224));board.paste(im,(0,0));d=ImageDraw.Draw(board)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
    small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
    d.text((w+24,30),'PROVISIONAL SPRITE PLACEMENT — ATLAS',font=font,fill='#6b2219')
    d.text((w+24,70),f'{len(chosen)} sites; {len(available)} approved sprite variants',font=small,fill='black')
    for i,e in enumerate(sorted(chosen,key=lambda e:-e['coordinates'][1]),1):
        x,y=sheet_anchor(e);x*=scale;y*=scale
        color='#a22220' if e['period_1180_eligible'] else '#315b9a'
        d.ellipse((x-18,y-18,x+18,y+18),fill=color,outline='white',width=3)
        d.text((x-7,y-13),str(i),font=font,fill='white')
        yy=130+(i-1)*145
        d.text((w+24,yy),f"{i}. {e['name']}",font=font,fill='black')
        lon,lat=e['coordinates'];d.text((w+24,yy+35),f'{lon:.3f} E, {lat:.3f} N',font=small,fill='black')
        d.text((w+24,yy+65),f"Width: {e['display_width_units']} sheet pixels",font=small,fill='black')
        d.text((w+24,yy+95),e['id'],font=small,fill='#6b2219')
    yy=130+len(chosen)*145+30
    for line in ['Markers show ground anchors, not city extents.',
                 'Provisional approval; repaint flags preserved.',
                 'Blue markers: later castles; construction dates in titles.',
                 'Dated later castles remain excluded from 1180.',
                 'Background atlas covers multiple periods.',
                 'Tripoli uses sourced coastal al-Mina anchor.']:
        d.text((w+24,yy),line,font=small,fill='black');yy+=40
    board.save(ROOT/'previews/sprite-placement-markup.jpg',quality=94)
    # A reproducible close view of inset anchors, with the same numbered key.
    detail=Image.new('RGB',(1400,1600),'#eee9dc');dd=ImageDraw.Draw(detail)
    ordered=sorted(chosen,key=lambda e:-e['coordinates'][1])
    for j,region in enumerate(('aegean','delta')):
        _,_,_,_,_,iw,ih,bx,by=inset_geometry(region)
        crop=board.crop((int((bx-50)*scale),int((by-50)*scale),int((bx+iw+50)*scale),int((by+ih+50)*scale)))
        crop.thumbnail((860,730));detail.paste(crop,(20,j*800+40))
        dd.text((20,j*800+15),region+' placement anchors',fill='#34291f')
        yy=j*800+60
        for n,e in enumerate(ordered,1):
            if e['map_region']==region:
                dd.text((910,yy),f'{n}. {e["name"]}',font=small,fill='#34291f');yy+=32
        dd.text((910,yy+20),'Sourced anchors; provisional',font=small,fill='#34291f')
    detail.save(ROOT/'previews/city-inset-placement-review.jpg',quality=94)
    assert len(features)==len(available) and len(selected)==len(chosen)
    print(f'Marked {len(chosen)} preferred sites; inventory includes {len(available)} approved PNGs')


if __name__=='__main__':
    main()
