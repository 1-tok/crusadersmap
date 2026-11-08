# Crusader Period · 1095–1291

This is the current period-specific occupation and siege edition. The user selected 1095–1291 rather than the older 1095–1571 atlas scope. Mainland Crusader sites are the focus; the Aegean and Egypt/Sinai provide geographic context.

All 147 source sites have stable CP identifiers, geographic anchors, an occupation/holding field, a siege field, source links and review notes. Each entry distinguishes selected dated occupations or attestations, regional dynastic context, religious presence, landscape markers and later holdings outside the chosen period. A dated attestation is not treated as proof of continuous control. Construction, possession, shared rule, raids and sieges are distinct concepts.

The index records selected sieges/campaigns at 39 sites. It does not claim every siege in two centuries has been found. “No siege recorded in this index” means a record is absent, not that no siege occurred. Some events have year-only precision or disputed campaign/conquest dates; their notes retain this. Multiple campaigns separated by semicolons are not one continuous siege. A few rapid captures appear in the inherited siege catalog and are identified accordingly.

The occupation field also remains selective. Many local transitions, exact tenure endpoints and inherited chronology claims require further review. Regional and monastic context is explicitly named and is not evidence for a continuous local military occupation. “No missing dated record” does not mean all histories are fully verified. The complete original PLACES/BATTLES catalogs remain unchanged as provenance.

Montfort and Château Pèlerin now fall within this cumulative period edition, with construction dates in their titles and dated occupation/siege records. Their separate circa-1180 availability restrictions remain intact. Bodrum’s Hospitaller castle and Arwad’s cataloged Templar holding fall after 1291: they remain grey geographic cross-references in the source-site index, with explicit outside-period titles, and are excluded as active holdings from the legacy renderer.

## Outputs

- `reviewed-history.json`: human-maintained scope, source references, selected corrections and added events.
- `site-history.json` / `site-history.geojson`: all 147 joined records, including original occupation strings and evidence status.
- `GAZETTEER.md`: printable/searchable text index matched to map numbers.
- `previews/Crusader-Period-1095-1291.html`: self-contained interactive map; numbered sites open their occupation/siege cards, with text search and region filtering.
- `previews/Crusader-Period-1095-1291.jpg`: checked map preview.
- `print/Crusader-Period-1095-1291.svg`: scalable 36 × 48 inch map with embedded terrain/artwork and vector markers/tooltips. Use the companion gazetteer for full printed chronology; the map does not squeeze every long history into the geography.

The terrain and projection come from the existing repository. New map markers preserve geographic anchors; displaced numbered callouts have leader lines. City/castle paintings remain illustrative, with the original historical/repaint flags. They do not represent one simultaneous political snapshot. The old Outremer print files remain archived outputs and have not been relabeled as if rebuilt.

## Build and validation

Run `python3 build_period_map.py` with Pillow, NumPy, SciPy, Shapely and pyproj, then `python3 -m unittest test_period_history`. The tests check 147 unique records, the 1095–1291 boundary, abbreviated siege-year expansion, separate Damietta campaigns, and exclusion of post-period siege events. The legacy Cairo source renderer also uses the new title, period-clipped holdings and attached siege labels; this session compiled its modified source but generated the new period edition using the Cairo-independent renderer.

Visual QA covered the title, terrain, numbered positions, source-art thumbnails, legend and card layout. Browser checks confirmed search, marker-to-card navigation and reset of filters. Historical review flags are part of the delivered dataset, not a historical-accuracy certification.
