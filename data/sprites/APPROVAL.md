# Sprite artwork and placement approval

All **16 available sprite PNGs** are approved for provisional map use at the user's request: place now, flag repaint later. The catalog preserves historical uncertainties and technical QA. Approval does not certify historical accuracy or merge this branch into main.

`catalog.json` is authoritative for every available variant and missing-source record. `placements.geojson` lists all available variants with geographic anchors, projected sheet anchors, display dimensions and top-left sheet positions. Draw only `preferred: true`: ten sites, one image per site. `placements-1180.geojson` contains only those ten selected images. Coordinates are approximate, with Tripoli using the historical batch's proposed coastal al-Mina anchor; its inherited coordinate is retained separately in the catalog.

`previews/sprite-placement-markup.jpg` marks these ten sites on the existing **multi-period** atlas. That background is not an 1180 map. `previews/sprite-layer-1180.svg` is the independent, positioned, transparent sprite layer. Final label collisions and print composition remain subject to review. Jerusalem is 1024 sheet pixels wide; other sprites are 512.

Montfort's main Teutonic castle is **excluded from 1180**. Its missing-source entry permits only later-period review, beginning with construction in the 1220s; it is not approved or placed. The other missing older standalone images are also not approved until recovered and checked.

Rebuild with `python3 sprite_catalog.py`, `python3 build_sprite_placements.py`, and `python3 render_sprite_layer.py`. See [provisional usage](PROVISIONAL-USAGE.md) for source recovery, QA, period rules and dependencies.
