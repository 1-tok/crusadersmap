# Greek Island Batch 02 — Crusader Map

Thirty-five transparent PNG geographic overlays for the Aegean inset, complementary to the 12 islands from Batch 01. Individual GSHHS intermediate island polygons (Basemap, area_thresh=1) determine the coastline; artistically enlarged Byzantine/medieval towns are rendered as schematic paintings, not archaeological reconstructions.

## Installation

All files go under `data/sprites/greek-islands/batch-02/`; **do not overwrite Batch 01**. `placement_manifest.json` assigns each PNG an `render_bbox_wgs84` [west,south,east,north] rectangle in EPSG:4326. Its **complete image** including transparent margins is intended to georeference to this rectangle. Reproject into the `aegean` inset from `frame.py`; do not naively paste the raw PNG at its intrinsic source pixel size. Preserve transparency, not sea backgrounds. Draw below map text and existing landmark callouts.

## Status and QA

`APPROVED_FOR_PROVISIONAL_PLACEMENT` is a compositing approval, **not** proof of final printed placement, matching coastline of the native map, or certified historical architecture. Specific sites such as Skaros, the Monastery of St John, and Andros Kato Kastro have date-sensitive notes in the JSON; do not depict later architecture in earlier phases. Some named art anchors have been nudged slightly inland to keep buildings visible; manifest retains true geographic town coordinates separately. No printed labels are baked into the art.

For provenance, see the manifest source links; all PNG content SHA256 hashes are recorded in `SHA256SUMS.txt`. This collection is designed to be used by the Aegean map compositor after a projection/shoreline trial.
