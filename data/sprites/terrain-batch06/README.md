# Crusader Map Terrain Batch 06 — 40 transparent overlap sprites

Forty transparent irregular-edged sprite cutouts are derived from two new hand-painted isometric sheets, each with twenty separate regional terrain illustrations.

The cleaned RGBA sprite sheets are `terrain_batch06_sheet_a.png` and `terrain_batch06_sheet_b.png`. Individual PNGs are in this directory; `manifest.json` records exact pixel rectangles and original SHA-256 checksums.

- Match painterly viewpoint, northward aerial view from south, warm muted medieval atlas palette.
- Layer **above** exactly four retained opaque rectangular background underlays. Put cities, mapped rivers, roads and labels above these cutouts.
- Water and reed wetland imagery is illustrative; align/mask to georeferenced hydrology before use.
- ImageGen halo pixels were removed by thresholded alpha connected-component extraction. Reassembled sheets retain sprite positions.
- Source sheet image dimensions are 1774 × 887 pixels, so **do not claim final 300 dpi print suitability for huge placements.** Native print size and scaling need review.
- There are no new opaque rectangle underlays in this batch.
- All assets are **provisional** for placement and print approval.

The original unprocessed sheet PNGs are included in the downloadable ZIP for audit and repaint reference, but not necessary for map construction.

PNG binaries and two cleaned atlases are committed together with this manifest. Print and geographic review remain pending.
