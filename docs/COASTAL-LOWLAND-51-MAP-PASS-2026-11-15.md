# Coast-reaching lowland underlay review — 15 November 2026

**Scope:** existing 51 individually extracted lowland PNG cutouts, retained four painted underlay textures, Nile Delta, Levantine littoral, Cyprus, Cilicia and Greek lowlands.

## Coastline protection
- The earlier `land >= 0.995` blurred-mask test intentionally omitted antialiased land pixels. This created a strip of original geographic wash at the shoreline.
- The revised renderer derives **exact raster land and lake pixels from the same geographic polygons** as the map base and applies textured wash up to every eligible land pixel. Edge strength is feathered **inside** the true land mask, never into sea or lakes. The existing azure sea layer and coastal ink are unchanged.
- A production verification workflow fails if painted coverage misses eligible land or changes the excluded sea/lake pixels.
- Source cutouts have rectangular, sometimes opaque edges; the review compositor feathers 14% of each source tile edge, then clips all pixels against actual vector land geometry minus lakes.
- The separated preview cutouts are drawn **before** the atlas terrain, roads, city, fortress, industry and label layers. They cannot cover those foreground sprites.

## All 51 cutouts — individual image QA and regional assignments
The automated preflight decodes **every registered canonical PNG**, verifies its true file, alpha, size, checksum, colour content, edge translucency and origin, and produces `reports/lowland-review-2026-11-15/lowland-51-contact-sheet.jpg` plus a per-image JSON audit.

All 51 receive a geographically bounded review region grounded in the existing atlas polygons; no named-town site coordinates are invented.

- Group 06 (12): **Nile Delta**. Hydrology and coastline-dependent; held until individual river/channel geometry is matched.
- Group 07 (12): Mediterranean lowlands, assigned across **Cyprus, Cilicia, Greek lowlands, Levantine coastal fields**. Dry-image cutouts with native RGBA and low cyan/blue coverage may enter the *review build* with exact coastline clipping.
- Group 08 (15): mixed Delta/Aegean/Levantine cutouts, assigned a region but **held** until land/water pixels and actual hydrographic alignment are reviewed.
- Group 09 (12): coastal rural tiles assigned among **Levantine coast, Cyprus and Cilicia**. Dry-image cutouts may enter the *review build* with vector shoreline clipping; water/shore-dependent imagery remains held.

**A colour-based automated screen cannot certify there is no painted water.** Release is *provisional visual review only*, not historical/print/production approval; any misoriented harbour or river depiction must still be rejected after reviewing the contact and geographic maps.

## Actual rebuild and side-by-side comparison
The workflow saves the prior full geographic composite before rendering, integrates the reviewed lowland underlays, and publishes direct projected before/after crops at the **same map raster scale** for:
1. Nile Delta
2. Acre–Gaza / Levantine coast
3. Cyprus
4. Cilicia
5. Greek cultivated lowlands

The QA report includes each changed pixel count and original region bbox. Inspect against the **current** placement logs, coast mask and foreground overlaps. Empty or unchanged areas are not automatically approved.

The 51 canonical PNGs are reused by path; nothing is uploaded twice and source masters/archived artwork are preserved. The original complete Dead Sea sprite remains untouched.

**Outstanding gate:** Human visual/archaeological validation, direct water alignment for groups 06 and 08, all ambiguous 09 imagery, final 300-DPI print review and period-specific variants.
