# Crusader sprite intake — 10 November 2026

**Committed to main:** 30 rural terrain PNGs (CSV-089–118) and 14 distinct source sheet groups (19 source PNGs).

The 30 terrain composite PNGs are at `data/sprites/rural-landscapes/png/` and registered in the existing placement manifest with `ready_for_renderer: false`. The 14 historical and terrain source sheets are at `source_sheets/`, including five oversized sheets preserved as lossless top/bottom pairs under `source_sheets/parts/`. Run `python3 tools/reconstruct_crusader_source_sheets.py --output-dir OUTPUT` to reconstruct pixel-identical full sheets. See `intake_manifest.json` for per-file SHA-256, image dimensions, provenance, and offsets.

**QA pending:** Crop individual scenes, remove bright edge halos and opaque backgrounds, assess historical identities/flags, validate south-facing viewpoint and coastline/river fit, then inspect the print preview. Generic or provisional art is not approved for renderer placement.
