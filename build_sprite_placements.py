"""Mark all catalog sprites on the existing atlas. Requires Pillow and pyproj."""
import json
from PIL import Image, ImageDraw, ImageFont
import frame
from sprite_catalog import BASE, ROOT, build, placements, write


def main():
    catalog=build()
    available=[e for e in catalog['assets'] if e['asset']]
    chosen=placements(catalog,1180)
    selected={e['id'] for e in chosen}
    features=[]
    for e in available:
        x,y=frame.to_px(*e['coordinates'])
        width=e['display_width_units']
        w,h=e['technical_qa']['dimensions_px'];height=width*h/w
        ax,ay=e['anchor_normalized']
        features.append(dict(type='Feature',id=e['id'],geometry=dict(type='Point',coordinates=e['coordinates']),
            properties=dict(sprite_id=e['id'],site_group=e['site_id'],name=e['name'],asset='data/sprites/'+e['asset'],
                sha256=e['technical_qa']['sha256'],preferred=e['id'] in selected,
                approval=e['approval']['status'],repaint_later=True,historical_accuracy_certified=False,
                availability=e['availability'],coordinates_verified=False,coordinate_source=e['coordinate_source'],
                anchor_normalized=e['anchor_normalized'],sheet_anchor_px=[round(x,3),round(y,3)],
                display_width_sheet_px=width,display_height_sheet_px=round(height,3),
                top_left_sheet_px=[round(x-ax*width,3),round(y-ay*height,3)])))
    write(BASE/'placements.geojson',dict(type='FeatureCollection',default_year=1180,
        note='All available variants; draw only preferred=true. Missing-source records remain in catalog.json. Montfort is excluded at 1180.',
        sheet=dict(width=frame.W,height=frame.H,projection=frame.PROJ,pixel_origin='upper-left'),features=features))
    im=Image.open(ROOT/'previews/crusader-stage3c-colour.jpg').convert('RGB')
    w,h=im.size;scale=w/frame.W
    board=Image.new('RGB',(w+650,h),(246,240,224));board.paste(im,(0,0));d=ImageDraw.Draw(board)
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',22)
    small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
    d.text((w+24,30),'PROVISIONAL SPRITE PLACEMENT — 1180',font=font,fill='#6b2219')
    d.text((w+24,70),f'{len(chosen)} sites; {len(available)} approved sprite variants',font=small,fill='black')
    for i,e in enumerate(sorted(chosen,key=lambda e:-e['coordinates'][1]),1):
        x,y=frame.to_px(*e['coordinates']);x*=scale;y*=scale
        d.ellipse((x-18,y-18,x+18,y+18),fill='#a22220',outline='white',width=3)
        d.text((x-7,y-13),str(i),font=font,fill='white')
        yy=130+(i-1)*145
        d.text((w+24,yy),f"{i}. {e['name']}",font=font,fill='black')
        lon,lat=e['coordinates'];d.text((w+24,yy+35),f'{lon:.3f} E, {lat:.3f} N',font=small,fill='black')
        d.text((w+24,yy+65),f"Width: {e['display_width_units']} sheet pixels",font=small,fill='black')
        d.text((w+24,yy+95),e['id'],font=small,fill='#6b2219')
    yy=130+len(chosen)*145+30
    for line in ['Markers show ground anchors, not city extents.',
                 'Provisional approval; repaint flags preserved.',
                 'Montfort excluded from the 1180 sprite layer.',
                 'Background atlas covers multiple periods.',
                 'Tripoli uses proposed coastal al-Mina anchor.']:
        d.text((w+24,yy),line,font=small,fill='black');yy+=40
    board.save(ROOT/'previews/sprite-placement-markup.jpg',quality=94)
    assert len(features)==len(available) and len(selected)==len(chosen)
    print(f'Marked {len(chosen)} preferred sites; inventory includes {len(available)} approved PNGs')


if __name__=='__main__':
    main()
