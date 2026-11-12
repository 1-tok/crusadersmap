# ZIP sprite intake — GitHub Actions

This extends the existing `tools/sprite_intake.py` and `data/sprites/automated-intake/` architecture. It does **not** replace legacy catalog entries, the established review-layer policy, or the renderer.

## One-time repository configuration

1. Open **Settings → Actions → General**. Enable **Read and write permissions** for workflows, and **Allow GitHub Actions to create and approve pull requests** (if available to your account). The workflow asks for `contents: write` and `pull-requests: write`.
2. Keep branch protection / review rules on `main`. The importer opens a pull request; it does not merge automatically.
3. Confirm Actions are enabled and that the `Sprite intake` workflow exists after merging the setup PR.

## Routine upload (no ChatGPT Work credits)

1. Produce a ZIP containing PNG images and optional same-basename `.json` metadata sidecars. Normal `README.md`, `.csv`, and `.txt` notes are accepted but not extracted.
2. In the GitHub web UI open **assets/sprites/incoming** on **main**, select **Add file → Upload files**, drag in the ZIP, and **Commit changes**. GitHub's browser upload file-size limit applies (typically 25 MiB per file); for larger packages use an authenticated Git client or split into smaller ZIPs.
3. The push runs **Sprite intake**. Its job validates the archive, extracts PNGs into temporary working directories, calls the existing pixel-deduplicating PNG intake tool, and runs tests.
4. When generated outputs differ, the job opens or updates a PR from `automation/sprite-intake-review` against `main`. Review the diff and the workflow's `sprite-intake-report` artifact, then merge the PR using normal branch protection.

**Files committed by the bot:** only `data/sprites/automated-intake/**` and `data/sprites/catalog.json`. The original ZIP already lives on main, unchanged. ZIP extraction staging is not committed. The bot does not auto-merge, rewrite legacy assets, or assert historical approval.

## Sidecar metadata

A PNG `fortress.png` may be accompanied by `fortress.json` (same folder):

```json
{
  "subject": "Unidentified fortified settlement",
  "category": "castle",
  "status": "provisional",
  "orientation": "south",
  "target_year": 1180,
  "map_region": "main",
  "anchor_normalized": [0.5, 0.95],
  "display_width_units": 512
}
```

Use `coordinates: [longitude, latitude]` and `coordinate_source` only if the placement is identified and evidenced. Otherwise geographic placement remains blocked; the sprite remains available for art review. A verified site is required before a historical place assignment. A sheet may include explicit `sprites: [{ "box": [left, top, right, bottom], ... }]` entries in its JSON sidecar, using exclusive right/bottom pixel bounds.

The existing importer performs pixel SHA-256 deduplication, alpha and dimensions checks, category classification, and generates `manifest.json`, `placements-review.geojson`, `processing-report.json`, and PNG outputs. It does **not** independently verify historical accuracy, reject red painted flags, produce geographic coordinates from an image, or guarantee print quality. Review flags and period gating remain in force.

## ZIP safety and limits

Only root-level ZIPs under `assets/sprites/incoming/` are processed. Archives must contain 1–250 files, at least one PNG, max 35 MiB per member, max 300 MiB uncompressed, and a max 200:1 compression ratio per member. Paths with traversal, absolute paths, Windows separators, drive prefixes, or symlinks are rejected. Unknown file types are rejected. Content-name collisions are rejected and previously extracted files are not overwritten with different content.

## Troubleshooting

- **No PR created:** check the job log for `create-pull-request` permissions and the repository setting allowing workflows to create PRs. A PR is not created when generated output is unchanged.
- **Duplicate sprites:** expected when an identical pixel image was already imported; see `processing-report.json`.
- **No map placement:** expected when coordinates or coordinate evidence are missing. The output is review inventory, not production geography.
- **Failed archive:** inspect `Safely extract uploaded ZIP batches` in the workflow logs. Correct the ZIP and commit a new one with a different filename.
- **Workflow not triggered:** pushes touching `assets/sprites/incoming/**` on main trigger the job. The workflow can also be started manually.

**Important:** GitHub Actions cannot reach back into ChatGPT's internal file storage. A ZIP still needs a one-time transfer into GitHub through the browser, Git CLI, or another authorized uploader. Once uploaded, extraction, processing, QA checks, registration, and pull request creation run without ChatGPT Work credits.
