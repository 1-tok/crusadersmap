"""Render Crusader Period 1095–1291 map and searchable occupation/siege index.
Uses the repository's terrain, Natural Earth geometry and projection; no Cairo required.
"""
import base64,html,io,json,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import frame as FR
from rough import Region
from period_history import build,ROOT
S=.23
W,H=round(FR.W*S),round(FR.H*S)
INK='#392d24';RED='#a33c32';PAPER='#eee4ce';BLUE='#345c72'
FONT=ROOT/'fonts/IMFeENrm28P.ttf'

def font(size):
    paths=[FONT,ROOT/'fonts/IMFellEnglish-Regular.otf',Path('/System/Library/Fonts/Supplemental/Arial.ttf')]
    return ImageFont.truetype(str(next(p for p in paths if p.exists())),size)


def main():
    history=build();rows=history['sites']
    regions={'main':Region(FR.PROJ,FR.X0,FR.X1,FR.Y0,FR.Y1,W,H)}
    for k in ('aegean','delta'):
        spec=FR.INSETS[k];regions[k]=Region.from_lonlat(spec['proj'],spec['ext'],round(4800*S))
    boxes={'main':(0,0),'aegean':(round(190*S),round(190*S)),
           'delta':(round(190*S),round(13760*S)-regions['delta'].h)}
    base,_=regions['main'].render(7,river_w=1)
    d=ImageDraw.Draw(base)
    for k in ('aegean','delta'):
        im,_=regions[k].render(6,river_w=1);x,y=boxes[k];base.paste(im,(x,y));d.rectangle((x-2,y-2,x+im.width+2,y+im.height+2),outline=INK,width=2)
        label='Aegean context · 1095–1291' if k=='aegean' else 'Egypt & Sinai · 1095–1291'
        d.rectangle((x+8,y+8,x+im.width-8,y+42),fill=PAPER)
        d.text((x+18,y+14),label,font=font(19),fill=INK)
    # No later-period inscriptions or old dated political labels are reused.
    d.rectangle((12,12,W-13,H-13),outline=INK,width=3)
    # Reuse approved art as illustrative landmarks; the period is a cumulative atlas,
    # not a claim that a single painting depicts every date in a site's history.
    catalog=json.loads((ROOT/'data/sprites/catalog.json').read_text())
    from sprite_catalog import atlas_placements
    aliases={'acre':'Akko','antioch':'Antakya','krak-des-chevaliers':"Qal'at al-Hisn",'belvoir':'Kokhav HaYarden','montreal-shobak':'Shobak','byblos':'Byblos','tortosa':'Tartus','arqah':'Arqa','chateau-pelerin':'Atlit'}
    selected_art=atlas_placements(catalog)
    art={aliases.get(e['site_id'],e.get('undated_name',e['name'])):ROOT/'data/sprites'/e['asset'] for e in selected_art}
    sourced_art={entry['source_site_id']:entry for entry in selected_art if entry.get('source_site_id')}
    for manifest in sorted((ROOT/'data/sprites').glob('greece-egypt*/manifest.json')):
        for e in json.loads(manifest.read_text())['assets']:
            if e.get('approval_for_placement') and (manifest.parent/e['file']).exists():
                art[e['name']]=manifest.parent/e['file']
    def anchor(row):
        entry=sourced_art.get(row['id'])
        coordinates=entry['coordinates'] if entry else row['coordinates']
        px,py=regions[row['region']].ll_px(*coordinates)
        bx,by=boxes[row['region']]
        return px+bx,py+by

    # Keep neighboring illustrations legible while pinning their leader lines
    # to the sourced location.
    art_offsets={'CP-081':(-25,4),'CP-082':(42,30),'CP-142':(-27,15)}
    illustrated={}
    art_bounds=[]
    for row in sorted(rows,key=lambda e:-e['coordinates'][1]):
        entry=sourced_art.get(row['id'])
        path=ROOT/'data/sprites'/entry['asset'] if entry else art.get(row['modern_name'])
        if path is None:continue
        px,py=anchor(row)
        im=Image.open(path).convert('RGBA')
        width=105 if row['modern_name']=='Jerusalem' else 56 if row['region']=='main' else 44
        if entry and entry.get('category')=='town':
            width=36
        dx,dy=art_offsets.get(row['id'],(0,0))
        if dx or dy:
            d.line((px,py,px+dx,py+dy),fill=INK,width=1)
        im.thumbnail((width,round(width*1.2)))
        left,top=round(px+dx-im.width/2),round(py+dy-im.height+4)
        base.paste(im,(left,top),im)
        art_bounds.append((left,top,left+im.width,top+im.height))
        illustrated[row['id']]=(px+dx,py+dy+15)
    from build_constantinople_detail import render_landscape_pairing
    city=next((entry for entry in selected_art if entry['site_id']=='constantinople'),None)
    if city:
        landscape=render_landscape_pairing(city)
        if landscape is not None:
            x,y=round(190*S),round(7920*S)
            landscape.thumbnail((880,380),Image.Resampling.LANCZOS)
            header=26
            base.paste(landscape,(x,y+header))
            panel=(x,y,x+landscape.width,y+header+landscape.height)
            d.rectangle((x,y,x+landscape.width,y+header),fill=PAPER)
            d.text((x+14,y+4),'Constantinople and the Bosphorus · circa 1180',font=font(19),fill=INK)
            d.rectangle(panel,outline=INK,width=2)
            art_bounds.append(panel)
    d=ImageDraw.Draw(base)
    buffer=io.BytesIO();base.save(buffer,format='PNG')
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="36in" height="48in" viewBox="0 0 {W} {H}" role="img" aria-label="Crusader Period 1095–1291: occupation and siege map">',
         '<title>Crusader Period · 1095–1291</title>',
         f'<image x="0" y="0" width="{W}" height="{H}" href="data:image/png;base64,{base64.b64encode(buffer.getvalue()).decode()}"/>']
    def rect(x,y,w,h):
        d.rectangle((x,y,x+w,y+h),fill=PAPER,outline=INK,width=2)
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PAPER}" stroke="{INK}"/>')
    def text(x,y,value,size=16,color=INK):
        d.text((x,y),value,font=font(size),fill=color)
        svg.append(f'<text x="{x}" y="{y+size}" font-size="{size}" fill="{color}" font-family="serif">{html.escape(value)}</text>')
    tx,ty,tw,th=round(2700*S),round(6750*S),round(3000*S),round(1100*S)
    rect(tx,ty,tw,th);text(tx+34,ty+35,'Crusader Period',54)
    text(tx+34,ty+113,'1095–1291',38,RED)
    text(tx+34,ty+179,'Occupations · holdings · recorded sieges',21)
    lx,ly=round(300*S),round(4850*S)
    rect(lx,ly,round(2200*S),round(1750*S))
    for j,line in enumerate(['HOW TO READ THIS MAP','147 numbered source sites','Red ring: a recorded siege in 1095–1291','Grey: occupation details require review','Numbers link to the occupation / siege index','Dates describe selected phases, not continuous rule','No siege recorded ≠ proof of no siege','Mainland focus; Aegean and Egypt give context']):
        text(lx+18,ly+18+j*43,line,20 if j==0 else 15,INK if j!=2 else RED)
    occupied=art_bounds+[(tx,ty,tx+tw,ty+th),(lx,ly,lx+round(2200*S),ly+round(1750*S))]
    label_font=font(12)
    for row in sorted(rows,key=lambda r:(r['id'] not in illustrated,r['region'],r['tier'],r['id'])):
        px,py=anchor(row)
        assert 0<=px<=W and 0<=py<=H,(row['id'],px,py)
        number=row['id'].split('-')[1]
        label=f"{number} {row['title']}" if row['id'] in illustrated else number
        text_width=d.textlength(label,font=label_font)
        half_width=max(13,math.ceil(text_width/2)+5)
        preferred_x,preferred_y=illustrated.get(row['id'],(px,py))
        x,y=preferred_x,preferred_y
        # Move nameplates and number badges while keeping the geographic anchor.
        for radius in (0,14,25,38,52,68,88,112,145,180):
            candidates=[(preferred_x,preferred_y)] if radius==0 else [
                (preferred_x+radius*math.cos(a*math.pi/8),preferred_y+radius*math.sin(a*math.pi/8)) for a in range(16)]
            found=False
            for cx,cy in candidates:
                b=(cx-half_width-2,cy-10,cx+half_width+2,cy+10)
                inside=14<b[0] and b[2]<W-14 and 14<b[1] and b[3]<H-90
                if inside and not any(not(b[2]<q[0] or b[0]>q[2] or b[3]<q[1] or b[1]>q[3]) for q in occupied):
                    x,y=cx,cy;occupied.append(b);found=True;break
            if found:break
        color=RED if row['sieges'] else '#827d75' if row['review_required'] else INK
        title=f"{row['id']} · {row['title']} | Occupation: {row['occupation']} | Sieges: {row['siege_label']}"
        row['map_anchor_px']=[round(px,2),round(py,2)];row['callout_px']=[round(x,2),round(y,2)]
        d.line((px,py,x,y),fill=color,width=1)
        d.ellipse((px-2,py-2,px+2,py+2),fill=color)
        d.rounded_rectangle((x-half_width,y-9,x+half_width,y+9),radius=7,fill=PAPER,outline=color,width=2 if row['sieges'] else 1)
        d.text((x,y),label,font=label_font,fill=INK,anchor='mm')
        svg.extend([f'<a href="#{row["id"]}" data-id="{row["id"]}" tabindex="0"><title>{html.escape(title)}</title>',
            f'<line x1="{px:.2f}" y1="{py:.2f}" x2="{x:.2f}" y2="{y:.2f}" stroke="{color}" stroke-width=".7"/>',
            f'<circle cx="{px:.2f}" cy="{py:.2f}" r="2" fill="{color}"/>',
            f'<rect x="{x-half_width:.2f}" y="{y-9:.2f}" width="{2*half_width}" height="18" rx="7" fill="{PAPER}" stroke="{color}" stroke-width="{2 if row["sieges"] else 1}"/>',
            f'<text x="{x:.2f}" y="{y+4:.2f}" font-family="serif" font-size="12" text-anchor="middle" textLength="{text_width:.2f}" lengthAdjust="spacingAndGlyphs" fill="{INK}">{html.escape(label)}</text></a>'])
    text(65,H-85,'CRUSADER PERIOD · 1095–1291  |  Gazetteer: CP-001–CP-147  |  Representative locations, not surveyed footprints',17)
    text(65,H-55,'Red rings are selected recorded sieges. Unresolved occupation dates and regional context are identified in the index.',15)
    svg.append('</svg>');svg='\n'.join(svg)
    preview=ROOT/'previews';prints=ROOT/'print';preview.mkdir(exist_ok=True)
    (prints/'Crusader-Period-1095-1291.svg').write_text(svg)
    base.save(preview/'Crusader-Period-1095-1291.jpg',quality=94)
    cards=[]
    for row in rows:
        references=row['references'] or [row['inherited_source']]
        links=' · '.join(f'<a href="{html.escape(r)}" target="_blank" rel="noreferrer">Source {i+1}</a>' for i,r in enumerate(references))
        cards.append(f'''<article id="{row['id']}" data-region="{row['region']}"><h2>{row['id']} · {html.escape(row['title'])}</h2><p class="alternate">{html.escape(row['name'])} · {row['region']}</p><h3>Occupation / holding</h3><p>{html.escape(row['occupation'])}</p><h3>Recorded sieges</h3><p>{html.escape(row['siege_label'])}</p><details><summary>Evidence and review notes</summary><p>{html.escape(row['occupation_status'].replace('-',' '))}</p>{''.join('<p>'+html.escape(n)+'</p>' for n in row['notes'])}<p>{links}</p><p>Siege list is selective. An empty record does not establish that no siege occurred.</p></details></article>''')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Crusader Period · 1095–1291</title><style>
*{box-sizing:border-box}body{margin:0;background:#eee4ce;color:#392d24;font:16px Georgia,serif}header{padding:22px 28px;border-bottom:1px solid #bcac8b;background:#f8f1e1}h1{font-size:32px;margin:0 0 7px}header p{margin:0;line-height:1.5}main{display:grid;grid-template-columns:minmax(500px,1fr) 430px;height:calc(100vh - 112px)}.map{overflow:auto;padding:16px}.map svg{width:100%;height:auto}aside{overflow:auto;border-left:1px solid #bcac8b;background:#fbf7ed}.filters{position:sticky;top:0;padding:16px;background:#f5eddb;border-bottom:1px solid #bcac8b}input,select{font:inherit;padding:10px;width:100%;margin-bottom:8px;border:1px solid #b3a58a;border-radius:4px}article{padding:20px;border-bottom:1px solid #d3c7b0}article.active{background:#f3dfb7;outline:2px solid #9c3b30;outline-offset:-2px}h2{font-size:21px;margin:0 0 6px}h3{font-size:14px;text-transform:uppercase;letter-spacing:.08em;margin:20px 0 5px;color:#8d342b}article p{line-height:1.5;margin:5px 0}.alternate{color:#77715f;font-size:14px}details{font-size:14px;margin-top:17px}a{color:#8b382e}svg a{cursor:pointer}svg a:hover rect,svg a:focus rect{fill:#f2c27f}#count{font:14px system-ui;color:#74664e}button{font:inherit;background:#5b4938;color:white;border:0;padding:8px 12px;margin-top:10px;border-radius:4px}@media(max-width:900px){main{display:block;height:auto}.map{max-height:70vh}aside{max-height:80vh}}@media print{header{position:static}main{display:block;height:auto}.map{overflow:visible;page-break-after:always}aside{overflow:visible}.filters{display:none}article{break-inside:avoid}details{display:block}details>*{display:block}}
</style><header><h1>Crusader Period <span style="color:#9c3b30">1095–1291</span></h1><p>Mainland Crusader States, with Aegean and Egyptian context. Click a numbered site for occupation periods, siege dates and evidence.</p></header><main><div class="map">__SVG__</div><aside><div class="filters"><input id="search" placeholder="Find a site, ruler, date or siege…" aria-label="Search occupation and siege records"><select id="region" aria-label="Region"><option value="">All 147 sites</option value="main">Mainland, Cyprus and Cilicia</option><option value="delta">Egypt and Sinai</option><option value="aegean">Aegean context</option></select><div id="count">147 records</div></div>__CARDS__</aside></main><script>
const cards=[...document.querySelectorAll('article')],search=document.querySelector('#search'),region=document.querySelector('#region');function filter(){let count=0;for(const c of cards){const show=(!region.value||c.dataset.region===region.value)&&c.textContent.toLowerCase().includes(search.value.toLowerCase());c.hidden=!show;if(show)count++}document.querySelector('#count').textContent=count+' site records'}search.addEventListener('input',filter);region.addEventListener('change',filter);document.querySelectorAll('svg a[data-id]').forEach(a=>a.addEventListener('click',ev=>{ev.preventDefault();search.value='';region.value='';filter();cards.forEach(c=>c.classList.remove('active'));let card=document.getElementById(a.dataset.id);card.classList.add('active');card.scrollIntoView({behavior:'smooth',block:'nearest'});}));
</script></html>'''.replace('__SVG__',svg).replace('__CARDS__',''.join(cards))
    (preview/'Crusader-Period-1095-1291.html').write_text(page)
    print('Rendered all',len(rows),'site markers, print SVG, preview and searchable chronology map')


if __name__=='__main__':main()
