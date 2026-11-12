# Terrain coverage execution queue — farming and lowlands
_Date: 2026-11-12. Scope: Crusader Map 1180 geographic review edition. Status: prioritized work plan, not evidence of coverage or production approval._

## Objective
Cover previously flat agricultural and lowland regions using existing geographically appropriate painted sprites, retaining all provisional and unapproved artwork in the review library. Do not confuse asset intake with actual map placement.

## Placement queue (today)
| Rank | Region | Existing candidate assets | Placement / QA |
|---|---|---|---|
| P0 | Broad green lowlands across appropriate land regions | `assets/terrain/large_area/rect_underlays_04/green_plain_edge_matched.png`; corresponding opaque source; agricultural assets from the 22-item intake pool | Clip underlay to suitable cultivated land; do not cover water, mountains, urban areas; add irregular transparent field cutouts on top; check repetition and print quality |
| P1 | Cilician plain and Amuq basin | `data/sprites/terrain-batch06/t06_a09_cilician_golden_wheat.png`; rural `CSV-093` | Resolve existing CSV-093 overlap with CP-065; inspect actual map before moving it; add orchard/grain variations |
| P1 | Nile Delta agricultural zones | rural `CSV-096`; intake agricultural/reed sets | Water artwork must match Rosetta/Damietta waterways; CSV-096 currently on hydrology hold; avoid arbitrary irrigation channels |
| P1 | Sharon/Acre coastal plain and Galilee/Samaria farm belt | `data/sprites/terrain-batch06/t06_a06_leventine_dry_grain_terraces.png`; `t06_a08_aegean_old_olive_grove.png` only if ecology/context appropriate; `data/landscape-assets/png/levant-farmland.png` if file available | Keep field pattern medieval and irregular, avoid ornamental regular-grid agriculture |
| P2 | Orontes and western Hauran lowlands | `data/sprites/terrain-batch06/t06_a14_orontes_lowland_stream.png`; `CSV-090`; `CSV-098` | CSV-090 overlaps CP-047/road and its watercourse is not mapped at trial position; mask river imagery, preserve anchor clearance |
| P2 | Aegean mainland agricultural plains and terraces | `data/landscape-assets/png/aegean-terraced-farmland.png`; `data/sprites/terrain-batch06/t06_a07_cilician_vineyard_terraces.png`, `t06_a08_aegean_old_olive_grove.png` | Use Aegean inset transform; distinguish flat grain plains from hillside terraces |
| P3 | Cyprus Mesaoria and other dry cultivated plains | crop/fallow/olive generic pool subject to ecosystem fit | Do not stamp river, island or village composites at fabricated points |
| P3 | Field-to-scrub, farmland-to-wetland and lowland-to-foothill seams | automated-intake terrain transitions Batch 20 and connectors Batch 21 | Verify individual sprite files, not source sheets, before map render; feather and clip to actual landcover |

## Work order
1. Render the **actual composited geographic map** with both insets; do not use sprite-grid diagnostics as the map.
2. Produce a region-by-region terrain gap register from that render; distinguish flat raster artwork from genuinely empty land. Record location/window, estimated uncovered map area, and ecological class.
3. Search the full review ledger, automated intake, terrain Batch 06, rural landscape catalog, and 4 rectangular gap underlays. Reuse compatible sprites (including provisional artwork) for review only; mark per-image QA.
4. Fill broad flat cultivated areas with the existing `green_plain` underlay, clip to landcover and preserve roads, rivers, cities and labels. Overlay organic transparent field/hedgerow/olive/orchard pieces with randomized non-repetitive motifs.
5. Use agricultural cutouts in Cilician/Amuq, Nile, Sharon/Acre, Orontes/Hauran, Aegean and Cyprus priority sequence. Avoid duplicate placement of same named sites, invented geographic locations and unsupported water.
6. Save before/after review crops, render visible asset counts, and list remaining gap polygons and all collisions; **only then** paint new high-native-resolution agricultural patches targeted to measured deficits.
7. Retain provisional, repaint-needed, date-restricted and unapproved items in the all-images gallery; do not mark them print-ready.

## Specific known blockers
- Automated intake review GeoJSON: all 226 geometries null; review eligibility does not imply geographic positioning.
- Rural CSV-093 Northern Amuq: proposed footprint collides with CP-065.
- Rural CSV-096 Rosetta floodplain: crosses the mapped Rosetta distributary.
- Rural CSV-090 Lower Orontes: overlaps CP-047 and a schematic road; river absent at proposed position.
- `green_plain`: existing edge-matched PNG verified on main, but derived from enlarged source; native-resolution print repaint needed if used prominently.
- Terrain-batch06: cutouts are provisional and require placement / native-resolution print QA.

## Acceptance
For each prioritized region, provide full-map crop before/after, actual visible field-sprite IDs and file paths, no invented water/coastline, site/label collision count, residual flat percentage (measured from render), and explicit review-versus-print QA status. Do **not** claim region covered merely because a sprite exists in GitHub.

References: `docs/FINAL-MAP-BUILD-READINESS.md`; `data/manifests/SPRITE-INTAKE-COVERAGE-AUDIT-2026-11-12.md`; `data/manifests/SPRITE-UNPLACED-PLACEMENT-RECOMMENDATIONS-2026-11-12.md`; `data/sprites/terrain-batch06/manifest.json`; `data/sprites/rural-landscapes/rural_landscape_placement_manifest.json`.
