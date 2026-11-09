# Rural landscape composites with small settlements (CSV-089 to CSV-118)

Thirty regional terrain pictures, each with small villages, hamlets, farmsteads or camps painted into the ground (hill villages, coastal hamlets, oasis settlements, irrigated valleys, wheat and olive country, marsh and river plains, caravan stops). They stand in for generic villages and country between the named places.

`rural_landscape_placement_manifest.json` holds each piece's terrain type, description, scale class, and its queued placement on the Crusader map (area, centre lon/lat and sheet pixels, footprint, z-order, review gate). `rural_landscape_placement_manifest.registered-2026-11-08.json` is the first registration, kept for the record.

These files were first committed to the 1-tok/atlas repository by mistake and were moved here on 9 Nov 2026.

**The 30 PNG files are not in the repository.** The manifest says `png_package_unavailable_for_review`, every `png_path` is null, and nothing can be rendered until the images are added. Add them as `data/sprites/rural-landscapes/png/CSV-089.png` onward, then fill in `png_path`.

Placement rules (from the manifest): never place a generic settlement on a named city or landmark; use coastal pieces only where the coast matches and river or marsh pieces only where the hydrography matches; scale so buildings read smaller than named settlements; blend edges and align roads, slopes and waterways; avoid obvious repetition and mirror only where safe.
