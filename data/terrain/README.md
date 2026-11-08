# Mountain terrain pieces: Palestine to Anatolia and Greece

Thirty-two reusable transparent PNGs, each 1024 pixels wide, matching the historical atlas's ink/watercolor palette and upper-left lighting. Original generations and complete prompts are preserved. Generated with built-in image_gen; `build_terrain.py` packages and checks them.

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

Full generation prompts are in `prompts.json` in the same order as the original five assets. The originals remain in `sources/` for alternate processing.

## Expansion: 12 interlay pieces

The kit now includes left/right Palestine foothill ends, an open limestone valley, a short Lebanon ridge and saddle, a Taurus cliff spur and short peaks, Anatolian steppe foothills and a small volcanic cone, plus Greek wooded foothills, an open gorge and a short ridge. They use the same upper-left lighting and are separate generated illustrations, not mirrored copies.

Use 20–35% overlap as a starting point and vary scale between about 0.65 and 1.15. Layer rear ridges first, connectors second, and low foothills last; preserve valley openings. Avoid mirroring and large rotations. These are overlap-friendly illustrations, not seamless tiles. `interlay-recipes.json` and `preview_terrain_interlay.py` reproduce three sample layouts; the mixed Lebanon/Taurus row demonstrates visual composition, not a surveyed geographic chain.

`expansion-prompts.json` saves eight full built-in image_gen prompts and summaries for four pieces generated in the preceding chat turn. Original source images are all retained. See `previews/terrain-catalog.jpg` for the individual catalog and `previews/terrain-interlay-examples.jpg` for assembled examples.

## Six narrow and branching connectors

The third set adds limestone and Greek narrow spines, dry and forested branching spurs, a high rocky spine and an open Anatolian saddle. Use them at smaller scale to join ridge tips and create branching chains. Their inherited family coordinates are regional context, not independent landmark positions. Full built-in image_gen prompts are saved in `connector-prompts.json`; originals remain in `sources/`. The full catalog grows automatically with the manifest.

## Placement approval and next pass pieces

See `APPROVAL.md` and `placements.geojson` for the approved artwork inventory, projected context anchors and family corridor guides. The three newest pieces are a dry limestone pass, wooded pass and rocky foothill fan. Their full built-in generation prompts are saved in `pass-prompts.json`. Placement markup is in `previews/terrain-placement-markup.jpg`; final terrain compositing is a separate step.

## Low-relief continuation

The library now contains 29 pieces. New `coastal-foothill-transition`, `dry-wadi-connector`, and `open-plateau-escarpment` assets use regional family anchors as context only. Their low-relief shapes should be placed on reviewed foothill/valley/plateau terrain rather than literally on the inherited mountain label anchor. Full built-in image_gen briefs are in `low-relief-prompts.json`; source images are retained. Artwork/placement-planning approval is recorded, while geographic and historical verification remain pending.

## Vegetation continuation

The kit now has 32 pieces, adding sparse cedar-like woodland, pine-covered slope and Mediterranean scrub fillers. Tree shapes are illustrative, not botanical identifications; medieval forest cover is unverified. Scale vegetation to neighboring sprites, avoid dense stacking, and preserve clear valleys and settlement labels. Full built-in image_gen prompts are in `vegetation-prompts.json`, with unchanged originals in `sources/`. These assets retain artwork and placement-planning approval only.

## First on-map usage proof

Run `python3 render_terrain_proof.py` (Pillow and pyproj) to render 16 trial placements from `render-plan.json`. Outputs are `previews/terrain-map-proof.jpg`, numbered bounds in `previews/terrain-map-proof-markup.jpg`, and an editable linked `previews/terrain-proof-overlay.svg`. `render-proof-report.json` records sheet bounds and nearby source settlement anchors. Existing print outputs are unchanged; original terrain is still visible underneath this overlay. Use the proof to judge placement and scale before integrating the assets into native rendering layers.
