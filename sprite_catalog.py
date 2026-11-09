"""Unified provisional sprite catalog, technical QA and year-gated placement export.

Run with Pillow installed: python3 sprite_catalog.py [--year 1180].
Paths in catalog.json and placements-*.geojson are relative to data/sprites.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
from PIL import Image

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'data/sprites'


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def qa(path):
    with Image.open(path) as im:
        assert im.mode == 'RGBA', (path, im.mode)
        alpha = im.getchannel('A')
        bounds = alpha.getbbox()
        assert bounds and alpha.getextrema()[0] == 0, path
        pad = min(bounds[0], bounds[1], im.width-bounds[2], im.height-bounds[3])
        assert pad >= 1, (path, 'paint touches canvas edge')
        return dict(status='pass', mode=im.mode, dimensions_px=list(im.size),
                    transparent_padding_px=pad, alpha_extrema=list(alpha.getextrema()),
                    painted_bounds_xyxy=list(bounds),
                    pixel_sha256=hashlib.sha256(im.width.to_bytes(4,'big')+im.height.to_bytes(4,'big')+im.tobytes()).hexdigest(),
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def placements(catalog, year, view='atlas'):
    """One preferred, approved, available image per site; missing files never place."""
    by_site = {}
    for e in catalog['assets']:
        if view is not None and e.get('placement_view','atlas') != view:
            continue
        period = e['availability']
        if e.get('geographic_placement_ready') is False:
            continue
        if not (e['asset'] and e['approval']['provisional_map_use']
                and e['technical_qa']['status'] == 'pass'):
            continue
        if year == 1180 and not e.get('period_1180_eligible', True):
            continue
        if not period['from_year'] <= year <= period['through_year']:
            continue
        site = e['site_id']
        if site not in by_site or e['selection_priority'] > by_site[site]['selection_priority']:
            by_site[site] = e
    return [by_site[k] for k in sorted(by_site)]


def atlas_placements(catalog):
    """Multi-period editorial view: 1180 sites plus approved later sites, dated."""
    by_site={e['site_id']:e for e in placements(catalog,1180)}
    for e in catalog['assets']:
        if e.get('period_1180_eligible',True) or not e.get('asset'):
            continue
        if not e['approval']['provisional_map_use'] or e['technical_qa']['status']!='pass':
            continue
        if e['site_id'] not in by_site or e['selection_priority']>by_site[e['site_id']]['selection_priority']:
            by_site[e['site_id']]=e
    return [by_site[k] for k in sorted(by_site)]


def build():
    legacy = read(BASE/'manifest.json')
    oldqa = {e['id']: e for e in read(BASE/'validation.json')['sprites']}
    assets = []
    for e in legacy['sprites']:
        assets.append(dict(
            id=e['id'], site_id=e['slug'], name=e['name'], category=e['category'],
            asset=e['asset'], source=e['source'], coordinates=[e['placement']['longitude'], e['placement']['latitude']],
            coordinate_source=e['placement']['coordinate_source'], coordinates_surveyed=False,
            repo_place_id=e['placement']['repo_place_id'], anchor_normalized=e['anchor_normalized'],
            display_width_units=512, selection_priority=20 if e['variant']=='standalone' else 10,
            historical=e['historical'], original_extraction_qa=oldqa[e['id']]))
    for e in read(BASE/'historical-1180/manifest.json')['assets']:
        assets.append(dict(
            id=e['id'], site_id=e['id'].removesuffix('-1180-v2'), name=e['id'].removesuffix('-1180-v2').title(),
            category='castle' if e['id'].startswith('belvoir') else 'city',
            asset='historical-1180/'+e['file'], source=dict(path='historical-1180/'+e['source'], sha256=e['source_sha256']),
            coordinates=e.get('proposed_placement_coordinates', e['coordinates']),
            inherited_coordinates=e['coordinates'],
            coordinate_source='historical batch proposed coastal anchor' if 'proposed_placement_coordinates' in e else 'places.py; inherited approximate map coordinates',
            coordinates_surveyed=False, repo_place_id=e['repo_place_id'],
            anchor_normalized=e['anchor_normalized'], display_width_units=e['display_width_units'], selection_priority=30,
            historical=dict(target_year=1180, accuracy='period-informed-interpretation',
                            requires_historical_review=True, requires_repaint_review=True,
                            review=e['review'], references=e['references'])))
    for e in read(BASE/'expansion/manifest.json')['assets']:
        assets.append(dict(e, asset='expansion/'+e['file'], source=dict(path='expansion/'+e['source'], sha256=e['source_sha256'])))
    for e in assets:
        e['technical_qa'] = qa(BASE/e['asset'])
        e['approval'] = dict(status='approved-provisional', provisional_map_use=True,
                             repaint_later=True, authority='User request, 2026-11-07',
                             historical_accuracy_certified=False)
        # These pictures are an 1180 brief, not evidence for the full atlas timeline.
        e['availability'] = dict(from_year=1180, through_year=1180,
                                 basis='working circa-1180 depiction only; other years require phase review')
        e['historical']['requires_repaint_review'] = True
        e['historical']['requires_historical_review'] = True
    archive_path=BASE/'archive-1180/imported.json'
    if archive_path.exists():
        assets.extend(read(archive_path)['assets'])
    for manifest in sorted(BASE.glob('greece-egypt*/manifest.json')):
        batch=read(manifest)
        # A new draft must not become approved just because its folder exists.
        if batch.get('release_status')!='published-provisional':
            continue
        for original in batch['assets']:
            e=dict(original)
            folder=manifest.parent.name
            approved_dates=e.get('date_ranges',{})
            first_year=approved_dates.get('approved_art_from',1180)
            last_year=approved_dates.get('approved_art_through',1180)
            e.update(asset=folder+'/'+e['file'],source=dict(path=folder+'/'+e['source'],sha256=e['source_sha256']),
                selection_priority=40,variant='generated-city',
                approval=dict(status='approved-provisional',provisional_map_use=True,repaint_later=True,
                    authority='User request, 2026-11-08',historical_accuracy_certified=False),
                availability=dict(from_year=first_year,through_year=last_year,
                    basis=f'circa-{first_year} depiction. Political occupation is tracked separately.'),
                historical=dict(target_year=first_year,requires_historical_review=True,requires_repaint_review=True,
                    references=e['references'],notes=e['repaint_flags']))
            e['technical_qa']=qa(BASE/e['asset'])
            assets.append(e)
    recovered_sites={e['site_id'] for e in assets if e.get('variant')=='archive-primary'}
    missing = []
    for slug, name, lon, lat, mark in [
        ('belvoir', 'Belvoir', 35.52, 32.60, 'P:belvoir'),
        ('kerak', 'Kerak', 35.70, 31.18, 'P:kerak'),
        ('montreal-shobak', 'Montréal (Shobak)', 35.53, 30.53, 'P:montreal'),
        ('montfort', 'Montfort', 35.24, 33.04, 'P:montfort')]:
        if slug in recovered_sites:
            continue
        later = slug == 'montfort'
        missing.append(dict(id=slug+'-prior-standalone-missing', site_id=slug, name=name,
            category='castle', asset=None, coordinates=[lon, lat], repo_place_id=mark,
            source=dict(status='not-recovered', note='Named by user; no attachment exposed by referenced chat and no corresponding standalone file recovered. Belvoir v2 is separately preserved; its identity with the requested earlier image is unconfirmed.'),
            selection_priority=0, technical_qa=dict(status='not-run-missing-source'),
            approval=dict(status='pending-source-recovery', provisional_map_use=False, repaint_later=True),
            availability=dict(from_year=1226 if later else 1180, through_year=1271 if later else 1180,
                available_at_default_year=not later,
                basis='1226 is construction start, not completion or approval for any phase' if later else 'working circa-1180 brief'),
            historical=dict(requires_historical_review=True, requires_repaint_review=True,
                later_period_only=later, exclude_from_1180=later,
                notes=['Main Teutonic castle begun in 1220s. Do not place at 1180. Review depicted phase before approving any later-year placement.'] if later else ['Do not substitute the sheet image and claim the missing standalone was recovered.'],
                references=['https://moses.creighton.edu/vr/Montfort/txt/intro.html'] if later else [])))
    catalog = dict(schema_version=1, default_year=1180,
        period_note='Circa 1180 is the default sprite brief, not the date of the existing 1095–1571 atlas.',
        approval_policy='Place available approved PNGs now as provisional art; flag repaint and historical review. Missing sources are not approved.',
        coordinate_order='longitude, latitude (WGS84); inherited map anchors, not surveyed footprints',
        anchor_convention='normalized PNG x/y; bottom-center painted-ground convention, not true georeferencing',
        units='display widths in full-size 10800 x 14400 atlas pixels',
        assets=assets+missing)
    enrich(catalog)
    write(BASE/'catalog.json', catalog)
    return catalog


def enrich(catalog):
    sites = read(BASE/'sites.json')['sites']
    catalog['schema_version'] = 2
    catalog['coordinate_order'] = 'longitude, latitude (EPSG:4326); sourced representative site points'
    catalog['coordinate_precision_policy'] = 'Published points transcribed exactly; not surveyed medieval footprints. See per-site evidence and uncertainty.'
    if not any(e['site_id']=='chateau-pelerin' for e in catalog['assets']):
        catalog['assets'].append(dict(id='chateau-pelerin-batch-missing', site_id='chateau-pelerin',
        name='Château Pèlerin', category='castle', asset=None, selection_priority=0,
        source=dict(status='not-recovered', note='Named in inaccessible 1180 batch; original ZIP and manifest not recovered.'),
        technical_qa=dict(status='not-run-missing-source'),
        approval=dict(status='pending-source-recovery', provisional_map_use=False, repaint_later=True),
        availability=dict(from_year=1218, through_year=1291, basis='Later-period site; depicted phase requires review'),
            historical=dict(requires_historical_review=True, requires_repaint_review=True)))
    ids, hashes = set(), {}
    for e in catalog['assets']:
        assert e['id'] not in ids, e['id']
        ids.add(e['id'])
        if e.get('variant')=='generated-city':
            s=dict(longitude=e['longitude'],latitude=e['latitude'],coordinate_evidence=e['coordinate_evidence'],
                historical_name=e['historical_name'],alternate_names=e.get('alternate_names',[e['name']]),
                crusader_phase=dict(from_year=e['availability']['from_year'],
                    through_year=e['availability']['through_year'],scope='Reviewed depiction year; not a Frankish-control range'),
                period_1180_eligible=e['period_1180_eligible'])
            if 'construction' in e:
                s['construction']=e['construction']
        else:
            s = sites[e['site_id']]
        e['legacy_coordinates'] = e.get('coordinates')
        e['coordinates'] = [s['longitude'], s['latitude']]
        e['geographic_placement_ready']=all(isinstance(v,(int,float)) for v in e['coordinates'])
        e.setdefault('map_region','main')
        e['latitude'], e['longitude'] = s['latitude'], s['longitude']
        e['coordinate_source'] = s['coordinate_evidence']['url']
        e['coordinate_evidence'] = s['coordinate_evidence']
        e['coordinates_surveyed'] = False
        e['historical_name'], e['alternate_names'] = s['historical_name'], s['alternate_names']
        if 'construction' in s:
            e['construction']=s['construction']
            e['undated_name']=s['historical_name']
            e['name']=f"{s['historical_name']} (begun {s['construction']['started_year']})"
        e['display_title']=e['name']
        e['site_type'] = e['category']
        e['date_ranges'] = dict(site_phase=s['crusader_phase'], approved_art=e['availability'])
        e['period_1180_eligible'] = s['period_1180_eligible']
        e['approval_for_placement'] = bool(e['asset'] and s['period_1180_eligible'] and e['technical_qa']['status']=='pass' and e['geographic_placement_ready'])
        # Library approval is year-scoped by availability; 1180 eligibility is separate.
        # Later-period art may be approved without ever becoming an 1180 stronghold.
        e['approval']['approved_for_default_year'] = e['approval_for_placement']
        e['historical']['exclude_from_1180'] = not s['period_1180_eligible']
        e['historical']['later_period_only'] = not s['period_1180_eligible']
        site_layer = {'castle': 'fortifications', 'monastery': 'religious-sites', 'landmark': 'landmarks'}.get(e['category'], 'settlements')
        e['map_layers'] = ['sprites-1180', site_layer] if s['period_1180_eligible'] else ['sprites-later-period', 'fortifications']
        e['map_layers'].append(e['map_region'])
        if e.get('placement_view')=='constantinople-detail':
            e['map_layers'].append('constantinople-detail')
        e['review_required'] = e['repaint_required'] = True
        e['uncertainty_notes'] = [s['coordinate_evidence']['uncertainty_note'], 'Provisional site eligibility does not certify every painted roof, wall, flag or terrain detail.']
        if e['asset']:
            assert re.fullmatch(r'[a-z0-9/-]+\.png', e['asset']), e['asset']
            assert (BASE/e['asset']).resolve().is_relative_to(BASE.resolve())
            q = e['technical_qa']
            # Identical RGBA pixels share a canonical asset path; paintings remain variants.
            key = q['pixel_sha256']
            e['duplicate_of'] = hashes.get(key, {}).get('id')
            if key in hashes:
                e['asset'] = hashes[key]['asset']
            else:
                hashes[key] = e
            w,h = q['dimensions_px']
            e['visual_footprint'] = dict(canvas_px=[w,h], painted_bounds_xyxy=q['painted_bounds_xyxy'],
                display_width_atlas_px=e['display_width_units'], display_height_atlas_px=e['display_width_units']*h/w,
                anchor_normalized=e['anchor_normalized'], geographic_scale=False)
    catalog['deduplication'] = dict(method='SHA-256 RGBA pixels and dimensions; preferred variant per site for placement', unique_pngs=len(hashes))


def export(catalog, year):
    features = []
    for e in placements(catalog, year):
        features.append(dict(type='Feature', id=e['id'],
            geometry=dict(type='Point', coordinates=e['coordinates']),
            properties=dict(site_id=e['site_id'], name=e['name'], asset=e['asset'],
                anchor_normalized=e['anchor_normalized'], display_width_units=e['display_width_units'],
                status=e['approval']['status'], repaint_later=True, year=year)))
        features[-1]['properties'].update(approval_for_placement=e['approval_for_placement'],
            replacement_review=e.get('replacement_review'),
            placement_view=e.get('placement_view','atlas'),
            map_region=e['map_region'],
            display_title=e['display_title'],construction=e.get('construction'),
            map_layers=e['map_layers'], historical_name=e['historical_name'],
            coordinate_evidence=e['coordinate_evidence'], visual_footprint=e['visual_footprint'])
    path=BASE/f'placements-{year}.geojson'
    write(path, dict(type='FeatureCollection', features=features))
    return path, len(features)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--year', type=int, default=1180)
    args=parser.parse_args()
    catalog=build()
    path, count=export(catalog, args.year)
    print(f'QA passed for {sum(e["asset"] is not None for e in catalog["assets"])} PNGs; {count} selected sites -> {path}')
