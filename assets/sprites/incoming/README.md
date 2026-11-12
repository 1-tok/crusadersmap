# Crusader Map — Upload sprites here

**[OPEN SPRITE UPLOAD FORM](https://github.com/1-tok/crusadersmap/upload/main/assets/sprites/incoming)**

This link opens GitHub's **native file-upload interface** in the exact watched directory on `main`. It does not require ChatGPT Work.

## Upload a ZIP or PNG batch

1. Click the upload link above while signed into GitHub as a repository contributor.
2. Drag in a **ZIP** (recommended) or individual **PNG** files with optional same-stem JSON sidecars.
3. Select **Commit directly to the main branch** for the *incoming source archive only*. Do not merge provisional sprite artwork or change production map catalog entries manually.
4. Open **[Sprite intake Actions](https://github.com/1-tok/crusadersmap/actions/workflows/sprite-intake.yml)**. The workflow validates input and opens a separate **review pull request** for the generated sprite PNGs, catalog entries, and placement review metadata.
5. Review the PR report and merge if technically acceptable. Historical accuracy and print approval are deliberately separate from accepting artwork for visual review.

You can also use Git CLI to add a larger ZIP to `assets/sprites/incoming/`, subject to repository file-size and GitHub limits. GitHub's browser file upload typically supports files up to 25 MiB each. For larger originals, Git LFS or an external upload service should be configured separately.

## Structure and behavior

- `assets/sprites/incoming/*.zip` — new uploaded original batch archives (retained unchanged).
- `assets/sprites/incoming/*.png` — single-image uploads (retained unchanged).
- `assets/sprites/incoming/<name>.json` — optional metadata sidecar.
- `tools/sprite_zip_intake.py` — validates and temporarily extracts ZIP input.
- `tools/sprite_intake.py` — validates PNGs, identifies duplicates using pixel hashes, generates RGBA image registration and review placement data.
- `data/sprites/automated-intake/png/` — generated individual sprite assets after the automation PR is merged.
- `data/sprites/automated-intake/manifest.json` — generated asset register.
- `data/sprites/automated-intake/placements-review.geojson` — review placement records, with null geometry when coordinates have not been verified.
- `data/sprites/automated-intake/processing-report.json` — per-file status.

**Safety:** A PNG without verified coordinates is a reviewable sprite, *not* a geographically placed historical site. Nothing is automatically authorized for final printing. Built-period and repaint review flags remain. No duplicate castle variants should be placed at the same historical site without editorial selection.

## Optional ZIP sidecars

For `castle.png`, place `castle.json` beside it in the ZIP:

```json
{
  "subject": "Unidentified mountain fortress",
  "category": "castle",
  "status": "provisional",
  "orientation": "south",
  "anchor_normalized": [0.5, 0.95],
  "target_year": 1180
}
```

If a genuinely identified site has evidence-backed coordinates, you may additionally supply `site_id`, `coordinates` as **[longitude, latitude]**, and `coordinate_source`. Never infer coordinates or historical period correctness from a generic painting.

For a composite sheet, supply a sidecar with explicit `sprites` crop rectangles. Uncertain composites must remain intact and marked for review; do not cut through neighboring roofs or flags.

## What this does *not* solve

This is a direct *GitHub browser* upload interface. GitHub Actions cannot retrieve files that exist only inside a ChatGPT conversation. Eliminating even the drag-and-drop step would require a separate, authenticated, file-capable ChatGPT connector or upload service able to send the binary PNG/ZIP bytes. Merely granting more GitHub permissions will not enable that capability.

Full workflow documentation: [docs/SPRITE-ZIP-INTAKE.md](../../../docs/SPRITE-ZIP-INTAKE.md).
