# Original city-source masters — recovery intake

**Status: awaiting binary upload.** This metadata-only commit does **not** assert that the ZIP or the five source PNGs are in GitHub.

The city review manifest already indexes **45 individual city review PNGs**, nine in each of five batches (07–11). These existing sprites must not be overwritten, duplicated, or implicitly marked print-ready.

## Single-file recovery artifact

Archive name: `crusadersmap_five_city_source_sheets_recovery.zip`

Expected archive SHA-256: `9b2ec7707d3b1800278e035a7cb9ec3c0cc495a970793fbe7c615e3fe11d6c47`

Expected archive size: **16,113,543 bytes**. Contains five RGBA PNG master sheets, a JSON recovery manifest, and a README. Each sheet is 1254 × 1254 pixels, in a 3 × 3 layout (nine paintings each).

| Batch | Proposed source file in ZIP | SHA-256 |
|---|---|---|
| 07 — Levant / Galilee | `source_sheets/batch-07-levant-galilee-source-sheet.png` | `5c9db1a36d763a6f1b4a7c59543414abd041563c35b061260f2d6b8771c23ddb` |
| 08 — Syria | `source_sheets/batch-08-syria-source-sheet.png` | `cd3f0a32e31da14cb837d72ebd7acfe0b8f05ca919959fedab4584c10e409c24` |
| 09 — Cilicia / Cyprus | `source_sheets/batch-09-cilicia-cyprus-source-sheet.png` | `a07a7b5595525c6b0847f84536480fc2ed424e0bf89c0fd10340822126443dec` |
| 10 — Aegean | `source_sheets/batch-10-aegean-1-source-sheet.png` | `43f28edde3dd51b910652535d57e5bb3cafdf8f6084ad0c8a86f32e00efcfae9` |
| 11 — Aegean / Egypt | `source_sheets/batch-11-aegean-egypt-source-sheet.png` | `6288e8817577ef1bf1f303d27488810d750d4131bb8fd850f3954275d3534032` |

## Binary intake instructions

1. Upload the recovery ZIP **unchanged** as `data/sprites/city-review-2026-11-10/source_sheets/crusadersmap_five_city_source_sheets_recovery.zip` to the `recovery/city-masters-nov13-2026` branch. It is below GitHub's usual browser-upload file limit.
2. Verify archive SHA-256 and each extracted PNG against the table before merging.
3. Preserve the original ZIP as a **non-rendered source-master archive**. Do **not** put this source-only archive in `assets/sprites/incoming/` because the generic sprite intake treats un-split PNG sheets as provisional sprite candidates.
4. Keep existing 45 cutouts and their approved *review* placements unchanged. The supplied source-sheet-to-batch mapping is inferred from image order and thematic grouping, **not pixel-verified** against the 45 derived cutouts.
5. After binary presence and checksums pass, merge the recovery PR to `main`. Do not mark historical fidelity, period accuracy, southern POV, coastline-water side, alpha-edge quality, or 300-dpi print readiness approved solely by this recovery.

These five masters are source references, not five standalone geographical sprites.
