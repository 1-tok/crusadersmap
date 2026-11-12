# Crusader Map — Submit sprite paintings

## [Upload PNGs or ZIPs to GitHub](https://github.com/1-tok/crusadersmap/upload/main/assets/sprites/incoming)

This one-click link opens GitHub's native upload page in the repository's watched inbox. Sign in to GitHub, drag in a ZIP containing the paintings and their metadata sidecars, and commit the **source ZIP** to `main`. The source goes to the inbox only; it is **not** approved for production use.

The existing [Sprite intake GitHub Action](https://github.com/1-tok/crusadersmap/actions/workflows/sprite-intake.yml) processes ZIPs and PNGs without ChatGPT Work credits. It runs extraction, PNG QA, pixel-based deduplication, manifest generation, and creates a review PR containing the processed assets and review-placement records. Merge that review PR after inspection. No auto-merge and no historical certification.

For the full specification, restrictions, and optional site-specific metadata, read [the inbox instructions](assets/sprites/incoming/README.md) and [the workflow reference](docs/SPRITE-ZIP-INTAKE.md).

### One-time Actions settings

Repository owner: verify **Settings → Actions → General** allows workflow write permissions and creation of pull requests. If a workflow reports insufficient permissions, correct that repository setting. The action requests `contents: write` and `pull-requests: write`.

### Important limitation

The link is a GitHub web upload UI, **not** an endpoint that ChatGPT can call with local image attachments. For direct ChatGPT-to-GitHub binary transfer, an authenticated file-capable connector or dedicated upload service still needs to be connected. This repository configuration does not falsely claim that missing capability.

### Asset review policy

- Accepted technical artwork may be provisionally shown on the **review** map.
- Geographic placement requires an identified site and coordinates with evidence.
- Year gates control when a structure existed; a standing Chastellet must not appear in 1180.
- Alpha-edge, native resolution, and historical accuracy remain separate approval checks.
