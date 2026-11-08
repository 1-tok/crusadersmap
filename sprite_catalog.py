"""Unified provisional sprite catalog, technical QA and year-gated placement export.

Run with Pillow installed: python3 sprite_catalog.py [--year 1180].
Paths in catalog.json and placements-*.geojson are relative to data/sprites.
"""
from pathlib import Path
import argparse
import hashlib
import json
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
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def placements(catalog, year):
    """One preferred, approved, available image per site; missing files never place."""
    by_site = {}
    for e in catalog['assets']:
        period = e['availability']
        if not (e['asset'] and e['approval']['provisional_map_use']
                and e['technical_qa']['status'] == 'pass'):
            continue
        if not period['from_year'] <= year <= period['through_year']:
            continue
        site = e['site_id']
        if site not in by_site or e['selection_priority'] > by_site[site]['selection_priority']:
            by_site[site] = e
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
            coordinates=e['coordinates'], coordinate_source='places.py; inherited approximate map coordinates',
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
    missing = []
    for slug, name, lon, lat, mark in [
        ('belvoir', 'Belvoir', 35.52, 32.60, 'P:belvoir'),
        ('kerak', 'Kerak', 35.70, 31.18, 'P:kerak'),
        ('montreal-shobak', 'Montréal (Shobak)', 35.53, 30.53, 'P:montreal'),
        ('montfort', 'Montfort', 35.24, 33.04, 'P:montfort')]:
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
    write(BASE/'catalog.json', catalog)
    return catalog


def export(catalog, year):
    features = []
    for e in placements(catalog, year):
        features.append(dict(type='Feature', id=e['id'],
            geometry=dict(type='Point', coordinates=e['coordinates']),
            properties=dict(site_id=e['site_id'], name=e['name'], asset=e['asset'],
                anchor_normalized=e['anchor_normalized'], display_width_units=e['display_width_units'],
                status=e['approval']['status'], repaint_later=True, year=year)))
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
