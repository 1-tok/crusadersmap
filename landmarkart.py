"""Landmark landscapes at their own coordinates."""
import terrainsp as TSP
MARKS = [("cedars-of-lebanon", 36.05, 34.24, 330), ("mount-hermon", 35.86, 33.42, 380), ("cappadocia", 34.83, 38.64, 380)]
USED = []


def draw(c, reg, edition):
    for key, lo, la, wd in MARKS:
        fn = next((f for f in TSP.G2P.get("landmark", []) if key in f), None)
        x, y = reg.ll_px(lo, la)
        if fn is None or not (60 < x < reg.w - 60 and 60 < y < reg.h - 60):
            continue
        TSP.gdraw(c, fn, x, y + 0.35 * wd * 0.5, wd, edition); USED.append(key)
