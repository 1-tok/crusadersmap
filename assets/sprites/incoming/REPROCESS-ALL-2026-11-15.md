# Full ZIP intake recheck — 2026-11-15

Project-owner request: reprocess **all new and previously untouched ZIP archives** from the canonical incoming folder, plus the existing pinned root-recovery allowlist, with the repository's existing safe, idempotent GitHub Actions intake.

This file is a harmless watched-path trigger for `.github/workflows/sprite-intake.yml`. The workflow extracts and hashes source PNGs, deduplicates by pixels, validates them, and proposes generated output on `automation/sprite-intake-review` via review PR. It must preserve original ZIPs and existing sprites.

Do not infer geographic placement or historical approval from successful extraction. The authoritative atlas scope is **1096–1600 CE**. Explicit coastal QA applies to Beirut and Tartus azure replacements, including west/north water-side registration against the map.

After successful intake: reconcile named locations with existing gazetteer coordinates, preserve unresolved candidates as review-only, update map preview manifest, run map preflight, rebuild the **full geographic** composite, and present it for owner visual approval.

Trigger origin: owner explicitly requested processing all new/untouched ZIPs for visual rebuild on 2026-11-15.
