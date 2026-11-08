# Mountain terrain pieces: Palestine to Anatolia and Greece

Five reusable transparent PNGs, each 1024 pixels wide, matching the historical atlas's ink/watercolor palette and upper-left lighting. Original generations and complete prompts are preserved. Generated with built-in image_gen; `build_terrain.py` packages and checks them.

| Asset | Suggested use |
|---|---|
| `png/palestine-limestone-ridge.png` | Low dry Judaean/Samarian ridges and limestone uplands |
| `png/lebanon-high-massif.png` | High limestone massifs in Lebanon / Hermon context |
| `png/taurus-ridge.png` | Rugged Anatolian karst ridges and escarpments |
| `png/anatolian-volcanic-massif.png` | Central Anatolian volcanic mountain typology |
| `png/pindus-forested-ridge.png` | Greek mountain ridges, cliffs and forested lower slopes |

## Place on the map

Use `manifest.json` for asset paths, hashes, dimensions, bottom-center anchors and regional placement guidance. Start at 512 sheet pixels wide and vary the size to fit terrain corridors. These are illustrative stamps, not geographic footprints or elevation models. Arrange linked pieces along the actual range, overlap tapered ends about 15%, and draw rear pieces before foreground pieces. Keep cities, roads, labels and coastlines legible. Avoid excessive rotation and mirroring because they change the consistent lighting. These stamps are overlap-friendly, not mathematically seamless tiles.

Coordinates are approximate regional label anchors. The Lebanon piece can be reused in the Hermon context with separate researched placement; its source coordinate is not a Hermon summit coordinate. The central Anatolian volcanic example is outside the current map frames: retain it for a future Anatolian extension rather than moving it onto the existing sheet. Range geometry, aspect and vegetation should guide final placement. No existing map terrain is automatically replaced.

These pieces evoke regional forms, not exact surveyed mountains or verified medieval vegetation/snow cover. Not every Greek range is limestone, and neither Lebanon nor Anatolia is geologically uniform. The volcanic piece is inspired by Erciyes-type morphology, not a certified portrait of that mountain.

## Build and checks

`python3 build_terrain.py` requires Pillow, NumPy and SciPy. It removes alpha below 16/255 and detached components under 20 pixels, trims, resizes and adds proportional transparent padding. Original sources are unchanged. The manifest stores before/after alpha counts, hashes and dimensions. Check `previews/terrain-library.jpg` on light and dark backgrounds. Resizing does not add native image detail.

## Regional references

These references support broad terrain choices, not the geometry or historical land cover of the generated images:

- Lebanon's limestone mountain geology: https://cas.gov.lb/images/excel/syb/2008/environment.pdf
- Taurus limestone karst: https://baly.kenyon.edu/slides/43096
- Geological variation among Pindus massifs: https://www.sciencedirect.com/science/article/abs/pii/S0169555X06005241
- Erciyes volcanic morphology: https://volcano.si.edu/volcano.cfm?vn=213010

Full generation prompts are in `prompts.json` in the same order as the five assets. The originals remain in `sources/` for alternate processing.
