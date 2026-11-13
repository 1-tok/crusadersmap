# Sprite intake — compatibility guide (superseded workflow note)

**Current authoritative upload process:** [ZIP/PNG intake and review PR workflow](SPRITE-ZIP-INTAKE.md), [incoming folder](../assets/sprites/incoming/README.md), and [AI context / precedence](AI-CONTEXT.md).

1. Paint and export original high-resolution transparent PNGs; preserve sources.
2. Upload ZIPs or individual PNGs (with optional JSON metadata sidecars) into `assets/sprites/incoming/` on `main` through GitHub's native upload UI, GitHub Desktop or git CLI.
3. The GitHub Actions Sprite intake workflow validates/extracts and deduplicates artwork, writes processing reports and opens or updates `automation/sprite-intake-review` as a PR **for generated outputs**.
4. Review PNG technical QA, duplicates, identity, dates, metadata and any geographic anchors. Merge the generated PR only after inspection. Neither upload nor merged intake is production/historical certification.
5. Inspect `data/sprites/automated-intake/processing-report.json`, `manifest.json` and `placements-review.geojson` after the generated PR is merged. A missing or null coordinate means **not geographically placed**; a review-gallery item is not a map placement.
6. Verify actual composite rendering separately using [final build readiness](FINAL-MAP-BUILD-READINESS.md). Keep originals, legacy catalog entries and repaint-required flags.

The earlier version of this page described generated assets being pushed automatically to `main`; it is superseded by the newer PR-based ZIP workflow. The source upload itself still goes to `main`. Do not force-push or silently modify the published catalog.

## Safeguards
- Exact-duplicate pixel images are deduplicated in generated inventory while originals remain.
- Unknown subjects, categories, chronology and locations are not invented.
- Uncertain composite sheets are not automatically treated as independently cuttable sprites without verified crops.
- Technical PNG QA does not verify architecture, geography, shoreline, alpha-edge quality at print scale or production readiness.
- GitHub Actions cannot fetch an image that exists only inside a ChatGPT conversation; a real binary upload is still required.

## Local checks
```bash
python -m pip install -r requirements-sprite-intake.txt
python -m unittest discover -s tests -p 'test_sprite_intake.py' -v
python tools/sprite_intake.py
```
