#!/usr/bin/env python3
"""Acquire a REAL (modern) Nile Delta hydrography reference for medieval review.

OpenStreetMap geometry is a modern spatial reference, NOT historical proof.
The service is an ArcGIS-hosted OSM African waterways mirror with original
waterway types. Download every river segment in our Delta bounding window;
download named canals as distinct, lower-confidence supporting references.
All observations are saved with source, line vertices and OSM feature IDs.
No interpolation or invented branch endpoints.
"""
from __future__ import annotations
import json
import os
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from shapely.geometry import shape, box, mapping
from shapely.ops import linemerge, unary_union

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/nile-delta-hydrography-review-2026-11-17"
DATA = OUT / "delta-osm-waterways.geojson"
REPORT = OUT / "source-and-connectivity.json"
ENDPOINT = "https://services-eu1.arcgis.com/zci5bUiJ8olAal7N/arcgis/rest/services/OSM_AF_Waterways/FeatureServer/0/query"
BBOX = (29.78, 29.98, 32.50, 31.65)
EXTENT = box(*BBOX)
KINDS = ("river", "stream", "canal")
MAX_PAGES = 45  # error rather than silently truncate
PAGE = 1500

def query(kind, offset):
    where = "waterway='" + kind + "'"
    if kind == "canal":
        where += " AND name IS NOT NULL"  # no thousands of anonymous modern ditches
    params = {
        "where": where,
        "geometry": ",".join(str(x) for x in BBOX),
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326", "outSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "objectid,osm_id2,name,waterway",
        "returnGeometry": "true", "returnZ": "false",
        "resultOffset": offset, "resultRecordCount": PAGE,
        "f": "geojson",
    }
    url = ENDPOINT + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent":"CrusaderMap-Nile-Delta-Review/1.0"}), timeout=110) as response:
        result = json.load(response)
    if "error" in result:
        raise RuntimeError(str(result["error"]))
    if result.get("type") != "FeatureCollection":
        raise RuntimeError("ArcGIS waterway API did not return GeoJSON")
    return result["features"]

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Always prefer the already-published, provenance-bearing geographic
    # waterway network on ordinary map rebuilds. ArcGIS query availability
    # must never determine whether the Nile is drawn in this atlas.
    # Explicit refresh is opt-in: REFRESH_NILE_WATERWAYS=1.
    if DATA.is_file() and os.environ.get("REFRESH_NILE_WATERWAYS") != "1":
        previous=json.loads(DATA.read_text())
        features=previous.get("features",[])
        meta=previous.get("metadata",{})
        kinds=Counter(f.get("properties",{}).get("waterway") for f in features)
        if (previous.get("type")=="FeatureCollection" and
            meta.get("no_synthetic_meander_or_split") is True and
            kinds["river"]>=2 and len(features)>=100):
            report={
                "status":"reused_committed_geographic_reference",
                "total_segments":len(features),
                "counts":dict(kinds),
                "source":meta.get("source_url",ENDPOINT),
                "geometry_file":DATA.relative_to(ROOT).as_posix(),
                "cache_verified":True,
                "historical_accuracy_certified":False,
                "note":"The prior OSM geometry is committed; no invented river lines and no dependency on ArcGIS availability"
            }
            REPORT.write_text(json.dumps(report,indent=2)+"\n")
            print("NILE HYDROGRAPHY",json.dumps(report))
            return
        raise AssertionError("Committed Nile cached geometry is incomplete; refusing to render")
    kept, counts, ids = [], Counter(), set()
    for kind in KINDS:
        for page in range(MAX_PAGES):
            incoming = query(kind, page*PAGE)
            for entry in incoming:
                props = entry.get("properties") or {}
                fid = str(props.get("osm_id2") or props.get("objectid") or entry.get("id"))
                key = (kind, fid)
                if key in ids:
                    continue
                ids.add(key)
                if not entry.get("geometry"):
                    continue
                geom = shape(entry["geometry"]).intersection(EXTENT)
                if geom.is_empty:
                    continue
                for line in (geom.geoms if geom.geom_type == "MultiLineString" else [geom]):
                    if line.geom_type != "LineString" or len(line.coords) < 3:
                        continue
                    # At this inset's review scale, discard sub-kilometre
                    # fragments of modern canals (but retain ALL river lines).
                    km = line.length*111.0
                    if kind == "canal" and km < 1.2:
                        continue
                    if kind == "stream" and km < .9:
                        continue
                    item = {
                        "type":"Feature",
                        "properties":{
                            "id":fid,"waterway":kind,
                            "name":props.get("name") or "",
                            "source":"OSM waterways via ArcGIS mirror",
                            "historically_verified":False,
                            "display_class":"major_river_reference" if kind=="river" else "modern_canal_reference" if kind=="canal" else "minor_watercourse_reference",
                        },
                        "geometry":mapping(line)
                    }
                    kept.append(item);counts[kind]+=1
            if len(incoming) < PAGE:
                break
        else:
            raise RuntimeError("Pagination limit reached for "+kind+"; would truncate network")
    if counts["river"] < 2 or sum(counts.values()) < 8:
        raise RuntimeError("Waterway source too sparse to replace original rivers: "+str(counts))
    contents = {
        "type":"FeatureCollection",
        "metadata":{
            "geography":"Nile Delta review inset, Egypt",
            "bbox_lon_lat":list(BBOX),
            "osm_geometry_date_utc":datetime.now(timezone.utc).isoformat(),
            "source_url":ENDPOINT,
            "historical_validity":"NOT established; these are modern reference geometries",
            "review_period":"1095-1571; medieval outlets and routes require separately verified paleohydrology",
            "no_synthetic_meander_or_split":True
        },
        "features":kept
    }
    DATA.write_text(json.dumps(contents, separators=(",",":"))+"\n", encoding="utf-8")
    report = {
        "status":"modern_geographic_network_acquired_medieval_review_not_certified",
        "bbox":list(BBOX),"counts":dict(counts),
        "total_segments":len(kept),
        "source":ENDPOINT,"geometry_file":DATA.relative_to(ROOT).as_posix(),
        "main_source":"OpenStreetMap contributors via ArcGIS",
        "limitations":[
            "The geometry shows mapped modern watercourses, not all medieval branches.",
            "Canals may have been dug or rerouted after the 16th century.",
            "The western Alexandrian canal and eastern Tinnis route require separate historical georeferencing.",
            "Waterway line endpoints from OSM are not forcibly joined; no fabricated connector lines."
        ]
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"saved":str(DATA),"counts":dict(counts),"total":len(kept)}))
if __name__=="__main__":
    main()
