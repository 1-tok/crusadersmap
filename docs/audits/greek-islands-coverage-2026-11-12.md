# Greek Islands — coverage and intake audit (2026-11-12)

Repository: `1-tok/crusadersmap` • branch surveyed: `main`

## Findings

- **71 individually numbered PNGs committed** under `data/sprites/greek-islands/`: Batch 01 (01–12), Batch 02 (13–47), Batch 03 (48–71). Batch 03 includes alternative `_DRAFT` copies that **must not** be counted as separate island subjects.
- **38 further numbered subjects proposed** in the earlier ChatGPT conversation (72–109), covering Batches 04 and 06–11; Batch 05 also has **four unnumbered concept images**. Therefore **109 numbered subject slots**, not 109 verified or mapped islands.
- Batch 01 and Batch 02 repository READMEs mark **47 assets approved for provisional placement**; coastline/print/historical QA remains open. Batch 03 README explicitly says **24 candidate images staged, not approved for placement** and `placement.enabled=false`.
- Batch 04 and Batch 05 `README.md` and `placement_manifest.json` are committed, but no individual PNG assets are in their directories. Provisional review approval is NOT geographic placement approval.
- The following archive files **are already on `main` under `assets/sprites/incoming/`**:
  - `crusader_greek_islands_batch04_draft.zip`
  - `crusader_greek_islands_batch05_intake.zip`
  - `crusader_greek_islands_batch06_intake.zip`
  - `crusader_greek_islands_batch08_intake.zip`
  - `crusader_greek_islands_batch09_intake.zip`
  - `crusader_greek_islands_batch10_intake.zip`
- **Batch 07 and Batch 11 archive files were not found in the recursive `main` tree** at audit time. Check branch/intake history and existing downloads before requesting reupload.
- The archive files above are **unprocessed intake**, not evidence that their contained PNGs have been extracted, QA-approved, mapped, or merged into the production compositor.
- Some drafts for Batches 05–11 are visually misleading: oversized castles, inaccurate coastlines, late buildings, and/or imperfect alpha-matte removal. Maintain original drafts in a separate review/gallery queue; do not georeference arbitrary compositions over real island coastlines.

## Batch coverage and next action

| Batch | Numbered subjects | Individual PNGs on main island directory | ZIP in main incoming | Review / next action |
| --- | --- | --- | --- | --- |
| 01 | 01–12 (12) | 12 | N/A | Provisional review; validate shoreline and print |
| 02 | 13–47 (35) | 35 | N/A | Provisional review; validate shoreline and period |
| 03 | 48–71 (24) | 24 plus draft variants | N/A | Staged; resolve geographic outlines and alpha |
| 04 | 72–75 (4) | 0 | Yes | Extract archive; inspect; preserve review metadata |
| 05 | 4 *unnumbered* concepts | 0 | Yes | Extract archive; resolve repeats/identities |
| 06 | 76–79 (4) | 0 | Yes | Extract archive; repaint exaggerated architecture |
| 07 | 80–85 (6) | 0 | Not found | Locate existing ZIP, then intake and QA |
| 08 | 86–91 (6) | 0 | Yes | Extract; alpha cleanup; coastline and history QA |
| 09 | 92–97 (6) | 0 | Yes | Extract; alpha cleanup; coastline and history QA |
| 10 | 98–103 (6) | 0 | Yes | Extract; repaint excessive architecture |
| 11 | 104–109 (6) | 0 | Not found | Locate existing ZIP; QA landscapes and history |

## Safety rules for compositor

1. **Never use ZIP presence or provisional review approval as placement authorization.**
2. Register each PNG's hash and local file path; verify it represents its intended island.
3. Require valid coastline shape, geographic `render_bbox_wgs84`, orientation, and no excessive transparent/opaque fringes before setting `placement.enabled=true`.
4. Keep the user's review approval separate from `historical_qa` and `print_qa`.
5. Do not overwrite existing Batches 01–03. Preserve original drafts and rejected images with non-destructive statuses.

This report records observed files and status only; it **does not** unzip archives or alter placement flags.
