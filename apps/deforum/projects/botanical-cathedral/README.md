# Botanical cathedral

A practice scene for learning an iterative filmmaking workflow: a botanical cathedral that can evolve toward underwater, coral-like forms. Workflow and intentional 3D motion take priority over finishing a polished film.

## Current state

Three five-second comparisons and three short diagnostics are preserved in this project’s `runs/` folder. The side-by-side comparison is in `exports/2026-09-06-comparison/`. Olof's playback review: 0.30 is too smooth and 0.50 flickers too much. Use 0.40 as a comparison baseline while keeping all three; no final visual recipe is selected.

Current practice cut: [v001](cuts/v001.md), a 3.5-second assembly with the preserved opening and a 2D continuation. [v002](cuts/v002.md) chooses a 3D continuation from the same anchor. Both await Olof's playback review. [Serverless session results](experiments/serverless-results.md) record all runs, camera measurements, timing and cleanup.

## Experiments

| Note | Question | Status |
| --- | --- | --- |
| [Baseline](experiments/baseline.md) | What does the existing SDXL feedback loop produce? | Rendered and reviewed. |
| [Continuation](experiments/continuation.md) | Can we retain a good prefix and replace only what follows it? | Rendered; v001 preserves the opening and selects eight new frames. |
| [3D parallax](experiments/3d-parallax.md) | Can a short intentional camera move produce convincing near/far parallax? | Guide and repaint rendered; differential parallax measured, edge artifacts remain. |
| [Model quality](experiments/model-quality.md) | Can we improve detail and flicker at similar recurring cost? | Researched; no new model run. |

[References](references/README.md) · [runs](runs/README.md) · [cuts](cuts/README.md) · [exports](exports/README.md) · [working convention](../../../../docs/workflow.md)
