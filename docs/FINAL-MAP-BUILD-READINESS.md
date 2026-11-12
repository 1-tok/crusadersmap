# Crusader Map — final build readiness and handoff (12 November 2026)

## Scope
Produce a 36 × 48 inch (10800 × 14400 pixel, 300 dpi) historical atlas with a main Levant/Cyprus view and Aegean and Egypt/Sinai insets. The baseline target is circa 1180, with later dated editions kept separate. The next phase is map assembly and QA, not new image generation.

## Mandatory source inventory
Use `python3 tools/build_sprite_handoff.py` to create the all-images ledger and review gallery. This scans the existing placement layers, the 226-image automated intake manifest, documented mountain and rural terrain sets, original Greek island overlays, and every additional PNG found under `data/sprites` and `data/terrain`. The gallery includes unapproved, rejected, provisional, duplicate and source artwork. It does not constitute approval to render every image on the map.

Consult:
- `data/manifests/SPRITE-UNPLACED-PLACEMENT-PROPOSALS-2026-11-12.json` for proposed regional pools and named-site coordinate candidates
- `data/manifests/SPRITE-UNPLACED-PLACEMENT-RECOMMENDATIONS-2026-11-12.md` for geographic and layer policy
- `data/manifests/crusader-period/site-history.json` for 147 site anchors and chronology
- `data/sprites/placements-1180.geojson` and review placement GeoJSON files for already located paintings
- `data/sprites/greek-islands/` for coast-matched island overlays, including later batches
- `data/terrain/manifest.json`, `data/sprites/terrain-batch06/manifest.json`, and `data/sprites/rural-landscapes/rural_landscape_placement_manifest.json` for terrain candidates.

## Five production priorities
1. **Site matching.** Show each suitable named castle, city, port and religious site at its correct existing site coordinate and correct edition year. Select only one visible primary variant per site. Keep other variants accessible in the review gallery. Do not move a named site merely to fill blank space.
2. **Terrain coverage.** Cover visually flat or bare land with geographically appropriate mountain ridges, scrub, grassland, agricultural field patterns and wooded hills. Preserve four underlying rectangular gap-fill pieces, with irregular transparent terrain sprites above them. Avoid repetitive stamping or inappropriate vegetation.
3. **Coast and hydrology.** Register Greek island artwork by WGS84 render bounding boxes and reproject to the Aegean inset. Clip water, marsh, shore and river imagery to actual shoreline/hydrography. Never allow decorative water to overwrite inland terrain, ports or labels.
4. **Rural and generic fillers.** Where an existing settlement is still a flat symbol and has no dedicated art, use a period/ecology-appropriate generic town or castle only if visual comparison supports it; otherwise retain the original symbol and log the gap. Place generic caravan, mill, farm, coastal tower, vegetation and ship scenes only at plausible road, agricultural, water or open-sea locations. Do not create fictitious towns or coordinates.
5. **QA, labels and period.** Keep named site symbols, roads and geographic labels above terrain. Protect an 1180 historical snapshot from later fabric (standing Chastellet after 1179, Chlemoutsi, later Kolossi tower, etc.). Review heraldry, buildings, transparency halos, original resolution, collisions and print-scale legibility.

## Recommended draw order
1. geographic basemap and vetted shoreline
2. four rectangular background gap-fill underlays
3. landform, mountains, desert, fields and forest underlays / cutouts
4. correctly aligned river/coastal/wetland transitions and projected Aegean islands
5. unique settlement/castle/religious site paintings
6. suitable fallback generic village, bridge, rural and harbor detail
7. maritime decoration inside water geometry
8. labels, roads, borders and final annotations (always legible)

## What must be reviewed, not silently hidden
All extracted individual PNGs, including those with `production_approved=false`, must be accessible in a review gallery. Site-specific artwork that is unapproved can be visible on the **review map** if its location and date are sound, with a clear review watermark/status. Keep a per-image reason when not shown on the geographic map: source master, duplicate, wrong era, no reliable coordinates, outside frame, technical defect, or ecological mismatch.

The entire auto-intake set currently has null geometry in its own review GeoJSON. Some named pieces have known anchors in other manifests. A review-library permission flag alone cannot establish geographic placement. Source sheets and contact sheets are never renderable stand-alone sprites.

## Run/check
- `python3 tools/build_sprite_handoff.py` for complete gallery/ledger; use `--strict` to fail on broken manifest PNG paths.
- `python3 -m unittest discover -s tests -p 'test_review_sprite_date_gates.py' -v` for review year/variant guards.
- `python3 render_sprite_layer.py --year 1180 --review` and `python3 tools/audit_review_map.py --year 1180` for diagnostic sprite-only imagery and collision checks.
- Inspect the existing build entry points `rough_compose.py`, `build_stage2.py`, `make_print.py`, `make_light.py`, `assemble_light.py` before modifying production rendering. The grid preview from `render_sprite_layer.py` is **not** the composited geographic atlas.

## Required acceptance outputs
- A fully assembled geographic review image at usable zoom/detail, with both insets.
- Gallery of **all** PNG assets, including unapproved/repaint-required artwork and source sheets marked accordingly.
- A ledger per asset: source, image file, unique site or generic class, frame, actual map usage (yes/no), year, primary/alternate, QA state, and reason if unplaced.
- A site coverage matrix for all 147 gazetteer locations: dedicated sprite / generic fallback / old flat marker / not visible, plus correct image path and map coordinates.
- A terrain gap register showing bare/flat regions requiring appropriate sprites and a collision register showing geographic and label overlap.
- Review-only JPEG/PNG plus print readiness assessment at 300 dpi, avoiding falsely treating upscaled low-resolution sprites as high resolution.

**No build is complete merely because sprite files exist or have been approved in manifests.** Completion requires verifiable visibility at the proper geographic location, appropriate terrain usage, and a final coverage report. Avoid painting additional sprites until that evidence shows a specific gap.
