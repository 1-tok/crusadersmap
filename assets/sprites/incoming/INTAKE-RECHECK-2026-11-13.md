# Sprite ZIP intake recheck — 2026-11-13

Trigger the existing `Sprite intake` GitHub Actions workflow on `main` to reprocess all archives under `assets/sprites/incoming/` with the safe PNG/JSON extraction and deduplication pipeline.

This file is an audit trigger, not a sprite. Preserve original ZIPs, master-sheet restrictions, provisional/repaint statuses, and separate QA gates for geographic placement and print approval. Review `data/sprites/automated-intake/processing-report.json` on `automation/sprite-intake-review` or the Actions artifact before merging. Archives at repository root are not included in this workflow and must be reconciled separately.
