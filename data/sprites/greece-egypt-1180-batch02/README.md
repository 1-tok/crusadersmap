# City batch 02 — circa 1180

Six new transparent paintings: Patras, Thebes, Rosetta, Tinnis, Bilbeis and a new Jaffa variant. Five additional geographic sites; Jaffa already has recovered archive artwork. Generated with built-in image_gen; exact prompts and original sources retained. All six are approved for immediate provisional placement at the sourced representative anchors in manifest.json, retaining review and repaint flags.

Patras and Thebes use the Aegean inset, Rosetta/Tinnis/Bilbeis the Egypt inset, and Jaffa the mainland projection. The shared catalog now imports both city batches automatically. Unified GeoJSON and markup previews apply the proper inset-to-sheet transform. Exact source transcription does not imply surveyed medieval city extents.

Tinnis has uncertain occupation intensity in1180, given differing descriptions of earlier decline and final evacuation1227. Bilbeis has differing coarse/infobox gazetteer points and is distinct from Pelusium. These uncertainties remain explicit. No later Frankish, Ottoman or Mamluk architectural phase is certified by these provisional paintings.

Rebuild with `python3 build_greece_egypt_sprites.py --batch greece-egypt-1180-batch02`, then `python3 sprite_catalog.py`, `python3 build_sprite_placements.py`, and `python3 render_sprite_layer.py`. Requires Pillow and pyproj; source preservation and pixel-hash validation follow batch01. See root previews/greece-egypt-1180-batch02-qa.jpg for light/dark review.
