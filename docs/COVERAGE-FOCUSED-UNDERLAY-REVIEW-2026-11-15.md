# Coverage-focused map pass — 15 November 2026

**Purpose:** eliminate unpainted-looking land interiors in the review composite without breaking historical shoreline, water masks, town placement, or typography. This is a *review rendering*, not a claim of final 300-DPI print acceptance.

## What is applied

- Existing geographically derived land, lake and sea masks remain authoritative. The masked land interior of each of the three atlas regions receives a low-strength painted texture contribution at the base-wash stage, before any roads, labels, settlements, coastline ink, river imagery or island art.
- The painter uses **only** the four previously retained edge-matched textures: desert sand, dry steppe, Canaan limestone scrub, and green lowland. A high-pass colour-preserving method brings actual painted strokes into the locally appropriate geographic wash without replacing the topography or turning naturally arid areas green.
- Texture contributions vary according to existing region-specific fertility and desert fields. Insets are rendered independently, and their pixels cover the corresponding main-map area.
- Sea, mapped lakes and the partially antialiased shoreline are excluded from painting by a fail-closed geographic mask. There are **no fabricated coordinates** for sprites.
- Underlay blending is enabled by default for the **colour review composite** only; set `CRUSADER_COVERAGE_UNDERLAYS=off` to compare against the prior plain geographic wash.

## Evidence emitted by the build

- `reports/rebuild-2026-11-12/outremer-current-composite.jpg`: actual geographic colour composite
- `reports/rebuild-2026-11-12/underlay-coverage-report.json`: masked interior land pixels, eligible painted pixels, pixels whose colour really changed, excluded boundary/water pixels and class-weight totals for main, Aegean and Delta frames
- `reports/rebuild-2026-11-12/terrain-gap-report.md`: *separate* low-detail screening, which is not a reliable exposed-base-layer detector
- `out/underlay-coverage-report.json`: ephemeral workflow artifact, verified by `tools/check_coverage_underlays.py`

The check fails if any of the three geographic regions was omitted, any eligible interior land pixel lacked texture contribution, or the underlay touched water. The report acknowledges that land pixels can receive underpaint even when more illustrative foreground features or a hand-fitted local overlay would improve the map.

## Still on hold

1. The 51 lowland cutouts are technically reconciled, but their individual geographic footprints remain unverified. The workflow **does not** scatter them or invent coordinates.
2. Canaan coastal batches 37–39 and water-bearing masks still require local shoreline registration before geographic placement.
3. Whole-island replacements are separate from registered old island overlays until their actual silhouettes are verified.
4. Coastal city water-side orientation, alpha fringes, foreground overlaps and historical-era variants require visual review.
5. The existing green lowland rectangle has known source resolution limitations; **not print-approved**.
6. This underpaint mask establishes **base wash underpaint coverage**, not independently verified absence of all stylistic gaps. Review the actual rebuilt map at coastal crops and full resolution before claiming completion.

The original four underlay PNGs and all previously approved/provisional artwork remain unchanged.
