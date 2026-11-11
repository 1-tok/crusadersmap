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
