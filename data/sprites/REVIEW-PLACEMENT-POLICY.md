# Draft map placement — 10 November 2026

Every draft, even one awaiting technical correction or art approval, is **approved for visual placement on the map review layer**. This is a visibility authorization, not a production acceptance.

Review variants live in `placements-review.geojson` (all periods), `placements-review-1180.geojson`, and `placements-review-1245.geojson`. All entries have `approval_for_placement=true`, `approval_for_review_placement=true`, `production_approved=false`, `review_required=true` and `placement_view=sprite-review`.

The existing released catalog and `placements-1180.geojson` are unchanged; the production renderer must not import review-only candidates automatically. The original failure and repair flags remain in each draft manifest. For the same site, toggle alternate images individually rather than stacking duplicate castles. The Safed rebuilding is dated circa 1245, Ajloun circa 1190, and Chastellet was destroyed in 1179. A site depiction must not be reused in the wrong year.

A review placement record means the PNG can be shown at its recorded representative WGS84 point for visual QA; it does not certify the medieval plan, coastline or precise building footprint. Review-layer compositing at print scale still requires QA.


## Rendering the map review layer

Run `python3 render_sprite_layer.py --year 1180 --review` to generate `previews/sprite-layer-review-1180.svg` and `previews/sprite-placement-review-1180.jpg`. Use `--year 1245 --review` for the Safed rebuilding. Add `--all-review-variants` for explicit side-by-side debugging; it may cause overlapping alternate paintings at the same anchor. The default production rendering command is unchanged. The review-only PNGs may have halos, opaque backgrounds or other issues: this is intentional visibility for quality review, not automatic final acceptance.
