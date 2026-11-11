# Terrain artwork and placement approval

Approved at the user's request for artwork and regional placement planning. All 32 final PNG assets are retained with original generations, prompts and technical checks. This approval is not historical or geographic certification and does not merge the branch into main.

`placements.geojson` inventories 32 variants plus five schematic family corridors. Point coordinates are shared regional context anchors, not instructions to pile every variant on the same location. Spread matching pieces along the appropriate range, varying scale and overlap while preserving rivers, valley gaps, settlements and labels. The corridor lines are editorial guides rather than surveyed ridge lines. The Lebanon/Hermon guide groups related artistic use cases; it does not define a single continuous mountain ridge.

Main-sheet and Aegean-inset anchors include projected sheet coordinates, image anchors, proposed display sizes and top-left positions. The inset calculation follows `rough.Region.from_lonlat` and the stage-1 layout without executing the rendering pipeline. Central Anatolian assets remain outside the current frame and have null sheet positions. Do not move those named examples into an incorrect location to fit the map.

`previews/terrain-placement-markup.jpg` marks four current-frame corridors and lists the fifth as future-extension context. It is a placement markup, not a completed terrain composite. Final collision-aware arrangement and accurate landform alignment remain to be done.

Rebuild with `python3 build_terrain_placements.py` (Pillow and pyproj). Build the assets first with `build_terrain.py`; regenerate the catalog with `preview_terrain_interlay.py`. Approval preserves the manifests' unverified medieval vegetation, snow and geographic-shape flags.

The next batch adds `dry-limestone-pass`, `forested-pass`, and `rocky-foothill-fan`. They were generated with built-in image_gen; complete briefs are in `pass-prompts.json`, and original images are in `sources/`.

## Low-relief continuation

The library now contains 29 pieces. New `coastal-foothill-transition`, `dry-wadi-connector`, and `open-plateau-escarpment` assets use regional family anchors as context only. Their low-relief shapes should be placed on reviewed foothill/valley/plateau terrain rather than literally on the inherited mountain label anchor. Full built-in image_gen briefs are in `low-relief-prompts.json`; source images are retained. Artwork/placement-planning approval is recorded, while geographic and historical verification remain pending.

## Vegetation continuation

The kit now has 32 pieces, adding sparse cedar-like woodland, pine-covered slope and Mediterranean scrub fillers. Tree shapes are illustrative, not botanical identifications; medieval forest cover is unverified. Scale vegetation to neighboring sprites, avoid dense stacking, and preserve clear valleys and settlement labels. Full built-in image_gen prompts are in `vegetation-prompts.json`, with unchanged originals in `sources/`. These assets retain artwork and placement-planning approval only.

## First on-map usage proof

The user's instruction to approve usage authorizes the library for map artwork. `render-plan.json` selects 16 trial instances from the approved 32-piece inventory, with editable geographic anchors, display widths and draw order. `render_terrain_proof.py` creates a map preview, a numbered bounds markup, a linked SVG overlay and a per-instance report. The SVG references repository PNGs; keep its `../data/terrain/` relationship when moving it.

The proof overlays the current raster preview: original procedural mountain marks and labels remain underneath. This is a usage/scale proof, not the final print composition. Approximate source-settlement anchor checks identified two nearby markers; those terrain footprints were reduced and their illustrative anchors adjusted. One still-nearby trial was deferred, leaving 16 proof placements. This check does not certify clearance from text, borders, all symbols or protected layout panels. Full native-layer replacement and label ordering remain future integration work.

All 32 assets are committed and approved for map artwork/placement planning. Geographic shape, precise positioning, vegetation, season and historical accuracy are still unverified. Approval is not a GitHub PR approval or a merge into main.
