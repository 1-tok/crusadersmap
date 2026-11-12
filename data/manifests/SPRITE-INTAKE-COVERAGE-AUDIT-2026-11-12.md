# Crusader Map — sprite intake and geographic coverage checkpoint
_Date: 2026-11-12. Repository main after PR #27 merge `5c1a20bc5c664561ee77644d17c15a58dfc04b1e`._

## Confirmed intake

Batch 15–21 source ZIPs are **all on main** (commits `14419de6`, `ad57e58f`, `f23cc98c`, `18180296`). PR #27 merged the automated review branch into main, preserving provisional states and duplicates tracking. The merged `data/sprites/automated-intake/manifest.json` registers **226 unique asset records**, all with corresponding file paths, across the broader Crusader sprite intake (not merely seven batches). `processing-report.json` has 238 input source records. These are **not** 226 approved placed map sites.

### Batch 15–21 source processing (from merged report)
| Batch | Source-image records | Newly imported during latest intake | Duplicated by pixel digest |
|---|---:|---:|---:|
| 15 — six landmark paintings | 7 | 0 | 7 |
| 16 — generic architectural sprites | 7 | 0 | 7 |
| 17 — mixed atlas | **No matching general B17 ZIP in report** | — | — |
| 18 — coast/rural atlas | 29 | 29 | 0 |
| 19 — mixed atlas | 32 | 32 | 0 |
| 20 — terrain transitions | 10 | 10 | 0 |
| 21 — terrain connectors | 22 | 22 | 0 |

Counts include uploaded source sheets as well as sprite cutouts, not just the advertised 6, 28, 31, 9 and 21 individual sprites. Duplicate means the exact pixel image already existed in a prior intake or merged record, **not** that the entire proposed site was satisfactorily represented on the map. The earlier Batch 17 mixed ZIP was not observed in the GitHub commit file lists checked; there is a *different* `crusader_map_batch17_trade_intake.zip` with five newly imported records. Verify Batch 17 generic archive separately before treating it as recovered.

### Other latest batches
- Greek island batches 08, 09 and 10: seven new image records each, plus flags for identity and coastline verification.
- Fortress batches 18 and 19: four newly imported image records each.
- Rural batches 18 and 19: six and eleven newly imported image records.
- Earlier Batch 14 and Batch 15 religious source inputs and some older fortresses/islands were detected as duplicates by hash.

## Geographic placement blocker

**All 226 features** in `data/sprites/automated-intake/placements-review.geojson` have `geometry: null`. All 226 are allowed *within the review asset library* but **zero** are geographically ready in this automated-intake file. This does not negate separately approved, located entries in `data/sprites/placements-review.geojson` and `data/sprites/placements-review-1180.geojson`: those need their own active-render verification.

The actual map `frame.py` insets include Aegean `(19.6,34.7,30.4,41.75)` and Egypt Delta `(29.5,27.7,35.2,31.8)` in WGS84 longitude/latitude. Do not assign Greek island imagery to the Levant main frame. Do not stretch illustrative coasts, rivers or reedbeds across mapped hydrology.

## Correct next tasks (no new commission until verified)
1. Check and recover the exact earlier `crusadersmap_batch17_mixed_atlas_upload_2026-11-12.zip` if still absent. Its generic paintings are not the same as `crusader_map_batch17_trade_intake.zip`.
2. Match original Batch 15–21 source ZIP inventory to *actual* PNG image paths in the consolidated manifest, using exact SHA-256/pixel hashes, and exclude original sheets as placeable sprites.
3. Merge known site anchors only into the appropriate *date-gated* review overlays, retaining alternate variant toggling and no automatic placement for anonymous art.
4. Render a diagnostic preview against the real map frame/insets, count actually visible sprites, collisions, overlaps with labels and shoreline/rivers, and keep transparency/print QA flags.
5. Build an outstanding-gap register from the actual composited map and named-site manifest before painting more sprites.

**Do not report the atlas as fully composited or production ready.** Technical PNG acceptance and user approval for review usage do not confer date/identity accuracy or 300-dpi suitability.
