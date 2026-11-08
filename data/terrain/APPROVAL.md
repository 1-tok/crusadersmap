# Terrain artwork and placement approval

Approved at the user's request for artwork and regional placement planning. All 26 final PNG assets are retained with original generations, prompts and technical checks. This approval is not historical or geographic certification and does not merge the branch into main.

`placements.geojson` inventories 26 variants plus five schematic family corridors. Point coordinates are shared regional context anchors, not instructions to pile every variant on the same location. Spread matching pieces along the appropriate range, varying scale and overlap while preserving rivers, valley gaps, settlements and labels. The corridor lines are editorial guides rather than surveyed ridge lines. The Lebanon/Hermon guide groups related artistic use cases; it does not define a single continuous mountain ridge.

Main-sheet and Aegean-inset anchors include projected sheet coordinates, image anchors, proposed display sizes and top-left positions. The inset calculation follows `rough.Region.from_lonlat` and the stage-1 layout without executing the rendering pipeline. Central Anatolian assets remain outside the current frame and have null sheet positions. Do not move those named examples into an incorrect location to fit the map.

`previews/terrain-placement-markup.jpg` marks four current-frame corridors and lists the fifth as future-extension context. It is a placement markup, not a completed terrain composite. Final collision-aware arrangement and accurate landform alignment remain to be done.

Rebuild with `python3 build_terrain_placements.py` (Pillow and pyproj). Build the assets first with `build_terrain.py`; regenerate the catalog with `preview_terrain_interlay.py`. Approval preserves the manifests' unverified medieval vegetation, snow and geographic-shape flags.

The next batch adds `dry-limestone-pass`, `forested-pass`, and `rocky-foothill-fan`. They were generated with built-in image_gen; complete briefs are in `pass-prompts.json`, and original images are in `sources/`.
