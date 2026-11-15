# Terrain gap report

Measured on the composite preview. Each frame is cut into square cells (320 px on the main sheet, 200 px in the insets, at print scale). A land cell counts as flat when its painted detail (brightness spread) is under 12, and thin when it is 12 to 16. Panels and sea are left out.

| Zone | Land cells | Flat | Thin | Share flat or thin |
|---|---:|---:|---:|---:|
| Egypt inset: Western and Eastern deserts | 163 | 4 | 21 | 15% |
| Egypt inset: Sinai | 185 | 4 | 19 | 12% |
| Lebanon and Damascus | 39 | 0 | 3 | 8% |
| Negev, Sinai, Arabah | 62 | 2 | 2 | 6% |
| North Syria (Antioch, Aleppo) | 63 | 1 | 3 | 6% |
| Aegean inset: islands and Crete | 16 | 0 | 1 | 6% |
| Syrian desert | 33 | 0 | 2 | 6% |
| Egypt inset: Delta | 51 | 0 | 3 | 6% |
| Aegean inset: Anatolia and Thrace | 119 | 0 | 4 | 3% |
| Aegean inset: Greece and the Balkans | 105 | 0 | 3 | 3% |
| Cilicia and the Taurus | 140 | 1 | 2 | 2% |
| Transjordan and Hauran | 153 | 0 | 1 | 1% |
| other | 40 | 0 | 0 | 0% |
| Upper Mesopotamia | 8 | 0 | 0 | 0% |
| Cyprus | 25 | 0 | 0 | 0% |
| Syrian coast and Orontes | 33 | 0 | 0 | 0% |
| Galilee, Samaria, Judea | 53 | 0 | 0 | 0% |

Whole sheet: 1288 land cells, 12 flat, 64 thin (6% flat or thin).

## Flat cells by position

| Zone | Lon | Lat | Sheet x | Sheet y | Detail |
|---|---:|---:|---:|---:|---:|
| Cilicia and the Taurus | 35.57 | 37.72 | 7360 | 320 | 9.2 |
| North Syria (Antioch, Aleppo) | 37.50 | 35.25 | 10240 | 4800 | 7.0 |
| Negev, Sinai, Arabah | 34.17 | 31.04 | 5120 | 12480 | 9.5 |
| Negev, Sinai, Arabah | 34.57 | 31.04 | 5760 | 12480 | 10.1 |
| Egypt inset: Sinai | 32.69 | 30.68 | 2790 | 10721 | 10.7 |
| Egypt inset: Sinai | 33.35 | 29.05 | 3390 | 12321 | 7.3 |
| Egypt inset: Sinai | 33.35 | 28.84 | 3390 | 12521 | 11.7 |
| Egypt inset: Sinai | 32.88 | 28.45 | 2990 | 12921 | 10.8 |
| Egypt inset: Western and Eastern deserts | 32.21 | 29.67 | 2390 | 11721 | 4.3 |
| Egypt inset: Western and Eastern deserts | 30.59 | 28.46 | 990 | 12921 | 9.5 |
| Egypt inset: Western and Eastern deserts | 31.05 | 28.26 | 1390 | 13121 | 8.6 |
| Egypt inset: Western and Eastern deserts | 31.96 | 27.85 | 2190 | 13521 | 9.5 |

The thin cells are listed with the flat ones in terrain-gap-cells.csv.

## What covers the land now

- Terrain stamps and landscape tiles: 69 different pieces, 6244 placements
- Generic settlement, farm, tree, rock and ruin pieces: 189 different pieces, 2356 placements
- Greek island overlays: 47
- Ships at sea: 8

**Interpretation:** Flat/thin classifications measure local texture contrast, not verified exposure of the base-map layer. The CSV preserves the upstream flag as `legacy_flat_flag`, derives `flat` from the documented <12 threshold, and marks `base_layer_exposure=unverified` pending visual geographic review.

