# Terrain gap report

Measured on the composite preview. Each frame is cut into square cells (320 px on the main sheet, 200 px in the insets, at print scale). A land cell counts as flat when its painted detail (brightness spread) is under 12, and thin when it is 12 to 16. Panels and sea are left out.

| Zone | Land cells | Flat | Thin | Share flat or thin |
|---|---:|---:|---:|---:|
| Aegean inset: islands and Crete | 16 | 1 | 3 | 25% |
| Egypt inset: Sinai | 185 | 7 | 24 | 17% |
| Egypt inset: Western and Eastern deserts | 163 | 5 | 14 | 12% |
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

Whole sheet: 1288 land cells, 17 flat, 52 thin (5% flat or thin).

## Flat cells by position

| Zone | Lon | Lat | Sheet x | Sheet y | Detail |
|---|---:|---:|---:|---:|---:|
| North Syria (Antioch, Aleppo) | 37.50 | 35.25 | 10240 | 4800 | 11.7 |
| Negev, Sinai, Arabah | 34.17 | 31.04 | 5120 | 12480 | 11.4 |
| Negev, Sinai, Arabah | 34.37 | 31.04 | 5440 | 12480 | 9.4 |
| Negev, Sinai, Arabah | 34.57 | 31.04 | 5760 | 12480 | 7.6 |
| Aegean inset: islands and Crete | 24.79 | 35.17 | 2390 | 3990 | 11.9 |
| Egypt inset: Sinai | 34.83 | 31.45 | 4590 | 9921 | 8.8 |
| Egypt inset: Sinai | 33.81 | 28.84 | 3790 | 12521 | 9.3 |
| Egypt inset: Sinai | 34.50 | 28.82 | 4390 | 12521 | 10.2 |
| Egypt inset: Sinai | 32.65 | 28.65 | 2790 | 12721 | 11.9 |
| Egypt inset: Sinai | 34.26 | 28.62 | 4190 | 12721 | 6.8 |
| Egypt inset: Sinai | 32.65 | 28.45 | 2790 | 12921 | 7.6 |
| Egypt inset: Sinai | 34.03 | 28.43 | 3990 | 12921 | 8.8 |
| Egypt inset: Western and Eastern deserts | 32.20 | 29.06 | 2390 | 12321 | 11.7 |
| Egypt inset: Western and Eastern deserts | 32.20 | 28.86 | 2390 | 12521 | 9.7 |
| Egypt inset: Western and Eastern deserts | 31.05 | 28.66 | 1390 | 12721 | 11.9 |
| Egypt inset: Western and Eastern deserts | 31.74 | 28.66 | 1990 | 12721 | 11.1 |
| Egypt inset: Western and Eastern deserts | 31.73 | 28.46 | 1990 | 12921 | 10.1 |

The thin cells are listed with the flat ones in terrain-gap-cells.csv.

## What covers the land now

- Terrain stamps and landscape tiles: 69 different pieces, 5772 placements
- Generic settlement, farm, tree, rock and ruin pieces: 189 different pieces, 2409 placements
- Greek island overlays: 47
- Ships at sea: 8

**Interpretation:** Flat/thin classifications measure local texture contrast, not verified exposure of the base-map layer. The CSV preserves the upstream flag as `legacy_flat_flag`, derives `flat` from the documented <12 threshold, and marks `base_layer_exposure=unverified` pending visual geographic review.

