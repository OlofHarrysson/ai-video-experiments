# Baseline: SDXL feedback

Status: completed initial comparison, 2026-09-06. [Full session report](baseline-results.md).

## Question

Can existing Difforum nodes run a controllable, inexpensive image-feedback animation on RunPod, and what changes with denoise?

## Comparison

Same initial image, incrementing seed sequence and 2D camera; denoise 0.30 / 0.40 / 0.50. See each run's saved graph for exact settings. No new run was made during the organization/research pass.

## Preserved runs

All six render attempts live in this project’s `runs/` folder. Each retains its original settings, receipt, frames and preview; the side-by-side comparison lives in `exports/`.

| Run | Purpose |
| --- | --- |
| [Fixed 0.40, 8 frames](../runs/20260906T081813768800Z-denoise-0.40-8f/) | First short diagnostic. |
| [Fixed 0.50, 8 frames](../runs/20260906T082022695982Z-denoise-0.50-8f/) | Higher-denoise fixed-seed diagnostic. |
| [Increment 0.40, 8 frames](../runs/20260906T082051314505Z-denoise-0.40-8f/) | Seed-mode comparison. |
| [0.30, 40 frames](../runs/20260906T082401782136Z-denoise-0.30-40f/) | Softest result. |
| [0.40, 40 frames](../runs/20260906T082559925877Z-denoise-0.40-40f/) | Middle comparison. |
| [0.50, 40 frames](../runs/20260906T082634500368Z-denoise-0.50-40f/) | Stronger repainting and more playback flicker. |
| [Side-by-side comparison](../exports/2026-09-06-comparison/) | All three full clips together. |

These are ignored local assets, not files available from a fresh Git clone.

## Findings and next decision

The infrastructure and feedback loop work. Incrementing seeds improved short-test detail. Olof's playback assessment supersedes still-frame preference: 0.30 becomes too smooth, 0.50 flickers too much. Preserve that distinction when evaluating the next attempt.

The next priority is continuation and 3D practice. Parameter tuning can use the 0.40 version as a comparison baseline without declaring it a final selection. The entire first session used approximately $0.24 observed credit; the Pod was deleted.
