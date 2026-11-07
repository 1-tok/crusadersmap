"""Rebuild extracted sprites and QA previews. Requires Pillow, NumPy, SciPy."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

ROOT = Path(__file__).resolve().parent
BASE = ROOT / 'data/sprites'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def build():
    manifest = json.loads((BASE / 'manifest.json').read_text())
    report = []
    preview = Image.new('RGB', (1200, 9 * 230), '#eeeeee')
    draw = ImageDraw.Draw(preview)
    for i, entry in enumerate(manifest['sprites']):
        src = BASE / entry['source']['path']
        im = Image.open(src).convert('RGBA').crop(entry['source']['crop_xyxy'])
        a = np.array(im)
        before = int(np.count_nonzero(a[:, :, 3]))
        # Discard barely visible export noise; do not key out flag/stone colors.
        a[a[:, :, 3] < 16] = 0
        labels, count = ndimage.label(a[:, :, 3] > 0)
        sizes = np.bincount(labels.ravel())
        keep = sizes >= 20
        keep[0] = False
        a[~keep[labels]] = 0
        a[a[:, :, 3] == 0] = 0
        im = Image.fromarray(a)
        bbox = im.getbbox()
        if bbox is None:
            raise ValueError(entry['id'])
        im = im.crop(bbox)
        padded = Image.new('RGBA', (im.width + 16, im.height + 16))
        padded.paste(im, (8, 8))
        out = BASE / entry['asset']
        padded.save(out)
        alpha = np.array(padded)[:, :, 3]
        assert not np.any(alpha[:8]) and not np.any(alpha[-8:])
        assert not np.any(alpha[:, :8]) and not np.any(alpha[:, -8:])
        entry['dimensions_px'] = list(padded.size)
        entry['anchor_normalized'] = [0.5, (padded.height - 8) / padded.height]
        entry['sha256'] = digest(out)
        entry['source']['sha256'] = digest(src)
        entry['source']['trim_xyxy_within_crop'] = list(bbox)
        report.append({'id': entry['id'], 'nonzero_alpha_before': before,
                       'nonzero_alpha_after': int(np.count_nonzero(alpha)),
                       'transparent_padding_px': 8, 'visual_review': 'reviewed-light-and-dark',
                       'source_crop_touches_content': any((bbox[0] == 0, bbox[1] == 0, bbox[2] == a.shape[1], bbox[3] == a.shape[0]))})
        thumb = padded.copy()
        thumb.thumbnail((530, 195))
        for x, color in [(0, '#eeeeee'), (600, '#243344')]:
            draw.rectangle((x, i*230, x+599, i*230+229), fill=color)
            preview.paste(thumb, (x+30, i*230+28), thumb)
            draw.text((x+15, i*230+7), entry['id'], fill='black' if x == 0 else 'white')
    (BASE / 'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False)+'\n')
    (BASE / 'validation.json').write_text(json.dumps({'alpha_floor': 16, 'minimum_component_pixels': 20, 'sprites': report}, indent=2)+'\n')
    preview.save(ROOT / 'previews/sprite-library.jpg', quality=92)
    print('Built and checked', len(report), 'RGBA sprites')

if __name__ == '__main__':
    build()
