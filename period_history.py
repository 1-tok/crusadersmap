"""Build period-specific site occupation and siege labels, preserving original catalogs."""
from pathlib import Path
import json,re
import places
ROOT=Path(__file__).resolve().parent
BASE=ROOT/'data/manifests/crusader-period'
TITLE='Crusader Period'
START,END=1095,1291


def slug(text):
    return re.sub('[^a-z0-9]+','-',text.lower()).strip('-')


def within(text):
    """Clip display to scope; retain full original chronology in the record."""
    parts=[]
    text=re.sub(r'\b(\d{4})\s*-\s*(\d{2})\b',lambda m:m[1]+' - '+m[1][:2]+m[2],text)
    for part in text.split(','):
        years=[int(y) for y in re.findall(r'\b\d{4}\b',part)]
        if years and min(years)>END:continue
        if not years:continue
        def trim(m):
            lo,hi=int(m[1]),int(m[2])
            return f'{max(lo,START)}–{min(hi,END)}'+(' (continues)' if hi>END else '')
        parts.append(re.sub(r'(\d{4})\s*-\s*(\d{4})',trim,part).strip())
    return '; '.join(parts)


def build():
    source=json.loads((BASE/'reviewed-history.json').read_text())
    refs=source['sources'];rows=[]
    for i,p in enumerate(places.PLACES,1):
        region,tier,mark,lon,lat,name,alt,modern,dates,arms=p
        key=modern or name;override=source['sites'].get(key,{})
        occupation=override.get('occupation',within(dates))
        status='selected-phases-reviewed' if override else 'inherited-chronology-requires-review'
        references=[refs[r] for r in override.get('references',[])]
        notes=[override['notes']] if override.get('notes') else []
        if not occupation:
            status='local-occupation-dates-unresolved'
            occupation='Local occupation dates not established in current sources'
            if dates:notes.append('Original later-period or non-dated record: '+dates)
        if region=='delta' and key not in ('Cairo','Alexandria','Damietta','Mansoura',"Pharaoh's Island",'Aqaba'):
            occupation='Egyptian regional context: Fatimid to 1171; Ayyubid 1171–1250; Mamluk 1250–1291 (continues)'
            status='regional-context-local-control-unresolved';references=[refs['egypt-periods']]
            notes.append('Dynastic chronology is regional context, not evidence for uninterrupted occupation of this individual site.')
        if mark in ('M:point_of_interest','M:holy_spring','M:ruin'):
            notes.append('Landscape, sacred place or archaeological site: an occupation period is not a separate military garrison tenure.')
            if not override and not dates and region!='delta':
                occupation='Landscape / pilgrimage marker; no independent military occupation period assigned'
                status='not-an-independent-garrison-tenure'
        sieges=[]
        for b in places.BATTLES:
            if b[0]==region and b[1]=='siege' and (b[5]==key or b[4]==name):
                for campaign in b[6].split(','):
                    text=within(campaign)
                    if text:
                        sieges.append(dict(period=text,from_year=min(int(y) for y in re.findall(r'\d{4}',text)),through_year=max(int(y) for y in re.findall(r'\d{4}',text)),references=[],review_required=True,source='Inherited BATTLES catalog; detailed siege limits require review'))
        if key in source['sieges']:
            sieges=[]
            for event in source['sieges'][key]:
                e=dict(event);e['references']=[refs[r] for r in event['references']];sieges.append(e)
        for e in sieges:
            assert START<=e['from_year']<=e['through_year']<=END
        refs_all=references+[r for e in sieges for r in e.get('references',[])]
        row=dict(id=f'CP-{i:03d}',source_index=i-1,region=region,tier=tier,mark=mark,
            title=override.get('display_title',key),name=name,modern_name=key,alternate_name=alt,coordinates=[lon,lat],
            in_scope=override.get('in_scope',True),
            occupation=occupation,occupation_status=status,source_occupation=dates,
            sieges=sieges,siege_label='; '.join(e['period'] for e in sieges) if sieges else 'No siege recorded in this index',
            siege_coverage='selected-documented-events; absence is not proof of no siege',
            notes=notes,references=list(dict.fromkeys(refs_all)),
            inherited_source='https://github.com/1-tok/crusadersmap/blob/22e91d258bca9603a2ecb261528e455ad19c63f1/places.py',
            coordinates_surveyed=False,review_required=bool(override.get('review_required',not bool(override))))
        rows.append(row)
    out=dict(schema_version=1,title=TITLE,from_year=START,through_year=END,
        subtitle='Selected occupations and recorded sieges',
        coverage=dict(site_records=len(rows),sites_with_siege_records=sum(bool(e['sieges']) for e in rows),
            sites_without_dated_occupation_record=sum(e['occupation_status']=='local-occupation-dates-unresolved' for e in rows),
            sites_requiring_review=sum(e['review_required'] for e in rows),
            geographic_references_outside_period=sum(not e['in_scope'] for e in rows)),
        historical_policy=source['policy'],sites=rows)
    (BASE/'site-history.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    features=[dict(type='Feature',id=e['id'],geometry=dict(type='Point',coordinates=e['coordinates']),properties=e) for e in rows]
    (BASE/'site-history.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features),indent=2,ensure_ascii=False)+'\n')
    lines=['# Crusader Period · 1095–1291','',out['historical_policy'],'',
           'All 147 source sites have occupation and siege fields. Unresolved local dates and regional context remain explicit. No siege recorded does not mean no siege occurred.','',
           '| Map ID | Site | Occupation / holding | Recorded sieges |','|---|---|---|---|']
    for e in rows:lines.append(f"| {e['id']} | {e['modern_name']} | {e['occupation']} | {e['siege_label']} |")
    (BASE/'GAZETTEER.md').write_text('\n'.join(lines)+'\n')
    print(out['coverage'])
    return out


def label_record(region,name):
    p=BASE/'site-history.json'
    if not p.exists():return None
    return next((e for e in json.loads(p.read_text())['sites'] if e['region']==region and e['name']==name),None)


if __name__=='__main__':build()
