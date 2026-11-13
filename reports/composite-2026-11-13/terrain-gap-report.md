# Terrain gap report

Measured on the composite preview. Each frame is cut into square cells (320 px on the main sheet, 200 px in the insets, at print scale). A land cell counts as flat when its painted detail (brightness spread) is under 12, and thin when it is 12 to 16. Panels and sea are left out.

| Zone | Land cells | Flat | Thin | Share flat or thin |
|---|---:|---:|---:|---:|
| Egypt inset: Western and Eastern deserts | 163 | 5 | 41 | 28% |
| Upper Mesopotamia | 8 | 0 | 2 | 25% |
| Syrian desert | 33 | 1 | 5 | 18% |
| Egypt inset: Sinai | 185 | 3 | 16 | 10% |
| Lebanon and Damascus | 39 | 0 | 2 | 5% |
| North Syria (Antioch, Aleppo) | 63 | 1 | 1 | 3% |
| Aegean inset: Anatolia and Thrace | 119 | 0 | 2 | 2% |
| Negev, Sinai, Arabah | 62 | 0 | 1 | 2% |
| Transjordan and Hauran | 153 | 0 | 1 | 1% |
| other | 40 | 0 | 0 | 0% |
| Cilicia and the Taurus | 140 | 0 | 0 | 0% |
| Cyprus | 25 | 0 | 0 | 0% |
| Syrian coast and Orontes | 33 | 0 | 0 | 0% |
| Galilee, Samaria, Judea | 53 | 0 | 0 | 0% |
| Aegean inset: Greece and the Balkans | 105 | 0 | 0 | 0% |
| Aegean inset: islands and Crete | 16 | 0 | 0 | 0% |
| Egypt inset: Delta | 51 | 0 | 0 | 0% |

Whole sheet: 1288 land cells, 10 flat, 71 thin (6% flat or thin).

## Flat cells by position

| Zone | Lon | Lat | Sheet x | Sheet y | Detail |
|---|---:|---:|---:|---:|---:|
| North Syria (Antioch, Aleppo) | 37.50 | 35.25 | 10240 | 4800 | 10.8 |
| Syrian desert | 37.28 | 34.55 | 9920 | 6080 | 11.3 |
| Egypt inset: Sinai | 34.34 | 30.85 | 4190 | 10521 | 10.1 |
| Egypt inset: Sinai | 32.68 | 30.28 | 2790 | 11121 | 10.9 |
| Egypt inset: Sinai | 32.64 | 27.84 | 2790 | 13521 | 11.4 |
| Egypt inset: Western and Eastern deserts | 31.05 | 28.86 | 1390 | 12521 | 11.0 |
| Egypt inset: Western and Eastern deserts | 30.59 | 28.46 | 990 | 12921 | 11.7 |
| Egypt inset: Western and Eastern deserts | 31.27 | 28.05 | 1590 | 13321 | 11.6 |
| Egypt inset: Western and Eastern deserts | 31.27 | 27.85 | 1590 | 13521 | 7.2 |
| Egypt inset: Western and Eastern deserts | 31.50 | 27.85 | 1790 | 13521 | 11.0 |

The thin cells are listed with the flat ones in terrain-gap-cells.csv.

## What covers the land now

- Terrain stamps and landscape tiles: 115 different pieces, 6868 placements
- Generic settlement, farm, tree, rock and ruin pieces: 255 different pieces, 2017 placements
- Greek island overlays: 46
- Ships at sea: 8
