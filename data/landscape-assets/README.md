# Desert, oasis, valley, road and Jordan-basin assets

Nine transparent assets complement the 32-piece mountain/vegetation kit:

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

Generated with built-in image_gen. Full prompts and unchanged originals are retained. `manifest.json` includes hashes, dimensions, image anchors, orientation, review flags and connection hints; `placements.geojson` records approximate regional context points. Roads deliberately have null geographic geometry. They are reusable graphics, not evidence of historical routes.

## Placement and layering

Put desert/valley pieces above the base wash and below cities, labels, roads and hydrography. Use small oasis motifs only at researched springs; the Jericho-region point is context rather than identification of a named oasis. Join road endpoints with overlap and adapt to researched route geometry. They are not mathematically seamless or guaranteed to have matching elevations at both ends.

Water assets use near-overhead north-up geometry rather than the oblique mountain view. Do not rotate them arbitrarily. The Jordan image is a schematic lower-river connector, not the entire river from its headwaters. Connect the Galilee southern outlet toward the Dead Sea northern inlet using the correct geographic course; do not stretch the decorative image straight between two lake centers. The manifest's endpoint coordinates are approximate guidance, not surveyed control points. Keep tributaries, crossings and shore settlements separate.

The Galilee and Dead Sea shapes are **illustrations requiring geographic fitting**, not replacements for the repository's Natural Earth geometry. Galilee's generated outline, inlet and outlet positions are generalized. The Dead Sea illustration avoids modern evaporation cells and shows a connected southern basin, but the exact medieval lake level, shoreline, Lisan geometry and aspect ratio have not been established. A different selected year or evidence may require repainting. Do not describe either as an accurate 1180 shoreline.

The existing map layers and print files are unchanged. Artwork is approved for the library and placement planning under the user's continuing instruction; final geographic and period accuracy remain unverified.

## Technical checks

Run `python3 build_landscape_assets.py` (Pillow, NumPy, SciPy). It removes alpha values below 16/255 and detached components under 20 pixels, trims, preserves aspect ratio, and adds transparent padding. Output long edges are 1024 px for terrain, 1536 px for lakes/roads and 2048 px for the river. Inspect the light/dark contact sheet at `previews/desert-water-road-assets.jpg`. Resizing does not add native detail. Connection hints are approximate and require visual checking.

## Geographic research

References support broad geography and the need for shoreline review, not the exact generated outlines:

- [NASA: Sea of Galilee](https://science.nasa.gov/earth/earth-observatory/sea-of-galilee-147685/): Jordan-fed freshwater lake and rift-valley context.
- [NASA: Dead Sea](https://www.nasa.gov/image-article/dead-sea-2/): Jordan inflow from the north and arid drainage setting.
- [USGS: Dead Sea change](https://eros.usgs.gov/earthshots/dead-sea-israel-jordan-west-bank): modern shoreline change makes current water outlines unsuitable as an unquestioned medieval reconstruction.
- [Late Holocene lake levels of the Dead Sea](https://pubs.geoscienceworld.org/gsa/gsabulletin/article-abstract/116/5-6/555/2079/Late-Holocene-lake-levels-of-the-Dead-Sea): lake-level variability; this does not identify a certified 1180 shoreline here.
