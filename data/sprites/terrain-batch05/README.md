# Terrain Batch 05 — transparent wetland, field and woodland connectors

This batch provides 15 individual and 3 wider composite irregular RGBA cutout sprites, prepared to supplement the 32 existing terrain stamps and 4 retained rectangular underlays.

**Current GitHub branch status:** manifest and import instructions committed. **Actual binary PNGs must be imported from** `crusadersmap_terrain_batch05_20261111.zip` before use. Do not render or claim placement for missing images.

## Source and placement
- Original artwork is extracted from a newly generated painted regional atlas; the labeled source sheet is **reference only** and must never be placed on the map.
- Every delivered PNG has true zero-alpha exterior pixels and an irregular transparent painted footprint, permitting layering over the four existing opaque rectangular gap-fill bases.
- Draw order: geographical base → 4 rectangular underlays → terrain RGBA cutouts → mapped water/coastline → roads and settlements → labels.
- Regions and SHA-256 checksums are in `manifest.json`. Locations are suggested usage areas, **not** precise geographic anchors.
- The wetland/riverbank stamps include illustrative streams or pools; mask them or omit them where they do not match actual hydrology.

## Import into a checked-out branch
```shell
git switch assets/terrain-batch05-20261111
python3 tools/import_terrain_batch05.py ~/Downloads/crusadersmap_terrain_batch05_20261111.zip
git add data/sprites/terrain-batch05/
git commit -m "Add 18 transparent terrain cutout PNGs (batch 05)"
git push origin assets/terrain-batch05-20261111
```

## QA policy
All placement and print approvals are **pending**. The individual crop artworks are only several hundred original pixels wide; composite bands retain source pixels but do not invent high-resolution details. Inspect seams, lighting, seasonal vegetation, water alignment, landcover, and final display size before inclusion in a 300 DPI print sheet. Do not place illustrated rivers across correctly georeferenced waterways.

Existing repository terrain stamps and the **four rectangular gap-fill underlays remain unchanged**.
