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
