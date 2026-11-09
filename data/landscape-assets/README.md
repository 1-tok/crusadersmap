# Desert, oasis, valley, road and Jordan-basin assets

Thirty-one transparent terrain and water assets complement the 32-piece mountain/vegetation kit:

| File in `png/` | Use |
|---|---|
| `sand-dunes.png` | Repeated low desert dune patches |
| `rocky-desert.png` | Rocky hamada and desert escarpment transitions |
| `palm-oasis.png` | Generic palm/spring motif; not a surveyed oasis |
| `broad-valley-floor.png` | Open dry valley connector |
| `road-straight.png` | Straight unpaved road section |
| `road-bend.png` | Curved unpaved road section |
| `jordan-river.png` | Schematic north-up Lower Jordan connector |
| `sea-of-galilee.png` | North-up Lake Tiberias illustration |
| `dead-sea.png` | North-up connected-basin historical interpretation |

Generated with built-in image_gen. Generation records and originals are retained. `manifest.json` includes hashes, dimensions, image anchors, orientation, review flags and connection hints; `placements.geojson` records approximate regional context points. Roads deliberately have null geographic geometry. They are reusable graphics, not evidence of historical routes.

## Placement and layering

Put desert/valley pieces above the base wash and below cities, labels, roads and hydrography. Use small oasis motifs only at researched springs; the Jericho-region point is context rather than identification of a named oasis. Join road endpoints with overlap and adapt to researched route geometry. They are not mathematically seamless or guaranteed to have matching elevations at both ends.

Water assets use near-overhead north-up geometry rather than the oblique mountain view. Do not rotate them arbitrarily. The Jordan image is a schematic lower-river connector, not the entire river from its headwaters. Connect the Galilee southern outlet toward the Dead Sea northern inlet using the correct geographic course; do not stretch the decorative image straight between two lake centers. The manifest's endpoint coordinates are approximate guidance, not surveyed control points. Keep tributaries, crossings and shore settlements separate.

The Galilee and Dead Sea shapes are **illustrations requiring geographic fitting**, not replacements for the repository's Natural Earth geometry. Galilee's generated outline, inlet and outlet positions are generalized. The Dead Sea illustration avoids modern evaporation cells and shows a connected southern basin, but the exact medieval lake level, shoreline, Lisan geometry and aspect ratio have not been established. A different selected year or evidence may require repainting. Do not describe either as an accurate 1180 shoreline.

The existing map layers and print files are unchanged. Artwork is approved for the library and placement planning under the user's continuing instruction; final geographic and period accuracy remain unverified.

## Technical checks

Run `python3 build_landscape_assets.py` (Pillow, NumPy, SciPy). It removes alpha values below 16/255 and detached components under 20 pixels, trims, preserves aspect ratio, and adds transparent padding. Output long edges are 1024 px for original terrain, 1536 px for expanded terrain and lakes/roads and 2048 px for the river. Inspect the light/dark contact sheet at `previews/desert-water-road-assets.jpg`. Resizing does not add native detail. Connection hints are approximate and require visual checking.

## Geographic research

References support broad geography and the need for shoreline review, not the exact generated outlines:

- [NASA: Sea of Galilee](https://science.nasa.gov/earth/earth-observatory/sea-of-galilee-147685/): Jordan-fed freshwater lake and rift-valley context.
- [NASA: Dead Sea](https://www.nasa.gov/image-article/dead-sea-2/): Jordan inflow from the north and arid drainage setting.
- [USGS: Dead Sea change](https://eros.usgs.gov/earthshots/dead-sea-israel-jordan-west-bank): modern shoreline change makes current water outlines unsuitable as an unquestioned medieval reconstruction.
- [Late Holocene lake levels of the Dead Sea](https://pubs.geoscienceworld.org/gsa/gsabulletin/article-abstract/116/5-6/555/2079/Late-Holocene-lake-levels-of-the-Dead-Sea): lake-level variability; this does not identify a certified 1180 shoreline here.

## Accepted artwork and whole-map dry-zone proof

The user accepted the initial nine assets and requested their placement plus more wasteland coverage. Six additional pieces now provide gravel, salt flat, badlands, sand/gravel transitions, dry steppe and escarpments. Full built-in image_gen prompts are in `wasteland-prompts.json`; originals are retained. Acceptance is recorded per asset and does not certify historic geography.

Run `python3 render_landscape_coverage.py` to render `previews/map-landscape-coverage.jpg`, bounds markup, and a separate transparent `previews/landscape-coverage-layer.png`. `coverage-plan.json` records every dry-zone, water, oasis and road placement. The proof uses the prior mountain proof when available. Dry texture is spread through broad editorial regions on the main map and Egypt/Sinai inset, not across seas or Greece. A warm-land color mask, panel exclusions, source-settlement clearances and ink preservation reduce interference. These are approximate raster protections, not complete final label collision checks.

The Jordan and two lakes use illustrative bounding-box fits with potential aspect distortion and unresolved shoreline accuracy; neither their position nor visual acceptance constitutes surveyed hydrology. The oasis is generic near Jericho. Straight road artwork follows selected control-point edges from the existing repository ROADS catalog; the curved road remains available for other routes, not forced onto the map. The original geographic data, map builds and print files are unchanged. This is an editable coverage proof, not a final production print.

## Expanded desert variants

Six user-accepted 1536 px assets link to their originals via `variant_of` in the manifest.
At equal painted width, their alpha bounds extend 2.0–3.1 times farther vertically
(using alpha ≥32/255). The badlands and escarpment have taller drawn relief.
See `previews/expanded-desert-comparison.jpg` and the generation records in
`expanded-wasteland-prompts.json`.

The coverage proof uses the deeper pieces as lightly blended foundations at
900–1250 px wide on the reference sheet. Original 520–780 px pieces break up
the edges and connect the larger landforms. The salt basin is a small contextual
accent on the dry-land mask. Each placement includes its bounds and region,
and the foundation and connector stamps include their terrain role.

## Greek islands, farmland and flat desert

Run `python3 build_aegean_islands.py` (Pillow and pyproj) after building the
landscape assets. It generates ten transparent island overlays for the Aegean
inset. Place each PNG using its padded sheet bounds in `island-placements.json`
and put labels and settlement sprites above it. Each island uses its principal
land polygon from the repository's Natural Earth coastline and an illustrated
interior. Adjacent islets are separate geographic features. Interior hills and
vegetation are decorative. Medieval shoreline and land cover remain unverified.

Use `levant-farmland.png` for irregular grain, fallow and olive plots and
`aegean-terraced-farmland.png` for low cultivated slopes. The point placements
are regional examples. Use `flat-desert-pavement.png` as a broad, low-contrast
desert base beneath higher relief. Generation prompts and originals are retained.

## Generic manual placement

The accepted island interior, farmland and gravel artwork are approved for
generic reuse. Their regional context points are optional. Three additional
stamps have no fixed coordinates. Use the rocky islet as a schematic island
symbol, the orchard mosaic for cultivated slopes and the flat sand sheet
as low-relief ground under other desert pieces. Named island overlays use
their matching coastline bounds. The manifest records each stamp's placement
role, and `generic-terrain-prompts.json` retains the prompts.

The rocky islet, orchard mosaic and flat sand sheet are approved for generic
placement across the map. The next three stamps also have no fixed coordinates.
Use the dry stone pasture to bridge farmland and uncultivated slopes, the
shallow desert wash as a dry drainage accent on flat ground, and the low scrub
islet as a schematic coastal symbol. The latter two represent illustrative
forms. Their positions are assigned by the map editor. Generation prompts are
in `generic-terrain-02-prompts.json`.
