# Map content manifests

A source audit and editorial placement plan for **Outremer, 1095–1571**, based on repository main at `22e91d258bca9603a2ecb261528e455ad19c63f1`. The map is a multi-period historical atlas, not a snapshot of all sites existing under one ruler in one year.

| File | Purpose |
|---|---|
| `locations.json` | 217 cities, castles, religious landmarks, events and candidate additions |
| `landscape.json` | 193 roads, island labels, terrain zones, waterways, political labels and candidate overlays |
| `locations.csv`, `landscape.csv` | Flat inventories for review and filtering; full geometry remains in JSON |
| `CATALOG.md` | Human-readable list of every entry |
| `proposals.json` | Editable editorial additions; inputs to the builder |
| `coverage.json` | Counts for comparing with the source catalogs |

Rebuild from the repository root with `python3 build_manifests.py`. This uses only Python's standard library and reads source syntax without importing or running the map renderer. The builder checks unique IDs, valid coordinate ranges, route references and retained place/event counts. These are structural checks, not historical verification.

## Coverage

The location inventory retains all **147 PLACES and 34 BATTLES** rows from `places.py`, then adds **36 candidate location records**. The landscape inventory retains **12 ISLES**, **nine ROADS**, **five EXTRA_RIVERS**, **80 procedural terrain distribution zones**, **13 active political lettering paths**, **six hand-restored lake centers**, and **five base-dataset references**. It adds **53 named landscape overlays** and **ten route corridor proposals**.

The source of each inherited entry identifies its file, assignment and zero-based row where applicable. Source dates, names, symbols, affiliations and coordinates are transcribed without silently correcting them. Existing source definitions are not proof that every label survives collision avoidance or is visible in the final print.

The active stage-2 pipeline is authoritative. Earlier experimental `rough_compose.py` lists and superseded stage-1 polity positions are not duplicated. Profile drawing functions are graphical motifs, not additional geographic records. The Jerusalem raster panel is recorded as a placement context for proposed detail landmarks; its internal painted features have not been individually inventoried or verified.

The five base datasets are referenced rather than copying the world's Natural Earth polygons into this manifest. Unnamed coasts, minor islands, rivers and lakes remain in those datasets and are clipped by the renderer. Elevation-generated hills and trees are procedural marks, not individually named sites. Consequently this is complete for explicit active catalogs, not a claim to enumerate every historical hamlet, road or landform in the eastern Mediterranean.

## Placement rules

- Coordinates use WGS84 longitude, latitude. Existing coordinates remain approximate source values; candidate coordinates are editorial anchors that require checking before drawing.
- `Point` geometry for a valley, mountain range, sea or political context is a **label anchor**, not its extent. Use surveyed lines or areas when drawing a physical feature.
- Existing roads retain schematic control points. The renderer smooths them; they are not historical surveys. Names were inferred from endpoints and intermediate points.
- New route corridors contain ordered place IDs and **null geometry**. Research medieval alignments, water stops, crossings and mountain passes before drawing them. Maritime proposals are optional connections, not fixed sailing tracks.
- Political paths are lettering baselines, never borders. This matches the existing map's choice to draw no political boundaries.
- Put Jerusalem's closely spaced landmarks in a detail view. Give landmark records a parent settlement during rendering to avoid stacked duplicate symbols. Proposed city landmarks elsewhere should similarly use a city detail, leader or metadata rather than a second full-sized city sprite.
- `off_map` entries document Edessa/Harran and the eastward corridor. Preserve the callout or introduce a new inset; do not move their coordinates onto the current sheet.
- CSV omits line geometry and nested provenance; use JSON as the authoritative machine-readable form.

## Decisions before final map production

1. **Time:** retain the 1095–1571 overview with dated labels, or select a year and research period-specific existence, ownership, names and building phases. Do not treat an association date as a settlement's complete lifespan. The sprite project's provisional 1180 date does not override the atlas scope.
2. **Priority:** retain the source catalog; consider high-priority additions first. Candidate priority is editorial, not a historical importance ranking. Landscape overlays may already exist physically as unnamed terrain; add names or refine geometry rather than duplicate it.
3. **Accuracy:** all records require historical review. Modern shorelines, DEM, forests and wetlands are not a medieval landscape reconstruction. River migration, drainage, harbor silting and reservoirs matter.

## Findings requiring review

- **Pelusium / al-Farama** has the alternate name `Belbeis` in the source, while Bilbays/Bilbeis is a separate inland record. Retained verbatim and flagged here; verify and correct the alias in a separate map-data change.
- **Li Vaux Moyse / Wadi Musa / Petra** combines distinct place/site concepts. Confirm whether the intended mark is the valley settlement or a particular Crusader castle before producing an asset.
- **Cana**, **Bethabara / baptism place**, **Montgisard** and some battlefield locations require identification-level review. A traditional identification is not a surveyed certainty.
- **Tripoli** needs a distinction between the medieval port settlement and inland Mont Pèlerin citadel. The new landmark proposal must not simply duplicate the existing city mark.
- **Cyprus and Aegean entries** span later medieval and early modern phases. Do not reuse Lusignan, Venetian or Hospitaller buildings and emblems unchanged for 1180. Source date spans sometimes extend beyond 1571 and should be clipped for a strict atlas time filter.
- **Safed, Beaufort, Margat, Ruad, Montfort and Château Pèlerin** illustrate why association dates cannot be used as founding dates or full control histories. They need phase- and owner-specific research.
- **Roads 8–9** lie in Cyprus and are drawn through the main-region coordinate system in the existing source. Keep that region assignment; it is not an Aegean-inset route.
- **Restored lakes** are procedural ellipses in `terrain.init_lakes`, not documentary medieval shorelines. They are retained as anonymous numbered source records rather than assigned confident historical names. Named Amuq/Hula overlays must be reconciled with these and the modern lake dataset.
- The renderer excludes lake names matching `MODERN_LAKES` and river names containing `Canal`. Its exclusions are substring heuristics, not historical validation: the exclusion list includes natural lakes as well as modern reservoir names. Audit this before changing hydrology. Do not add the modern Suez Canal to a medieval map.
- A proposed `Montréal–Ayla desert way stations` record deliberately has no coordinates: research is needed before creating individual site records.

## Reference use and limits

Most inherited entries are **repository-backed**, not independently re-researched. Proposed coordinates and unsourced candidate notes are editorial suggestions, not certified gazetteer data. The references below support the identity and significance of selected landmark/landscape candidates, not every coordinate or medieval reconstruction:

- [Old City of Jerusalem](https://whc.unesco.org/en/list/148): Holy Sepulchre and Dome of the Rock context.
- [Bethlehem and Church of the Nativity](https://whc.unesco.org/en/list/1433/): church and pilgrimage landscape.
- [Qadisha and Cedars of God](https://whc.unesco.org/en/list/850/): holy valley and woodland context; not a reconstruction of medieval forest boundaries.
- [Patmos](https://whc.unesco.org/en/list/942/): monastery and pilgrimage context. Do not derive a precise foundation year from this inventory.
- [Medieval Rhodes](https://whc.unesco.org/en/list/493/): Hospitaller built environment. Source dates vary between 1522 conquest and 1523 departure; preserve the distinction when researching chronology.

These manifests plan content; they do not alter existing rendering, certify historical accuracy, or commission hundreds of new sprite assets.
