# Bosphorus companion sprites — circa1180

Three provisionally approved transparent sprites: Galata/Sykai, Chrysopolis/Skoutarion and Chalcedon. Continuing user authorization permits provisional placement with historical review flags; it does not certify the architecture. All originals, cleanup variants, exact prompts and hashes are preserved. Generation used built-in image_gen with the original Acre painting as style reference only.

## Coordinates and historical evidence

| Sprite | Published longitude, latitude | Evidence and precision |
|---|---|---|
| Galata / Sykai |28.974600,41.025700|[ToposText Sykai](https://topostext.org/place/410290USyk), medium confidence; area point, **not the waterfront fort**|
| Chrysopolis |29.012856,41.020639|[Digital Atlas of the Roman Empire](https://imperium.ahlfeldt.se/places/22696), published precision**2000m**; ancient-place point reused only as representative location|
| Chalcedon |29.025789,40.983393|[Oxford RPC Calchedon](https://rpc.ashmus.ox.ac.uk/city/362), representative ancient-city point, not exact1180 harbour|

[Dalleggio d’Alessio,1961](https://www.persee.fr/doc/rebyz_0766-5598_1961_num_19_1_1265) supports north-bank settlement and the waterfront fort; [Sağlam’s architectural study](https://in-scription.edel.univ-poitiers.fr/index.php?id=480) distinguishes this Kastellion from the later Genoese tower. Its fort elevation in our sprite is hypothetical.

[Belke,2021,pp.223–230](https://www.ancientportsantiques.com/wp-content/uploads/Documents/PLACES/Bosphorus-BlackSea/Chalcedon-Belke2021.pdf) supports the Asian-shore harbours and Comnenian ferry traffic. Chrysopolis had a silting natural harbour and became the principal crossing during the Comnenian period. Chalcedon occupied a low peninsula between harbour areas; precise shorelines remain disputed. The Skutarion palace is attested near Manuel I’s death but omitted here because its visual plan is uncertain. Our churches, houses, jetties and wall fragments are generic schematic choices, not identified excavated1180 buildings.

## Placement contract

Each companion displays at256 pixels; Constantinople remains1024. Regional Aegean anchors are only about10–25 pixels apart, so these images must **not** be overlaid directly on that regional view. `placement_view: constantinople-detail` enforces exclusion from the ordinary1180 overlay.

Run `build_constantinople_detail.py` for the independent enlarged geographic anchor diagnostic, embedded SVG sprite overlay and `../placements-constantinople-detail-1180.geojson`. Geography is uniformly magnified60× relative to the regional projection, with no geographic offsets. All four sprite bounds fit without overlap. The diagnostic uses a geographic grid; it supplies no reconstructed coastline and is not a finished historical map.

Manifest dates approve only the circa1180 depiction. All three keep repaint/replacement flags. Raw sources are preserved; packaging only normalizes transparent pixels, crops/pads and resizes under the existing user instruction.
