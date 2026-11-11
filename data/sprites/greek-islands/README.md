# Greek Island overlays — Crusader Map

**Status:** APPROVED_FOR_PROVISIONAL_PLACEMENT (user approval, 2026-11-10). **Not yet composited into the final map.**

Contains 12 separate RGBA PNG island overlays, placement_manifest.json, placement_index.csv, source manifest, and checksums. The geographic render bounding box of each image is `[west, south, east, north]` in WGS84. Georeference the full image rectangle (including transparent margins) to that bounding box. The source is GSHHS intermediate via Basemap. The island outline is north-up; buildings are obliquely viewed from the south, and settlements are deliberately enlarged.

**Placing into the map:** If the target map is not an equirectangular longitude/latitude view, reproject the sprite footprint rather than setting a naive fixed pixel width/height. Clip/use existing ocean and coastline layers as required; do not cover map labels. Keep an island out of the composition if its geographic bbox lies beyond the map's actual extent. Islands are compositional overlays, not settlement markers; villages/towns remain painted into their own island sprites.

**QA still open:** Verify shoreline registration against the final map coastline (and medieval shoreline where relevant), enlarged landmark overlap, provenance of buildings, and suitability for the 1097–1291 diachronic phases. A composite-ready status does not imply authentic reconstruction or final print placement. Do not label the PNGs individually inside the artwork.

Raw source geometry/town coordinates are preserved in `source_manifest.json`; per-file hashes in `SHA256SUMS.txt`.

## Placement in this repository

All PNGs and metadata live under `data/sprites/greek-islands/`. Each placement record points to this path and assigns `region: aegean` using the Aegean inset defined by `frame.INSETS['aegean']` in `frame.py` (lon/lat extent 19.6,34.7,30.4,41.75). All 12 geographic bounds intersect the inset. Do not place the images in the principal Levantine map area. The actual compositor currently does not ingest this JSON automatically; map overlay insertion, map-projection warping and a printed preview remain separate tasks.
