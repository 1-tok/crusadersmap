# Lowland terrain — map-build readiness (15 November 2026)

## Build decision
The existing **nine explicitly curated dry-land sprites** from the November 13 Part 1 and Batch 10–11 ZIPs are eligible for *provisional review-map rendering* through `tools/import_recent_terrain_zips.py` → `assets/generic2.json` → `terrainsp.py` / `terrain.py`. The existing placer selects fertile, low-elevation cells for `patchg` and excludes random `patchg` stamps from the Nile Delta. This is an ecological preview pool, **not nine confirmed rendered placements**.

The **51 corrected, byte-duplicate cutouts** from sheets 06–09 have been reconciled one-for-one to canonical intake files in `LOWLAND-51-CANONICAL-PLACEMENT-AUDIT-2026-11-15.json`. Their review GeoJSON geometries are all null. They are approved as *review artwork* but **not yet geographically placed or shown in a verified map render**. No default `patchg` classification was assigned to the 51 because filename/group and deduplication alone do not establish absence of water or appropriate viewpoint.

## Required geographic integration
| Region | Immediate build input | Held pending alignment or inspection |
| --- | --- | --- |
| Nile Delta | Existing mapped geographic land/water masks, terrain underlays and already-vetted fields | Group 06 coastal transitions; group 08 mixed Delta tiles; floodplain and reed/water pieces |
| Cyprus | Curated `05_cyprus_mediterranean_orchards` as provisional generic farmland | Group 07 candidates until per-cutout land-only visual QA |
| Cilician plain | Existing terrain-batch06 farmland and curated generic `patchg` | Groups 07/08/09 until land/water and regional QA |
| Greek lowlands | Existing Aegean farms and curated `11_greek_cyprus_anatolia_levant_lowlands_{02,03,07,08,09,12,13,14}` | Group 07/08 pending individually reviewed ecology and inset scale |
| Levant coastal plain | Existing farmland and curated dry `patchg` | Coastal group 09 pending sea-side orientation and coastline clipping |

## Build acceptance checks
1. Run `.github/workflows/rebuild-current-map.yml` on `main` after any renderer/asset-pool change. Workflow's generated `out/usage.json`, terrain utilization report, and full-map composite determine what is actually visible.
2. Inspect full-map crops for all five priorities and compare to terrain-gap cells; do not infer visibility from pool registration.
3. Match any water-bearing cutout to coastline/rivers; north-facing view from the south, sea on the correct side. Do not fabricate a geo-coordinate.
4. Keep masters out of renderer, prohibit duplicate intake, and maintain provisional / historical / print QA flags.
5. Promote a corrected-cutout canonical asset to preview `patchg` only after individual inspection confirms dry land, transparent alpha, ecological fit, correct orientation and nonduplicative appearance; **do not promote a whole sheet based on its filename**.

**Result:** Nine already-curated dry-field candidate inputs remain build-eligible. The 51 corrected pieces are canonical, queued for visual geographic review and blocked from automatic scatter. The map rebuild and actual sprite visibility are not established by this document.
