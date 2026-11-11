# Draft map placement — 10 November 2026

Every draft, even one awaiting technical correction or art approval, is **approved for visual placement on the map review layer**. This is a visibility authorization, not a production acceptance.

Review variants live in `placements-review.geojson` (all periods), `placements-review-1180.geojson`, and `placements-review-1245.geojson`. All entries have `approval_for_placement=true`, `approval_for_review_placement=true`, `production_approved=false`, `review_required=true` and `placement_view=sprite-review`.

The existing released catalog and `placements-1180.geojson` are unchanged; the production renderer must not import review-only candidates automatically. The original failure and repair flags remain in each draft manifest. For the same site, toggle alternate images individually rather than stacking duplicate castles. The Safed rebuilding is dated circa 1245, Ajloun circa 1190, and Chastellet was destroyed in 1179. A site depiction must not be reused in the wrong year.

A review placement record means the PNG can be shown at its recorded representative WGS84 point for visual QA; it does not certify the medieval plan, coastline or precise building footprint. Review-layer compositing at print scale still requires QA.

