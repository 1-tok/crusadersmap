# Crusader sprite intake — 10 November 2026

**Committed to main:** 30 rural composite PNGs (CSV-089–118) and the original sheet `fortified_town_variants_01.png`.

**Outstanding:** 13 of the 14 source sheets from this intake were provided in ChatGPT but have *not* been committed to GitHub. These are tracked as `pending_binary_upload` in `pending_upload_manifest.json`.

## Placement and QA

The 30 rural sprites are registered in `data/sprites/rural-landscapes/rural_landscape_placement_manifest.json`. Their existing study coordinates and review gates are preserved. All are `ready_for_renderer: false` until alpha, source quality, terrain match, and map-geometry review.

Source-sheet paintings must be extracted into independent RGBA cutouts, checked for colored edge halos/opaque backgrounds, and attributed to historically documented subjects before using them as named settlements, fortresses or churches. Coastal paintings require coastline/sea-side alignment; river paintings require matching river courses. Generic hamlets and scenery should not overlap named landmarks or their labels.

## Source provenance and remaining upload

The user's two uploaded `crusader_terrain_sprites_batches_04_06` archives were duplicates. The local verified package held 30 terrain sprites and 14 distinct sheets (44 PNG files), but this repository intake merges only the 31 available binaries. Remaining originals must be uploaded before claiming completion.

The `tools/register_crusader_drop_2026_11_10.py` script verifies the rural PNG paths and updates their QA fields without enabling production rendering. It should not be run automatically as a production approval.
