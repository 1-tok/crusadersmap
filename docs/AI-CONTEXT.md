# Crusader Map — active AI context and documentation index
_Consolidated 2026-11-13. Applies to the current repository; historical reports below retain their original dates and meanings._

## Read this first / authority order
1. Latest explicit project-owner instruction, when compatible with known facts and safety, overrides an earlier instruction on the **same issue**. A later instruction does not silently change unrelated requirements.
2. This index expresses the reconciled workflow. [Final map readiness](FINAL-MAP-BUILD-READINESS.md) controls assembly and evidence of actual placement. [ZIP intake](SPRITE-ZIP-INTAKE.md) and [incoming folder instructions](../assets/sprites/incoming/README.md) control new upload processing. [Review placement policy](../data/sprites/REVIEW-PLACEMENT-POLICY.md) controls preview status, subject to the coordinate/date conditions below.
3. Machine-readable manifests, actual PNG files, branch HEAD and successful job outputs establish **what exists**; older status prose is a dated snapshot, not live evidence. If text and machine state disagree, inspect and report the discrepancy rather than silently guessing.
4. Older audit/README/batch notes remain provenance. Do not interpret an older date or a historic archival label as a current command. Record unresolved ambiguities instead of fabricating resolution.

## Project identity and historical periods
- Atlas coverage: Eastern Mediterranean Crusader-era through the early modern period, **1095–1571**. Print format is 36 × 48 in portrait, 300 dpi (10800 × 14400 px), main Levant/Cyprus geography with Aegean and Egypt/Sinai insets.
- **Circa 1180 is the default historical review snapshot**, *not* the full multi-period atlas. Later phases are separate dated layers/editions. Do not depict post-1180 construction in an 1180 snapshot.
- Chastellet/Jacob's Ford: standing fort destroyed in 1179; 1180 depiction requires ruins, not standing fort. Montfort: construction from 1226; Château Pèlerin: from 1218. Neither appears as a completed castle in 1180. Chlemoutsi and the later surviving Kolossi tower likewise fail an 1180 gate.
- Owner's later instruction to show Montfort/Château Pèlerin as completed fortresses is a **stylistic/phase request for a later-period edition**, not a historically valid 1180 depiction. Keep dated artwork rather than falsifying the 1180 layer. Uncertain painted phase must be flagged for verification.

## Rendering and artwork invariants
- Viewed from the **south looking north**: elevated oblique, consistent top-and-south-side view; cities/castles need the same perspective. Coastline/sea must appear on the geographically correct side after the sprite is positioned on the map; no blanket left/right rule across differently oriented shores.
- Art should resemble existing Crusader Map paintings, not Dutch-map or other project artwork. Individual cuttable RGBA PNG sprites with transparent backgrounds; preserve original high-resolution sources and don't replace with low-resolution upscales. A sheet is only a source until properly separated.
- Prefer existing dedicated artwork for a named settlement; before repainting, examine inventory, prior branches, variants, period and visual defects. One visible primary depiction per named place per year/view, but retain alternatives for review.
- Generic terrain and large underlays fill only geographically appropriate land; clip to land, rivers, shoreline, roads, city positions and insets. Never invent watercourses, islands, settlements or site coordinates to fill gaps.
- Rendering order: geographic basemap → four rectangular gap underlays → natural/farming terrain → aligned coastline/rivers/islands → named settlements and fortresses → appropriate local generic accents → water-only decoration → clear labels, roads, borders and annotations on top.
- Prioritize **integrating existing imagery and proving map coverage** before commissioning more art. See [lowland terrain priorities](TERRAIN-FARMING-LOWLAND-PRIORITIES-2026-11-12.md) for Nile Delta, Sharon/Acre, Cilicia, Greek lowlands, Cyprus and transition zones.

## Mandatory POV and coastal-water orientation — 13 November 2026

**NORTH-FACING POV is a hard acceptance requirement for every new or revised city, castle, port, island settlement and coastal terrain sprite.** This means the **observer/camera stands south of the subject and looks north**, from a consistent elevated oblique angle. It does **not** mean viewing the north-facing wall from the north or looking south. Do not switch viewpoints between assets to make the water easier to draw.

For an unrotated north-up map and an unmirrored north-facing sprite:
- **Top/background = north**, **bottom/foreground = south**; **image left = west**, **image right = east**.
- **Sea west of the site** (e.g., many eastern Mediterranean mainland shoreline sites): paint water on **image left**. **Sea east of the site**: paint water on **image right**. **Sea north**: water behind the subject; **sea south**: water in the foreground. For bays, peninsulas, offshore castles and islands, trace the actual shoreline shape and multiple water-facing sides rather than imposing a single side.
- Placement must follow the site's **real coastal geometry and the map projection**, not a convenient painterly composition. Do not flip/mirror or rotate a finished sprite merely to fix a wrong water side: this also reverses architecture, shadows, gates or landmarks. Repaint/re-compose with the same south-to-north viewpoint instead.
- Inland sites must **not** contain invented sea, harbors, offshore water or rivers; rivers/wetlands must align with actual hydrography, and shore-only water must be clipped to the coastline.
- Record `camera_position: south`, `camera_looks_toward: north`, `north_up: true`, the site's actual `water_bearings` (subset of N/E/S/W, or a shoreline geometry reference), and `coast_orientation_qa: pass|repaint_required|not_applicable|unverified` in new review metadata when supported. Existing schemas should be extended deliberately rather than introducing unsupported fields that would break intake.
- Before approving placement, check named-site longitude/latitude against coastline; compare the PNG silhouette, visible shore and compass bearings; inspect the **full geographic composite**, including Aegean/Egypt inset transforms. Flag mismatches as `repaint_required` and do not mark print approved. A visually convincing castle with the sea on the wrong side fails placement QA.

**Reference decision:** the later owner instruction explicitly prioritizes north-facing POV **so coastal water faces the correct side on the assembled map**. This paragraph supersedes vague earlier "side view", "orientation: south" or generic oblique wording wherever ambiguity exists. `orientation: south` in older sidecars means **camera located south, looking north**, never camera looking south.

## Four distinct states — never collapse them
1. **Source uploaded:** source ZIP/PNG exists under `assets/sprites/incoming/`; does not prove extraction.
2. **Technical intake passed:** individual PNG verified, deduplicated and registered; does not prove historical identity, geographic coordinates, placement or print quality.
3. **Review map placement:** identifiable subject, evidenced geographic anchor, compatible year and reviewed image selected; preview-visible, with review/repaint warnings. General authorization to *review artwork* does not override missing coordinates or a blocked candidate flag.
4. **Production/print approved:** separate historical, alpha-edge, native-resolution, positional, collision and full-composite QA gate. Must not be inferred from any earlier state.

If a review GeoJSON has null geometry or `candidate_only=true` / `approval_for_review_placement=false`, keep it in gallery or staging, not a geographically positioned map layer. A file existing on GitHub does not establish actual placement. Never describe a sprite-only grid/diagnostic as the full composed geographic atlas.

## Upload and approval — current path
- Upload source ZIP or PNG via [GitHub incoming folder](../assets/sprites/incoming/README.md). The **source alone** lands on `main`.
- GitHub Actions validates/extracts, makes technical reports, and opens/updates a **review PR** for `data/sprites/automated-intake/**` and `data/sprites/catalog.json`. Review then merge, without auto-merging or assigning historical approval. [ZIP specification](SPRITE-ZIP-INTAKE.md).
- Older [SPRITE-INTAKE.md](SPRITE-INTAKE.md) originally described automatic output commits to main; that flow is superseded by PR review. It remains as a compatibility guide, not authority for bypassing PR review.
- ChatGPT image attachments cannot be automatically fetched from a chat into GitHub by a GitHub Action. Upload through an authenticated binary-capable channel.

## Operational reading route
| When working on… | Read in this order |
|---|---|
| New agent / overall project | This file → [root README](../README.md) → [final build readiness](FINAL-MAP-BUILD-READINESS.md) |
| ZIP/PNG ingestion | [incoming folder](../assets/sprites/incoming/README.md) → [ZIP intake](SPRITE-ZIP-INTAKE.md) → [intake closure audit](../data/manifests/SPRITE-CLOSURE-QUEUE-2026-11-12.md) |
| Geographic site placement | [review placement policy](../data/sprites/REVIEW-PLACEMENT-POLICY.md) → [provisional usage](../data/sprites/PROVISIONAL-USAGE.md) → [site history](../data/manifests/crusader-period/site-history.json) → placement GeoJSON |
| Full composite / print QA | [final build readiness](FINAL-MAP-BUILD-READINESS.md) → [terrain priorities](TERRAIN-FARMING-LOWLAND-PRIORITIES-2026-11-12.md) → QA reports |
| Coverage / missing artwork | [sprite closure queue](../data/manifests/SPRITE-CLOSURE-QUEUE-2026-11-12.md) **including its latest addenda** → [manifests README](../data/manifests/README.md) → current catalog and filesystem |

## Resolved instruction conflicts (2026-11-13)
| Earlier wording / conflict | Current interpretation |
|---|---|
| `docs/SPRITE-INTAKE.md`: workflow pushes processed catalog directly to main | Newer ZIP workflow: outputs go to PR for review; only original uploaded source is committed directly to main |
| Every draft 'approved for visual placement' | Art may be browsed in review gallery; geographic map placement still needs coordinates, year gate and candidate approval |
| 'All artwork approved' / 'sprite uploaded' / 'map complete' conflated | Source, technical intake, review placement, production and actual composite use are separate verified states |
| 1180 as a map-wide default versus full atlas 1095–1571 | 1180 for review snapshot; 1095–1571 for dated multi-period atlas |
| Early missing fortress and religious batch records versus later Nov 12 ingestion | The **addendum** in `SPRITE-CLOSURE-QUEUE-2026-11-12.md` supersedes the earlier awaiting-intake statements; still do not claim map placement |
| Historical-looking completed Montfort/Château Pèlerin requested for 1180 | Preserve historical construction-date gates; completed depiction belongs only to a researched later phase |
| Numerous image requests versus current build handoff | Final composite placement, terrain gap measurement and QA have priority before generating new duplicates |

## Live verification checklist
1. Check `main` HEAD, current files, incoming ZIPs, completed Actions and merged PRs; do not trust older counts blindly.
2. Verify each manifest path exists and matches its actual source/image hash. Review duplicates and historical QA flags.
3. Select correct year, site ID, WGS84 anchor and projection/inset; preserve alternate versions without double placing.
4. Render the **full geographic** composite; capture used PNG IDs and crops plus missing/flat areas, collisions and QA holds.
5. Report the difference between present, intake-passed, eligible, visibly placed and print-approved. Never claim success without render/artifact evidence.

## Remaining uncertainties
This consolidation is a documentation reconciliation, **not** proof all repository Markdown has been exhaustively inspected, all date claims historically validated, or every legacy renderer is updated. Remaining data-specific disagreements must be logged with a source path and evidence before changing art or geography. Do not delete historic audit notes merely for contradicting a newer status.
