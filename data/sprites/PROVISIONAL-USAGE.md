# Provisional map usage

The user authorized “place now, flag repaint later” on 2026-11-07. `catalog.json` is the unified operational catalog. Each available, 1180-eligible PNG has `approval_for_placement: true` for immediate provisional use after technical QA; that approval is **not historical certification**. Architecture, heraldry, terrain, orientation and reconstructed heights remain subject to review and repaint.

The default brief is **circa 1180**. The existing atlas is a multi-period work covering 1095–1571. This addition does not turn its print editions into an 1180 snapshot.

## Placement

`placements-1180.geojson` selects one approved image per site, preferring the newer period-informed versions, and standalone Krak over its sheet crop. All alternatives remain individually approved and available in the catalog, but consumers should not place duplicates. Coordinates are WGS84 longitude/latitude, researched representative site points from `sites.json`. Published values are transcribed with source URLs, anchor meaning and uncertainty notes. They are not surveyed medieval footprints. Historical source manifests retain original approximate coordinates as provenance; use `catalog.json` and `placements-1180.geojson` operationally. A renderer mark such as `M:castle_frankish` is not a unique site identifier; use `site_id` (Byblos also records the place name Gibelet).

`previews/sprite-layer-1180.svg` is a self-contained transparent layer positioned with the atlas's `frame.py` projection and full 10800 × 14400 viewBox. It places sprites at the recorded bottom-ground anchors without inland nudging. `previews/sprite-placement-1180.jpg` is the labeled grid diagnostic; it is not a coastline map or a new print edition. Labels, collisions, precise footprints and final print composition still need review. Display widths inherit the batch convention: Jerusalem 1024 atlas pixels; others 512. These illustrative footprints are exaggerated, not geographic scale.

Only the explicitly reviewed 1180 brief is enabled for recovered images. Other years require additional phase review rather than automatically reusing an 1180 painting across the whole atlas timeline.

## Montfort and Château Pèlerin

Both castles have been recovered and approved as **later-period provisional artwork only**. Neither is eligible for circa 1180. Montfort uses a 1226–1271 review window; Château Pèlerin uses 1218–1291. The initial years represent construction commencement, not completion of every painted structure. Exact depicted phases and castle layouts remain unverified and require repaint review. `approval.provisional_map_use` is library approval, while `approval_for_placement` and `approval.approved_for_default_year` apply specifically to 1180. The selector always checks the year window.

Montfort reference: https://moses.creighton.edu/vr/Montfort/txt/intro.html

## Source recovery — completed 2026-11-08

The user supplied `crusader_sprite_library_1180_batch.zip`. All 46 members are preserved unchanged under `archive-1180/`: 16 primary sprites, 24 alternates, four reference sheets, original README and manifest. Every original was compared byte-for-byte with the supplied ZIP. `archive-1180/member-hashes.json` records original file hashes and the ZIP SHA-256; `recovery.json` closes the former missing-source records.

The standalone Belvoir, Kerak, Montréal/Shobak and Montfort paintings are recovered. The package also supplies Tortosa, Sidon, Caesarea, Jaffa, Arqah and Château Pèlerin. Archived metadata is retained as provenance, not treated as an instruction or historical certification. In particular, the original Montfort `available_after_year: 1220` has been superseded operationally by the sourced 1226 construction commencement. Its original value remains unchanged in the preserved manifest.

`import_archive_sprites.py` creates padded RGBA copies and `archive-1180/imported.json`. Raw images and sheets remain unchanged. Forty recovered sprite records join the existing sixteen: **56 catalog records, 40 distinct normalized RGBA artworks**, with pixel-identical images linked to canonical asset paths. The 1180 placement export selects fifteen sites, preferring the newer researched versions where available and recovered standalone Kerak/Shobak over their old sheet crops. The explicit 1250 example selects only Montfort and Château Pèlerin; it is a later-castle review layer, not a complete 1250 map.

All recovered images are provisionally approved with repaint and historical-review flags. Technical cleanup cannot fix clipped source artwork, invented architecture or neighboring fragments in sheet crops. The archive QA contact sheet shows light/dark comparisons. Tortosa's generic river/bridge composition, Château Pèlerin's invented hilltop layout, flags, and later construction phases remain flagged. Caesarea's 1251 Louis IX wall phase must not be treated as established 1180 fabric (https://hadashot.iaa.org.il/report_detail_eng.aspx?id=13).

## Rebuild and check

Use Python 3.10+ with Pillow, NumPy, SciPy and pyproj:

```sh
python3 build_sprites.py
python3 build_historical_sprites.py
python3 -c "from pathlib import Path; from build_historical_sprites import build, ROOT; build(ROOT/'data/sprites/expansion', ROOT/'previews/sprite-expansion.jpg')"
python3 import_archive_sprites.py
python3 sprite_catalog.py
python3 build_sprite_placements.py
python3 -m unittest test_sprite_catalog
python3 render_sprite_layer.py
```

The inherited packaging trims low-alpha export noise and tiny detached components, resizes non-destructively from preserved sources, clears zero-alpha RGB before resampling and adds transparent padding. QA checks RGBA, nonempty alpha, transparent edges, dimensions and SHA-256 hashes. Compare light/dark contact sheets for halos and clipping. Source crop clipping flags remain visible in the unified catalog. Tests specifically enforce Montfort's year gate, missing/failed/unapproved exclusion, and variant deduplication. These checks do not establish historical accuracy.

## Sourced placement contract

`sites.json` records historical names, site types via catalog entries, first Frankish date ranges, and sourced latitude/longitude. `catalog.json` schema v2 adds explicit placement approval, period eligibility, layer membership, painted pixel bounds, atlas display dimensions and normalized anchors. `date_ranges.site_frankish_phase` describes the historical site; `date_ranges.approved_art` enables the reviewed 1180 brief or the explicitly restricted later-castle window. Date endpoints are coarse year ranges, not daily political-control boundaries. All available variants are provisionally approved, but the placement export selects only one per site. Missing originals receive no approval.

Coordinate conflicts are retained in uncertainty notes: Acre uses the UNESCO periodic-report Old City point, and Krak uses the current UNESCO map point rather than inconsistent older nomination coordinates. Shobak moves east to the published castle location. Tripoli uses coastal El Mina rather than inland later Tripoli. Sources vary in precision and authority; representative city points are not exact medieval centroids.

Catalog generation validates unique IDs, safe lowercase PNG paths, RGBA alpha, transparent padding and hashes. Pixel-and-dimension SHA-256 detects identical PNG artwork independent of encoding; artistic alternatives remain separate. All 56 catalog records pass QA, representing 40 distinct normalized RGBA artworks and fifteen preferred 1180 placements. `recovery.json` documents completed archive recovery. The five newly added city anchors inherit approximate `places.py` coordinates; they are not newly surveyed locations.

## Later sites with construction dates

The multi-period atlas view includes **Montfort (begun 1226)** and **Château Pèlerin (begun 1218)** in their display titles. `sites.json` holds construction-date references and date-type notes; catalog titles, placement exports, SVG titles and later-castle labels inherit those fields. `placements-atlas.geojson` and `sprite-layer-atlas.svg` include seventeen sites. Blue markers distinguish the two later additions in `sprite-placement-markup.jpg`. This combined view is not a single-year reconstruction. The strict 1180 layer remains fifteen sites with both later castles excluded.

Montfort commencement: https://moses.creighton.edu/vr/Montfort/txt/intro.html . Château Pèlerin conventional commencement: https://theses.gla.ac.uk/30916/1/2018haberlinphd.pdf . Archaeological reports also give 1217–1218 for the initial work: https://www.crfj.org/wp-content/uploads/2019/12/Rapport-CRFJ-2018.pdf .
