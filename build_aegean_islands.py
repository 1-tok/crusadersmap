"""Fit illustrated interiors to the map's existing Aegean coastline polygons."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps
from pyproj import Transformer

from build_terrain_placements import project
from frame import INSETS

ROOT = Path(__file__).resolve().parent
LIB = ROOT / 'data/landscape-assets'
LAND = 'data/ne_10m_land.geojson'
ISLANDS = {
    'Crete': (24.90, 35.20),
    'Rhodes': (28.00, 36.18),
    'Euboea': (23.90, 38.59),
    'Lesbos': (26.30, 39.28),
    'Chios': (26.02, 38.40),
    'Naxos': (25.49, 37.08),
    'Kos': (27.14, 36.83),
    'Lemnos': (25.19, 39.91),
    'Paros': (25.14, 37.06),
    'Samos': (26.83, 37.74),
}


def contains(ring, point):
    x, y = point
    inside = False
    for (x0, y0), (x1, y1) in zip(ring, ring[1:]):
        if (y0 > y) != (y1 > y) and x < (x1-x0)*(y-y0)/(y1-y0)+x0:
            inside = not inside
    return inside


def build():
    features = json.loads((ROOT / LAND).read_text())['features']
    polygons = []
    for feature in features:
        geometry = feature['geometry']
        coords = geometry['coordinates']
        polygons.extend(coords if geometry['type'] == 'MultiPolygon' else [coords])

    transform = Transformer.from_crs('EPSG:4326', INSETS['aegean']['proj'], always_xy=True)
    ref = ISLANDS['Naxos']
    ox, oy = transform.transform(*ref)
    sx, sy = project('aegean', *ref)
    nx, _ = transform.transform(26.49, 37.08)
    tx, _ = project('aegean', 26.49, 37.08)
    scale = (tx - sx) / (nx - ox)
    source = LIB / 'png/aegean-island-interior.png'
    # Central crop is opaque and avoids importing the source's painted edges.
    texture = Image.open(source)
    w, h = texture.size
    texture = texture.crop((w//4, h//4, w*3//4, h*3//4))
    assert texture.getchannel('A').getextrema()[0] >= 224
    (LIB / 'islands').mkdir(exist_ok=True)
    preview = Image.new('RGB', (1200, 1050), '#8faab9')
    draw = ImageDraw.Draw(preview)
    assets = []
    for index, (name, point) in enumerate(ISLANDS.items()):
        matches = [p for p in polygons if contains(p[0], point)]
        assert len(matches) == 1, (name, len(matches))
        rings = []
        for ring in matches[0]:
            x, y = transform.transform(*zip(*ring))
            rings.append(list(zip(x, y)))
        x, y = zip(*rings[0])
        left, bottom, right, top = min(x), min(y), max(x), max(y)
        assert right-left < 300000 and top-bottom < 300000, name
        factor = 950/max(right-left, top-bottom)
        width, height = round((right-left)*factor)+26, round((top-bottom)*factor)+26
        mask = Image.new('L', (width*2, height*2))
        paint = ImageDraw.Draw(mask)
        for i, ring in enumerate(rings):
            paint.polygon([((13+(x-left)*factor)*2, (13+(top-y)*factor)*2) for x,y in ring],
                          fill=255 if i == 0 else 0)
        image = ImageOps.fit(texture, (width, height), centering=(.3 + .1*(index % 5), .5))
        image.putalpha(mask.resize(image.size, Image.Resampling.LANCZOS))
        bbox = image.getbbox()
        assert bbox and bbox[0] > 0 and bbox[1] > 0 and bbox[2] < width and bbox[3] < height
        path = f'islands/{name.lower()}.png'
        image.save(LIB / path)
        pad = 13/factor
        assets.append(dict(id=name.lower(), name=name, file=path, region='aegean',
                           context_anchor_lonlat=point, dimensions_px=image.size,
                           bounds_sheet_px=[sx+(left-pad-ox)*scale, sy-(top+pad-oy)*scale,
                                            sx+(right+pad-ox)*scale, sy-(bottom-pad-oy)*scale],
                           sha256=hashlib.sha256((LIB/path).read_bytes()).hexdigest(),
                           historical_accuracy_certified=False))
        image.thumbnail((350, 212))
        col, row = index % 3, index // 3
        preview.paste(image, (col*400+(400-image.width)//2, row*260+29), image)
        draw.text((col*400+16, row*260+8), name, fill='#202d32')
    manifest = dict(schema_version=1, coastline_source=LAND,
                    coastline_reference='https://www.naturalearthdata.com/downloads/10m-physical-vectors/10m-land/',
                    projection=INSETS['aegean']['proj'], texture=str(source.relative_to(ROOT)),
                    placement='Bounds include transparent padding in reference sheet pixels. Layer below labels.',
                    review='Modern map polygons and illustrative interior texture; medieval shoreline and land use unverified.',
                    islands=assets)
    (LIB/'island-placements.json').write_text(json.dumps(manifest, indent=2)+'\n')
    preview.save(ROOT/'previews/aegean-island-assets.jpg', quality=94)
    print(f'Built {len(assets)} geographically fitted island sprites')


if __name__ == '__main__':
    build()
