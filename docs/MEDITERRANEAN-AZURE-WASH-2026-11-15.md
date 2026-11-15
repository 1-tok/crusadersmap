# Mediterranean Azure Wash — review implementation (2026-11-15)

This is a non-destructive **render-time** recolor of existing sea art. It does not replace or modify source PNGs.

## Palette and controls
- Offshore azure: `#166F9F`
- Shore turquoise: `#54C9CB`
- Default wash strength: 78%. Original light and dark brushwork is carried into the new palette.
- `MEDITERRANEAN_AZURE_WASH=0` disables grading of painted sea textures and masked sprite water. The base terrain colour fallback remains azure.

## What is active
- `sea.py`: applies shoreline-weighted grade to the existing v62, oct31 and deep/shallow sea fields in the colour edition.
- `terrain.py`: aligns the geographic sea wash with the same palette.
- `sprites.py`: on the colour edition, optionally applies water-only grading to city/castle sprites **only if** a reviewed PNG mask exists at `assets/sprites/water-masks/<original sprite filename>`. Masks are grayscale, white for water, black for structures/land; same pixel dimensions as the sprite.
- Parchment edition and original RGBA source sprites are unchanged.

## Required QA before merge
1. Run `python build_stage2.py 0.30 colour` in a build environment with dependencies/fonts/data available.
2. Compare the main Levant and Cyprus coastline, Aegean inset and Nile Delta inset against previous composite; look for seams and oversaturation.
3. Check sprite roofs, flags, cliffs and transparent margins at print scale.
4. Create and review individual sprite water masks, particularly around harbors. **No new masks have been approved or supplied with this change**, so those sprites retain their original painted-water colour.
5. After visual approval, merge PR and rebuild the full composite.

Do not equate a proposed palette or successful source commit with a completed print-quality map rebuild.


## Owner visual acceptance and main rebuild integration (2026-11-15)
The owner approved the sea appearance after reviewing GitHub Actions run 43731295324.
The azure grading code was merged with PR #53. Commit `657d2be0349020b7add8533426d899d00397eb34` integrates the same provisional harbor water mask generation into `.github/workflows/rebuild-current-map.yml` **before** the normal composite render. This makes the reviewed visual treatment reproducible in Actions without editing source PNGs.

**Scope of approval:** sea hue/gradient and the displayed review treatment. Automatically generated per-sprite masks have not been individually inspected or print-approved. The build publishes `reports/rebuild-2026-11-12/harbor-water-mask-report.json` and the harbor comparison gallery for further QA. Preserve provisional status until individual masks are reviewed. The normal map rebuild's success and full-scale artifact still require confirmation.
