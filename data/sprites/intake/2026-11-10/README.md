# Crusader sprite intake — 10 November 2026

**Uploaded:** 30 CSV terrain PNGs plus 14 full-resolution source sheet groups (19 PNG files). All binary assets are committed to this branch.

- Rural PNGs: `data/sprites/rural-landscapes/png/CSV-089.png` through `CSV-118.png`.
- Nine whole source PNGs: `source_sheets/*.png` (some repacked with lossless PNG compression).
- Five other source sheets: ten lossless top/bottom PNGs in `source_sheets/parts/`. Use `python3 tools/reconstruct_crusader_source_sheets.py --output-dir OUTPUT` to rebuild pixel-identical full sheets.
- See `intake_manifest.json` for original hashes, image dimensions, part offsets and QA states.

**Not approved for renderer/map placement:** all source sheets still need individual cropping, alpha/halo cleanup, historical-identification checks and southern point-of-view verification. Existing terrain placement study coordinates and review gates remain intact; their PNG paths are registered while `ready_for_renderer` remains false.
