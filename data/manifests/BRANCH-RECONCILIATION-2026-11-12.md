# Crusader Map — all-branch reconciliation, 12 November 2026

## Definitive current intake result

- GitHub browser uploads are **working**: original ZIP files are present in `assets/sprites/incoming/` on `main`.
- Five recent Actions runs failed *after* image extraction, registration and unit tests passed. The failure was GitHub's repository-level restriction: **"GitHub Actions is not permitted to create or approve pull requests."**
- Run 43269449847 generated commit `d17af65d8b62bee81c355bd43c7b72cf66c64ece`: **53 unique new sprites, 41 duplicate instances, zero processing errors**.
- PR #24 recovered all 53 generated PNG Git blobs and appended their records without replacing existing catalog data. The automated intake registry now held **82** records; the unified catalog **187**.
- PR #25 changed the workflow to display a prominent warning/action-summary with the permission fix rather than presenting successful PNG validation as a processing failure.
- To enable **automatic** PR creation, repository owner must visit **Settings → Actions → General → Workflow permissions → Allow GitHub Actions to create and approve pull requests**. Connected tools in this session can read permissions and create PRs but cannot change that repository-wide Actions setting.

## Branch reconciliation policy

Do not force-merge all diverged branches. Preserve unique, verified art and useful manifests without restoring obsolete catalogs, bypassing chronological rules, or mixing unrelated 1662 Dutch map imagery with the Crusader atlas. Review-only approvals are not production certifications. Do not delete archival branches.

### Successfully incorporated

- PR #16 — Greek islands batch-04 provisional placement metadata.
- PR #17 — named fortress concepts and historical/date restrictions.
- PR #18 — settlement batch-07 intake manifest.
- PR #21 — missing terrain underlay assembly workflow and tooling.
- PR #22 — four distinctive intake fortress PNGs and append-only metadata.
- PR #24 — 53 PNGs and 53 placement-review/catalog records from failing automated intake.
- PR #25 — workflow permission diagnostic and nonfatal fallback.
- Greek islands batch-05 planning metadata is already present on `main` (the branch is behind, with no remaining commits to merge).

### Already incorporated; do not merge again

These branches are fully behind `main` or have no unmatched changes: `artwork/greek-islands-batch-04-provisional`, `artwork/greek-islands-batch-05-review`, `artwork/religious-batch-14-provisional`, `assets/crusader-batch13-review-2026-11-11`, `assets/crusader-rural-landscapes-2026-11-09`, `assets/greek-islands-batch-02-2026-11-10`, `assets/greek-islands-batch-03-2026-11-10`, `assets/greek-islands-batch-03-2026-11-12`, `assets/greek-islands-batch-03-draft-2026-11-11`, `assets/greek-islands-coastline-2026-11-10`, `assets/terrain-batch05-png-upload-20261111`, `assets/terrain-batch06-20261111`, `automation/sprite-intake-pipeline-20261111`, `feature/permanent-zip-sprite-intake-2026-11-11`, `feature/sprite-upload-interface-2026-11-12`, `import/fortress-concepts-12-2026-11-11`, `import/settlement-batch07-2026-11-11`, `import/settlement-sprites-2026-11-11`, `reconcile/automated-review-four-2026-11-12`, `reconcile/queued-uploads-2026-11-12`, and `reconcile/unique-assets-2026-11-12`.

### Historical branches requiring selective review — keep, do not overwrite newer live files

- `assets/crusader-sprite-library`: older sprite PNG versions and scripts; their live counterparts exist in the newer catalog. No blind replacement.
- `assets/historical-batch-01`: older terrain proofs, island render scripts and landscape inventories; some historically useful files have no live-path equivalents, but are not validated against newer renderer.
- `assets/intake-2026-11-10-pending-binaries`: source PNG sheets and intake metadata already recovered on main; branch versions of README/manifests differ. Do not roll back.
- `assets/provisional-sprite-expansion`: older combined atlas outputs, historical scripts, gazetteers. Do not replace current build and manifests without regression test.
- `assets/terrain-batch05-20261111`: three intended files already on main; prior attempted PR #19 closed as superseded.
- `automation/sprite-intake-review`: mutable staging branch managed by GitHub Actions. Do not bulk merge its history; recover new generated PNGs and append records against current main instead.
- `build/latest-artwork-2026-11-09`: old mixed artwork tree, including `1662` sea imagery potentially belonging to the Dutch map project; audit by content and provenance before selectively recovering any Crusader-only originals. Do not merge wholesale.
- `data/map-content-manifests`: predecessor of current historical location/landscape inventories; avoid overwriting new map data.
- `terrain-assets-access-20261110`: needed assembly workflow/tools recovered in PR #21; remaining objects already present on main, branch contains divergent older history.

## Deployment and follow-up

1. Enable GitHub Actions PR creation in repository settings (administrator UI).
2. Continue uploading original ZIPs through the watched `assets/sprites/incoming/` folder. Uploading a ZIP and approving produced artwork are separate operations.
3. Monitor the Sprite intake workflow; after the setting is enabled, the bot should open a review PR. Until then, generated output is staged on the automation branch and can be recovered through an explicitly verified manual PR.
4. Never use unverified site coordinates, 1180/1250 phase-gated structures, or draft water/river alignment as automatic print approvals.
5. Periodically compare remaining diverged branches at **Git-object and pixel levels** and record provenance before importing variants. Older raw PNGs can be retained in an isolated archive only after checking whether normalized versions already exist.

This report distinguishes **completed safe merges** from **legacy branches intentionally not merged**. It is not a claim that every historical file has become an active production sprite.
