# Coastal city & fortress multi-era sprite queue (1180–1600)

Created 2026-11-12. Status: **queued / repaint and historical QA required**. This is an artwork plan, not a claim that image binaries have been delivered or approved. Existing sprites stay intact.

## Global art rules
- Elevated camera from geographical south, looking north; no perspective flip to force sea to the top. In the eastern Mediterranean, west-facing coast generally places sea toward image left, but each peninsula, bay, river mouth and fortress footprint must be checked individually.
- Named-site-specific shoreline and topography; absolutely no invented water for inland Montfort, Beaufort, Safed, Toron or other upland fortresses.
- Transparent RGBA PNG cutouts with generous clean alpha margins, no baked-in labels, frame, checkerboard, banners or fictitious heraldry; match existing watercolor/ink atlas sprites; aim at 2048px-plus masters when practical.
- Every sprite record: site_id, variant era start/end, historical ownership, geographic notes, camera direction, water side, site-specific evidence, QA flags and independent placement/review approval.
- Maintain separate era variants, do not overwrite 1180 illustrations. Later works must not leak into strict earlier reconstructions except the explicitly authorized exceptions below.

## User-authorized project chronology exceptions
- Chateau Pelerin / Atlit: depict as **completed** in project's 1180 presentation, though construction historically began 1218. Record alternate_history_1180_exception=true; also produce historically dated 1218–1291 variant. Coastal peninsula fortress, Mediterranean to west and around seaward sides; verify exact peninsular orientation.
- Montfort: depict as **completed** in project's 1180 presentation, though main Teutonic construction was in the 1220s. Record alternate_history_1180_exception=true; also produce 1220s–1271 historically dated variant. Inland ridge over Nahal Kziv, NO sea visible.

## Priority A: southern-view coastal and near-coast revision
1. Tyre — 1180 and 1250; peninsula, causeway and harbor alignments; no post-period harbor works.
2. Acre — 1180, 1250, 1400 and 1550; account for 1291 destruction and changed Mamluk/Ottoman urban scale, not continuous Crusader skyline.
3. Sidon — 1180 and post-1228; do not put the post-1228 sea castle into 1180.
4. Caesarea — 1180 and post-1251; do not put Louis IX rebuilding into 1180.
5. Tortosa/Tartus — 1180 and 1250; Templar cathedral and district researched, avoid generic river-bridge fantasy.
6. Ascalon — 1180 and 1550 only as supported by settlement history; no unbroken large fortified city assumption after 1270 destruction.
7. Jaffa — 1180, 1250 and 1550; verify harbor and urban size for each phase.
8. Tripoli — 1180 maritime al-Mina and 1400/1550 later inland Mamluk city as geographically separate footprints, never reuse same location.
9. Beirut — 1180, 1400, 1550; phase-specific walls and port.
10. Latakia and Batroun — 1180 and 1550; coastal profile QA.

## Priority B: fortresses
11. Chateau Pelerin / Atlit — project 1180 exception and historical 13th-century version.
12. Montfort — project 1180 exception and historical 13th-century version; inland, not shoreline.
13. Margat / Marqab — 1180 and 13th-century expansion; volcanic ridge with sea distant west, no shoreline touching castle.
14. Krak des Chevaliers — 1180, 1250 and later Mamluk phase; phase-appropriate outer defenses.
15. Safed — 1180 site phase and post-1240 rebuilding; no 1240s fabric on historically strict 1180 variant.
16. Beaufort — 1180/1250; ridge/high cliff above Litani, inland.
17. Toron / Tibnin — 1180/1250; hilltop, inland.
18. Belvoir, Ibelin, Blanchegarde, Chastel Rouge and Sahyun — preserve distinct dated construction phases.

## Priority C: Cyprus, Aegean, eastern Mediterranean 1300–1600
19. Famagusta — 1200/1350/1550 Venetian walls and later bastions only in matching phases.
20. Kyrenia, Limassol, Paphos, Kolossi, St Hilarion, Buffavento, Kantara — individual medieval/late medieval variants, no generic castle substitutions.
21. Rhodes — Byzantine, Hospitaller (post-1309), Ottoman (post-1522) separate skyline and defenses.
22. Chios — Genoese and Ottoman era versions; sea-facing fortified harbor.
23. Candia/Heraklion — Venetian walls and 16th-century fortifications.
24. Methoni, Koroni, Nafpaktos and Monemvasia — fortified harbors and Ottoman/Venetian changes by date.
25. Alexandria — 1180, 1400, 1550; Qaitbay fort only after late 15th century, not 1180.
26. Istanbul/Constantinople — Byzantine 1180 and Ottoman 1550 skyline; do not backdate Ottoman mosques.

## Supporting sprites
- Era-correct medieval galleys, lateen/coastal freighters, 16th-century shipping, docks, quays, shore batteries, bastions, watchtowers, walls, churches, mosques, markets and warehouses.
- Dedicated shore/water overlays must be clipped to actual map hydrology and preserve named-site footprints.

## Acceptance gates
Art production -> transparent cutout QA -> south-view camera QA -> shoreline-side QA -> site/time historical QA -> review-only map placement -> explicit final approval. Generated concept sheets, especially those with labels, false chronology or baked-in backgrounds, are NOT production sprites.
