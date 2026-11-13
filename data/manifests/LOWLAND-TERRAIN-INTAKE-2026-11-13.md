# Crusader Map — November 13 lowland terrain intake closure

## Verified repository intake, as of 2026-11-13

The source ZIPs `assets/sprites/incoming/crusader_lowlands_part1_large_2026_11_13.zip` (5 large RGBA PNGs) and `assets/sprites/incoming/crusader_lowlands_batch10_11_2026_11_13.zip` (27 standalone PNGs plus 2 source master sheets) are present on main. The automated processing report includes **34 source-image entries** for those archives, including the two reference masters. The 32 individual candidate sprites were processed and deduplicated; report statuses of `duplicate` indicate prior registration rather than absence. Production approval and actual map placement are NOT implied.

The intake script now ignores master PNGs in archives that also contain standalone cutouts; masters already imported in older registries must remain **source-only, never map-placed**, pending a separate safe cleanup. The fix and its regression test were committed on 2026-11-13.

## Still awaiting ZIP transfer

The 51 separate candidate cutouts from sheets 06–09 of `crusader_lowlands_complete_2026_11_13.zip` have not been verified in the repository intake. A dedicated nonduplicating archive was prepared:

- ZIP: `crusader_lowlands_13nov_remaining_51_ONLY.zip`
- ZIP SHA-256: `a437536bfa7a087f3db5e5b5608aa85c460290f9c76cd7ccfc899e1f3a290708`
- ZIP bytes: 14,233,954 (under 20 MB)
- 51 PNG images, each paired with a same-basename JSON sidecar; 102 ZIP members total
- Source groups: 06 = 12, 07 = 12, 08 = 15, 09 = 12
- No original master/contact sheets
- PNG SHA-256 verified against the previous manifest; archive CRC check passed

**Upload exactly this archive to `assets/sprites/incoming/` on main.** On push, `.github/workflows/sprite-intake.yml` processes the ZIP and updates `automation/sprite-intake-review` or opens a review PR. Do not duplicate uploads of Part 1 or Batch 10–11.

## Geographic and visual review policy

- Target areas: Nile Delta; Greek/Aegean lowlands; Cyprus agricultural plains; Cilician/Anatolian fields; Palestine and Levant coastal plains.
- Upload/PNG intake is not map placement; the new 51 sprites carry provisional status and no fabricated lat/lon.
- Source masters and unsplit sheets may not be drawn as map sprites.
- All rivers, reedbeds, marshes, canals, and seaward edges require geographic water/shore alignment and southern-oblique orientation QA before placement. Do not scatter them as general farmland.
- Dry field/orchard cutouts may become region-masked generic land pieces only after visual QA and duplication/scale checks, below settlements, roads, geographic waterways, and labels.
- Historical and 300-DPI print approvals remain false.
- After import review, regenerate the full atlas and measure actual rendered sprite usage, overlap and terrain gaps.

## Follow-up checkpoint — verified 13 November

- GitHub PR #32 merged into `main`; the current intake report contains **34** entries for the two existing November 13 source archives (5 large, 27 cutouts, 2 masters). These remain provisional. The 51 additional cutouts are not in current processing-report entries, and their ZIP is not in `assets/sprites/incoming`.
- The initially prepared 51-cutout ZIP had a sidecar error: all 51 pieces were assigned `map_region: delta`. **DO NOT upload that superseded ZIP.**
- Corrected ZIP (exact PNG bytes preserved): `crusader_lowlands_13nov_remaining_51_REGION_QA.zip`, SHA-256 `d48c93c2e5ebaf6917412cd36f1ab0305555cc8834652c905816214980902e06`, 14,238,995 bytes, 51 PNGs and 51 JSON sidecars, CRC verified.
- Corrected region gates: group 06 (12 cutouts) stays `delta`; group 07 (12), group 08 (15), group 09 (12) are `review_unassigned`, with appropriate candidate-region hints rather than a false Delta assignment.
- All 51 remain `placement_review_required: true`, `approval_for_placement: false`, `production_approved: false`; existing water and shoreline holds preserved.
- Once corrected ZIP is pushed to the incoming folder, check the workflow's resulting PR/review branch, merge *only after verifying source counts and no master-sheet placements*, then inspect a new compositor run. No sprite is shown on a map just because a ZIP or registry record exists.

Prior instructions calling for upload of `crusader_lowlands_13nov_remaining_51_ONLY.zip` are superseded by this correction.
