# City batch04 — circa1180

Six new city sprites: Nafpaktos, Monemvasia, Corfu, Chios, Ascalon and Beirut. Generated with built-in image_gen; exact prompts and source PNGs retained. The selected normalized transparent sprites are approved for immediate provisional placement, with sourced representative coordinates, ground anchors, visual footprints, map layers and repaint/research uncertainties recorded in manifest.json.

The four Greek cities use the Aegean inset; Ascalon and Beirut use the mainland projection. The unified catalog imports this batch automatically. The archaeological park point for Ascalon locates the ancient/medieval city, not modern Ashkelon; the Beirut point locates the historic archaeological core and does not identify the medieval Latin cathedral site. Gazetteer precision is not surveyed positional accuracy.

Artwork targets the earlier Byzantine forms of Nafpaktos, Monemvasia, Corfu and Chios, omitting later Venetian/Genoese/Ottoman monuments. Ascalon uses the researched semicircular landward rampart concept, without treating all tower details as verified. Beirut omits the later grand Ibelin palace and modern skyline. All urban layouts, terrain proportions, harbor shapes and building heights remain interpretive.

Rebuild with `python3 build_greece_egypt_sprites.py --batch greece-egypt-1180-batch04`, then `python3 sprite_catalog.py`, `python3 build_sprite_placements.py`, `python3 render_sprite_layer.py`, and `python3 refresh_city_sprite_coverage.py`. Dependencies: Pillow, NumPy and pyproj. QA and contact previews are saved under root previews/.

Initial Chios, Ascalon, Beirut and Nafpaktos drafts are retained as unapproved source provenance; the selected inputs use separate `*-cutout.png` files. Exact correction prompts are in `cutout-edits.json`. Decorative borders, flags and broad background haze are removed from the placement assets.
