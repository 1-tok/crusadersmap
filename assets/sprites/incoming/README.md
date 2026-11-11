# Sprite intake drop folder

Upload PNG files here using **Add file → Upload files** on GitHub. Include an optional same-stem `.json` metadata sidecar. The GitHub Action records and preserves original PNGs and adds validated copies to the sprite library. Never delete originals automatically.

Metadata example:
```json
{"subject":"Ascalon","category":"city","site_id":"ascalon","coordinates":[34.56,31.67],"coordinate_source":"editorial approximate; not surveyed","target_year":1180,"display_width_units":512,"orientation":"south","water_side":"west","status":"provisional"}
```
Coordinates are optional. They are not inferred from place names. Missing coordinates mean cataloged artwork with `geographic_placement_ready=false`, and placement review is required.
For a sheet, supply `"sprites":[{"box":[0,0,512,512],"subject":"Castle A","category":"castle"}, ...]` (pixel bounds are left,top,right,bottom). Without reliable declared rectangles or clearly isolated alpha components, the sheet stays intact as one provisional asset.
