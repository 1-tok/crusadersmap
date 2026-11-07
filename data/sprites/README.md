# Crusader city and castle sprite library

Nine RGBA PNGs: eight atlas-sheet extractions and a separate Krak painting. Original uploads are retained unchanged in `sources/`. These are artistic assets, not verified reconstructions of 1180. The manifest's `period_accurate: false` means accuracy is not established, not that every feature is proven wrong.

## Use

Read `manifest.json`, resolve `asset` relative to this folder, and draw the PNG using its normalized bottom-center anchor. `placement.repo_place_id` links to the existing `places.py` catalog. Coordinates retain that catalog's approximate values and are not independently surveyed. No existing map rendering behavior is changed.

Sheet identities follow the prior chat's row order: Jerusalem, Acre, Antioch, Tripoli; Krak, Belvoir, Kerak, Montréal. The images themselves have no labels, so identities require review. Both Krak variants represent the same site and should not be placed together by default.

## Rebuild and validate

Install Pillow, NumPy and SciPy in your Python environment, then run `python3 build_sprites.py` from the repository root. This regenerates PNGs, dimensions, hashes, trim bounds, `validation.json`, and `previews/sprite-library.jpg` for comparison on light and dark backgrounds.

Extraction uses explicit source rectangles (exclusive right/bottom bounds), discards alpha values below 16/255 and detached components under 20 pixels, trims, and adds eight transparent pixels of padding. RGB is cleared where alpha is zero. No color key is used, preserving red painted flags. The report records removals and content touching source crop boundaries. Padding checks detect output-edge contact but cannot restore artwork clipped by the original canvas or prove historical accuracy. The source has tightly packed cells; sheet-edge artwork and crop boundaries merit review at larger display sizes. Keep the originals for alternative extraction settings.

## Historical review

1180 is a provisional date from the source chat, not a user-confirmed date. All entries require architectural, heraldic and repaint review. The standalone Krak is an alternate artistic composition rather than a more authoritative reconstruction. UNESCO dates Hospitaller construction from 1142 to 1271; the French Ministry of Culture describes multiple construction phases across that interval. This supports a phase-review flag, not certification of either image for 1180:

- https://whc.unesco.org/en/list/1229/
- https://archeologie.culture.gouv.fr/crac-chevaliers/fr/presentation-du-chateau

Other entries carry visual-review observations rather than independently researched architectural claims. Source hashes document provenance; user-supplied artwork is included without imposing a new repository-wide license.
