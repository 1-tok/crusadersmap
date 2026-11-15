"""Non-destructive Mediterranean water grading for sea tiles and explicitly masked sprite water.

The mask is required for sprite artwork: hue alone cannot distinguish harbor water
from blue roofs, sails or banners. Inputs are never modified in place.
"""
import os
import numpy as np
from PIL import Image

DEEP = np.array([22, 111, 159], dtype=np.float32)  # luminous azure, offshore
COAST = np.array([84, 201, 203], dtype=np.float32)  # turquoise, near shore


def enabled():
    return os.environ.get("MEDITERRANEAN_AZURE_WASH", "1").lower() not in ("0", "false", "off")


def grade_rgb(rgb, coast_weight, strength=0.78):
    """Retain painterly luminance / microtexture while shifting water chroma.

    coast_weight: 0 offshore, 1 at the shoreline; array broadcasts over RGB.
    Explicitly use this only where the caller already knows pixels are water.
    """
    src = np.asarray(rgb, dtype=np.float32)
    if not enabled():
        return src.copy()
    shore = np.clip(np.asarray(coast_weight, dtype=np.float32), 0, 1)
    if shore.ndim == src.ndim - 1:
        shore = shore[..., None]
    target = DEEP * (1 - shore) + COAST * shore
    # Preserve the painted light/dark pattern without reintroducing dark-blue hue.
    luminance = src @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    local = np.clip((luminance - 145) * 0.38, -40, 40)[..., None]
    target = target + local
    return np.clip(src * (1 - strength) + target * strength, 0, 255)


def grade_masked_sprite(sprite, water_mask, coast_weight=0.85, strength=0.78):
    """Grade RGBA only under a reviewed L-mode water mask, preserving original alpha.

    Mask must match sprite dimensions; no automatic blue-pixel detection is allowed.
    """
    im = sprite.convert("RGBA")
    mask = water_mask.convert("L")
    if im.size != mask.size:
        raise ValueError("Sprite water mask must match source sprite dimensions")
    arr = np.asarray(im, dtype=np.float32).copy()
    graded = grade_rgb(arr[..., :3], coast_weight, strength)
    alpha = (np.asarray(mask, dtype=np.float32) / 255.0)[..., None]
    arr[..., :3] = arr[..., :3] * (1 - alpha) + graded * alpha
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
