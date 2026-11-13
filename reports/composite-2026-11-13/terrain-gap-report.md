# Terrain gap report

Measured on the composite preview. Each frame is cut into square cells (320 px on the main sheet, 200 px in the insets, at print scale). A land cell counts as flat when its painted detail (brightness spread) is under 12, and thin when it is 12 to 16. Panels and sea are left out.

| Zone | Land cells | Flat | Thin | Share flat or thin |
|---|---:|---:|---:|---:|
| Upper Mesopotamia | 8 | 0 | 2 | 25% |
| Syrian desert | 33 | 4 | 4 | 24% |
| Egypt inset: Western and Eastern deserts | 163 | 3 | 35 | 23% |
| Lebanon and Damascus | 39 | 1 | 5 | 15% |
| Egypt inset: Sinai | 185 | 1 | 15 | 9% |
| North Syria (Antioch, Aleppo) | 63 | 3 | 2 | 8% |
| Transjordan and Hauran | 153 | 1 | 2 | 2% |
| other | 40 | 0 | 0 | 0% |
| Cilicia and the Taurus | 140 | 0 | 0 | 0% |
| Cyprus | 25 | 0 | 0 | 0% |
| Syrian coast and Orontes | 33 | 0 | 0 | 0% |
| Galilee, Samaria, Judea | 53 | 0 | 0 | 0% |
| Negev, Sinai, Arabah | 62 | 0 | 0 | 0% |
| Aegean inset: Greece and the Balkans | 105 | 0 | 0 | 0% |
| Aegean inset: Anatolia and Thrace | 119 | 0 | 0 | 0% |
| Aegean inset: islands and Crete | 16 | 0 | 0 | 0% |
| Egypt inset: Delta | 51 | 0 | 0 | 0% |

Whole sheet: 1288 land cells, 13 flat, 65 thin (6% flat or thin).

## Flat cells by position

| Zone | Lon | Lat | Sheet x | Sheet y | Detail |
|---|---:|---:|---:|---:|---:|
| North Syria (Antioch, Aleppo) | 36.86 | 35.44 | 9280 | 4480 | 9.6 |
| North Syria (Antioch, Aleppo) | 37.51 | 35.43 | 10240 | 4480 | 11.0 |
| North Syria (Antioch, Aleppo) | 37.50 | 35.25 | 10240 | 4800 | 9.5 |
| Syrian desert | 37.28 | 34.55 | 9920 | 6080 | 11.5 |
| Syrian desert | 37.47 | 33.67 | 10240 | 7680 | 10.0 |
| Syrian desert | 37.47 | 33.50 | 10240 | 8000 | 11.5 |
| Syrian desert | 37.26 | 33.33 | 9920 | 8320 | 9.7 |
| Lebanon and Damascus | 36.84 | 33.50 | 9280 | 8000 | 9.8 |
| Transjordan and Hauran | 37.04 | 32.80 | 9600 | 9280 | 10.1 |
| Egypt inset: Sinai | 34.34 | 30.85 | 4190 | 10521 | 11.0 |
| Egypt inset: Western and Eastern deserts | 31.05 | 28.26 | 1390 | 13121 | 11.2 |
| Egypt inset: Western and Eastern deserts | 31.27 | 27.85 | 1590 | 13521 | 7.2 |
| Egypt inset: Western and Eastern deserts | 31.50 | 27.85 | 1790 | 13521 | 10.4 |

The thin cells are listed with the flat ones in terrain-gap-cells.csv.

## What covers the land now

- Terrain stamps and landscape tiles: 115 different pieces, 6836 placements
- Generic settlement, farm, tree, rock and ruin pieces: 425 different pieces, 2273 placements
- Greek island overlays: 96
- Ships at sea: 8
