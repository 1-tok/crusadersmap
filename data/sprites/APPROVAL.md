# Recovered sprite approval — 2026-11-08

The user-supplied ZIP has been recovered completely and verified byte-for-byte. All **16 primary sprites and 24 alternates** are provisionally approved as map artwork, with historical review and repaint flags. The original manifest, README, reference sheets and PNGs are preserved unchanged under `archive-1180/`.

Together with the existing library there are 56 catalog records representing 40 distinct normalized RGBA artworks. `catalog.json` is authoritative. `placements.geojson` lists all variants and geographic/projected anchors; `placements-1180.geojson` selects fifteen preferred sites without duplicate paintings at a site. `previews/sprite-placement-markup.jpg` marks those fifteen sites on the existing multi-period atlas. It is location markup, not a finished 1180 print composition.

**Montfort and Château Pèlerin are approved only for later periods and are excluded from 1180.** The 1250 export is an example containing only these two later castles. Approval is provisional, not historical certification. Source clipping, approximate coordinates, heraldry, generic fortress layouts and later architectural phases retain review/repaint flags.

See [provisional usage](PROVISIONAL-USAGE.md), [recovery record](recovery.json), and the unchanged [archive manifest](archive-1180/manifest.json). Rebuild with `import_archive_sprites.py`, `sprite_catalog.py`, `build_sprite_placements.py` and `render_sprite_layer.py`.

## Dated later sites in the atlas

The multi-period placement view now includes **Montfort (begun 1226)** and **Château Pèlerin (begun 1218)**, with blue location markers and dated titles. `placements-atlas.geojson` and `previews/sprite-layer-atlas.svg` select seventeen sites: fifteen from the working 1180 set plus the two later castles. `preferred` in the all-variant inventory refers to this combined atlas view; `preferred_1180` and `placements-1180.geojson` retain the strict 1180 selection. The dates identify construction commencement, not completion of every painted building. Original archive metadata remains unchanged.

Rebuild the combined layer with `python3 build_sprite_placements.py` and `python3 render_sprite_layer.py --atlas`.
