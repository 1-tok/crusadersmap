# City batch 03 — circa 1180

Six new individual transparent paintings: Methoni, Koroni, Andravida, Chania, Rethymno and Suez. Built-in image_gen was used; original PNGs, exact prompts and source paths are preserved. All six are approved for immediate provisional placement with historical and repaint review flags retained.

The five Greek cities use the Aegean inset; Suez uses the Egypt inset. manifest.json records sourced representative coordinates, historical names, asset paths, alpha QA, pixel hashes, visual footprints, anchors, date window1180 and map layers. The unified catalog imports this batch automatically. placements-1180.geojson supplies geographic placement; shared placements.geojson also supplies projected sheet anchors and footprints.

Period constraints: Andravida is shown as an unfortified earlier town, not the later Frankish capital with Gothic cathedral. Methoni and Koroni use earlier Byzantine defenses rather than later Venetian fortifications. Chania shows a modest Byzantine enclosure rather than the post1252 Venetian city. Rethymno omits the Fortezza1573-1580. Suez is a small decayed settlement; the12th-century account describes Suez and nearby Qulzum as mostly destroyed, so surviving occupation is uncertain. The Suez point is a coarse modern city-region reference, not exact medieval geolocation, and must not be silently relabeled as the Qulzum archaeological site.

These paintings are provisional interpretations, not surveyed architectural reconstructions. Coarse gazetteer points and exaggerated visual footprints remain explicit in the manifest. Review uncertainty does not block provisional use of these sourced points. Damietta's unresolved coordinate remains outside this batch and outside geographic export.

Rebuild: `python3 build_greece_egypt_sprites.py --batch greece-egypt-1180-batch03`, followed by `python3 sprite_catalog.py`, `python3 build_sprite_placements.py`, `python3 render_sprite_layer.py`, and `python3 refresh_city_sprite_coverage.py`. Light/dark QA and contact previews are in root previews/.

The three initial landscape/haze drafts are retained under sources/ with `retained-draft-not-approved` status; the selected Chania, Rethymno and Suez inputs are the separate `*-cutout.png` files. `cutout-edits.json` records exact edit prompts. Build dependencies: Pillow, NumPy and pyproj.
