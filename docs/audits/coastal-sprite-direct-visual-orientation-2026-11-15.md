# Coastal city sprites — direct visual orientation audit (15 November 2026)

**Status:** direct source-PNG review, not a final composite coastline registration. The master atlas covers **1096–1600 CE**; legacy selected assets here are mostly marked as 1180 variants. Do not equate a visually plausible sprite with verified shoreline registration, and do not overwrite the original artwork.

## Method and evidence limits
- Opened the **actual GitHub PNG contents**, compared painted water position, terrain/land access, harbor and walls against the prescribed elevated oblique south-to-north viewpoint.
- Cross-checked each site's current selected asset and representative point against `assets/sprites.json`, `data/sprites/placements-atlas.geojson`, and the older `reports/rebuild-2026-11-12/coastal-city-orientation-audit.csv`.
- The older CSV's `visual_water_side_verified=false` for every entry was **not** a completed visual audit. Its `expected_water_side=left / west` is an oversimplification for peninsulas, harbors and promontories.
- Actual shoreline **pixel-to-coast mask intersection**, 300-dpi composite alignment, local coordinate transforms, and north-angle registration were not measured. Findings below do not certify print readiness.
- Acre's selected source PNG could not be visually fetched through the available GitHub file response (empty content); leave it **not inspected**, never classify it as passing or failing visual QA.

## Individually inspected selected artwork

| Place | Selected asset | Observed visual evidence | QA judgment / action |
|---|---|---|---|
| Tyre | `data/sprites/expansion/tyre-1180-v1.png` | Water along left/west and foreground; protected enclosed basin sits upper-left; town attaches to land to right/east | **CONDITIONAL**: broadly plausible western water and peninsula but verify northern harbor, connection/causeway and coast mask. Do not flip blindly |
| Jaffa | `data/sprites/greece-egypt-1180-batch02/jaffa-1180-v1.png` | Steep urban promontory with sea front-left/west-southwest, land access right/east | **RETAIN PROVISIONALLY**: broad water orientation plausible; check northwest harbor location, actual headland and coastal edge |
| Caesarea | `data/sprites/archive-1180/clean/archive-crs-023-caesarea.png` | Front/right enclosed harbor and seaward antiquities/walls; water principally at front and lower sides | **REWORK CANDIDATE**: no verified correspondence to historical harbor layout and west-facing coast; review era of walls before replacing. Existing sprite remains a provisional historical variant |
| Sidon | `data/sprites/archive-1180/clean/archive-crs-022-sidon.png` | Generic town with broad foreground enclosed harbor; no independently depicted offshore northern castle islet | **REWORK CANDIDATE**: match northern harbor and eastern shore; offshore Sea Castle is valid only for a post-1227/28 phase, not mandatory in an 1180 variant |
| Tripoli | `data/sprites/historical-1180/tripoli-1180-v2.png` | Sea left and foreground/right around a peninsular town with land connection to back/right | **RETAIN PROVISIONALLY**: plausible for coastal al-Mina, not the later inland Mamluk city; check exact shore/mole footprint and do not reuse anchor for inland Tripoli |
| Beirut | `data/sprites/greece-egypt-1180-batch04/beirut-1180-v1.png` | Harbor basin prominently foreground/right, with land mass left/back | **LIKELY ORIENTATION MISMATCH**: port is expected on northern side of historic promontory; verify water-side/camera relation and seek a geography-correct variant, rather than horizontal-flipping this city |
| Tortosa / Tartus | `data/sprites/archive-1180/clean/archive-crs-009-tortosa.png` | A narrow river crossed by a multi-arch bridge fronts an inland-looking castle; no credible Mediterranean shoreline or Templar waterfront | **REPAINT REQUIRED**: fails subject-specific coastal geography. Preserve as archival asset; do not certify for production use |

## Selected source not visually inspected
- **Acre:** `data/sprites/historical-1180/acre-1180-v2.png`; geographic anchor `[35.084, 32.928]`. The connector returned no image content for this file. **HOLD VISUAL QA**. The historic peninsula and east/southeastern harbor must be checked in the real image before approval.

## Placement-anchor observations
- Tyre `[35.1958333,33.2691667]`: documented archaeological peninsula representative point.
- Jaffa `[34.7552,32.0549]`: Old Jaffa representative point, not surveyed shoreline.
- Caesarea `[34.89,32.5]`, Sidon `[35.37,33.56]`, Tartus `[35.89,34.89]`: inherited approximate catalog points; need independent shoreline/city-footprint registration.
- Tripoli `[35.81783,34.447]`: coastal al-Mina point, explicitly not later inland urban center.
- Beirut `[35.505141,33.896339]`: old-core location, not the harbor centroid.
- The existing `anchor_normalized` and 512-pixel display widths are visually illustrative. They do **not** prove coast masks or perspective are accurate.

## Additional cities still pending direct PNG inspection
Acre, Alexandria, Ascalon, Batroun, Byblos, Famagusta, Kyrenia, Limassol, Larnaca, Paphos, Latakia, Baniyas, and associated island and Bosphorus waterfronts from the old audit report. Do not imply the entire registry has been visually inspected.

## Production gate
1. Prioritize Tartus repaint and Beirut geographically corrected variant; retain originals and provenance.
2. Coastline-mask/register Tyre, Sidon, Caesarea, Jaffa and al-Mina Tripoli against historical harbor geometry; perform phase review across 1096–1600 rather than imposing a blanket 1180 cutoff.
3. Inspect Acre's actual image and the other pending assets; capture explicit per-image visual verdicts.
4. Produce a geographically composed review image and check overlaps and alpha margins at final atlas scale before promoting any candidate to production approval.

**No production placement approval or manifest coordinates were changed by this audit.**
