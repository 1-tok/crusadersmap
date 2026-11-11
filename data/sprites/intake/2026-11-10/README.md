# Crusader sprite intake — 10 November 2026

**Status: assets attached in ChatGPT; binary PNG files NOT YET pushed to GitHub.**
This branch is a staging record only. Do not treat it as an image upload or a map-placement approval.

A verified local intake package contains:

- 30 cutout terrain PNG files, `CSV-089.png` to `CSV-118.png`, for the *existing* main-branch rural landscape manifest. Expected destination: `data/sprites/rural-landscapes/png/`.
- 14 distinct raw sprite sheets, expected destination: `data/sprites/intake/2026-11-10/source_sheets/`, with sheet names and provenance in the package's `intake_manifest.json`.
- The user's two 23 MB ZIP uploads are bit-identical; use one only. Three originals in the ZIP are pixel-identical to three of the loose terrain sheets and were deduplicated in the package.

## After adding the PNGs

Copy `data/` and `tools/` from the `crusader_map_sprite_repo_ready_2026-11-10.zip` package into a checkout of this branch. Then run:

```bash
python3 tools/register_crusader_drop_2026_11_10.py --check
python3 tools/register_crusader_drop_2026_11_10.py
git add data/sprites/rural-landscapes data/sprites/intake/2026-11-10
git commit -m "Import 30 landscape sprites and 14 Crusader source sheets"
git push origin assets/intake-2026-11-10-pending-binaries
```

The script preserves existing placement coordinates and review gates and deliberately sets `ready_for_renderer: false`.

## QA rules

- Verify silhouettes and alpha edges at 100% zoom; several loose sheets have colored red/yellow/green edge contamination or opaque black backgrounds.
- Source sheets are **not** individual sprite PNGs yet; crop and catalog them before use.
- Historical building forms, identifying individual towns/castles, flags, and orientation require separate QA. Rendered architecture should not automatically be treated as an accurate named historical monument.
- Only place coastal features with matched coast-facing geometry; only place river features against a matching river reach.
- Check for collisions with historical city markers, labels, landmarks and existing art.

This record intentionally does not set asset paths in the *live* manifest while the referenced PNGs are absent.
