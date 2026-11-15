# Full-map coverage validation — 2026-11-15

Status: **source-audit reconciliation only; new composite not yet rendered or visually certified**.

## Evidence

- Historical source: `reports/rebuild-2026-11-12/terrain-gap-report.md`, `terrain-gap-cells.csv`.
- 1288 measured land cells; reported 18 flat and 58 thin, 76 flagged (5.90%).
- Metric is raster brightness spread; below 12 = flat, 12–16 = thin. This is **not** direct proof of exposed bottom/base layer.
- Regional flags: Sinai inset 6 flat/23 thin; Egyptian desert inset 6/19; Syrian desert 1/2; Delta 1/3; remaining regions 4/11.
- **CSV data consistency defect:** flat-cell rows in the Markdown include `main` coordinates 35.57,37.72 (9.3), 37.51,35.43 (9.4), 37.47,33.50 (9.3), 36.84,33.50 (10.9), 37.25,32.62 (10.1), but those rows have `flat=False` in the CSV. Other sub-12 cells are also false. Recompute `flat` from measured `detail`, verify all 76 rows and agree Markdown counts before automated decisions.
- `docs/AI-CONTEXT.md` establishes cumulative master scope **1096–1600 CE**, not a strict 1180 map.
- Existing `rebuild-current-map.yml` renders `build_stage2.py 0.30 colour`, calls `make_registers.py`, and publishes `reports/rebuild-2026-11-12/`; this report documents interpretation, **not proof that a new run succeeded**.

## Review decision matrix

| Class | Criteria | Action |
|---|---|---|
| Confirmed base-layer exposure | Compare real composite crop and alpha/composition against map geometry; visible unpainted land without intentional open terrain | Select compatible existing underlay/sprite, preserve coast/rivers/labels, then rebuild |
| Flat but natural | Desert, semi-desert, bare rock, sparse steppe consistent with ecology | Retain intentional openness; no automatic greenery or detail stamping |
| Thin detail needing enhancement | Cultivated land or settlements beside visually abrupt texture gaps | Reuse appropriate registered cutouts for review, only after footprint/collision QA |
| Unresolved | Missing current artifact, conflicting register, uncertain ecology or footprint | Keep review-only and report unresolved |

## Geographic order

1. Nile Delta and Rosetta/Damietta (4 flagged): verify hydrology before placing wetlands/field imagery; avoid CSV-096 on distributary.
2. Cilicia/Amuq, Levantine cultivated shore, Galilee/Samaria, Greece, Cyprus: inspect visually even where old variance metrics show zero; absence of flag does not prove quality.
3. Sinai and Egyptian deserts (54 flagged): inspect for truly missing underlay but **do not automatically fill** low-variance natural deserts.
4. Syrian desert, Lebanon/Damascus, Transjordan: distinguish sparse habitat from unpainted ground.
5. Recheck Greek islands and coastal sprites with correct south-looking-north angle, geography and 1096–1600 historical phase.

## Next rebuild acceptance

- Record HEAD SHA, workflow run ID, timestamp, command, success status and artifact URLs.
- Produce full composite with Aegean and Egypt/Sinai insets; do not substitute a sprite-only grid.
- Fix cell classification and publish both computed integer counts and a per-cell status/decision reason.
- Verify existing PNG file/hash, geographic anchor, actually visible footprint, print QA state, duplicate status and placement log; ZIP extraction alone is not coverage.
- Provide before/after crops for real changes, visible asset identifiers, remaining exposure polygons, and collision counts (roads, labels, towns, coastline).
- Retain provisional/repaint-required states and separate print-approved from review-visible.
- No claim of completion until these post-render records exist.
