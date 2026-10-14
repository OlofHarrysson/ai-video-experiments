# Crisp city-to-crystal passage

2026-10-12. Olof asks to return to filmmaking with the new settings, create a short part of the planned multi-world journey, and prioritize crisp, highly detailed digital art with clear color over blurry, gray watercolor-like treatment.

## Direction

Create a six-second continuous passage: an engraved black-and-gold city opens into a cyan, rose and ivory crystal world. Start from a screened fresh opening and develop the camera from its actual composition. The city road and aperture supply continuity as materials change; no cuts, dissolves, independently inserted destination still or protected masks. Travel should maintain momentum through overlapping push, drift and bank, without repeated acceleration/braking.

Two [opening candidates](openings.json) hold the material prompt fixed and vary the seed. Krea 2 Turbo generates the opening at 1536x1024. The recurrent passage uses Euler, three partial repaint intervals, CFG1, editing-adapter strength 0.25, reference boost 0.01 and grounding 768. Both target initialization and clean reference inputs use the already-warped previous painting. Detailed descriptions specify physical material relief, clear air, small highlights and deliberate palettes. The reference instruction will permit the authored transformation rather than demand the original scene remain unchanged. No extra refinement pass is added after the failed still gate.

Screen the opening and the first short stretch before extending. Preserve every draft and branch. Inspect all generated paintings, native checkpoints and dense interpolation windows. RIFE finishing remains outside feedback at 24 fps, with the established 4.5x source-clock conversion. This is an artistic passage test; differences from the old film are not an isolated adapter ablation or proof of a universal quality improvement.

## Latest film

[The completed thirty-second Crystal Gate](finale.md) preserves the liked fourteen-second opening and extends the canyon through branching glass crowns into a porcelain/glass bloom. [Watch](http://localhost:3028/world-seed-crisp-passage). The last five seconds use previous-painting initialization without the extra reference-conditioning route; other selected passages keep the preferred adapter. Euler/noise 0.72/three updates remains unchanged. All earlier drafts and rejected experiments are preserved. Human review of the new ending is pending.

## Original six-second result

The six-second draft is **The Crystal Gate** (`nr-cp-city-crystal-a`). [Watch the video](../../exports/v002/nr-cp-city-crystal-a/faster/rife-moving-tail/preview.mp4) · [Full-resolution reviewer](http://localhost:3028/world-seed-crisp-passage) · [Frozen direction, prompts and settings](passage-a.json).

Opening B was selected after viewing both native candidates: its wider road supplies a legible route and its foreground carvings are cleaner. Both candidates and all subsequent paintings are preserved. The camera combines a sustained push, sideways drift and gradual bank. The passage was screened at two and four seconds before continuation.

The actual development is more restrained than the storyboard: a black-and-gold city becomes a porous ivory/rose gateway studded with cyan and violet crystals. The city moves out of view, the outer rings become faceted, and small green cells appear. The main cyan crystal and curved road persist across all 54 paintings. We approach the new environment rather than completing the planned expansive garden reveal.

**Assistant judgment:** the clear air, dark separation and solid contours move away from the earlier hazy treatment. The opening is the richest painting. Fine basalt engraving simplifies during recurrence; later forms have clean edges but broad smooth surfaces. Small cells, lights and crystal facets change, and an additional smaller cyan crystal appears near the end. This does not solve meticulous detail in every frame or establish superiority to Olof's selected film. On 2026-10-13, Olof says he likes this direction and asks to make the movie longer. This supports continuing the six-second draft; the original thirty-second film remains separately selected.

The recipe uses the preferred 0.25 editing adapter with Euler, boost 0.01 and primary noise 0.72. A transformation-permitting reference instruction replaces the study's exact-scene preservation wording. The new opening, motion and scene prompts also differ from the older film, so this is an artistic application, not an isolated test of the adapter. No refinement result is fed back into the loop.

## Inspection and reproduction

All 54 source paintings were viewed in contact sheets, alongside native opening/middle/end checkpoints. Dense displayed-frame windows cover the opening handoff and prompt transitions. [Execution and screening receipt](execution.json) records the exact coverage, finishing checks, preservation and resources. Frame inspection supports the stated shape/detail observations; it does not replace normal-speed human judgment of rhythm.

From `apps/deforum`, generate openings with `projects/world-seed/experiments/prompt-study/stills.py` and [openings.json](openings.json). The reference-aware recurrent runner is `projects/world-seed/experiments/noise-reference/run.py`; its new `--through-frame` option supports checkpoints at source frames 204 and 420 without changing the frozen plan. Omit it for the full chain through 636. Supply an explicitly provisioned deployment. Existing records are immutable and verified on resume.

Finish with `projects/world-seed/experiments/finish.py nr-cp-city-crystal-a pair --version v002`, inspect the first interval, then use `full` and `tail`. RIFE preserves all 54 paintings at nine paintings per delivery second, producing 144 frames at 24 fps and 1536×1024. The extra moving tail is outside the feedback loop. Every unique painting, generation graph, lineage record and draft remains in the local exports; [execution.json](execution.json) owns final verification and resource status.
