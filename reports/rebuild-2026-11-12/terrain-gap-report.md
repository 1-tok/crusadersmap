# Terrain gap report

Measured on the composite preview. Each frame is cut into square cells (320 px on the main sheet, 200 px in the insets, at print scale). A land cell counts as flat when its painted detail (brightness spread) is under 12, and thin when it is 12 to 16. Panels and sea are left out.

| Zone | Land cells | Flat | Thin | Share flat or thin |
|---|---:|---:|---:|---:|
| Egypt inset: Sinai | 185 | 6 | 23 | 16% |
| Egypt inset: Western and Eastern deserts | 163 | 6 | 19 | 15% |
| Syrian desert | 33 | 1 | 2 | 9% |
| Egypt inset: Delta | 51 | 1 | 3 | 8% |
| Lebanon and Damascus | 39 | 1 | 1 | 5% |
| Aegean inset: Anatolia and Thrace | 119 | 0 | 4 | 3% |
| North Syria (Antioch, Aleppo) | 63 | 1 | 1 | 3% |
| Cilicia and the Taurus | 140 | 1 | 2 | 2% |
| Galilee, Samaria, Judea | 53 | 0 | 1 | 2% |
| Transjordan and Hauran | 153 | 1 | 1 | 1% |
| Aegean inset: Greece and the Balkans | 105 | 0 | 1 | 1% |
| other | 40 | 0 | 0 | 0% |
| Upper Mesopotamia | 8 | 0 | 0 | 0% |
| Cyprus | 25 | 0 | 0 | 0% |
| Syrian coast and Orontes | 33 | 0 | 0 | 0% |
| Negev, Sinai, Arabah | 62 | 0 | 0 | 0% |
| Aegean inset: islands and Crete | 16 | 0 | 0 | 0% |

Whole sheet: 1288 land cells, 18 flat, 58 thin (6% flat or thin).

## Flat cells by position

| Zone | Lon | Lat | Sheet x | Sheet y | Detail |
|---|---:|---:|---:|---:|---:|
| Cilicia and the Taurus | 35.57 | 37.72 | 7360 | 320 | 9.3 |
| North Syria (Antioch, Aleppo) | 37.51 | 35.43 | 10240 | 4480 | 9.4 |
| Syrian desert | 37.47 | 33.50 | 10240 | 8000 | 9.3 |
| Lebanon and Damascus | 36.84 | 33.50 | 9280 | 8000 | 10.9 |
| Transjordan and Hauran | 37.25 | 32.62 | 9920 | 9600 | 10.1 |
| Egypt inset: Sinai | 32.69 | 30.68 | 2790 | 10721 | 10.8 |
| Egypt inset: Sinai | 33.13 | 29.25 | 3190 | 12121 | 7.2 |
| Egypt inset: Sinai | 33.35 | 29.05 | 3390 | 12321 | 3.3 |
| Egypt inset: Sinai | 33.80 | 28.63 | 3790 | 12721 | 11.4 |
| Egypt inset: Sinai | 34.26 | 28.42 | 4190 | 12921 | 9.5 |
| Egypt inset: Sinai | 32.42 | 28.25 | 2590 | 13121 | 10.6 |
| Egypt inset: Delta | 31.04 | 30.69 | 1390 | 10721 | 11.9 |
| Egypt inset: Western and Eastern deserts | 32.21 | 29.67 | 2390 | 11721 | 8.2 |
| Egypt inset: Western and Eastern deserts | 31.51 | 28.86 | 1790 | 12521 | 11.9 |
| Egypt inset: Western and Eastern deserts | 30.59 | 28.46 | 990 | 12921 | 8.3 |
| Egypt inset: Western and Eastern deserts | 31.05 | 28.26 | 1390 | 13121 | 10.7 |
| Egypt inset: Western and Eastern deserts | 32.19 | 28.25 | 2390 | 13121 | 11.4 |
| Egypt inset: Western and Eastern deserts | 31.96 | 27.85 | 2190 | 13521 | 9.5 |

The thin cells are listed with the flat ones in terrain-gap-cells.csv.

## What covers the land now

- Terrain stamps and landscape tiles: 70 different pieces, 6310 placements
- Generic settlement, farm, tree, rock and ruin pieces: 189 different pieces, 2369 placements
- Greek island overlays: 47
- Ships at sea: 8
