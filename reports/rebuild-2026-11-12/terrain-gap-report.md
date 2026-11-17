# Terrain gap report

Measured on the composite preview. Each frame is cut into square cells (320 px on the main sheet, 200 px in the insets, at print scale). A land cell counts as flat when its painted detail (brightness spread) is under 12, and thin when it is 12 to 16. Panels and sea are left out.

| Zone | Land cells | Flat | Thin | Share flat or thin |
|---|---:|---:|---:|---:|
| Aegean inset: islands and Crete | 16 | 1 | 3 | 25% |
| Egypt inset: Western and Eastern deserts | 163 | 2 | 14 | 10% |
| Egypt inset: Sinai | 185 | 3 | 15 | 10% |
| Lebanon and Damascus | 39 | 0 | 2 | 5% |
| Negev, Sinai, Arabah | 62 | 3 | 0 | 5% |
| Egypt inset: Delta | 51 | 0 | 2 | 4% |
| Syrian desert | 33 | 0 | 1 | 3% |
| Aegean inset: Greece and the Balkans | 105 | 0 | 2 | 2% |
| Aegean inset: Anatolia and Thrace | 119 | 0 | 2 | 2% |
| North Syria (Antioch, Aleppo) | 63 | 1 | 0 | 2% |
| Cilicia and the Taurus | 140 | 0 | 1 | 1% |
| Transjordan and Hauran | 153 | 0 | 1 | 1% |
| other | 40 | 0 | 0 | 0% |
| Upper Mesopotamia | 8 | 0 | 0 | 0% |
| Cyprus | 25 | 0 | 0 | 0% |
| Syrian coast and Orontes | 33 | 0 | 0 | 0% |
| Galilee, Samaria, Judea | 53 | 0 | 0 | 0% |

Whole sheet: 1288 land cells, 10 flat, 43 thin (4% flat or thin).

## Flat cells by position

| Zone | Lon | Lat | Sheet x | Sheet y | Detail |
|---|---:|---:|---:|---:|---:|
| North Syria (Antioch, Aleppo) | 37.50 | 35.25 | 10240 | 4800 | 11.7 |
| Negev, Sinai, Arabah | 34.17 | 31.04 | 5120 | 12480 | 11.4 |
| Negev, Sinai, Arabah | 34.37 | 31.04 | 5440 | 12480 | 9.4 |
| Negev, Sinai, Arabah | 34.57 | 31.04 | 5760 | 12480 | 7.6 |
| Aegean inset: islands and Crete | 24.79 | 35.17 | 2390 | 3990 | 11.9 |
| Egypt inset: Sinai | 34.51 | 29.02 | 4390 | 12321 | 8.1 |
| Egypt inset: Sinai | 34.26 | 28.62 | 4190 | 12721 | 10.4 |
| Egypt inset: Sinai | 33.79 | 28.23 | 3790 | 13121 | 9.8 |
| Egypt inset: Western and Eastern deserts | 31.73 | 28.25 | 1990 | 13121 | 10.9 |
| Egypt inset: Western and Eastern deserts | 31.96 | 27.85 | 2190 | 13521 | 11.8 |

The thin cells are listed with the flat ones in terrain-gap-cells.csv.

## What covers the land now

- Terrain stamps and landscape tiles: 69 different pieces, 6305 placements
- Generic settlement, farm, tree, rock and ruin pieces: 189 different pieces, 2380 placements
- Greek island overlays: 47
- Ships at sea: 8

**Interpretation:** Flat/thin classifications measure local texture contrast, not verified exposure of the base-map layer. The CSV preserves the upstream flag as `legacy_flat_flag`, derives `flat` from the documented <12 threshold, and marks `base_layer_exposure=unverified` pending visual geographic review.

