# Draft map placement — 10 November 2026

Every draft, even one awaiting technical correction or art approval, is **approved for visual placement on the map review layer**. This is a visibility authorization, not a production acceptance.

Review variants live in `placements-review.geojson` (all periods), `placements-review-1180.geojson`, and `placements-review-1245.geojson`. All entries have `approval_for_placement=true`, `approval_for_review_placement=true`, `production_approved=false`, `review_required=true` and `placement_view=sprite-review`.

The existing released catalog and `placements-1180.geojson` are unchanged; the production renderer must not import review-only candidates automatically. The original failure and repair flags remain in each draft manifest. For the same site, toggle alternate images individually rather than stacking duplicate castles. The Safed rebuilding is dated circa 1245, Ajloun circa 1190, and Chastellet was destroyed in 1179. A site depiction must not be reused in the wrong year.

A review placement record means the PNG can be shown at its recorded representative WGS84 point for visual QA; it does not certify the medieval plan, coastline or precise building footprint. Review-layer compositing at print scale still requires QA.


## Rendering the map review layer

Run `python3 render_sprite_layer.py --year 1180 --review` to generate `previews/sprite-layer-review-1180.svg` and `previews/sprite-placement-review-1180.jpg`. Use `--year 1245 --review` for the Safed rebuilding. Add `--all-review-variants` for explicit side-by-side debugging; it may cause overlapping alternate paintings at the same anchor. The default production rendering command is unchanged. The review-only PNGs may have halos, opaque backgrounds or other issues: this is intentional visibility for quality review, not automatic final acceptance.

## Clarification — geographic review placement (13 November 2026)

The blanket visual-review authorization above allows every draft to be **available for inspection in a gallery or diagnostic art review**; it is **not** authorization to invent a geographic location. A feature with null geometry, missing coordinate provenance, incompatible period, `candidate_only=true` or `approval_for_review_placement=false` must remain unpositioned until it is verified and explicitly selected. The older statement that all review records have placement approval describes the November 10 curated review layers, **not** the later automated-intake pool. Production approval and actual visibility in a full-map composite are additional independent checks. See [AI context](../../docs/AI-CONTEXT.md) and [final map readiness](../../docs/FINAL-MAP-BUILD-READINESS.md).

## Mandatory north-facing POV review (13 November 2026)

Reviewers must confirm the camera is **south of the feature looking north** from an elevated oblique view. For the unmirrored north-up image, image left is west, image right is east, top is north and foreground is south. Confirm sea and harbor water appear in the site's actual cardinal direction (west/left, east/right, north/behind, south/foreground; mixed shoreline for peninsulas and islands). Never make water fit by mirroring the artwork. Fail/repaint any misplaced shoreline or invented water before claiming geographic or print approval. See [mandatory POV specification](../../docs/AI-CONTEXT.md#mandatory-pov-and-coastal-water-orientation--13-november-2026).
