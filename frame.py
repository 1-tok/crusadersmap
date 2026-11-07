"""Sheet, projection and inset frames for the Crusader States map (36 x 48 in portrait)."""
from pyproj import Transformer
W, H = 10800, 14400                     # 36 x 48 in at 300 dpi
PROJ = "+proj=lcc +lat_1=30 +lat_2=36.5 +lat_0=33.2 +lon_0=35.9 +datum=WGS84 +units=m"
X0, X1 = -486_000, 170_000
Y0, Y1 = -345_000, 530_000
MPP = (X1 - X0) / W                     # metres per print pixel
fwd = Transformer.from_crs("EPSG:4326", PROJ, always_xy=True)
inv = Transformer.from_crs(PROJ, "EPSG:4326", always_xy=True)

def to_px(lon, lat):
    x, y = fwd.transform(lon, lat)
    return (x - X0) / MPP, (Y1 - y) / MPP

INSETS = {
    # name: projection, lon/lat extent, box on the sheet (x, y, w, h) in print px
    "aegean": dict(proj="+proj=lcc +lat_1=36 +lat_2=40 +lat_0=38 +lon_0=25 +datum=WGS84 +units=m",
                   ext=(19.6, 34.7, 30.4, 41.75), title="Romania: the Aegean and Constantinople"),
    "delta": dict(proj="+proj=lcc +lat_1=30 +lat_2=31.5 +lat_0=30.7 +lon_0=31.1 +datum=WGS84 +units=m",
                  ext=(29.5, 27.7, 35.2, 31.8), title="Egypt and Sinai: the Delta to Cairo"),
}
