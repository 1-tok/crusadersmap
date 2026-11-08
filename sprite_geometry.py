"""Sprite sheet anchors matching build_stage1.Region inset layout without loading terrain."""
from functools import lru_cache
from pyproj import Transformer
import frame


@lru_cache(None)
def inset_geometry(region):
    cfg=frame.INSETS[region]
    f=Transformer.from_crs('EPSG:4326',cfg['proj'],always_xy=True)
    lo0,la0,lo1,la1=cfg['ext']
    x0,_=f.transform(lo0,la1);x1,_=f.transform(lo1,la1)
    _,y1=f.transform((lo0+lo1)/2,la1);_,y0=f.transform(lo0,la0)
    width=4800;height=round(width*(y1-y0)/(x1-x0))
    bx,by=(190,190) if region=='aegean' else (190,13760-height)
    return f,x0,x1,y0,y1,width,height,bx,by


def sheet_anchor(entry):
    region=entry.get('map_region','main')
    lon,lat=entry['coordinates']
    if region=='main':return frame.to_px(lon,lat)
    f,x0,x1,y0,y1,w,h,bx,by=inset_geometry(region)
    x,y=f.transform(lon,lat)
    return bx+(x-x0)/(x1-x0)*w,by+(y1-y)/(y1-y0)*h
