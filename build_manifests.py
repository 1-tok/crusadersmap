"""Build reviewable map-content inventories without importing rendering modules.
Python standard library only. Editorial additions live in data/manifests/proposals.json.
"""
import ast
import collections
import csv
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'data/manifests'
REV = '22e91d258bca9603a2ecb261528e455ad19c63f1'

def assignment(file, name):
    for node in ast.parse((ROOT/file).read_text()).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return node.value
    raise KeyError((file, name))

def literal(file, name):
    return ast.literal_eval(assignment(file, name))

def slug(s):
    return re.sub('[^a-z0-9]+', '-', s.lower()).strip('-')

def point(lon, lat):
    return None if lon is None else {'type':'Point', 'coordinates':[lon,lat]}

def provenance(file, name, index=None):
    return {'file':file, 'assignment':name, 'index_zero_based':index, 'base_commit':REV,
            'url':f'https://github.com/1-tok/crusadersmap/blob/{REV}/{file}'}

def write(name, obj):
    (OUT/name).write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')

def build():
    proposals=json.loads((OUT/'proposals.json').read_text())
    places=literal('places.py','PLACES'); battles=literal('places.py','BATTLES'); isles=literal('places.py','ISLES')
    loc=[];land=[]
    def existing(ident,name,kind,region,geo,source,**kw):
        return dict(id=ident,name=name,category=kind,region=region,geometry=geo,status='existing_source_definition',recommendation='retain_with_review',historical_review_required=True,placement_accuracy='approximate_repository_coordinates',source=source,**kw)
    for i,(region,tier,mark,lon,lat,name,alt,modern,dates,arms) in enumerate(places):
        if 'castle' in mark or 'tower' in mark: kind='castle_or_fortification'
        elif any(k in mark for k in ['church','cathedral','monastery','spring']):kind='religious_site'
        elif 'ruin' in mark:kind='ruin'
        elif 'point_of_interest' in mark:kind='landmark'
        else:kind='settlement_or_profile'
        castle_profiles={'pelerin','safed','belvoir','montfort','beaufort','kerak','montreal','ajlun','krak','margat','saone','masyaf','baghras','hilarion','sis','mistra','bodrum'}
        religious_profiles={'bethlehem','hebron','nazareth','sinai'}
        if mark.startswith('P:'):
            profile=mark[2:]
            kind='castle_or_citadel' if profile in castle_profiles else 'religious_settlement_or_site' if profile in religious_profiles else 'holy_mountain' if profile=='tabor' else 'city_or_town'
        if modern in {'Sea of Galilee','Mount Carmel','Cana','Jordan baptism place'}:
            kind={'Sea of Galilee':'lake_landmark','Mount Carmel':'holy_mountain','Cana':'pilgrimage_site','Jordan baptism place':'holy_site'}[modern]
        ident='place-'+slug(region+'-'+modern)
        loc.append(existing(ident,modern,kind,region,point(lon,lat),provenance('places.py','PLACES',i),names={'map':name,'alternative':alt,'modern':modern},tier=tier,renderer_mark=mark,dates_verbatim=dates,affiliations_verbatim=list(arms),classification_basis='renderer symbol plus editorial profile classification; profile may combine settlement and landmark',temporal_rule='dates describe selected associations, not complete existence or continuous ownership'))
    for i,(region,kind,lon,lat,name,modern,year) in enumerate(battles):
        related=[p['id'] for p in loc if p['name']==modern and p['region']==region]
        loc.append(existing('event-'+slug(region+'-'+kind+'-'+name),name,kind,region,point(lon,lat),provenance('places.py','BATTLES',i),modern_name=modern,dates_verbatim=year,related_place_ids=related,temporal_rule='event marker; display in historical overview or event-year layer'))
    for i,(region,lon,lat,name,modern) in enumerate(isles):
        land.append(existing('island-'+slug(modern),modern,'island_label',region,point(lon,lat),provenance('places.py','ISLES',i),map_name=name,geometry_role='label_anchor_not_island_boundary'))
    for row in proposals['locations']:
        name,kind,lon,lat,region,priority,note,*refs=row
        loc.append(dict(id='proposed-'+slug(name),name=name,category=kind,region=region,geometry=point(lon,lat),status='proposed_addition',recommendation='add_after_review',priority=priority,notes=[note],references=refs,historical_review_required=True,placement_accuracy='editorial_approximation_not_surveyed',temporal_rule='research existence, building phases and appropriate names for selected year',source={'file':'data/manifests/proposals.json','section':'locations'}))
    roads=literal('build_stage2.py','ROADS')
    road_names=['Levant coastal corridor: Antioch–Ascalon','Acre–Tiberias–Damascus corridor','Jaffa–Jerusalem corridor','Jerusalem–Hebron corridor','Antioch–Aleppo corridor','Aleppo–Hama–Homs–Damascus corridor','Tripoli–Homs corridor','Kyrenia–Nicosia–Famagusta corridor','Nicosia–Limassol corridor']
    for i,coords in enumerate(roads):
        land.append(dict(id=f'road-existing-{i+1:02}',name=road_names[i],category='road',region='main',geometry={'type':'LineString','coordinates':coords},geometry_role='existing_schematic_control_points_not_surveyed_alignment',status='existing_source_definition',recommendation='retain_with_review',historical_review_required=True,source=provenance('build_stage2.py','ROADS',i),notes=['Descriptive name inferred from control points; source paths have no names. Renderer smooths control points.']))
    for i,coords in enumerate(literal('terrain.py','EXTRA_RIVERS')):
        land.append(dict(id=f'river-extra-{i+1:02}',name=['Orontes (inferred)','Litani (inferred)','Yarmuk (inferred)','Ceyhan (inferred)','Tarsus river (inferred)'][i],category='river',region='main',geometry={'type':'LineString','coordinates':coords},geometry_role='schematic_source_course',status='existing_source_definition',recommendation='retain_with_review',historical_review_required=True,source=provenance('terrain.py','EXTRA_RIVERS',i)))
    for region,constant in [('main','MAIN'),('aegean','AEGEAN'),('delta','DELTA')]:
        node=assignment('terrain.py',constant)
        for kw in node.keywords:
            if kw.arg not in ['green','desert','conifer','decid','marsh','dune','oasis']:continue
            for i,zone in enumerate(ast.literal_eval(kw.value)):
                land.append(dict(id=f'zone-{region}-{kw.arg}-{i+1:02}',name=f'{region} {kw.arg} zone {i+1}',category='terrain_zone',terrain_type=kw.arg,region=region,status='existing_source_definition',recommendation='retain_with_review',geometry=point(*zone[:2]),geometry_role='procedural_distribution_anchor_not_boundary',zone_parameters_verbatim=list(zone[2:]),parameter_units='km; Gaussian field scale for 3-value zones, elliptical scales for marsh; oasis has no scale',historical_review_required=True,source=provenance('terrain.py',constant+'.'+kw.arg,i)))
    # Political text paths are lettering guides, never territorial polygons.
    pol=assignment('build_stage2.py','POL')
    for key,rows in zip(pol.keys,pol.values):
        region=ast.literal_eval(key)
        for i,row in enumerate(rows.elts):
            name,modern,dates,coords=[ast.literal_eval(n) for n in row.elts[:4]]
            land.append(dict(id='polity-'+slug(name),name=modern,map_name=name,category='political_label',region=region,dates_verbatim=dates,status='existing_source_definition',recommendation='retain_with_review',geometry={'type':'LineString','coordinates':coords},geometry_role='lettering_baseline_not_border',historical_review_required=True,source=provenance('build_stage2.py','POL.'+region,i)))
    for row in proposals['landscape']:
        name,kind,lon,lat,region,priority,*refs=row
        land.append(dict(id='landscape-'+slug(name),name=name,category=kind,region=region,geometry=point(lon,lat),geometry_role='proposed_label_anchor_not_boundary_or_course',status='proposed_named_overlay',recommendation='add_label_or_refine_existing_terrain_after_review',priority=priority,references=refs,historical_review_required=True,notes=['May already be represented by unnamed base geometry or procedural relief; do not add duplicate physical geometry. Medieval shorelines, vegetation and wetland extent require review.'],source={'file':'data/manifests/proposals.json','section':'landscape'}))
    lookup={}
    for p in loc:
        lookup[p['name']]=p['id']
    for i,(name,region,stops,note) in enumerate(proposals['routes']):
        ids=[lookup[s] for s in stops]
        land.append(dict(id=f'route-proposed-{i+1:02}',name=name,category='route_corridor',region=region,status='proposed_addition',recommendation='research_before_drawing',geometry=None,waypoint_place_ids=ids,waypoint_names=stops,historical_review_required=True,notes=[note],source={'file':'data/manifests/proposals.json','section':'routes'}))
    # Capture all six hand-restored lake anchors from init_lakes, without executing it.
    tree=ast.parse((ROOT/'terrain.py').read_text())
    lake_calls=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef) and node.name=='init_lakes':
            for child in ast.walk(node):
                if isinstance(child,ast.AugAssign) and isinstance(child.target,ast.Name) and child.target.id=='LAKES_OK':
                    lake_calls=child.value.elts
    for i,call in enumerate(lake_calls):
        lo,la,rx,ry=[ast.literal_eval(a) for a in call.args]
        land.append(dict(id=f'lake-restored-{i+1:02}',name=f'Hand-restored lake {i+1}',category='restored_lake',region='delta' if lo<34 else 'main',geometry=point(lo,la),geometry_role='procedural_ellipse_center_not_historically_surveyed_shoreline',ellipse_radii_degrees=[rx,ry],status='existing_source_definition',recommendation='review_identity_and_medieval_extent',historical_review_required=True,source={'file':'terrain.py','function':'init_lakes','base_commit':REV}))
    for key,file,role in [('land','data/ne_10m_land.geojson','coast_and_land'),('islands','data/ne_10m_minor_islands.geojson','minor_islands'),('lakes','data/ne_10m_lakes.geojson','lake_polygons'),('rivers','data/ne_10m_rivers_lake_centerlines.geojson','river_centerlines'),('elevation','data/tiles','elevation_tiles')]:
        land.append(dict(id='base-layer-'+key,name=role,category='base_dataset',region='all_rendered_regions',status='existing_source_definition',recommendation='retain_with_medieval_geography_review',geometry=None,dataset_path=file,historical_review_required=True,source={'file':'terrain.py','base_commit':REV},notes=['Retain dataset reference rather than duplicate global features. Renderer clips to each region. Modern data are not a reconstruction of medieval coastlines or vegetation.']))
    issue_map={
        'Pelusium':['alias-conflicts-with-bilbeis'],
        'Petra':['settlement-versus-castle-identity'],
        'Tripoli':['port-versus-inland-citadel'],
        'Cana':['traditional-location-identification'],
        'Jordan baptism place':['traditional-location-identification'],
        'Montgisard':['battlefield-location-review'],
        'Safed':['association-dates-not-complete-site-history'],
        'Arnoun':['association-dates-not-complete-site-history'],
        "Qal'at al-Marqab":['association-dates-not-complete-site-history'],
        'Arwad':['association-dates-not-complete-site-history'],
        'Montfort':['building-phase-review'],
        'Atlit':['building-phase-review']}
    for e in loc:
        e['review_flags']=['historical-validation-pending']+issue_map.get(e['name'],[])
        if e['status']=='proposed_addition': e['review_flags'].append('coordinate-and-period-research-pending')
    for e in land:
        e['review_flags']=['historical-geography-review-pending']
        if e['category'] in ['road','route_corridor']:e['review_flags'].append('alignment-unverified')
        if e['category']=='political_label':e['review_flags'].append('not-a-territorial-boundary')
    common=dict(schema_version=1,repository='1-tok/crusadersmap',base_commit=REV,scope={'period':[1095,1571],'mode':'multi-period_atlas_not_single_year','regions':['main','aegean','delta','jerusalem_detail','off_map']},coordinate_system='EPSG:4326; longitude, latitude',coverage='Complete explicit active source catalogs plus editorial candidates; not a claim to enumerate every historical settlement or feature of the region',historical_policy='All inherited dates and affiliations are unverified source transcriptions. Proposals are review candidates, not certified historical reconstructions.')
    write('locations.json',dict(common,entries=loc));write('landscape.json',dict(common,hydrology_source_policy={'lake_name_substrings_excluded':literal('terrain.py','MODERN_LAKES'),'river_name_substring_excluded':'Canal','warning':'Source heuristics retained, not endorsed as historical filters; some excluded lakes are natural.'},entries=land))
    for filename,entries in [('locations.csv',loc),('landscape.csv',land)]:
        with (OUT/filename).open('w',newline='') as f:
            fields=['id','name','category','region','status','recommendation','priority','longitude','latitude','dates','notes']
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
            for e in entries:
                g=e.get('geometry');coords=g['coordinates'] if g and g['type']=='Point' else [None,None]
                w.writerow(dict(id=e['id'],name=e['name'],category=e['category'],region=e['region'],status=e['status'],recommendation=e['recommendation'],priority=e.get('priority',''),longitude=coords[0],latitude=coords[1],dates=e.get('dates_verbatim',''),notes='; '.join(e.get('notes',[]))))
    counts={'source_places':len(places),'source_events':len(battles),'source_island_labels':len(isles),'source_roads':len(roads),'locations_total':len(loc),'landscape_total':len(land),'location_status_counts':dict(collections.Counter(x['status'] for x in loc)),'landscape_category_counts':dict(collections.Counter(x['category'] for x in land))}
    write('coverage.json',counts)
    # Structural coverage checks: retained rows, unique IDs, valid coordinates and route references.
    assert len([e for e in loc if e['source'].get('assignment')=='PLACES'])==len(places)
    assert len([e for e in loc if e['source'].get('assignment')=='BATTLES'])==len(battles)
    all_entries=loc+land; ids=[e['id'] for e in all_entries];assert len(ids)==len(set(ids))
    for e in all_entries:
        for ref in e.get('waypoint_place_ids',[]):assert ref in ids
        g=e.get('geometry')
        if g:
            points=[g['coordinates']] if g['type']=='Point' else g['coordinates']
            assert all(-180<=lo<=180 and -90<=la<=90 for lo,la in points)
    lines=['# Complete map content catalog','', 'Generated by `build_manifests.py`. See README for scope, review rules and limitations.','']
    for title, entries in [('Cities, locations, landmarks and events',loc),('Roads, landscape and terrain',land)]:
        lines += ['## '+title,'','| ID | Name | Category | Region | Status |','|---|---|---|---|---|']
        for e in entries:
            lines.append('| '+' | '.join(str(e[k]).replace('|','/') for k in ['id','name','category','region','status'])+' |')
        lines.append('')
    (OUT/'CATALOG.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(counts,indent=2))

if __name__=='__main__':build()
