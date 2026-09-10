# Two prompts and a wider noise range

## Plan before rendering

Olof requests two successive prompts and 0.3/0.4/0.5/0.6 starting-noise benchmarks to study scene transitions. Interpret halves temporally: eight seconds, cathedral prompt for repaint times 1/2/3 seconds, mechanical-moth prompt at 4/5/6/7 seconds. The initial painting is the preserved accepted cathedral anchor. Reuse the two archived natural-language prompts from the opening-art audition; change subject while retaining the painterly sculptural aesthetic. Every next painting is initialized from the warped previous output. No independent redraw, mask, conditioning blend or reference-image branch.

Use native 24 fps, one repaint per second, three Euler sampling intervals, CFG1, Krea Turbo FP8, the same seed sequence and time-based Lanczos twist/expansion. Seven repaints per branch, 28 calls total. RIFE 4.25 scale 1 finishing remains identical across branches; final second uses the native motion path after the last painting. This inherited path reaches its endpoint at local second 7, so the final second is effectively a hold. The first new-prompt painting lands at four seconds, so offline interpolation begins showing that change between seconds three and four. This is an interpolation boundary, not an early prompt switch in generation.

The previous first-sigma-only override cannot be lowered to 0.3/0.4/0.5 while retaining later sigma 0.512844: the schedule would increase noise on its first interval. Use proportional schedules based on the previous 0.60 branch instead. At0.60 it is the same numeric schedule; at 0.30 every nonzero sigma is halved. This changes the whole noise path, retaining its relative spacing and three intervals. The lower levels are a new schedule experiment, not an exact continuation of the previous fixed-later-sigma test.

| Start | Second sigma | Third sigma | End |
| ---: | ---: | ---: | ---: |
| 0.3 | 0.256422 | 0.155451 | 0 |
| 0.4 | 0.341896 | 0.207267 | 0 |
| 0.5 | 0.427370 | 0.259084 | 0 |
| 0.6 | 0.512844 | 0.310901 | 0 |

Core [ManualSigmas](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_custom_sampler.py#L1030) accepts the explicit descending schedule. These are experimental schedules for this checkpoint, not author-recommended recipes. Prompts use the [Krea author's natural-language guidance](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md), with frozen text and no per-frame expansion.

Inspect every painting, the prompt-switch neighborhood and final states. Distinguish successful subject change from changes in ornament; lower noise might preserve architecture so strongly that a moth never forms. Save raw and interpolated versions plus all graphs, prompt schedules, input/output hashes and cleanup receipts. Use the retained model/runtime volume and one owned RTX PRO4500 Pod at the observed $0.72/hour. Delete owned compute after verified local download; retain the authorized volume and leave the unrelated regional-composition Pod alone.

## Results

All four recurrent branches are complete. First-pass inspection of every painting finds the strongest response at **0.6**, while **none develops a complete, coherent moth within four new-prompt repaints**. That distinction matters: some attractive morphing occurs without fully reaching the requested new scene. Human playback judgment remains pending.

| Start noise | Observed behavior after the prompt switch |
| ---: | --- |
| 0.3 | Original arch/seed layout stays dominant; softened, flatter surfaces. No recognizable moth. |
| 0.4 | Some ornament and seed-shape changes, still clearly the cathedral. No recognizable moth. |
| 0.5 | More rebuilding and changing central ornament, but the seed and architecture remain the main forms. |
| 0.6 | Strongest partial transformation: antenna-like structures emerge on the upper-left arch, the seed acquires wing-like veins and the arch develops translucent purple sections. Still a hybrid scene. |

Recommend **0.6 as the transition candidate**, with 0.3 as the useful preservation extreme. This is not a successful full scene replacement. Lower noise and the prior image together constrain subject change; this shot does not isolate noise schedule, prompt wording and length of continuation as independent causes. The differing branches also arrive at the prompt switch with different paintings. A stronger later test would fork the same pre-switch painting and vary only the transition phase.

A useful next hypothesis is time-varying noise: retain the scene at a lower level, then allow more change during the prompt transition. A longer continuation or a more gradual sequence of target descriptions may also matter. None of those follow-ups has been rendered in this study.

- [Main comparison](../exports/prompt-noise-v001/shortlist/preview.mp4): 0.3 left, 0.6 right.
- [All four](../exports/prompt-noise-v001/all-four/preview.mp4): top 0.3/0.4, bottom 0.5/0.6.
- Individual finished clips: [0.3](../exports/prompt-noise-v001/sigma-03/cadence-24/interpolated/preview.mp4), [0.4](../exports/prompt-noise-v001/sigma-04/cadence-24/interpolated/preview.mp4), [0.5](../exports/prompt-noise-v001/sigma-05/cadence-24/interpolated/preview.mp4), [0.6](../exports/prompt-noise-v001/sigma-06/cadence-24/interpolated/preview.mp4).

Each branch preserves raw `preview.mp4`, all paintings, warped inputs, exact prompt schedule in `study.json`, executed ComfyUI graphs and finishing receipts. Source: [prompt schedule and generation](prompt_noise.py), [study review](prompt_noise_review.py), [shared verification/assembly](starting_noise_review.py). The shared review now takes the experiment timing instead of assuming a six-second length; re-verifying the previous 0.60 result passes unchanged.


## Execution receipts

All 28 GPU repaints completed. The 0.6 branch's first three paintings are **pixel-identical** to the previous 0.60 study before the prompt switch, validating the schedule bridge despite the change from SetFirstSigma to ManualSigmas. PNG file hashes differ because saved workflow metadata differs; decoded pixels do not.

The retained ComfyUI commit is `12d5279438bfefc058a269eae805ceab6047777f`, PyTorch `2.10.0+cu128`. Model files were verified without downloads (12.58s encoder, 0.65s VAE, 29.31s diffusion model). First graph took 83.01s including model setup; subsequent graphs about 5.1s. The complete recurrent batch took 324.45s including spatial warps, transport and per-job saving. Raw frame assembly and RIFE finishing run on the Mac.

Archive: 477 files, SHA256 `996d1e9b3c215e9210b708204fea3dadcdc1ee2791e251f2176c1d019c13ef96`. Every archive file is size/hash verified locally, including all 28 generated images, inputs and executed graphs. The queue was empty before deleting owned Pod `s4penh5qp5cwxr`. The retained 50 GB model volume remains. The unrelated regional-composition Pod was not modified by this task. Private receipts are in `apps/deforum/work/prompt-noise-session/`.


## Final validation and review

All four finished clips are 1536×1024, 192 frames, 24 fps and 8.000 seconds. All 8 painting timestamps in each clip are pixel-identical to the generated anchors. Each RIFE source and output hash is verified; settings, pinned model weights and implementation match the prior full-scale RIFE 4.25 baseline. The first-pair midpoint gate was inspected for every branch. Final frames 168–191 use the native path after the last repaint instead of RIFE's repeated-image padding. Both comparison videos also pass full decoding and eight-second timing checks.

Every requested/executed graph, prompt, seed, feedback parent, warped initialization and generated output was verified for all 28 calls. All raw-frame hashes and selected intermediate warps pass. The shared review still verifies the previous six-second 0.60 raw and finished outputs without overwriting them. Twelve timing/interpolation tests pass. Receipt equality allows numerically identical JSON integers/floats while preserving existing files byte-for-byte; this handles the old integer final-tail timestamp with the generalized timing calculation.

Visual review: 32 paintings in four contact sheets, full-size final paintings, four first-pair midpoints, six evenly spaced comparison samples and every frame from 5.416667–5.583334s; the 5.5s 0.6 image was also inspected full-size. Some doubled/softened fine architecture remains in the interpolated frames. Sampled images establish scene evolution and specific artifacts, not a definitive human smoothness preference.
