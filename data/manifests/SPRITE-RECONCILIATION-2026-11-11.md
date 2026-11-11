# Crusader sprite reconciliation — 11 November 2026

## Verified `main` status

As checked after commit `09094365fdfb581cd3bb6251aa462a62b64282db`, the repository holds **545 PNG files**. This is **not** a count of distinct sprites or map placements: it includes archived masters, original paintings, duplicates and review variants.

- **45 individual city paintings** are in `data/sprites/city-review-2026-11-10/sprites/` (five batches of nine). Review-only, not production-approved. The draft map includes 43 candidates in the 1180 review, while Mystras and Mansoura are later-period review subjects. Original source sheets remain in an offline ZIP.
- **30 rural composite terrain PNGs** CSV-089–118 are in `data/sprites/rural-landscapes/png/`, with placement metadata; `ready_for_renderer=false` and historical, alpha and geographical QA pending.
- **47 Greek-island coastline overlays** (12 original + 35 batch-02) are present; the map compositor still needs reprojection, coast verification and final overlay blending.
- **32 mountain/vegetation terrain outputs, 34 landscape/water/field outputs, 10 older island interior outputs**, plus 66 matching source paintings, were copied from `assets/historical-batch-01` to `data/terrain/` and `data/landscape-assets/`. These are illustrative, not print-certified or automatically composed.
- **Three natural-landmark artworks** (`NAT-L017` Cappadocia, `NAT-L018` Cedars of Lebanon, `NAT-L019` Mount Hermon) were recovered to `data/sprites/natural-landmarks/`. Cappadocia lies outside the current frames.
- **Four rectangular terrain gap-fill underlays** with four edge-matched variants (8 PNGs) exist at `assets/terrain/large_area/rect_underlays_04/`; their use must stay below irregular RGBA cutouts and be geographically masked.
- **Two fortress-batch12 review paintings** exist (Anavarza and Kızkalesi). The Kızkalesi painting is the wrong-sized coastal-city concept and explicitly requires repainting as an offshore castle; neither painting is final.

## Uncommitted image art / direct recovery targets

1. **13 of 14 source sprite sheets from the 10 November intake** still need binary upload. Only `fortified_town_variants_01.png` was committed. Their source catalog is `data/sprites/intake/2026-11-10/pending_upload_manifest.json`. These sheets also need proper cutout extraction, artifact identity, alpha cleanup and style QA before production.
2. **35 transparent terrain redo-03 PNGs** (16 replaced regions + 19 supplements) are specified in `assets/terrain/large_area/manifest_transparent_redo_03.json`, but the binary files are **not** in `main`. Their older opaque expansion-02 imagery is superseded, not the desired production art.
3. **City source/master collage images** behind the 45 already-committed review cutouts are not in GitHub and must be preserved if high-resolution repainting/editing is required.
4. **Legacy `build/latest-artwork-2026-11-09` branch** still has assets under old `assets/` paths absent from `main`. Many city/terrain files are alternate copies, and some sea files are labelled `1662` and may belong to another project. Do not merge wholesale before deduplication and provenance checks.

## Unpainted or repaint-required named fortresses

The current nine-subject fortress-batch12 plan has **seven unpainted** subjects:
Chastellet/Jacob's Ford, Bourzey, Shaizar, Masyaf, Qadmus, Darbsak, Feke.
Anavarza is painted provisionally; Kızkalesi requires replacement.

Other named fortress priorities from the prior manifest include Buffavento, Kantara, Kolossi, Chlemoutsi, and, if a distinct castle rather than a city is required, Harim.

Safed and Bagras already have review artwork; avoid duplicate commissions. Chastellet exists only 1178–79 and must not be shown standing in an 1180 layer. Later castles such as Montfort and Château Pèlerin must respect their year gates.

## Incomplete map-production work

- Integrate city, island, terrain and landmark manifests with the atlas compositor; review-only placement approval is not a final print-layer merge.
- Review alpha edge halos/red-yellow-cyan speckling, crop margins, painting native resolution and 300-DPI legibility. Do not confuse interpolated enlargement with new detail.
- Compare coastal/river sprite orientation, georeferenced shoreline and roads against underlying features; view from the south; keep labels above art.
- Keep layer hierarchy: base, geographic gap-fill underlays, irregular terrain, coast/hydrography, historical settlement and landmark sprites, then names/labels.
- Enforce year/phase gates, especially for 1180 versus later Crusader works.
- Historical review and unique-site attribution remain needed for generic-looking fortress or church paintings.

## Inventory caveats

The older `data/manifests/REMAINING-CITIES-CASTLES-2026-11-10.md` describes a pre-publication backlog of 45 cities. It is **not** the current art-creation queue: the 45 city review paintings were subsequently committed. Treat individual manifests and `data/sprites/city-review-2026-11-10/README.md` as more recent evidence for current image availability.
