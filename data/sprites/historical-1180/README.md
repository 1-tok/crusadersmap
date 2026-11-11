# Period-informed batch 01: Jerusalem, Belvoir, Acre, Antioch and Tripoli, circa 1180

Five new, non-destructive alternatives to the original artistic sprites. Generated with built-in `image_gen` from the saved `prompts.json`, then packaged with the existing library's low-alpha noise cleanup. Original generations remain in `sources/`.

- Jerusalem: 2048 px wide; recommended display width 1024 map units, **twice** the standard 512-unit width. This is twice the linear size, approximately four times the footprint, not twice the area.
- Belvoir: 1024 px wide; recommended display width 512 map units.

The generator did not honor the requested native resolution exactly. Packaging resizes the originals to these delivery widths; it does not manufacture new architectural detail. Source dimensions, output dimensions, hashes and padding checks are recorded in `manifest.json`.

## Evidence and interpretation

These are **period-informed reconstruction candidates**, not certified historically accurate models. Internal visual review checks major constraints, but does not replace an archaeologist's assessment. The manifest records supported features separately from speculative detail.

Jerusalem places the sacred esplanade in the eastern city, separates the Holy Sepulchre and western citadel, and omits Ottoman tilework. The modern blue ceramic exterior dates to Suleiman's sixteenth-century restoration. Gold was present in the monument's early history; the precise roof finish in 1180 has not been established here. The gray dome is deliberately flagged as provisional, not presented as evidence of an originally un-gilded building. Courtyard, wall circuits, landmark proportions, roofs and urban density are generalized for map readability. References in the manifest support individual constraints rather than the entire painting.

Belvoir replaces the original fantasy-like keep with quadrangular towers, concentric enclosures and a dry ditch. Anne Baud and Olivier Guyotat's study in Medievalista 33 (2023), “Belvoir, study of the interior castle: construction site and spatial organization,” describes the enclosure plan. Its indexed PDF text was available during research; direct page/PDF access was blocked by the publisher's bot check, so figures were not inspected. Do not claim that the generation was traced from their archaeological plan. Reconstructed heights, exposed roof curves, service buildings and precise gates remain unverified.

## Rebuild and inspect

Run `python3 build_historical_sprites.py` with Pillow, NumPy and SciPy installed. Packaging removes alpha below 16/255 and detached components smaller than 20 pixels, preserves transparent originals, and adds proportional padding. Compare `previews/historical-batch-01.jpg` on light and dark backgrounds.

The build and validation check RGBA mode, transparent padding, stable hashes and 2:1 display-width ratio. They do not establish historical accuracy. No existing atlas rendering is changed. Consumers should read this batch manifest explicitly; the legacy manifest and generated original-library sprites remain preserved for comparison.

Next research candidates: Acre, Antioch, Tripoli and Krak des Chevaliers, each with an explicitly selected date and architectural phase. Do not generate one generic castle shape for all of them.

## Acre addition

Acre is a standard 1024-pixel-wide port sprite. Its brief excludes the later walled Montmusard suburb and Ottoman skyline. The Israel Antiquities Authority dates the suburb to the late twelfth century and its enclosure to the thirteenth century: https://hadashot.iaa.org.il/report_detail_eng.aspx?id=1561 . Precise streets, church facades, tower counts and harbor works remain interpretive. `acre-prompt.txt` records the brief and transparency edit using built-in image_gen. The source and final PNG are retained. Light/dark visual review passed after packaging; historical certification remains pending.

## Antioch and Tripoli additions

Both use standard 1024-pixel output width and 512-unit display width. Prompts are retained in their named text files; built-in image_gen generated both assets. Antioch emphasizes the riverside lower town, ascending walls and partly unbuilt mountain enclosure. Its topography and schematic defenses draw on the academic references in the manifest; exact church forms and 1180 massing are unverified.

Tripoli represents the low coastal city at al-Mina and intentionally excludes inland Mont Pelerin. The original catalog coordinate points nearer inland Tripoli, so the manifest preserves that coordinate and adds a proposed coastal anchor [35.81,34.45] requiring placement review. Medieval shoreline and port layout remain interpretive. Chlela’s 2025 doctoral research provides the coastal/inland distinction; neither sprite was traced from a surveyed archaeological plan. Original generations are preserved. Light/dark previews and transparent-padding checks passed; specialist historical review is pending.
