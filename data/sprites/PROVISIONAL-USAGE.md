# Provisional map usage

The user authorized “place now, flag repaint later” on 2026-11-07. `catalog.json` is the unified operational catalog. Each recovered PNG is approved for provisional map use after technical QA; that approval is **not historical certification**. Architecture, heraldry, terrain, orientation and reconstructed heights remain subject to review and repaint.

The default brief is **circa 1180**. The existing atlas is a multi-period work covering 1095–1571. This addition does not turn its print editions into an 1180 snapshot.

## Placement

`placements-1180.geojson` selects one approved image per site, preferring the newer period-informed versions, and standalone Krak over its sheet crop. All alternatives remain individually approved and available in the catalog, but consumers should not place duplicates. Coordinates are WGS84 longitude/latitude, inherited from `places.py`, and approximate. A renderer mark such as `M:castle_frankish` is not a unique site identifier; use `site_id` (Byblos also records the place name Gibelet).

`previews/sprite-layer-1180.svg` is a self-contained transparent layer positioned with the atlas's `frame.py` projection and full 10800 × 14400 viewBox. It places sprites at the recorded bottom-ground anchors without inland nudging. `previews/sprite-placement-1180.jpg` is the labeled grid diagnostic; it is not a coastline map or a new print edition. Labels, collisions, precise footprints and final print composition still need review. Display widths inherit the batch convention: Jerusalem 1024 atlas pixels; others 512. These illustrative footprints are exaggerated, not geographic scale.

Only the explicitly reviewed 1180 brief is enabled for recovered images. Other years require additional phase review rather than automatically reusing an 1180 painting across the whole atlas timeline.

## Montfort

**Do not place the main Teutonic castle in 1180.** Creighton University's archaeological overview dates construction start to 1226, records work still seeking support in 1230, and describes multiple later building phases. The missing Montfort image has `later_period_only: true`, `exclude_from_1180: true` and a 1226–1271 historical review window. The start year does not imply completion, that all depicted buildings existed then, or that a missing image is approved. On recovery it needs technical QA and phase-specific review before later-period placement.

Reference: https://moses.creighton.edu/vr/Montfort/txt/intro.html

## Source recovery

Recovered and retained: original eight-up sheet, its eight transparent crops, standalone Krak, and the separately committed Jerusalem, Acre and Belvoir v2 sources/PNGs. New Byblos and Tyre generations, exact prompts and source files are in `expansion/`.

The referenced ChatGPT chat returned **no attachments**. Additional older standalone Belvoir, Kerak, Montréal/Shobak and Montfort images named in the request could not be recovered from that chat, the workspace, or the inspected repository branches. Catalog placeholders record the gap with `asset: null` and no usage approval. Belvoir v2 is preserved, but has not been identified as the older requested standalone. Sheet crops are not falsely counted as those separate originals. Attach those four original images to complete recovery.

## Rebuild and check

Use Python 3.10+ with Pillow, NumPy, SciPy and pyproj:

```sh
python3 build_sprites.py
python3 build_historical_sprites.py
python3 -c "from pathlib import Path; from build_historical_sprites import build, ROOT; build(ROOT/'data/sprites/expansion', ROOT/'previews/sprite-expansion.jpg')"
python3 sprite_catalog.py
python3 -m unittest test_sprite_catalog
python3 render_sprite_layer.py
```

The inherited packaging trims low-alpha export noise and tiny detached components, resizes non-destructively from preserved sources, clears zero-alpha RGB before resampling and adds transparent padding. QA checks RGBA, nonempty alpha, transparent edges, dimensions and SHA-256 hashes. Compare light/dark contact sheets for halos and clipping. Source crop clipping flags remain visible in the unified catalog. Tests specifically enforce Montfort's year gate, missing/failed/unapproved exclusion, and variant deduplication. These checks do not establish historical accuracy.
