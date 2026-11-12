# Greek Islands — Batch 05 review

**Approval:** User authorized provisional map placement/review on 2026-11-12. This approval is logged for *visual review*, not cartographic placement.

**Image status:** Four illustrated concepts exist in the conversation, but their PNG binaries have **not** been transferred into the GitHub repository. The four original source filenames are listed in `placement_manifest.json`.

**Critical QA blocker:** The generated concepts resemble/repeat Batch 04 island scenes rather than reliably depicting the intended new islands: Agathonisi, Pserimos, Telendos and Meganisi. Consequently **do not assign those island identities or force them onto an island's coastline**. Georeference and print-quality verification are not complete.

**Review workflow:**
1. Upload the source PNGs to `data/sprites/greek-islands/batch-05/incoming/` via GitHub intake, preserving originals.
2. Inspect alpha and remove red/blue fringe artifacts.
3. Compare visually and via checksums against Batch 04; classify duplicate or repaint-required.
4. Repaint as needed for Agathonisi, Pserimos, Telendos and Meganisi using real island outlines and appropriate circa 1180 settlement references.
5. Only after shoreline validation and registered `render_bbox_wgs84`, set `placement.enabled=true` for *provisional composite review*. Keep final print approval separate.

This is a non-destructive review record; it neither places sprites nor overrides earlier batch states.
