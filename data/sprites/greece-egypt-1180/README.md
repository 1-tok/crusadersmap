# Greece and Egypt — circa 1180, batch 01

Nine new individual transparent city paintings: Athens, Thessaloniki, Corinth, Chalkida, Heraklion (Chandax), Rhodes, Cairo, Alexandria and Damietta. Generated with built-in image_gen; exact prompts and source-image provenance are in prompts.json. Original generated alpha is preserved in sources/. Packaging crops transparent margins, scales proportionally and adds 26 pixels of transparent padding; painted content is not changed.

manifest.json records unique IDs, asset paths, historical names, regions/layers, sourced WGS84 coordinates, painted footprints, ground anchors, period eligibility, approval and repaint flags. All nine assets have provisional geographic placement with review and repaint flags. Damietta uses the published Abu el-Maati mosque inventory point as a representative anchor for the earlier city.

placements-1180.geojson contains the eight sourced anchors. Greece belongs to the aegean inset; Egypt to delta. Do not use mainland frame.to_px for these features. Coordinates are representative published points, not surveyed city boundaries. Artwork display width defaults to 512 full-atlas pixels. Project footprints and anchors using the correct inset before composing a print edition.

Known repaint flags include invented waterfront along Athens and Corinth, schematic street plans, wall circuits and building heights, and phase-specific church/minaret silhouettes. Cairo's generated water strip is also schematic and must not be read as the actual Fatimid city edge. Earlier Byzantine Rhodes is intended, not the later Hospitaller city. None of the paintings is historical certification. Review flags do not hold the eight geographically grounded assets from provisional placement.

The unified catalog now imports this batch automatically alongside recovered archive artwork and batch02. Shared GeoJSON, SVG layers and sheet markup use the Aegean and Egypt inset projections. Damietta’s mosque anchor and historical uncertainty are recorded in the manifest.

Rebuild with `python3 build_greece_egypt_sprites.py` (Pillow). QA checks real RGBA transparency, empty padded edges, unique pixel hashes and safe individual outputs. Light/dark preview: previews/greece-egypt-1180-qa.jpg at repository root.
