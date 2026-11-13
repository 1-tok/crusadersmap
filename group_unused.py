"""Sort every image in the usage list into: on the map, superseded, reference only, blocked, held, broken, no room, not picked.
Rewrites deliver/image-usage-and-off-map-list.csv with the group columns and writes deliver/unused-sprites-analysis.md."""
import csv, collections
P = "deliver/image-usage-and-off-map-list.csv"
R = list(csv.DictReader(open(P)))
T = [(("alternate variant", "alternate of", "superseded", "archived earlier", "uncatalogued original"), "Superseded", "a newer or preferred painting of the same site is on the map"),
     (("source sheet", "source master", "atlas sheet", "sheet or", "reference only"), "Reference only", "sheet or master that the individual cut-outs were taken from"),
     (("missing",), "Broken", "file missing from the repository"), (("checkerboard",), "Broken", "checkerboard painted into the background"),
     (("joined",), "Broken", "two pieces joined in one cut-out"),
     (("concept island", "draft or concept island", "island outline"), "Blocked", "island with no coordinates anywhere in the repository"),
     (("island painting", "island on hold"), "Blocked", "held island already covered by a registered overlay, or with no island outline under its centre point"),
     (("named fortress candidate", "no coordinates"), "Blocked", "named site with no coordinates in the repository"),
     (("named monument", "dome of the rock", "pyramids"), "Held", "shows a named monument that already stands in its own city painting"),
     (("repaint-required",), "Held", "marked repaint-required by its own file name"), (("concept sketch",), "Held", "low-resolution concept sketch, superseded by the repaint"),
     (("volcano",), "Removed", "volcano or basalt piece, removed on request"),
     (("hidden",), "No room", "site painting whose place has no room on the sheet"),
     (("not drawn", "not in the build kit", "falls outside"), "Not picked", "in a pool or queue but not placed in this build")]
for r in R:
    r["group"], r["group_reason"] = ("On the map", "") if r["on_map"] == "yes" else next(((g, w) for ks, g, w in T if any(k in r["explanation"].lower() for k in ks)), ("Other", r["explanation"][:70]))
with open(P, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["image", "source", "kind", "label", "on_map", "group", "group_reason", "explanation"]); w.writeheader(); w.writerows(R)
g = collections.Counter(r["group"] for r in R); d = collections.Counter((r["group"], r["group_reason"]) for r in R)
md = ["# Unused sprites: what is superseded and what did not make it", "", "%d images in the repository ledger; %d are on the composite." % (len(R), g["On the map"]), "",
      "| Group | Images | What it means |", "|---|---:|---|"]
for name in ("Superseded", "Reference only", "Blocked", "Held", "Broken", "No room", "Not picked", "Removed", "Other"):
    if g[name]:
        md.append("| %s | %d | %s |" % (name, g[name], "; ".join("%s (%d)" % (b, v) for (a, b), v in sorted(d.items(), key=lambda kv: -kv[1]) if a == name)))
md += ["", "Every image is listed with its group and reason in image-usage-and-off-map-list.csv.", "", "## Images that did not make it, one by one", ""]
for name in ("Blocked", "Held", "Broken", "No room", "Not picked", "Removed"):
    rows = [r for r in R if r["group"] == name]
    if rows:
        md += ["### %s (%d)" % (name, len(rows)), ""] + ["- `%s`: %s" % (r["image"].split("/")[-1], r["explanation"]) for r in rows] + [""]
open("deliver/unused-sprites-analysis.md", "w").write("\n".join(md) + "\n")
print(dict(g))
