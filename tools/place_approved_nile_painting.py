"""Production placement of the *approved painted* Nile Valley section.

Only four genuine approved panels V2 are used. They are stitched at original
pixel boundaries, without rotation, mirroring or warping, and overlaid into
the Egypt inset at the validated Natural Earth geographic fit. City and
fortress art and every map label are rendered AFTER this underlay.

This places ONE proven river section only; the Cairo and southern extensions
remain separate follow-on work. No claim of full-Nile seam certification.
"""
import hashlib
import json
from pathlib import Path

import cairo
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"data/sprites/nile-painted-modular-2026-11-17-v2"
QA=ROOT/"reports/egypt-nile-painted-modular-review/geographic-fit-v2-qa.json"
REPORT=ROOT/"reports/rebuild-2026-11-12/nile-painted-production-placement.json"
_BUFFERS=[]
_REPORT=None

def draw(c, reg, edition):
    global _REPORT
    if edition!="colour":
        _REPORT={"status":"not_applicable_to_monochrome"}
        return
    source=json.loads((PACK/"manifest.json").read_text())
    fit=json.loads(QA.read_text())
    if not (source["exact_pixel_stitch"] and source["source_caption_and_border_removed"]
            and fit["geographic_alignment_pass"] and fit["status"]=="geographic_fit_candidate"):
        raise AssertionError("Painted Nile section has not passed approval-gated GIS QA")
    if source["image_size"] != [1144,1203] or len(source["assets"])!=4:
        raise AssertionError("Unexpected production Nile painted panel manifest")
    if reg.w!=4800:
        raise AssertionError(f"Egypt inset scaled geographic region changed: {reg.w}")
    # Review enlarged the 0.30-scale atlas by a further factor of 2.2.
    # Convert its known fit back into the native inset coordinates exactly.
    conversion=1.0/(.30*2.2)
    uniform_scale=fit["fit"]["uniform_scale"]*conversion
    x_native=fit["fit"]["translation_xy"][0]*conversion
    y_native=fit["fit"]["translation_xy"][1]*conversion
    native_w=round(source["image_size"][0]*uniform_scale)
    native_h=round(source["image_size"][1]*uniform_scale)
    if not (.3<uniform_scale<1.5 and 0<x_native<reg.w and 0<y_native<reg.h):
        raise AssertionError("Nile painted source outside geographic frame")
    if native_w<150 or native_h<150:
        raise AssertionError("Painted Nile production section too small")
    stitched=Image.new("RGBA",tuple(source["image_size"]),(0,0,0,0))
    boundaries=[]
    for panel in sorted(source["assets"],key=lambda x:x["source_crop_y0"]):
        if panel["rotation_degrees"] or panel["mirror"]:
            raise AssertionError("Riverbank sprite rotation and mirroring forbidden")
        path=PACK/panel["path"]
        with Image.open(path) as im:
            if im.mode!="RGBA":
                raise AssertionError("Expected genuine RGBA Nile painting")
            panel_image=im.copy()
        if panel_image.width!=source["image_size"][0] or panel_image.height!=panel["source_crop_y1"]-panel["source_crop_y0"]:
            raise AssertionError("Painted Nile section has inconsistent tile dimensions")
        boundaries.append((panel["source_crop_y0"],panel["source_crop_y1"]))
        # Real source tiles come from the same continuous painting, stitch
        # exactly along their shared pixel boundaries.
        stitched.paste(panel_image,(0,panel["source_crop_y0"]))
    if boundaries!=[(0,300),(300,600),(600,900),(900,1203)]:
        raise AssertionError("Painted river panel sequence has a gap or overlap")
    resized=stitched.resize((native_w,native_h),Image.Resampling.LANCZOS)
    rgba=np.asarray(resized,dtype=np.float32).copy()
    # Fade only the OUTER footprint into the existing desert/lowland
    # underlay. Never fade between the four source tiles.
    px=np.arange(native_w,dtype=np.float32)+.5
    py=np.arange(native_h,dtype=np.float32)+.5
    xedge=np.minimum(px,native_w-px)
    yedge=np.minimum(py,native_h-py)
    fx=np.clip(xedge/max(1,native_w*.09),0,1)
    fy=np.clip(yedge/max(1,native_h*.07),0,1)
    alpha=rgba[:,:,3]/255*np.minimum(fx[None,:],fy[:,None])
    # Cairo FORMAT_ARGB32 expects premultiplied BGRA bytes.
    bgra=np.empty((native_h,native_w,4),dtype=np.uint8)
    bgra[:,:,:3]=(rgba[:,:,[2,1,0]]*alpha[:,:,None]).astype(np.uint8)
    bgra[:,:,3]=np.uint8(np.clip(alpha*255,0,255))
    backing=bytearray(bgra.tobytes())
    _BUFFERS.append(backing)
    surface=cairo.ImageSurface.create_for_data(backing,cairo.FORMAT_ARGB32,native_w,native_h,native_w*4)
    c.save()
    try:
        c.rectangle(0,0,reg.w,reg.h)
        c.clip()
        c.set_source_surface(surface,round(x_native),round(y_native))
        c.get_source().set_filter(cairo.FILTER_BEST)
        c.paint()
    finally:
        c.restore()
    visible=int(np.count_nonzero(alpha>.1))
    if visible<15_000:
        raise AssertionError("Approved painted Nile image was not visibly overlaid")
    _REPORT={
        "status":"production_atlas_painted_section_active",
        "source_asset_batch":"data/sprites/nile-painted-modular-2026-11-17-v2",
        "panel_count":4,
        "pixel_exact_original_source_seams":True,
        "rotation_degrees":0,"mirrored":False,"nonuniform_distortion":False,
        "native_egypt_inset_pixel_xy":[round(x_native,3),round(y_native,3)],
        "source_scale_to_4800px_region":round(uniform_scale,5),
        "drawn_dimensions_px":[native_w,native_h],
        "visible_pixels_alpha_gt_0_1":visible,
        "draw_order":"after terrain ink; before city, fortress, and map labels",
        "upstream_and_delta_extensions":"not yet painted or connected",
        "geo_fit_median_deviation_in_enlarged_preview_px":fit["fit"]["median_centerline_deviation_px"],
        "historical_landuse_certified":False,
    }

def save_report():
    if not _REPORT or _REPORT["status"]!="production_atlas_painted_section_active":
        raise AssertionError("Production Nile painting never rendered")
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(_REPORT,indent=2)+"\n")
    return _REPORT
