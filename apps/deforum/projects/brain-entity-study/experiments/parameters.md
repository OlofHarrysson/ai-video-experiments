# Learning the feedback parameters

Status: six six-second clips completed and reviewed through timestamped frames. Olof approved the guide-off comparison and emphasized that guidance, previous-image influence, steps and noise need experimental understanding specific to each model, prompt and artwork. Existing settings are hypotheses, not a known optimum.

## First comparison

Use the exact archived v002 workflow and packed input. Change only `DifforumFeedbackSampler.control_strength` from 0.40 to 0.0. Keep denoise 0.82, 30 steps, CFG 7, noise 0.025, sharpening 0.35, color coherence 0.25, incrementing seed 7301+frame, LoRA 1.1, prompt schedule and camera unchanged. The sampler skips ControlNet application when strength is zero. Preserve the original graph rather than reconstructing it from a mutable recipe.

If the image still simplifies, investigate feedback/prompt settings before building a richer guide. If detail improves, test the tradeoff in movement and use the result to choose small isolated parameter comparisons. Richer illustrated keyframes remain a possible next step after this diagnostic.

## Procedure

Run `parameters.py` from the app directory. Every job records its parent workflow SHA-256 and an explicit list of parameter changes. Render six-second clips at 8 generated FPS; compare with preserved v002 and extract timestamped frames with `video_review.py`. Show every new video in chat. Prefer a few informative comparisons to a large unexplained grid; a one-seed observation is provisional.

Reuse the GPU-verified image and a bounded warm session. No model or node installation is needed for these settings changes. Archive every generation before deleting the session volume. Research notes belong in [Feedback parameters](../../../../../docs/research/feedback-parameters.md).

## Second comparisons

All four variants use P01 (`20260907T074620462314Z-p01-guide-off-48f`) as their immutable parent. Change one value per clip: P02 denoise 0.82 → 0.70; P03 CFG 7 → 4.5; P04 steps 30 → 15; P05 image-space noise 0.025 → 0.075. Keep the same anchor, seed sequence, prompt schedule and camera. These are diagnostic values, not recommended defaults.

## Adaptive prompt comparison

P02 retains the circular portal but still flattens; P03 lower CFG also flattens at the midpoint. Add P06, holding P01's first prompt constant for all 48 frames. Only node 12's prompt schedule changes; keep every sampler value, including denoise 0.82, unchanged. This tests the scheduled content change as a cause of simplification. It does not isolate prompt wording from conditioning interpolation, and does not test removing “flat cel shaded colors.”

## Results

P01 guide-off completed. Timestamped frames show more semantic transformation and richer detail at the beginning and end, but flattening persists around three seconds. The sparse guide is therefore not the sole explanation. Playback judgment remains separate from sampled-frame inspection. The parameter and prompt comparisons below are complete.


### Parameter comparisons

| Clip | Isolated change from P01 | Sampled-frame finding |
| --- | --- | --- |
| P02 | Denoise 0.82 → 0.70 | Preserves the portal composition much longer, including a figure at 0.54s. From about 2.7s, large smooth circular bands dominate; detail only partially recovers late. More continuity, less invention. |
| P03 | CFG 7 → 4.5 | Portal becomes an alien head and a dome building early, then a smooth orange/teal eye-like oval around 2.7–3.3s. Branching detail returns later. Lower CFG does not solve the midpoint. |
| P04 | Steps 30 → 15 | Strong early portal/figure/organic-head transformations, followed by a very flat oval midpoint. Sparse tree-like structures appear late. Execution 74.498s versus P01 130.541s, about 43% faster, with no claim of equal visual quality. |
| P05 | Image noise 0.025 → 0.075 | Rich portal/alien imagery early, then the same smooth oval midpoint. Around 4.3–5.9s, branching tunnels, a castle-like scene and flowing folds return. Extra noise changes the trajectory, but does not prevent the collapse. |
| P06 | Keep frame-zero prompt throughout | Strongest sustained detail in this round: mechanical rims remain articulated through 2.7–3.3s; a figure reappears under an architectural opening and persists through several middle samples. Late frames retain engraved rings and a glowing central aperture. The sequence no longer deliberately follows the slit-to-organic prompt transition. |

All comparisons use the same seeded inputs, but this session has not measured complete GPU bit determinism. Each source graph was verified against its archived parent: exactly one changed input, matching recorded change, identical packed anchor and verified parent graph SHA-256. Findings describe timestamped samples; they do not establish perceived flicker or the user's artistic preference.


## Interpretation and next practice

P06 preserves more middle-frame complexity with the same denoise, CFG, steps, noise and camera as P01. This supports the scheduled prompt change as a contributor to simplification in this sample; it does not separate wording from conditioning interpolation. The style phrase “flat cel shaded colors” remained in P06, so that phrase alone does not force the collapse.

Olof's subsequent playback assessment finds P06 too discontinuous. Use P01/P03 and likely P04 as the motion references; retain P06 as a clarity diagnostic. Follow the [architecture and temporal-continuity comparison](../../../../../docs/research/deforum-architecture-comparison.md) before selecting another recipe: investigate intermediate-frame synthesis, noise continuity and classic cadence. Richer intermediate prompts remain one creative component, rather than the entire solution. Test 15 steps again on a successful temporal recipe before adopting it as a faster default. A second seed or repeat run would strengthen confidence before committing to a longer shot.

## Playback and exact runs

Each clip contains 48 preserved source frames at 8 generated FPS; H.264 delivery repeats these at 24 FPS, 1024×576, six seconds. No optical-flow interpolation is applied. Contact sheets include 12 overview timestamps and the midpoint at 2.875, 3.0 and 3.125 seconds. Each export has its own immutable source-indexed cut.

| Clip | Run | Queue / startup (s) | Execution (s) | Video and review |
| --- | --- | ---: | ---: | --- |
| P01 | `20260907T074620462314Z-p01-guide-off-48f` | 117.856 | 130.541 | [Video](../exports/p01-guide-off/preview.mp4) · [review](../exports/p01-review/v001/review.json) · [frames](../exports/p01-review/v001/contact-sheet.jpg) |
| P02 | `20260907T075455357470Z-p02-denoise-070-48f` | 1.225 | 125.470 | [Video](../exports/p02-denoise-070/preview.mp4) · [review](../exports/p02-review/v001/review.json) · [frames](../exports/p02-review/v001/contact-sheet.jpg) |
| P03 | `20260907T075457156677Z-p03-cfg-45-48f` | 11.801 | 132.179 | [Video](../exports/p03-cfg-45/preview.mp4) · [review](../exports/p03-review/v001/review.json) · [frames](../exports/p03-review/v001/contact-sheet.jpg) |
| P04 | `20260907T075457157015Z-p04-steps-15-48f` | 124.415 | 74.498 | [Video](../exports/p04-steps-15/preview.mp4) · [review](../exports/p04-review/v001/review.json) · [frames](../exports/p04-review/v001/contact-sheet.jpg) |
| P05 | `20260907T075520676682Z-p05-noise-075-48f` | 122.911 | 125.524 | [Video](../exports/p05-noise-075/preview.mp4) · [review](../exports/p05-review/v001/review.json) · [frames](../exports/p05-review/v001/contact-sheet.jpg) |
| P06 | `20260907T075838222133Z-p06-constant-prompt-48f` | 0.125 | 125.488 | [Video](../exports/p06-constant-prompt/preview.mp4) · [review](../exports/p06-review/v001/review.json) · [frames](../exports/p06-review/v001/contact-sheet.jpg) |


## Runtime, timing and preservation

All six jobs completed on the existing RTX 4090 workers `6g6jw5hibofrhb` and `wbzjxqffeb9pj5`, observed using image `f106834b7`. Collected runtime diagnostics report ComfyUI 0.34.0, PyTorch 2.11.0+cu128 and RTX 4090 for every run. The earlier packaging-only GitHub build completed during this session and automatically changed the endpoint's requested image to `d40729dd1`; the endpoint was pinned back to `f106834b7`. None of these jobs was assigned to the new-image workers. Preserve this distinction between requested endpoint configuration and actual execution evidence.

P01 cached startup took 117.856s. Subsequent delay includes worker availability and queued jobs, not necessarily model setup; P06 began after 0.125s on the warm worker. Fewer steps reduced execution work; denoise 0.70 still ran 30 sampling intervals and did not halve render time. Total execution time is not the account's complete billed time: idle/startup and initializing workers can add overhead.

All 318 cloud objects (296,152,091 bytes) were compared byte-for-byte and by SHA-256 with local archives, including request inputs and manifests; a second inventory was unchanged. All six videos passed duration, resolution, FPS and frame-count checks; every cut preserves exact source hashes. Workers were set to min/max zero, idle timeout restored to five seconds, and the owned volume was detached and deleted. Worker, Pod and volume inventories were empty. The active local deployment receipt was moved into the closed session archive.

Observed account balance moved from $47.8552404447 to $47.5937108891 (about $0.26), with current spend/hour reported as zero after cleanup. Billing can settle later; this is an observed balance change, not a final invoice. Private verification and account receipts remain in ignored `work/brain-parameters-session/`.


## User playback assessment — 2026-09-07

Olof finds the round substantially better than the previous videos. P06 is clear but lacks temporal consistency and feels like still images, so it should remain a clarity diagnostic rather than the next motion baseline. P01 has interesting morphing and better continuity, but needs more gradual change across intermediate frames. P02 begins well, becomes boring late. P03 is very good with a flatter ending. P04 is probably the clip called “Before,” also described as cool (transcription interpretation). P05 is good but shares the abrupt-change issue.

Next work is an architecture/workflow comparison with original Deforum, the newer implementation and current ComfyUI practice. The previous proposal to focus on intermediate prompt content remains one possible component; it is insufficient as a complete plan for the temporal problem. No temporal quality conclusion should be inferred from P06's contact sheet alone.
