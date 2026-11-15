# Greek island artwork — actual renderer usage and unplaced subject audit (15 November 2026)

## Verdict
**Not all island sprites are on the map.** This is a source-code, registry and existing render-output audit, not a fresh full-resolution build. The only verified island render output remains the 12 November geographic review with 47 of 47 legacy registered island PNGs drawn. Later marker commits did not promote paintings.

- Active renderer: `islandart.py` reads `assets/islands.json` (**47** legacy island artwork entries), not `data/sprites/review/island-batches-25-31-pins-2026-11-15.geojson`.
- Renderer proof: `reports/greek-islands-review-2026-11-12/render-audit.json` confirms **47 rendered**, zero missing in that review (Corfu included). This proof does NOT certify the newest full composite.
- Last general rebuild inventory: `reports/rebuild-2026-11-12/image-usage-and-off-map-list.csv` lists 47 legacy Greek-island assets on-map and 94 Greek-island directory files off-map; off-map includes duplicate drafts/masters, so 94 is NOT a number of distinct needed islands.
- Batches 25–31: **28 artwork records**, 24 pixel duplicates in intake registry (duplicate means already imported, NOT necessarily drawn). 15 named islands already have older active artwork; **13** do not. The 28 location-only review markers are NOT painted sprite placements. Zero of these 28 newer paintings is selected by `assets/islands.json`.
- The historical deduplicated candidate queue (12 November) has 93 review-only unique candidate binary hashes, including multiple paintings of the same island. It predates Batches 25–31 and must not be added to the newer count directly.

## Non-superseded subject-level follow-up queue
Names are de-duplicated by island subject; older versions, draft twins and source master sheets are excluded as separate map subjects. A listed subject has no entry in the active 47-image renderer. This is **not** historical/geographic approval of its candidate artwork.

### 13 genuinely new subjects in Batches 25–31 (prefer newer candidates)
- agathonisi
- agistri
- antikythera
- antiparos
- antipaxos
- delos
- elafonisos
- gavdos
- paxos
- psara
- rhenia
- spetses
- telendos

### 14 other unrepresented subjects with Batch 03 staged artwork
- Aegina
- Chalki
- Donousa
- Hydra
- Imbros
- Irakleia
- Kastellorizo
- Koufonisia
- Lipsi
- Poros
- Salamis
- Schinoussa
- Sikinos
- Tenedos

### 35 other unrepresented subjects represented by early concept/draft queues
- Arki/Marathi
- Fournoi
- Oinousses
- agios-efstratios
- antimilos
- arkoudi
- atokos
- chrysi
- despotiko
- dia
- dokos
- ereikoussa
- gioura
- gramvousa
- gyaros
- kalamos
- kastos
- kinaros
- kyra-panagia
- levitha
- makronisos
- mathraki
- meganisi
- othonoi
- oxia
- peristera
- petalas
- piperi
- polyaigos
- pserimos
- sapientza
- saria
- schiza
- skantzoura
- thirasia

**Total distinct named unrepresented subjects in this reconciled queue: 62.** This excludes all 47 already active original islands, source-sheet artifacts, duplicate draft versions and later replacements for existing islands. Subject-name normalization is heuristic; inspect cluster identity and candidate quality before artwork promotion.

### 15 more Batches 25–31 paintings that are replacement alternatives (not new island subjects)
- alonissos
- chios
- corfu
- euboea
- ithaca
- kalymnos
- karpathos
- kasos
- lefkada
- lesbos
- rhodes
- samothrace
- skiathos
- symi
- tilos

These 15 islands already have earlier art on the map. Leave current art in place unless replacement is deliberately selected, verifies distinct coastline, improves historical scene and passes viewpoint/print QA.

## Placement / review gates
1. Keep current 47 active overlays; do not overlay the same island twice.
2. For each genuinely unrepresented subject, select one best non-superseded source image. Check image identity, alpha and printing resolution; inspect south-oblique north-looking POV, correct seaward side and accurate island silhouette.
3. Establish `render_bbox_wgs84` from geographically registered IMAGE BOUNDS, not a center marker, for every new island painting. Point GeoJSON is not a valid raster registration.
4. Review 1097–16th-century historical period and date-specific settlement/fortification differences; the filename's 1180 is not global atlas cutoff.
5. Add only verified overlays to active renderer configuration, build a new Aegean/Ionian composite, and save renderer-used ID proof and visual QA image.
6. Reconcile earlier concepts against newer paintings by named subject and pixel identity. Preserve superseded originals in version history but exclude them from placement counting.

**Limitations:** No new map render or image-level shoreline comparison was executed in this audit. Latest composite completion is unverified; this report must not be interpreted as a final print approval.
