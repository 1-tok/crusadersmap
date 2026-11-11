#!/usr/bin/env python3
"""Reassemble pixel-identical source sheets stored as top/bottom PNGs."""
from pathlib import Path
from PIL import Image
import json,argparse

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output-dir',required=True)
    args=p.parse_args()
    repo=Path(__file__).resolve().parents[1]
    data=json.loads((repo/'data/sprites/intake/2026-11-10/intake_manifest.json').read_text())
    out=Path(args.output_dir);out.mkdir(parents=True,exist_ok=True)
    for item in data['source_sheets']:
        store=item['storage']
        if store['kind']!='split_vertical_lossless':continue
        canvas=Image.new('RGBA',tuple(item['dimensions_px']))
        for part in store['pieces']:
            pic=Image.open(repo/part['path']).convert('RGBA')
            canvas.paste(pic,tuple(part['offset_xy']))
        path=out/(item['id']+'.png')
        canvas.save(path,optimize=True)
        print(path)

if __name__=='__main__':main()
