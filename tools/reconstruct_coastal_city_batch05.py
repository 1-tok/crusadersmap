#!/usr/bin/env python3
"""Reassemble SHA-256 pinned coastal Batch 05 PNGs from raw Git part blobs."""
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/manifests/coastal-city-batch05-regenerated-2026-11-16.json"
OUT = ROOT / "assets/sprites/qa_provisional/coastal-batch05-2026-11-16"
REPORT = ROOT / "reports/coastal-city-batch05-2026-11-16/reconstruction-qa.json"

def main():
    batch = json.loads(MANIFEST.read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for spec in batch["files"]:
        chunks = [ROOT / p for p in spec["parts"]]
        if not all(p.is_file() for p in chunks):
            raise FileNotFoundError("Missing one or more binary parts for " + spec["city"])
        data = b"".join(p.read_bytes() for p in chunks)
        digest = hashlib.sha256(data).hexdigest()
        if len(data) != spec["size_bytes"] or digest != spec["sha256"]:
            raise ValueError("Binary integrity failure for " + spec["city"])
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("Not PNG: " + spec["city"])
        dest = OUT / spec["filename"]
        dest.write_bytes(data)
        with Image.open(dest) as im:
            im.load()
            if list(im.size) != spec["expected_dimensions"] or im.mode != "RGBA":
                raise ValueError("Unexpected image dimensions or mode: " + spec["city"])
            alpha_min, alpha_max = im.getchannel("A").getextrema()
            if alpha_min != 0 or alpha_max < 200:
                raise ValueError("Invalid transparency: " + spec["city"])
            records.append({"city":spec["city"],"path":str(dest.relative_to(ROOT)),"size_bytes":len(data),
                            "sha256":digest,"dimensions":list(im.size),"alpha_extrema":[alpha_min,alpha_max],
                            "coastal_orientation":spec["coastal_orientation"],
                            "historical_accuracy":"pending_review","map_placement":"pending_review"})
    REPORT.write_text(json.dumps({"batch":batch["batch"],"status":"SIX_ORIGINAL_PNGS_RECONSTRUCTED_QA_PROVISIONAL",
                                   "files":records,"approved_for_map_placement":False},indent=2)+"\n")
    print("Reconstructed",len(records),"PNG assets. Byte identity verified. Placement pending review.")
    if len(records)!=6: raise ValueError("Expected six city sprites")
if __name__=="__main__": main()
