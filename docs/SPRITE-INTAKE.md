# Upload new Crusader Map paintings without ChatGPT Work

1. Paint sprite images in normal ChatGPT and save original PNG files.
2. Visit [incoming folder](https://github.com/1-tok/crusadersmap/tree/main/assets/sprites/incoming), choose **Add file → Upload files**, drag one or many PNGs and commit to **main**. Keep files under GitHub's web upload limit; use git or Git LFS for larger originals.
3. Optionally add each PNG's same-stem JSON file to declare subject/category/location and exact sheet rectangles. See [metadata example](../assets/sprites/incoming/README.md).
4. GitHub Actions **Sprite intake** starts on PNG upload to main; you may also use **Actions → Sprite intake → Run workflow** to re-run. This uses repository GitHub Actions minutes, not ChatGPT Work credits.
5. Open the run's **sprite-intake-report** artifact or inspect `data/sprites/automated-intake/processing-report.json`. Output PNGs are in `data/sprites/automated-intake/png/`.
6. Inspect `data/sprites/automated-intake/manifest.json` for categorization, historic/repaint review flags and `geographic_placement_ready`. The existing unified `data/sprites/catalog.json` receives the new entries.
7. Inspect `data/sprites/automated-intake/placements-review.geojson` for review availability. Only entries with explicit coordinates **and** coordinate source qualify for geographic placement. Provisional status does not imply historical accuracy.

The workflow commits generated assets and metadata to main via `GITHUB_TOKEN` and does not remove the originals. Its push does not retrigger itself because only intake-folder changes trigger the workflow; commits made using `GITHUB_TOKEN` also do not start new push workflows. To upload large batches without Work, use the GitHub website, GitHub Desktop, or a local `git add assets/sprites/incoming && git commit && git push`.

## Safeguards

* The old catalog and sprite library are preserved. `sprite_catalog.py` rebuilds append the separate persistent intake manifest. Existing catalog entries are not overwritten by intake IDs.
* Exact-duplicate RGBA pixels are registered once; duplicates remain among original uploaded files.
* Original PNGs are never deleted. Single-sprite copies preserve original PNG bytes. Rectangular sheet crops are encoded losslessly.
* Unclear sheets are retained intact, unless the accompanying JSON provides explicit crop boxes or `auto_extract: true` yields conservatively separated alpha components (requires optional NumPy/SciPy).
* Fully transparent images and opaque underlays are retained for review. Unknown names, categories and coordinates are never invented.
* This workflow does not claim painted architecture, geography or coastlines are accurate.
* If branch protections disallow workflow writes to main, use a bot-approved PR strategy or adjust repository Actions permissions to **Read and write**. Do not force-push.

## Run locally

```bash
python -m pip install -r requirements-sprite-intake.txt
python -m unittest discover -s tests -p 'test_sprite_intake.py' -v
python tools/sprite_intake.py
```
