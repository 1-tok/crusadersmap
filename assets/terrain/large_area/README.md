# Large-area terrain sprite staging

This directory is reserved for painted large-area terrain underlays generated for the Crusader Map. Original and feathered PNG assets are **not included in this branch yet**. Keep source paintings and feathered overlays separate and treat all region placements as provisional until geographic masks, scale, color, and edge blending are checked.

Intended classes: Egyptian and Transjordan desert; Canaan scrub; dry steppe; Greek limestone uplands; Anatolian plateau; Levant mountains; Mediterranean coastal transitions.

Use terrain underlays beneath rivers, roads, cities, symbols, and labels. Preserve project-specific projection/geographic land masks. Do not overwrite elevation tiles under `data/tiles/`.

## Regional Terrain Expansion 02 (16 assets)

See `manifest_regional_expansion_02.json`. The full generated art and the 16 painted atlas-panel extractions are supplied separately as `crusadersmap_terrain_expansion_02_20261110.zip` in the ChatGPT conversation. **The manifest is committed, but binary PNGs have NOT been pushed to the repository.** Each entry has `binary_status: not_yet_uploaded`.

To install from a local checkout once the ZIP has been downloaded:

```sh
unzip crusadersmap_terrain_expansion_02_20261110.zip -d .
git add assets/terrain/large_area/
git commit -m 'Add provisional terrain expansion 02 PNGs'
git push origin HEAD
```

For large canvas composition, prefer feathered RGBA overlays and geographically masked placements over edge-joining opaque images. Enlarged 1536×1024 paintings are interpolated from smaller panel crops, **not** true native-resolution art; paint QA is required before print.

## Transparent Terrain Redo 03 — review queue

The **16 original expansion-02 regions** have replacement hand-painted **irregular RGBA cutout sprites** and **19 supplemental variants** in the separately downloadable archive `crusadersmap_terrain_transparent_redo_03_20261110.zip`.

See `manifest_transparent_redo_03.json` for paths, expected dimensions, placement review and print QA. **Old 02 images are superseded** for map use. **No PNG binaries from redo 03 have been uploaded to GitHub yet**; the manifest is not evidence of an image commit. Unzip the conversation archive into a checkout and commit its `assets/terrain/large_area/transparent_redo_03/*.png` files before enabling the placements.

Alpha corners and cutout edges have been checked; overlap previews exist in the conversation. Seamless tiling, geographic placement and 300-DPI print quality are **not approved**. Source crops average only several hundred pixels wide, so large print placements need new high-native-resolution repaints; preserve the original extract as a reference, not a falsely sharp enlargement.

## Exactly four retained rectangular gap-fill underlays

**Exception to transparent-only art:** keep four full-size opaque RGB rectangles strictly **below** the irregular RGBA cutouts: `desert_sand`, `dry_steppe`, `canaan_scrub`, `green_plain`. See `manifest_rectangular_underlays_04.json`.

Each has an untouched rectangular source and a second, edge-matched version (exact opposing-edge pixel matches). These provide desert, dry steppe, limestone scrub and green lowland fill where standalone transparent pieces leave patches uncovered. Clip the rectangles to real geography and landcover, then layer transparent cutouts above them; keep roads, hydrology, cities and labels on their usual upper layers. Match palette, motif scale and overlaps on the final map.

**QA:** Repeat-pattern and print-scale inspection remains pending. The `green_plain` was derived from an enlarged reference-atlas crop and requires native-resolution repaint if used prominently at 300 DPI. Underlay PNG binaries are available in the separately downloadable `crusadersmap_rect_underlays_04_20261110.zip`, **not on GitHub until explicitly uploaded**. Do not confuse manifest commits with binary image commits.
