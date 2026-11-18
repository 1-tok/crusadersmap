#!/usr/bin/env python3
"""Egypt-only GIS fit and visual QA of four real painted river corridor tiles.

Find the best similarity transform LIMITED to uniform scale + translation.
NEVER rotate, mirror, or bend a painting; if the water course does not match,
mark as repaint-required, not production-ready. The stitched PNGs are actual
painted tiles, not procedural river glyphs or detached field stamps.
"""
import json,math,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from scipy.interpolate import interp1d

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.build_egypt_inset_painted_proof import SOURCE,ZOOM,bounds,projected,source_paths,lines

PACK=ROOT/"data/sprites/nile-painted-modular-2026-11-17"
OUT=ROOT/"reports/egypt-nile-painted-modular-review"
REPORT=OUT/"geographic-fit-qa.json"
PREVIEW=OUT/"nile_painted_geographic_trial.jpg"

def painted_water_rows(image):
    rgb=np.array(image.convert("RGB"),dtype=np.float32)
    alpha=np.array(image.getchannel("A"),dtype=np.uint8)
    # Source colors identify the *painted* blue channel, not farms/desert.
    blue=(rgb[:,:,2]>1.11*rgb[:,:,0]) & (rgb[:,:,2]>1.01*rgb[:,:,1]) & (rgb[:,:,2]>88) & (alpha>200)
    points=[]
    for y in range(25,image.height-25,16):
        xx=np.flatnonzero(blue[y])
        xx=xx[(xx>image.width*.22)&(xx<image.width*.81)]
        if len(xx)>12:
            points.append((y,float(np.median(xx))))
    if len(points)<25:raise AssertionError("Painted Nile blue channel cannot be measured")
    return np.array(points)

def map_valley_x_by_y():
    segments=[]
    for category,fid,g in source_paths():
        if category!="valley":continue
        for line in lines(g):
            pts=np.asarray([projected(float(x),float(y)) for x,y in line.coords])
            for a,b in zip(pts[:-1],pts[1:]):
                if np.linalg.norm(b-a)>.01:segments.append((a,b))
    if not segments:raise AssertionError("Actual upstream geographic Nile is unavailable")
    # Sample river x at each horizontal map y. Find nearest to the expected
    # central Nile path when multiple source centerline fragments appear.
    h=round((bounds()[3]-bounds()[1])*ZOOM)
    record=[]
    for yy in range(20,h-20,4):
        xs=[]
        for a,b in segments:
            if min(a[1],b[1])<=yy<=max(a[1],b[1]) and abs(a[1]-b[1])>.0001:
                t=(yy-a[1])/(b[1]-a[1])
                xs.append(a[0]+t*(b[0]-a[0]))
        if xs:record.append((yy,float(np.median(xs))))
    if len(record)<75:raise AssertionError("Actual Nile centerline does not cover candidate inset")
    return np.asarray(record)

def fit(painted,actual):
    # Optimization only scale, x translation, y translation. North stays up.
    ypaint,xpaint=painted.T
    ay,ax=actual.T
    f=interp1d(ay,ax,bounds_error=False,fill_value=np.nan)
    best=None
    for scale in np.arange(.54,1.01,.025):
        for yoff in np.arange(0,1850,24):
            dest_y=yoff+scale*ypaint
            geo=f(dest_y)
            ok=np.isfinite(geo)
            if ok.sum()<len(ypaint)*.90:continue
            xpos=float(np.median(geo[ok]-xpaint[ok]*scale))
            delta=geo[ok]-(xpos+xpaint[ok]*scale)
            mae=float(np.median(np.abs(delta)))
            p90=float(np.quantile(np.abs(delta),.9))
            score=mae+.30*p90
            if best is None or score<best["score"]:
                best={"score":score,"scale":float(scale),"x":xpos,"y":float(yoff),
                      "median_abs_error_px":mae,"p90_abs_error_px":p90,
                      "samples":int(ok.sum()),"map_y_min":float(np.min(dest_y[ok])),
                      "map_y_max":float(np.max(dest_y[ok]))}
    if best is None:raise AssertionError("No south-to-north painted section lies inside the actual Nile valley")
    return best

def main():
    manifest=json.loads((PACK/"manifest.json").read_text())
    if manifest["seams"]["image_join"]!="exact_pixel_reconstruction_pass":
        raise AssertionError("Required pixel-exact tile join not certified")
    src=Image.new("RGBA",tuple(manifest["size"]))
    for entry in manifest["assets"]:
        if entry["rotation_degrees"] or entry["mirror"]:
            raise AssertionError("Nile bank paintings must not rotate/mirror")
        im=Image.open(PACK/entry["path"]).convert("RGBA")
        src.paste(im,(0,entry["source_crop_y0"]))
    painted=painted_water_rows(src)
    actual=map_valley_x_by_y()
    fitdata=fit(painted,actual)
    output_size=(round(src.width*fitdata["scale"]),round(src.height*fitdata["scale"]))
    scaled=src.resize(output_size,Image.Resampling.LANCZOS)
    full=Image.open(SOURCE).convert("RGB")
    x0,y0,x1,y1=bounds()
    area=full.crop((x0,y0,x1,y1))
    area=area.resize((round(area.width*ZOOM),round(area.height*ZOOM)),Image.Resampling.LANCZOS)
    view=area.convert("RGBA")
    view.alpha_composite(scaled,(round(fitdata["x"]),round(fitdata["y"])))
    OUT.mkdir(parents=True,exist_ok=True)
    view.convert("RGB").save(PREVIEW,quality=93)
    # Status is deliberately conservative: moving a painting to the centerline
    # cannot fix a wrong river bend or periods of overpainted city artwork.
    pass_geometry=fitdata["median_abs_error_px"]<=25 and fitdata["p90_abs_error_px"]<=52
    report={
      "status":"geographic_fit_candidate" if pass_geometry else "repaint_required_course_mismatch",
      "source":"exact four painted Nile PNG panels",
      "published_review_image":PREVIEW.relative_to(ROOT).as_posix(),
      "panel_count":4,"seam_reconstruction":"pixel_exact_pass",
      "no_rotation":True,"no_mirroring":True,"no_nonuniform_deformation":True,
      "source_nile_geometry":"Natural Earth river centerline",
      "fit":{"uniform_scale":round(fitdata["scale"],4),
             "translation_xy":[round(fitdata["x"],2),round(fitdata["y"],2)],
             "median_centerline_deviation_px":round(fitdata["median_abs_error_px"],2),
             "p90_centerline_deviation_px":round(fitdata["p90_abs_error_px"],2),
             "samples":fitdata["samples"]},
      "geographic_alignment_pass":pass_geometry,
      "hydrologic_join_at_Cairo":"not_applicable_until_section_promotion",
      "historical_land_use_certified":False,
      "production_approved":False,
      "note":"If mismatch is high, repaint to source bend: do not apply GIS warping or rotate bank sprites."
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print("NILE PAINTED GEOGRAPHIC TRIAL",json.dumps(report))
if __name__=="__main__":main()
