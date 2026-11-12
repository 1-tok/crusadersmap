#!/usr/bin/env python3
"""Conservative, repeatable PNG intake. Never alters input images or legacy entries."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path
from PIL import Image, UnidentifiedImageError

CATEGORIES = {
    "city", "town", "village", "settlement", "castle", "fortification",
    "church", "mosque", "monastery", "landmark", "port", "harbor", "island",
    "mountain", "hill", "escarpment", "desert", "steppe", "scrubland",
    "farmland", "river", "lake", "marsh", "coastal_underlay", "road",
    "bridge", "terrain_transition", "rectangular_underlay", "terrain",
}
STATUS = {"approved", "provisional", "repaint_required", "placement_review_required"}
DEFAULTS = {"schema_version": 1, "assets": []}

def read_json(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(obj, ensure_ascii=False, indent=2) + "\n"
    if not path.exists() or path.read_text(encoding="utf-8") != data:
        path.write_text(data, encoding="utf-8")

def slug(value):
    return re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-") or "untitled"

def sha(data):
    return hashlib.sha256(data).hexdigest()

def valid_coords(value):
    return (isinstance(value, list) and len(value) == 2
            and all(type(v) in (int, float) for v in value)
            and -180 <= value[0] <= 180 and -90 <= value[1] <= 90)

def pixel_digest(im):
    return sha(im.width.to_bytes(4, "big") + im.height.to_bytes(4, "big") + im.convert("RGBA").tobytes())

def components(im):
    """Only split sheet with unmistakably disjoint large alpha islands and wide gaps."""
    try:
        import numpy as np
        from scipy import ndimage
    except ImportError:
        return []
    a = np.asarray(im.convert("RGBA").getchannel("A")) > 8
    labels, n = ndimage.label(a, structure=np.ones((3, 3), dtype=bool))
    if n < 2 or n > 32:
        return []
    objects = ndimage.find_objects(labels)
    boxes = []
    for i, region in enumerate(objects, 1):
        if region is None:
            continue
        ys, xs = region
        area = int((labels[region] == i).sum())
        if area < 1000 or (xs.stop-xs.start) < 50 or (ys.stop-ys.start) < 50:
            return []
        boxes.append((xs.start, ys.start, xs.stop, ys.stop))
    if len(boxes) < 2:
        return []
    # Require each candidate to have at least 6 pixels of separation from others.
    for i, a in enumerate(boxes):
        for b in boxes[i+1:]:
            dx = max(0, a[0]-b[2], b[0]-a[2])
            dy = max(0, a[1]-b[3], b[1]-a[3])
            if max(dx, dy) < 6:
                return []
    return sorted(boxes, key=lambda b: (b[1], b[0]))

def extract(im, meta):
    if "sprites" in meta:
        rows = meta["sprites"]
        if not isinstance(rows, list) or not rows:
            raise ValueError("sprites must be a nonempty array")
        boxes = []
        for part in rows:
            b = part.get("box")
            if (not isinstance(b, list) or len(b) != 4
                    or not all(type(v) is int for v in b)
                    or not (0 <= b[0] < b[2] <= im.width and 0 <= b[1] < b[3] <= im.height)):
                raise ValueError("invalid sheet box")
            boxes.append((tuple(b), part))
        return boxes, "declared_rectangles"
    auto = components(im) if meta.get("auto_extract") is True else []
    if auto:
        return [(b, {}) for b in auto], "isolated_alpha_components"
    return [((0, 0, im.width, im.height), {})], "intact_image_or_uncertain_sheet"

def unpack_archives(incoming):
    """Safely unpack only root-level PNG and matching JSON files from uploaded ZIPs.

    Preserve ZIP originals. Never overwrite an existing intake file.
    """
    for archive in sorted(incoming.glob("*.zip")):
        with zipfile.ZipFile(archive) as zf:
            members = zf.infolist()
            if len(members) > 256 or sum(info.file_size for info in members) > 250_000_000:
                raise ValueError(f"ZIP exceeds safety limits: {archive.name}")
            for info in members:
                name = info.filename
                # Reject traversal, nested images and hidden paths. The original
                # image collage may be stored in originals/ in the ZIP, untouched.
                if (info.is_dir() or "/" in name or "\\\\" in name
                        or name.startswith(".") or Path(name).suffix.lower() not in (".png", ".json")):
                    continue
                target = incoming / name
                payload = zf.read(info)
                if len(payload) != info.file_size:
                    raise ValueError(f"Invalid ZIP member size: {name}")
                if target.exists():
                    if target.read_bytes() != payload:
                        raise ValueError(f"ZIP member conflicts with existing intake: {name}")
                else:
                    target.write_bytes(payload)


def process(root):
    incoming = root / "assets/sprites/incoming"
    base = root / "data/sprites"
    if incoming.exists():
        unpack_archives(incoming)
    out = base / "automated-intake"
    registry_file = out / "manifest.json"
    registry = read_json(registry_file, dict(DEFAULTS))
    registry.setdefault("assets", [])
    known = {e["id"]: e for e in registry["assets"]}
    digests = {e["technical_qa"]["pixel_sha256"]: e["id"] for e in registry["assets"]
               if e.get("technical_qa", {}).get("pixel_sha256")}
    # Compare against all currently cataloged pixels, not only prior incoming batches.
    existing_catalog = read_json(base / "catalog.json", {"assets": []})
    for existing in existing_catalog.get("assets", []):
        key = existing.get("technical_qa", {}).get("pixel_sha256")
        if key:
            digests.setdefault(key, existing["id"])
    report = {"schema_version": 1, "results": [], "registered": 0, "duplicates": 0, "errors": 0}
    for path in sorted(incoming.rglob("*")) if incoming.exists() else []:
        if not path.is_file() or path.suffix.lower() != ".png":
            continue
        relative = path.relative_to(root).as_posix()
        entry = {"source": relative}
        try:
            meta = read_json(path.with_suffix(".json"), {}) or {}
            if not isinstance(meta, dict):
                raise ValueError("sidecar must be a JSON object")
            original = path.read_bytes()
            with Image.open(path) as image:
                if image.format != "PNG":
                    raise ValueError("not a PNG")
                image.verify()
            with Image.open(path) as image:
                image.load()
                image = image.convert("RGBA")
                pieces, method = extract(image, meta)
                source_hash = sha(original)
                entry["extraction"] = method
                entry["pieces"] = []
                for index, (box, part) in enumerate(pieces, 1):
                    options = dict(meta)
                    options.pop("sprites", None)
                    options.update(part)
                    cropped = image.crop(box)
                    digest = pixel_digest(cropped)
                    category = options.get("category", "unclassified")
                    if category not in CATEGORIES:
                        category = "unclassified"
                    subject = str(options.get("subject", path.stem))
                    ident = "INTAKE-" + digest[:20]
                    if digest in digests or ident in known:
                        entry["pieces"].append({"id": digests.get(digest, ident), "status": "duplicate"})
                        report["duplicates"] += 1
                        continue
                    status = options.get("status", "provisional")
                    if status not in STATUS:
                        status = "placement_review_required"
                    coords = options.get("coordinates")
                    ready = valid_coords(coords) and bool(options.get("coordinate_source"))
                    alpha = cropped.getchannel("A")
                    extrema = alpha.getextrema()
                    bounds = alpha.getbbox()
                    issues = []
                    if not bounds:
                        issues.append("fully_transparent")
                    if extrema[0] == 255:
                        issues.append("opaque_background_verify_intended_underlay")
                    if category == "unclassified":
                        issues.append("category_unverified")
                    if not ready:
                        issues.append("coordinates_unverified")
                    if options.get("orientation") != "south":
                        issues.append("southern_pov_unverified")
                    if method == "intact_image_or_uncertain_sheet" and ("sheet" in path.stem.lower() or "collage" in path.stem.lower()):
                        issues.append("possible_unsplit_sheet")
                    # A valid PNG remains an available provisional artwork, even if QC flags exist.
                    filename = f"{slug(subject)}-{digest[:12]}.png"
                    dest = out / "png" / filename
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    if not dest.exists():
                        if box == (0, 0, image.width, image.height):
                            dest.write_bytes(original)  # exact bytes: no lossy re-encoding
                        else:
                            cropped.save(dest, "PNG")
                    else:
                        with Image.open(dest) as check:
                            if pixel_digest(check) != digest:
                                raise RuntimeError(f"nonmatching existing output: {dest}")
                    year = options.get("target_year", 1180)
                    if type(year) is not int:
                        year = 1180
                    width = options.get("display_width_units", 512)
                    if type(width) not in (int, float) or not (1 <= width <= 10800):
                        width = 512
                    site_id = slug(options.get("site_id") or subject)
                    record = {
                        "id": ident, "site_id": site_id, "name": subject,
                        "display_title": subject, "category": category,
                        "asset": dest.relative_to(base).as_posix(),
                        "variant": "automated-intake", "source": {
                            "path": relative, "sha256": source_hash,
                            "crop_xyxy": list(box), "extraction": method},
                        "coordinates": coords if ready else None,
                        "coordinate_source": options.get("coordinate_source") if ready else None,
                        "coordinates_surveyed": False,
                        "coordinate_evidence": {"status": "user_supplied_unverified" if ready else "missing"},
                        "geographic_placement_ready": bool(ready),
                        "map_region": options.get("map_region", "main"),
                        "anchor_normalized": options.get("anchor_normalized", [0.5, 0.95]),
                        "display_width_units": width, "selection_priority": 1,
                        "placement_view": "atlas",
                        "map_layers": [category, options.get("map_region", "main")],
                        "layer_priority": options.get("layer_priority"),
                        "water_side": options.get("water_side"),
                        "overlap_instructions": options.get("overlap_instructions", "transparent alpha overlap; review edges"),
                        "orientation": options.get("orientation", "unverified"),
                        "historical": {"target_year": year, "accuracy": "unverified",
                            "requires_historical_review": True, "requires_repaint_review": status == "repaint_required"},
                        "historical_accuracy_certified": False,
                        "approval": {"status": status, "provisional_map_use": True,
                            "repaint_later": status == "repaint_required",
                            "historical_accuracy_certified": False},
                        "approval_for_placement": bool(ready),
                        "placement_review_required": not ready,
                        "period_1180_eligible": year == 1180,
                        "availability": {"from_year": year, "through_year": year,
                            "basis": "unverified image brief; not verified building period"},
                        "technical_qa": {"status": "pass", "mode": "RGBA",
                            "dimensions_px": list(cropped.size), "alpha_extrema": list(extrema),
                            "painted_bounds_xyxy": list(bounds) if bounds else None,
                            "pixel_sha256": digest, "sha256": sha(dest.read_bytes()),
                            "review_flags": issues},
                        "review_required": True, "repaint_required": status == "repaint_required",
                        "review_flags": issues,
                    }
                    known[ident] = record
                    digests[digest] = ident
                    report["registered"] += 1
                    entry["pieces"].append({"id": ident, "status": status, "asset": record["asset"]})
            report["results"].append(entry)
        except (OSError, ValueError, UnidentifiedImageError, RuntimeError, json.JSONDecodeError) as exc:
            entry["error"] = str(exc)
            report["errors"] += 1
            report["results"].append(entry)
    registry["assets"] = sorted(known.values(), key=lambda e: e["id"])
    write_json(registry_file, registry)
    # Do not mutate legacy entries, only add new intake IDs to the existing generated catalog.
    catalog_file = base / "catalog.json"
    if catalog_file.exists():
        catalog = read_json(catalog_file)
        legacy = [e for e in catalog["assets"] if e.get("variant") != "automated-intake"]
        catalog["assets"] = legacy + registry["assets"]
        write_json(catalog_file, catalog)
    features = []
    for e in registry["assets"]:
        features.append({"type": "Feature", "id": e["id"],
                         "geometry": {"type": "Point", "coordinates": e["coordinates"]} if e["geographic_placement_ready"] else None,
                         "properties": {"sprite_id": e["id"], "asset": "data/sprites/" + e["asset"],
                             "site_id": e["site_id"], "approval": e["approval"]["status"],
                             "approval_for_review_placement": True,
                             "geographic_placement_ready": e["geographic_placement_ready"],
                             "historical_accuracy_certified": False,
                             "anchor_normalized": e["anchor_normalized"],
                             "display_width_units": e["display_width_units"],
                             "review_flags": e["review_flags"]}})
    write_json(out / "placements-review.geojson", {"type": "FeatureCollection", "features": features})
    write_json(out / "processing-report.json", report)
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = process(args.root.resolve())
    print(json.dumps(result, indent=2))
    raise SystemExit(1 if result["errors"] else 0)
