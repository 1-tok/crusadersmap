# Approved Nile vertical bank sprites — Claude placement handoff

**Owner status:** all 14 paintings approved as artwork for geographic integration. **Map placement is not approved until visual proof.** Keep existing print master unchanged.

## Inputs

- Manifest: `data/sprites/nile-vertical-banks-2026-11-21/manifest.json`
- Source ZIP filename: `nile_vertical_banks_2026_11_21.zip`
- Required inbound repository path: `assets/sprites/incoming/nile_vertical_banks_2026_11_21.zip`
- Verified intake workflow: `.github/workflows/nile-vertical-bank-intake.yml`
- Expected generated PNG directory: `data/sprites/nile-vertical-banks-2026-11-21/`
- Existing original bank reference: `data/sprites/nile-painted-upright-2026-11-17/`
- Geospatial river: original Natural Earth/OSM lines already used by the atlas.
- Existing print master: `reports/rebuild-2026-11-12/outremer-current-composite.jpg`

## Important binary ingestion status

The 14 PNG images were generated and checksummed separately from GitHub. Their manifest and the GitHub Actions ingestion workflow are committed, but **do not assume the PNG binaries have been committed**. First verify all 14 files actually exist on the target branch and that SHA-256 matches the manifest. If not, upload the ZIP to the exact incoming path above and run the ingestion workflow. Never replace committed assets with tiny procedural fallbacks.

## 14 approved painted sprites

- Five already approved left-bank vertical strips `leftbank_vertical_approved_01.png` ... `05.png`
- Five already approved right-bank vertical strips `rightbank_vertical_approved_01.png` ... `05.png`
- `leftbank_straight_06_village_shaduf.png`
- `rightbank_straight_06_village_feluccas.png`
- `leftbank_meander_01_rocky_farmland.png`
- `rightbank_meander_01_plateau_fields.png`

**Bank naming convention:** The left-bank-named artwork has water along its right edge; right-bank-named artwork has water along its left edge. This describes the artwork orientation only; do not infer Nile hydrological left/right without verifying flow direction and map perspective.

## Integration instructions

1. Verify the PNG files have alpha transparency and none has a baked checkerboard or opaque white background. If alpha isn't clean, mark for cutout correction, do not hard-clip most artwork away.
2. Inspect all 14 at consistent map production scale, preserve elevated oblique south-looking-north painting style. No arbitrary 29-pixel reductions, mirroring, 90-degree rotation, or nonuniform warping.
3. Match the appropriate water-side facing artwork to mapped Nile segments: straight variants on genuinely straight sections, gentle meander variants on matching bends; prevent reversed bank orientation.
4. Decide source geo-footprints and meaningful print-pixel dimensions before placement. Compare with Cairo buildings, agricultural plots, and monument scale.
5. Treat source water edges as potential shoreline masks; do not duplicate an incorrectly shaped water corridor over mapped geography. Reject candidate if shoreline doesn't fit the bend; do not force it with extreme clipping.
6. Keep green fields inside a defensible Nile alluvial mask. Respect west/east desert zone and the Giza/Saqqara monuments. Desert tiles remain a separate subsequent workstream.
7. Preserve city, fortress, monument, industry, and label layer priority above underlay landscape sprites. Prevent collisions.
8. Render actual full print canvas and enlarged regional before/after, each with readable scale annotations; include a placement audit containing asset filename, bank, geolocation, pixel bounds, retained source alpha ratio, river overlap, field-outside-floodplain, desert and monument overlaps, and seam QA.
9. Publish results to a review branch/PR against `main`; **do not auto-merge or activate the production placement** until the owner approves the rendered appearance.

## Acceptance criteria

All 14 artworks are available as separate real PNGs in the repository; no derived dummy replacements. The printed Nile visibly contains long vertical bank paintings that transition cleanly into neighboring panels. Each chosen strip has correct water-side orientation; agricultural land does not cover desert; water continuity matches mapped geography; no microscopic or mostly-clipped sprites. The owner reviews a genuine map-scale composite before production merge.
