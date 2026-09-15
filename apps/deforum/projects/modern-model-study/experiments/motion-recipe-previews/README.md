# Floating drift and travelling look-around

2026-09-15. Olof approves previewing the first two reference-inspired recipes from the [motion palette](../../../../../../docs/motion-palette.md). Both use the same existing pomegranate-city painting, with spatial movement only.

| Preview | Movement | Assistant observation |
| --- | --- | --- |
| [Floating drift](../../exports/motion-recipe-previews-v001/floating-drift/preview.mp4) | Horizontal and vertical travel reverse at different times, with a small underlying drift, gentle roll and gradual scale change | Clear gliding path; the main fruit and bridge remain recognizable. Larger vertical travel exposes reflected artwork along the lower edge. |
| [Travelling look-around](../../exports/motion-recipe-previews-v001/travelling-look-around/preview.mp4) | Overlapping travel, flat-sheet plane tilts, roll and push/pull | More visible perspective change, especially on the fruit and stairs. Later sheet narrowing exposes duplicate forms at the sides. This is not depth parallax or an object turning to show hidden surfaces. |

Human preference is pending. Compare them in the [linked reviewer](http://localhost:3028/motion-recipes); the same comparison is currently the root page. The [previous film comparison](http://localhost:3028/continuous-motion) remains available.

## What is held fixed

- One source painting: `exports/continuous-motion-hour-v001/c3-banking-voyage/anchors/0000.png`. Both frame-zero PNGs are identical after the shared 960×640 Lanczos resize.
- Ten seconds, 240 frames, 24 fps, **1× time**. There is no additional 1.5× speedup. Preserve these displayed timings explicitly if a selected path is integrated into a faster recurrent delivery.
- Each frame samples the original image with the shared relative warp from time zero to that frame's timestamp. Lanczos interpolation here means spatial image resampling; no RIFE frame generation is involved.
- No new diffusion, depth inference, optical flow or cloud resources. Every subsequent frame is labelled as a spatial warp of the single source painting in the reviewer.
- Reflected borders supply texture where the mapping goes outside the source. Their repeated shapes are boundary filling, not newly generated objects. No attempt to repair them is included in this motion comparison.

These previews isolate the planned geometry. They do not simulate repeated resampling or a diffusion model's reinterpretation. Floating drift approximates phase-offset travel with existing eased phrases; it does not reproduce Safety Marc's sine curves or turbulent guide field. Look-around similarly adapts the combined travel/turn idea without the original depth and guide contributions.

## Reproduce and inspect

From `apps/deforum`, run `uv run --locked python projects/modern-model-study/experiments/motion-recipe-previews/render.py <case>`. Configurations are in `configs/`; outputs refuse overwrite. `build_review.py` rebuilds the saved `media_review/sessions/motion-recipes.json` comparison. Devrun owns the reviewer service; routine delivery uses terminal verification.

Both videos fully decode at the expected dimensions, count, duration and frame rate. Every raw frame differs from the others, every sampled transform is finite and invertible, and the source image remains unchanged. Source/config/runner hashes, raw-frame hashes, sampled PNG hashes and video hashes are preserved. The executed runner snapshots accompany their immutable manifests.

Review uses overviews at 0, 2, 4, 6, 8 and 9 seconds plus dense windows around each recipe's slowest measured geometric interval. Those window frames reproduce the recorded raw pixel hashes. The minimum median grid speed is approximately 31 px/s for floating and 9 px/s for look-around at preview resolution; these are geometric diagnostics, not quality or perceptual-smoothness scores. Raw samples, contact sheets and verification receipts are in `exports/motion-recipe-previews-v001/`.
