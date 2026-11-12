"""Terrain gap report: land cells of the rendered sheet that are still flat wash (little painted detail)."""
import json, os, csv
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ZONES = [("Cyprus", 32.2, 34.5, 34.7, 35.75), ("Cilicia and the Taurus", 32.5, 36.0, 37.2, 38.5), ("North Syria (Antioch, Aleppo)", 35.7, 35.0, 38.2, 37.2),
         ("Syrian coast and Orontes", 35.7, 33.9, 37.0, 35.0), ("Lebanon and Damascus", 35.1, 33.0, 37.0, 33.9), ("Galilee, Samaria, Judea", 34.2, 31.2, 35.6, 33.0),
         ("Transjordan and Hauran", 35.6, 30.0, 37.5, 33.0), ("Syrian desert", 37.0, 30.0, 41.0, 36.0), ("Negev, Sinai, Arabah", 32.6, 27.0, 35.6, 31.2),
         ("Upper Mesopotamia", 37.2, 36.0, 41.0, 38.5)]


def zone(lon, lat, key):
    if key == "aegean":
        return "Aegean inset: " + ("Greece and the Balkans" if lon < 24.5 else ("islands and Crete" if lon < 26.6 and lat < 39.9 else "Anatolia and Thrace"))
    if key == "delta":
        return "Egypt inset: " + ("Delta" if lat > 30.4 and 30.0 < lon < 32.4 else ("Sinai" if lon > 32.4 else "Western and Eastern deserts"))
    for n, w, s, e, nn in ZONES:
        if w <= lon < e and s <= lat < nn:
            return n
    return "other"


def run(img, TER, REG, BOX, hard=()):
    S = img.shape[1] / 10800.0
    lum = img[..., :3].astype(np.float32).mean(axis=2)
    rows = []
    for k in ("main", "aegean", "delta"):
        reg = REG[k]; t = TER[k]; bx, by = BOX[k]
        land = t.land_l; lh, lw = land.shape
        cell = 320 if k == "main" else 200
        for gy in range(int(reg.h // cell)):
            for gx in range(int(reg.w // cell)):
                x0, y0 = gx * cell, gy * cell
                if not land[min(lh - 1, int((y0 + cell / 2) / reg.h * lh)), min(lw - 1, int((x0 + cell / 2) / reg.w * lw))]:
                    continue
                X0 = bx + x0; Y0 = by + y0
                if any(r[0] < X0 + cell and X0 < r[2] and r[1] < Y0 + cell and Y0 < r[3] for r in hard):
                    continue
                if k == "main" and any(BOX[q][0] - 20 < X0 + cell / 2 < BOX[q][0] + REG[q].w + 20 and BOX[q][1] - 20 < Y0 + cell / 2 < BOX[q][1] + REG[q].h + 20 for q in ("aegean", "delta")):
                    continue
                p = lum[int(Y0 * S):int((Y0 + cell) * S), int(X0 * S):int((X0 + cell) * S)]
                if p.size < 50:
                    continue
                sd = float(p.std())
                Xm = reg.x0 + (x0 + cell / 2) / reg.w * (reg.x1 - reg.x0); Ym = reg.y1 - (y0 + cell / 2) / reg.h * (reg.y1 - reg.y0)
                lon, lat = reg.inv.transform(Xm, Ym)
                rows.append(dict(region=k, zone=zone(lon, lat, k), lon=round(float(lon), 2), lat=round(float(lat), 2), sheet_x=int(X0), sheet_y=int(Y0),
                                 cell_px=cell, detail=round(sd, 1), flat=sd < 9.0))
    json.dump(rows, open(os.path.join(HERE, "out", "terrain_cells.json"), "w"))
    return rows
