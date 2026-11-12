# Unplaced Crusader Map artwork — editorial placement recommendations
**Audit date:** 2026-11-12. **Authority:** current `main` `data/sprites/automated-intake/manifest.json`, `data/manifests/crusader-period/site-history.json`, `frame.py`, and existing review placements.

Machine-readable per-image register: [SPRITE-UNPLACED-PLACEMENT-PROPOSALS-2026-11-12.json](SPRITE-UNPLACED-PLACEMENT-PROPOSALS-2026-11-12.json).

## Scope and what is *not* yet placed
226 consolidated intake image records were classified. **12 are source masters/sheets and must never be drawn as standalone map sprites**; **30 are Aegean island concepts** requiring boundary/projection verification; **38 are named candidate illustrations** (26 records matched to 11th–13th century gazetteer anchors, 12 names require coordinate research). Other inputs are generic pools to place manually according to landscape type, not at invented point coordinates. These classifications are suggestions, not a statement that the active compositor has drawn any of these assets.

The 226 automated-intake GeoJSON records all have null geometry, even though `approval_for_review_placement=true` is recorded for review-library use. The separately approved `placements-review.geojson` has geographic features; do not double-place those same site identities.

## Recommended regions and draw order

| Art type | High-value placement pool | Strict placement instruction |
|---|---|---|
| 30 island concepts | **Aegean inset only**, subject to extent intersection and island-outline proof | Compare with existing 5 island batches and vector coastline; no re-use in main Levant view; reject overlaps and island duplicates |
| 11 coast / headlands / coves | Levantine coast, Cyprus coast and Aegean inset | Fit coast edge; do not invent bays or project sea inland |
| 15 river / reeds / marsh | Nile Delta inset, Orontes tributary valleys, Jordan and Galilee water margins | Mask to georeferenced historical hydrology, not an arbitrary sheet position |
| 22 agricultural, fields, orchards | Cilician plain; Galilee/Samaria; Greek and Peloponnesian hills; Nile Delta agricultural edge | Use below towns, castles, roads; adjust crops and irrigation by region |
| 11 woodland stamps | Galilee/Mount Carmel; Lebanon; Cyprus uplands; Aegean rural uplands | Break visually repetitive tree patterns; preserve local ecologies |
| 11 mountain and 3 arid forms | Taurus, Lebanon/Anti-Lebanon and Greek uplands; Sinai, Transjordan, Negev | Place over appropriate elevation, below settlements, road markers and labels |
| 11 infrastructure pieces | Historic rural corridors near roads, rivers or named settlement margins | Only if compatible era, technology and watercourse; don't invent quarries, aqueducts or bridges at named sites |
| 10 trade/caravan pieces | Transjordan desert approach, Sinai tracks, Damascus–Cilicia corridor | Road-adjacent decoration only, not a newly asserted historical trade route |
| 6 ships | Levant, Cyprus and Aegean open water near historically existing ports | Check vessels' sail form and heraldry; avoid medieval ownership errors |
| 38 religious motifs | Candidate church/abbey detail panels in Jerusalem, Cyprus, Aegean and Sinai | **Hold unassigned** unless architectural period/identity is authenticated; no indiscriminate domes/minarets |
| 5 generic towns and 3 generic forts | Fallback detail marks only after existing named sprite search | Do not replace a better named painting or display two variants simultaneously |

## Named sites: reuse approximate gazetteer anchors, but stage as review candidates

Matched source examples include Darbsak CP-065, Feke CP-076, Chastellet/Jacob's Ford CP-035, Kızkalesi CP-077, Kantara CP-084, Kolossi CP-086, Chlemoutsi CP-102, Harim CP-062, Apamea CP-061, Nabi Samwil CP-024, Mount Tabor CP-028, Kykkos CP-089 and Bellapais CP-090. **There are duplicate intake variants**, so 26 matched image records do not mean 26 distinct places. Chastellet may stand only during 1178–1179; later surviving Kolossi tower imagery and Chlemoutsi are excluded from 1180. Kızkalesi needs the actual offshore island/water-side detail validated before use. All sites' footprints and southern viewpoint remain under review.

The **12 named unmatched records** are Lampron, Toprakkale/Til, Qal'at Ja'bar, Harran citadel, Gökvelioğlu Castle, Tumlu Kalesi, Birecik Castle, Savranda/Servantikar, Ravanda/Ravendel, Silifke/Seleucia, Qal'at Najm, and Softa Kalesi. They need sourced coordinates and an explicit map frame/inset check; some may be outside the existing sheet. Do not move sites arbitrarily onto the frame.

## Placement safety rules

1. Use global paint order: map base → the **four** retained rectangular underlays → irregular transparent terrain → geographically constrained coasts/rivers → settlements/castles/details → labels.
2. The main print sheet is 36 × 48 in, 10800 × 14400 px. Inset WGS84 extents: Aegean **19.6–30.4°E, 34.7–41.75°N**, Egypt/Sinai **29.5–35.2°E, 27.7–31.8°N**. Both need their own projection transform.
3. Never assign a generic image a fabricated lat/lon. Document a target **region pool** first; then choose a position only after seeing the actual render and resolving hydrology and overlap.
4. Keep technical QA (RGBA) distinct from historical reconstruction, date, geography, visibility, and 300-dpi print suitability.
5. Verify placed/not placed with actual compositor output. A manifest entry alone is not evidence of visibility.
6. Cutout sprite masters/collages remain stored but never rendered as one sprite.

## Immediate implementation priority
**A.** Use the 26 named-anchor candidates for manual alternate-variant review against existing map sites. **B.** Add regional terrain pool overlays in the actual composition in the lower-content areas, starting with Cilician fields, Orontes and Nile wetlands, Transjordan drylands and Taurus/Lebanon foothill gaps. **C.** Review Aegean island concepts against vector coast and inset frame. **D.** Place ships and caravan/farm details only after establishing empty water/road corridors. **E.** Religious/architectural generics remain optional, not mass-placed.

**No new paintings are warranted from the numeric deficit alone.** Recompute the true remaining gaps from the rendered final map, then commission site-specific corrections.
