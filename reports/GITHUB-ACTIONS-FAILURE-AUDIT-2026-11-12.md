# GitHub Actions failure audit — 12 November 2026

**Scope:** All 43 workflow runs returned by the GitHub Actions API at audit time, including 18 historical failures. The red historical runs cannot be changed retroactively. This file distinguishes current workflow status from past failures.

## Failure categories

| Workflow | Historical failed runs | Root causes | Remediation |
|---|---:|---|---|
| Sprite intake | 8 in the initial 43-run snapshot | Six older runs attempted to create PRs using an Actions token without repository permission; two recent runs rejected `crusader_map_location_underlays_1180_2026-11-12.zip` because it bundled `build_location_underlays.py`, SVGs and no PNGs | PR creation was already `continue-on-error` with user-facing explanation in the workflow; intake now quarantines unsupported archive payloads and skips source-only archives with warnings, while keeping malicious path/member size/zip bomb checks |
| Rebuild latest Crusader map composite | 6 | Missing `scikit-image`, introduced invalid Python source in `placer.py`, concurrent `main` pushes rejected | Dependency and source fixed, retry-safe push implemented; run 43318873172 succeeded |
| Review map diagnostic preview | 2 | SyntaxError in `render_sprite_layer.py` | Parenthesis corrected; follow-up discovered/solved `tools/audit_review_map.py` import path. Run 43341598740 succeeded |
| 1180 integrated sprite proof | 1 | Root module not on Python import path | Fixed in `tools/render_1180_integrated_proof.py`; later full proof succeeded |
| Greek islands geographic review | 1 | Root module not on Python import path | Fixed in `tools/greek_islands_review.py`; run 43340257254 succeeded |

## Actions taken in the present audit

- Corrected the missing closing parenthesis in `render_sprite_layer.py`.
- Corrected root import path in `tools/audit_review_map.py`.
- Adjusted `tools/sprite_zip_intake.py` so unsupported files inside mixed ZIPs are **never extracted** (including scripts or SVGs), but valid PNGs remain importable. Path traversal, symlinks, member count, file size, compression-ratio and archive-size guards still fail unsafe archives.
- Source-only archives without PNGs are preserved and reported as skipped; no underlay scripts or SVGs are silently executed or treated as PNGs.
- Added tests for quarantining Python+SVG alongside a valid PNG and for skipping source-only ZIPs.
- Updated `.github/workflows/sprite-intake.yml` to run upon ingestion code/test changes, not just uploaded files.

## Follow-up and permission issue

The `Sprite intake` workflow's PR-creation step is `continue-on-error`, and failures receive a warning with a manual review-PR URL. To allow its GitHub Actions token to **open a PR automatically**, an administrator must enable:

**Settings → Actions → General → Allow GitHub Actions to create and approve pull requests**.

This setting is outside source-code permissions and has not been changed in this audit. Alternatively open a review PR manually from `automation/sprite-intake-review`. Do not auto-merge without historical/geographic QA.

## Useful links

- [GitHub Actions](https://github.com/1-tok/crusadersmap/actions)
- [Latest map rebuild success](https://github.com/1-tok/crusadersmap/actions/runs/43318873172)
- [Greek island review success](https://github.com/1-tok/crusadersmap/actions/runs/43340257254)
- [Review map diagnostic success](https://github.com/1-tok/crusadersmap/actions/runs/43341598740)
- [Intake workflow](https://github.com/1-tok/crusadersmap/actions/workflows/sprite-intake.yml)

**Note:** A successful intake job confirms processing and tests, not historical approval or that new sprites have reached the map render.
