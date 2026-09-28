# Watermelon in a scene

Authorized 2026-09-28 11:23:36 UTC: maximum one hour and $10 new spend. Deadline 12:23:36 UTC. Compare insertion into a fixed tabletop scene, full-scene generation from a layout, and short authored motion. Preserve every result, assess geometry, background changes, grounding and temporal consistency. Prior spatial-control-lab outputs are references; their cost is excluded.

Working allowances: $0.25 per Sunburst image (token-billed, deliberately above the published typical table), $0.072 per Seedream edit with two inputs, and verified configuration-specific prices for video. Reserve $2 for retries; stop all new submissions before the deadline with time left to collect and review.

## Results and reproduction

Read [the screened report](report.md), [run index](run-index.json), [still measurements](still-measurements.json) and [video measurements](video-measurements.json). The run index resolves CDN inputs to local assets and hashes where available. Original exact API JSON, request receipts and results are retained inside ignored run folders. These local media assets are required to reproduce the reviews; a Git clone alone does not contain them.

The existing [Remotion guide project](../../../remotion/projects/watermelon-guides/README.md) owns authored geometry and comparison rendering. From that directory, with its dependencies installed:

```sh
node scripts/render-scene.mjs
node scripts/render-scene-comparison.mjs
node scripts/render-scene-lock.mjs
```

The first script expects the preserved background output and generates scene, mask and layout assets. The second expects all seven Sunburst stills and the two selected native videos. The third reuses those prepared public assets to render deterministic background compositing. `public/` assets and rendered media are ignored.

From the repository root, review preserved model outputs and refresh the compact evidence:

```sh
uv run --script apps/comfyui/projects/watermelon-scene/collect_fal.py
uv run --script apps/comfyui/projects/watermelon-scene/review_stills.py
uv run --script apps/comfyui/projects/watermelon-scene/review_video.py
python3 apps/comfyui/projects/watermelon-scene/record_results.py
```

`collect_fal.py` downloads from the original saved result URLs only when the corresponding output is absent. It preserves the originals, verifies images through Pillow and videos through ffprobe, and records hashes. `inspect_jobs.py` lists submissions without a saved result receipt; it does not submit or cancel jobs.
