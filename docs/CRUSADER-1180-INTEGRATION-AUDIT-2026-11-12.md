# Crusader Map — 1180 integration and remaining-gap audit (12 November 2026)

**Status:** Repository-static audit + browser diagnostic prepared. **Not** a new raster print render or a bytewise verification of all repository image files. No paintings commissioned.

## Deliverables
- [147-site audit and gap register](../data/manifests/crusader-1180-integration-audit-2026-11-12.json)
- [Interactive composition diagnostic](../previews/1180-integration-diagnostic.html) — download/open in a browser with network access. Base colour map and 59 standard sprite registrations are enabled by default; 10 explicitly 1180-dated and 43 undated review selections are separate toggles. The diagnostic loads original image paths over HTTPS and is **not** a final raster or validated build.
- Existing [1180 standalone sprite overlay](../previews/sprite-layer-1180.svg) (89 MB) and [gridded placement diagnostic](../previews/sprite-placement-1180.jpg).

## Geographic audit
- Actual frame: 36 × 48 inches, 10,800 × 14,400 px at 300 DPI, Lambert Conformal Conic. Main frame projected bounds: X −486,000 to 170,000 m, Y −345,000 to 530,000 m.
- Aegean inset longitude/latitude reference range 19.6–30.4 E, 34.7–41.75 N; Egypt/Sinai inset 29.5–35.2 E, 27.7–31.8 N.
- **147/147** historical gazetteer anchors fall within their assigned main frame/inset, as do **59/59** standard 1180 placement records, **58/58** review records, and **8/8** staged fortress candidates. This is a center-point check, **not** proof that a 512-pixel sprite footprint is fully visible or avoids overlaps.
- New Euphrates subjects in fortress Batch 19 were not part of these repository layers; they remain an out-of-frame expansion reserve, not map placement candidates.

## Counts — distinct populations, not additive
| Inventory | Count | Meaning |
|---|---:|---|
| Historical gazetteer sites | 147 | all inside assigned map/inset |
| Standard placements for 1180 | 59 | records currently in `placements-1180.geojson` and eligible for standard sprite-layer renderer |
| Review placement records | 58 | records in `placements-review-1180.geojson` |
| Review records selected by renderer | 53 | `approval_for_review_placement && default_visible`; 10 explicitly dated 1180; **43 lack a literal 1180 depiction_year**, requiring historical gating before use |
| Staged fortress candidates | 8 | separately stored; **not read by the review renderer** unless promoted to review manifest |
| Automated intake | 226 | technical PNG QA passed, **226 missing coordinates** and **0 geographic placement-ready**, so auto-placement is blocked |

## Rendering reality
1. `render_sprite_layer.py` handles standard placements and optional `--review` selections. It writes a **standalone** `previews/sprite-layer-1180.svg` and diagnostic JPEG, not a finished terrain/labels/ink composition.
2. `make_print.py`, `make_svg.py` and `assemble_svg.py` build their own output using base and ink. They do **not** explicitly import the sprite overlay; the current print is **not verified to contain the 59 + 53 artworks**.
3. The current preview HTML is a *visual diagnostic* that references the map and sprites from GitHub; the resulting remote images have not been independently rendered/tested in this audit.
4. The review renderer tests approval/default visibility, **not** `depiction_year==1180`; fix this before drawing the review-only layer for a strict 1180 print.
5. Some politico-historical labels in `build_stage2.py` belong to later dates (e.g. Kingdom of Cyprus since 1192, Empire of Nicaea/Latin Empire since 1204). The print pipeline needs a year-gated political label pass.

## Priority gap register
The JSON includes every historical site with matched standard/review/candidate assets or an **unmatched** flag. The matching uses explicit CP IDs or a conservative name-and-coordinate check, and therefore some sites with different names may still be unmatched despite assets being present. It is a work queue, **not** a claim that every unmatched site requires a new painting.

1. **P0 — date gate:** exclude later construction (Atlit 1218, Montfort 1226, Ajloun begun 1184, Chlemoutsi 1220s, Kolossi surviving tower 15th c.). Display Jacob's Ford as ruins after 1179, not the standing 1178–79 Chastellet.
2. **P0 — renderer integration:** choose one variant per site, unify the standard and review manifests, validate actual image paths, place sprites between appropriate terrain and label layers, and rebuild a **new** 1180 map.
3. **P0 — coordinate reconciliation:** assign evidence-backed coordinates/geometry only to named assets. The 226 intake files cannot be treated as mapped; many terrain fillers need region/polygon masks rather than single point coordinates.
4. **P1 — visual QA:** alpha fringes, native DPI, southern oblique orientation, shoreline direction (offshore Kızkalesi), buildings and monuments, cliff/river alignment, clipping, label occlusion.
5. **P1 — source recovery:** compare repo intake and source sheets with hashed cutouts, particularly older terrain Batch 05 and city master images; preserve original files and reject duplicate site variants.
6. **P2 — print:** proof a whole-map composite at preview resolution, inspect 1180 political labels and 36 × 48 output, then export and inspect the high-resolution print separately.

### Example unmatched site anchors (not confirmed missing artwork)
Shobak, Petra, Deir al-Balah, Tell es-Safi, Yavne, Latrun, Nabi Samwil, Mount Tabor, Sebastia, Cana, Gerasa. Natural locations may need symbols instead of castle paintings; some major settlements have assets recorded under alternate names.

### Acceptance gates
- **Geographic:** center and full footprint inside designated frame/inset; precise coast/river alignment.
- **Asset:** verified file path, SHA256 and alpha/print QA.
- **Historical:** explicit 1180 phase and correct polity; excluded later forms.
- **Rendering:** visual proof the final composite includes the chosen artwork once, no occlusion problems.
- **Approval:** review display is not final historical or print approval.

**Recommended next command in a proper working checkout:** `python3 sprite_catalog.py --year 1180 && python3 render_sprite_layer.py --year 1180`; this regenerates the standard overlay, **not** the final integrated print. A new composer step and strict review-year selector are needed for the complete build.
