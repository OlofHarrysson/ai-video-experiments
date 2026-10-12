# Saved-painting refinement study

2026-10-12. Olof authorizes testing a separate refinement pass on saved paintings, then continuing to video only if the still result is promising. The video comparison must include feeding refined paintings back into the loop.

## Frozen first stage

[Six probes](refinement-probes.json) use source-frame indices 12, 108 and 204 from the liked `nr-ref-tidal-edit025` branch: early, middle and late. Each receives one stationary repaint at starting sigma 0.15 or 0.30. These are refinement noise levels; adapter strength remains 0.25. The input is the saved painting encoded into the target latent and supplied clean through the reference path. No additional spatial transform is applied. The same detailed scene prompt and existing preservation instruction remain fixed, with reference boost 0.01, grounding 768, CFG1, Euler and three sigma intervals. Resolution remains 1536x1024. Seeds are matched across strengths for each source and recorded separately from the primary loop's seeds. No sharpening, resize, mask or fixed-opening reference is added.

Inspect every full painting and matched native-resolution crops of shell, terrain/spires and sky. A useful result adds convincing fine material relief while keeping the existing silhouettes, object count and palette. Merely stronger edges, larger holes, extra specks or redesigned geometry are insufficient. Source grain need not be pixel-identical, but visible changes must support the intended surfaces. Record the gate decision before launching any video work.

## Conditional video stage

If a refinement setting passes the still gate, compare the existing base trajectory with refinement applied only to its saved paintings and a separate trajectory that refines each new painting before its refined output is warped and fed into the next primary generation. Retain the same opening, primary prompt/noise, Euler sampler, adapter settings, camera, primary seed trajectory and finishing where applicable. Refine after primary generation, before RIFE; interpolation remains outside feedback. The two refinement arms must use matched refinement seeds and settings. Subsequent primary images in the feedback arm necessarily differ. Screen complete raw-painting overviews and dense interpolation windows. Check any promising recipe on a second world before generalizing.

## Results

**The still-image gate did not pass.** All six outputs completed and were inspected against their saved source. Keep the unrefined paintings. The conditional video comparison and second-world check were not started; this decision was recorded before any video work. Neither feedback policy has been evaluated by this study.

| Saved source | Refinement at 0.15 | Refinement at 0.30 |
| --- | --- | --- |
| Early, frame 12 | Close to the source; small changes to cracks and edges, without convincing richer relief. | Larger foreground dimples and redrawn cracks/shell flecks. Main planet and moon remain; added marks do not resolve finer grain. |
| Middle, frame 108 | Smooth shell chambers remain smooth. Small local edge and terrain changes. | Stronger patch-like patterns on the upper moon and altered terrain ripples. No convincing fine-grain recovery; all three sky objects remain. |
| Late, frame 204 | Principal shapes remain recognizable; no meaningful recovery of granular shell or terrace relief. | Some rougher terrace edges and reorganized small chambers, while broad smooth surfaces persist. Sky markings change; major objects remain. |

The assistant inspected all three native source paintings, all six complete generated paintings, and nine matched native crop sheets covering shell, terrain and sky. Crops use identical coordinates, without resampling or sharpening. Overview sheets are resized and serve composition review only. The more visible 0.30 variant is preserved as the comparison, not selected as an improvement. Human taste judgment is pending.

[Native detail comparison](../../exports/refinement-review-v001/refinement-comparison.png) · Full compositions: [early](../../exports/refinement-review-v001/early-overview.png), [middle](../../exports/refinement-review-v001/middle-overview.png), [late](../../exports/refinement-review-v001/late-overview.png). Each sheet runs saved painting → 0.15 → 0.30 from left to right. Exact original PNGs and hashes are listed in the [inspection manifest](../../exports/refinement-review-v001/inspection-manifest.json).

This tests one extra native-resolution repaint with the current Krea model, full prompt and reference recipe. It does not establish that other refinement prompts, models, resolutions or schedules fail. A change in surface appearance may be useful artistically, but these probes did not show the detail gain required to advance this particular experiment. The original film, Euler baseline and liked adapter 0.25 remain unchanged.

## Verification and resources

All six jobs pass exact requested/executed/PNG graph, successful history, parent/input/output hash, recomputed stationary transform and 1536x1024 dimension checks. For each saved source, the two requested graphs differ only in the sigma list and output prefix. The stationary transform reproduces every source pixel exactly; this isolates a new diffusion pass rather than adding camera resampling. A total of 102 local case/run files (58,636,944 bytes) is recorded by hash. Remote inputs and outputs match their local copies; twelve verified owned duplicates and the two temporary reference links are removed after an empty-queue check.

The L4 Pod is deleted and its absence verified. The reusable model volume is retained. Estimated compute is **$0.0813**, excluding storage and not a posted-billing figure. The public proxy returned HTTP403, so the local runner used an SSH tunnel to the same ComfyUI service; generation data flow and model settings were unchanged. Startup readiness failed before any generation submission, then the verified runtime completed all six jobs. Runtime source/log evidence is preserved by SHA256. [Execution receipt](refinement-execution.json); private operational receipts remain under `work/refinement-study-session/`.

Recheck from `apps/deforum` with `uv run --locked python projects/world-seed/experiments/noise-reference/run.py check projects/world-seed/experiments/noise-reference/refinement-probes.json`.
