# Crusader Map — cross-chat sprite closure queue (2026-11-12)

**Scope:** Crusader Period atlas 1095–1291 (with circa-1180 review layer). **Purpose:** reconcile parallel project chats with repository evidence before commissioning duplicate sprites. **Status:** provisional audit; not a complete filesystem or print-certification pass.

## Confirmed repository status

- Fortress Batch 13: 73 individual PNG cutouts committed: four named Bourzey, Shaizar, Masyaf, Qadmus, plus 69 generic fillers. Named placements exist in `data/sprites/placements-review-1180.geojson`. Production QA outstanding. Evidence: `data/manifests/fortress-batch13-progress-2026-11-11.json` and `data/sprites/intake/2026-11-11/README.md`.
- City collection: 45 city review paintings committed, not production certified. Source/master collages remain recovery targets. Evidence: `data/manifests/SPRITE-RECONCILIATION-2026-11-11.md`.
- Greek islands: 12 original, 35 batch 02 and 24 batch 03 candidates (71 total). Batch 03 merged in PR #13, with QA holds; do not treat 71 as 71 distinct correct geographic sites or final placements.
- Terrain: 40 RGBA cutouts in Batch 06 committed; 30 rural composites registered, four rectangle underlay designs retained. Terrain Batch 05 documentation is contradictory (early import-required section versus later binary-transfer note); verify each of the 18 referenced PNG paths and SHA256 before marking complete.
- Religious Batch 14: 12 concepts documented in `data/sprites/intake/2026-11-12/religious-batch14-pending.json` with binary_present_in_repository=false at that manifest's snapshot.
- Two incoming ZIPs landed on main November 12: `assets/sprites/incoming/crusader_fortress_next_12_intake.zip` and `assets/sprites/incoming/crusader_religious_batch_14_intake.zip`, added in commits 304f169 and c1e5338. Source ZIP commit does **not** certify extracted individual files or renderer placement. No open PR found by repository PR search at audit time.

## Priority 0 — process new uploads

1. Run/check `.github/workflows/sprite-intake.yml` against both incoming ZIPs. Verify workflow success, processed report, extracted file list, hash/dedup report and whether review PR was created. If no PR, inspect Action permissions and run logs; do not claim extraction is complete.
2. Match fortress ZIP contents by identity to Darbsak (CP-065), Feke (CP-076), Jacob's Ford (CP-035), Kızkalesi (CP-077). Preserve the accepted elevated oblique view *from the south*. Create review placements only with verified identity, asset path and existing geographical anchors.
3. Chastellet/ Jacob's Ford standing fort was destroyed in 1179: use ruins in 1180; standing reconstruction only in a 1178–1179 phase.
4. Kızkalesi must be a small **offshore** castle, not a shore-attached town. Repaint if supplied ZIP retains the old design.
5. Extract and QA the 12 religious concepts, keeping their candidate identities unverified. Hagia Sophia candidate has later minarets and must be repainted/excluded for circa 1180.

## Priority 1 — conditional missing named artwork

- Darbsak, Feke, Jacob's Ford and Kızkalesi: **await binary intake inspection**, not automatically unpainted; the accepted batch may already provide the needed art.
- Buffavento, Kantara, Kolossi, Chlemoutsi: inspect all branches/catalogs for dedicated sprite and phase suitability before commissioning.
- Harim: only make a separate fortress if the existing city treatment cannot represent it.
- Do **not** re-commission Bourzey, Shaizar, Masyaf, Qadmus, Safed or Bagras without a specific QA defect.

## Priority 2 — recovery, QA and rendering

- Verify 13 older missing source sheets from Nov 10 intake and 35 transparent redo-03 terrain binaries against subsequent commits; deduplicate before uploading.
- Verify Terrain Batch 05 18 files by physical path+checksum. Batch 06 40 files are already documented as committed.
- Restore 45 city master/source sheets for high-resolution rework if needed; do not mistake these for 45 absent review sprites.
- Integrate city, island, fortress, terrain and religious *approved review* manifests into compositing pipeline, while keeping production approval separate. Preserve alpha, clipping, coastline and river alignment, the four underlay designs, and year/phase gates.
- Print review: inspect native pixel size versus intended physical output; 300-DPI enlargement cannot manufacture detail. Put labels above artwork.
- Exclude obsolete star-fort filler `map_fillers_set_a-010.png`, non-period fortifications, and unrelated 1662 Dutch-map assets.

## Closure criteria

Every required site or terrain family needs: unique site ID, source/master path, actual RGBA PNG path (verified to exist), asset hash, phase/date gate, reference coordinate/geometry, viewer orientation, transparent-edge QA, historical QA, placement-review flag, and production/print approval flag. Use distinct states `missing_binary`, `awaiting_intake`, `provisional_review`, `repaint_required`, `production_approved`.

Do not update counts based solely on historical manifest text: check actual HEAD and source ZIP processing on each reconciliation.

## Intake verification addendum — 12 November 2026 (after PR #14 and PR #15)

**This addendum supersedes the earlier `await binary intake inspection` statuses above.** GitHub main now includes `data/sprites/automated-intake/processing-report.json` and `data/sprites/automated-intake/manifest.json`. The report records 12 unique fortress PNG imports requiring placement review, 12 duplicate copies of those fortress files, 12 provisional religious PNG imports, and one source collage. The 25 distinct manifest records have technical PNG QA status `pass`; this does **not** certify site identity, geography, period, composition or print suitability.

| Subject | Imported PNG | Next gate |
|---|---|---|
| Chastellet / Jacob's Ford | `data/sprites/automated-intake/png/chastellet-jacob-s-ford-6b5a1ae89a82.png` | Verify ruins variant for 1180, standing only 1178–79 |
| Darbsak | `data/sprites/automated-intake/png/darbsak-30eaae615a8d.png` | historical/geographic placement review |
| Feke | `data/sprites/automated-intake/png/feke-vahka-9222ed7f72b9.png` | historical/geographic placement review |
| Kızkalesi | `data/sprites/automated-intake/png/k-zkalesi-afb58e1ddd84.png` | verify offshore castle silhouette; repaint if oversized shore-attached city |
| Buffavento | `data/sprites/automated-intake/png/buffavento-eb686a366b52.png` | Cyprus ridge and construction-phase review |
| Kantara | `data/sprites/automated-intake/png/kantara-21cdd6fda271.png` | Cyprus ridge and construction-phase review |
| Kolossi | `data/sprites/automated-intake/png/kolossi-2cad1dc9839e.png` | exclude later tower forms from 1180 |
| Chlemoutsi | `data/sprites/automated-intake/png/chlemoutsi-clermont-a7440d538d45.png` | built after 1180; later-period map only |
| Bourzey, Shaizar, Masyaf, Qadmus | imported second variants in automated intake | compare with already committed Batch 13 artwork, avoid duplicates |

The 12 religious candidates are present in `data/sprites/automated-intake/manifest.json`; their old `religious-batch14-pending.json` metadata is a **prior snapshot**, not current binary availability. Imported religious records have `category: unclassified` and `coordinates: null`: classify and identify first, before geographic placement. Hagia Sophia retains repaint-required later-minaret warning. Generic religious concepts remain unplaced.

**Blocking finding:** all 25 imported manifest entries have `coordinates: null`. The processing tool correctly did not invent coordinates. Do not mark these automatically placed or production approved. Next work is conservative matching to existing `places.py` / source gazetteer anchors, phase filtering, historical visual QA, and review-only placement records.

Recent main commits: automated intake `0b7f1aff`; religious PR merges `77d8812e` and `404732d1`.

## Geographic candidate staging — 12 November 2026

New **non-rendering** candidate FeatureCollection: `data/sprites/placements-intake-fortress-candidates-2026-11-12.geojson`, committed as `1368b3a9`. Reused original `CP-` coordinates from `data/manifests/crusader-period/site-history.json` for eight imported fortress candidates (Chastellet/Jacob's Ford, Darbsak, Feke, Kızkalesi, Buffavento, Kantara, Kolossi, Chlemoutsi). Every candidate has `approval_for_review_placement=false`, `default_visible=false`, `candidate_only=true`, and `production_approved=false`. These are geographic research anchors, not claims that the artwork depicts the site accurately.

Darbsak and Feke are tagged with a proposed 1180 review phase; Chastellet has 1179 standing-only; Kızkalesi, Buffavento, Kantara, Kolossi and Chlemoutsi receive **later-period review placeholders**, not historical construction-date certifications. Kızkalesi offshore depiction and Kolossi's later surviving tower require particular scrutiny. Unclassified religious Batch 14 sprites remain without coordinates; do not guess identities.

**Next action:** manually inspect the eight individual PNGs, correct historical architectural errors, then explicitly approve chosen visual-review placements without promoting them to production rendering. Do not duplicate the four fortress Batch 13 images already placed on review layers.
