"""Ships as sea decoration: a few fixed open-water positions on the main sheet, clear of coasts, panels and insets."""
import terrainsp as TSP
SHIPS = [(34.75, 34.25), (35.15, 35.75), (33.55, 36.05), (34.55, 33.35), (34.05, 32.35), (35.35, 36.55), (32.55, 34.2), (34.9, 36.35)]
USED = []


def draw(c, reg, edition, is_water=None):
    pool = TSP.POOL_SHIP
    for i, (lo, la) in enumerate(SHIPS):
        if not pool:
            return
        x, y = reg.ll_px(lo, la)
        if is_water is not None and not is_water(x, y):
            continue
        TSP.gdraw(c, pool[i % len(pool)], x, y, 170, edition)
        USED.append((pool[i % len(pool)], lo, la))
