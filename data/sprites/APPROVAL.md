# Sprite artwork and placement approval

Approved at the user's request for map artwork and placement planning. All 14 sprite PNGs are retained with provenance and historical review notes. Approval does not certify historical reconstruction accuracy or merge changes into the default branch.

`placements.geojson` is the consolidated asset inventory and placement markup. It lists every variant with its repository path, SHA-256, geographic ground anchor, projected sheet pixel anchor, normalized image anchor, proposed display size and top-left position. Coordinates remain approximate and require geographic review. Pixel positions use `frame.py`'s Lambert conformal conic projection and the 10800 × 14400 print sheet, upper-left origin.

Eight preferred site variants are selected: new Jerusalem, Acre, Antioch, Tripoli and Belvoir; standalone original Krak; original Kerak and Montréal. Alternative variants remain approved library artwork but are not drawn on top of their preferred counterparts. Older Krak, Kerak and Montréal still require historical/repaint review.

Jerusalem is 1024 sheet pixels wide, twice the standard 512-pixel sprite width. At preview scale multiply coordinates and display sizes by preview_width / 10800. Align each sprite's normalized ground anchor to the geographic point. The listed top-left positions apply that rule and do not resolve overlap with adjacent cities, existing symbols, labels or layout panels.

The placement preview marks eight geographic anchor points on the existing colour map; it is markup for the next rendering pass, not a completed sprite-composited map. Tripoli uses proposed coastal al-Mina coordinates [35.81, 34.45], while the inherited catalog coordinate is preserved in its original manifest. All coordinates remain flagged unverified.

Rebuild the inventory and markup with `python3 build_sprite_placements.py` (Pillow and pyproj). The builder verifies 14 RGBA assets, dimensions, file hashes and eight preferred site choices. Historical uncertainties in both underlying manifests remain authoritative.
