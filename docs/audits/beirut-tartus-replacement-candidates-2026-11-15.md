# Beirut and Tartus coastal replacement artwork — 15 November 2026

**Scope:** two corrective sprite candidates for the cumulative 1096–1600 CE Crusader Map. **Status: artwork generated locally; PNG binaries not yet ingested into GitHub**. Do not mark as uploaded, placed or production-approved.

## Candidate PNG intake
| Site | Candidate filename | Dimensions | SHA-256 | Status |
|---|---|---|---|---|
| Beirut | `beirut-coastal-review-1096-1600.png` | 875 × 703 RGBA | `e9cedb304af19f2bec69a8f19ed01396e98cc295d743087292fc27a04f6379df` | Generated; awaiting PNG intake |
| Tartus / Tortosa | `tartus-coastal-review-1096-1600.png` | 889 × 704 RGBA | `bd218e3d12871b3b3509a6517939c94bec083618d12a80ac96656d2f887d55dc` | Generated; awaiting PNG intake |

The PNGs are also packaged together with a `manifest.json` in `beirut-tartus-coastal-review-sprites.zip`, generated in the associated ChatGPT conversation. This Markdown file is **not evidence that either binary is in the repository**.

## Geography and orientation
- **Beirut:** new conceptual harbor painted toward the rear/upper-right from an elevated southern-facing camera rather than the earlier front/right-facing harbor. Verify historic north-side port geometry and shoreline attachment on the actual map; camera perspective and monumental details remain interpretive.
- **Tartus:** replacement removes the wrong river and bridge and instead represents a Mediterranean-facing Crusader/Templar waterfront, with water toward west/left and shoreline walls. Check the actual historic coastal citadel, cathedral and defensive circuit before production use.
- Both cutouts were separated from a combined illustration, with transparent RGBA alpha and basic exterior chromatic fringe cleanup. They are smaller than ideal 2048px masters and may have residual edge halos; **do not certify print quality** without inspection.
- Retain existing primary asset files as archival variants: `data/sprites/greece-egypt-1180-batch04/beirut-1180-v1.png` and `data/sprites/archive-1180/clean/archive-crs-009-tortosa.png`. Do not silently overwrite either.

## Uptake workflow
1. Upload ZIP to `assets/sprites/incoming/` and let the existing intake workflow extract/deduplicate. Match SHA-256 against the values above.
2. Link extracted files to Beirut's existing historic-core anchor `[35.505141,33.896339]` and Tartus's **approximate inherited** anchor `[35.89,34.89]`. Do not invent more precise coordinates.
3. Add review-only candidate variants to placement metadata; select one visible variant per site; retain source and historic-period provenance.
4. Render actual geographical composite. Confirm coastline-mask match, north-facing oblique camera, local harbor orientation, alpha cleanliness, collisions and print scale before choosing candidates as primaries.

This note is a review handoff, **not a production placement authorization**.
