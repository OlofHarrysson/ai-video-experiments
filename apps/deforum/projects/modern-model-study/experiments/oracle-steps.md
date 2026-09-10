# Oracle: noise, sampling steps and more recurrent repaints

## Plan before rendering

Olof requests a lower-noise/more-steps test, earlier prompt transition and more time for successive repaints. He dislikes the moth subject and chooses Oracle or another subject instead. Use the archived Oracle prompt. Keep the recurrent warped-image initialization; interpolation never feeds back into generation.

Prior evidence: [Turbo schedule comparison](turbo-schedule.md) matched sigma 0.310901 for one versus eight sampling intervals. Eight smaller intervals flattened Krea more in both the no-motion latent diagnostic and short RGB-warp clip. Those clips had no RIFE and no prompt change. The earlier [SDXL noise/steps study](../../motion-guide-study/experiments/noise-steps.md) found doubling 18→36 steps did not convincingly remove added RGB grain. That different model/noise mechanism is context, not an answer for this Krea test.

Four matched 12-second clips: low3=(0.4,3 intervals), low9=(0.4,9), high3=(0.6,3), high1=(0.6,1). Low9 subdivides each interval of low3 into three equal sigma intervals, retaining exactly the same start/end noise and Euler sampler. High1 is one experimental jump 0.6→0, not the native final interval of the normal Turbo schedule (which begins near 0.311). Every repaint ends at zero; more intervals subdivide the same denoising path, while later recurrent repaints add fresh noise to a newly warped image.

Shared accepted cathedral opening, then an identical 0.6/3-step cathedral repaint at second 1 in all branches. Oracle first applies at second 2 and continues through second 11: ten Oracle repaints rather than the previous four. Verify all four pre-switch paintings have identical pixels. This isolates transition recipe differences from differing pre-switch states. Forty-four fresh calls total; each branch has 11 repaints. The common first repaint does not use its branch's later test settings.

Preserve Krea Turbo FP8, frozen natural-language prompts, incrementing matched seeds, CFG 1, 1536×1024, Lanczos spatial mapping, native 24fps, one-second repainting and RIFE 4.25 scale 1. The inherited spatial path settles at local second7, so later paintings continue evolving in a stationary view. First Oracle painting is at 2s, with RIFE connecting it from the common 1s painting. Final 11–12s follows the settled native path after the last painting. No prompt embedding blend, reference conditioning or mask.

Judge the low3/low9 pair for detail and subject emergence, high3/high1 for large-update behavior, and each branch at 4/7/11s for the effect of additional Oracle repaints. Do not rank only by low pixel difference. Screen every painting and selected interpolated windows; show a small meaningful comparison in chat with all four indexed. Use the retained EU model/runtime cache and one owned Pod at the observed $0.72/hour. Download/hash-check before deleting compute, retaining the authorized volume.

## Results

All 44 recurrent repaints are complete and archived locally. Human playback preference is pending. Every variant uses the same opening and pixel-identical first repaint, also matching the earlier 0.6 benchmark. Source inspection covers all twelve paintings per branch and full-size selected endings; interpolation review follows below.

| Case | Oracle sampling | Painting review |
| --- | --- | --- |
| low3 | 0.4 start, 3 intervals | Retains the architecture, develops a profile in the arch and an eye in the seed late in the sequence. Broad shading flattens. |
| low9 | 0.4 start, 9 intervals | Similar partial transformation, without a convincing recovery of depth. More patch-like/segmented color, especially around the seed. |
| high3 | 0.6 start, 3 intervals | Eye in the arch at 2s; a separate porcelain face replaces the seed around 5s and continues developing through 11s. Stronger depth and subject change. |
| high1 | 0.6 start, 1 interval | Smooth glossy structure and an eye embedded in the arch. The seed persists through 11s rather than becoming a distinct face. |

The matched low3/low9 test does not support “more steps fixes low-noise flattening” for this setup. The high3/high1 pair demonstrates that splitting the same noise range changes what the model develops: three intervals produce the clearest target subject here, while one favors broad glossy forms. Neither finding establishes a universal optimum or a model defect. These are custom schedules on a distilled model, one prompt pair and one deterministic seed sequence.

More recurrent repaints give the new subject additional opportunities to appear: in high3, the face is clear by the fourth Oracle repaint (5s), and later repaints elaborate it. This run does not isolate duration from prompt choice relative to the earlier moth study. Low-noise runs still do not become the requested frontal Oracle portrait after ten Oracle repaints. All branches inherit the same path, which settles at 7s; late change comes from repainting rather than continued camera travel.

Assistant's tentative creative pick is high3 for subject transformation and depth; high1 is a meaningful alternative for architectural morphing. Do not promote either to Olof's accepted baseline before feedback.

## Verification and resources

- 44 successful jobs; requested and executed graphs, seed sequence, warped previous-image initialization and output lineage are archived.
- ComfyUI 0.34.0, cached Krea Turbo FP8, Qwen encoder and VAE hashes verified before inference. No model download or runtime reinstall.
- Actual float32 sigma arrays from the pinned `ManualSigmas` node are archived. The low9 grid retains the three low3 interval boundaries.
- Owned Pod `dv41x66qdl5d71`, RTX PRO 4500 Blackwell, $0.72/hour. Batch runtime 455.56 seconds including local-to-container orchestration. Total allocated session was about fifteen minutes (roughly $0.18 at the quoted compute rate; not a billing receipt).
- All 733 archived files verified by size and SHA-256. Archive SHA-256: `5a2f91c5dfc0bd50d0a09ba3ba91a6d57cf800624e50ad43f9ff12c0892aad11`.
- Final queue empty, owned Pod deleted, subsequent live Pod listing empty. Authorized 50 GB model/runtime volume `vd3jnbwko1` retained.
- Private execution/archive/cleanup receipts: `apps/deforum/work/oracle-steps-session/`. Every generation remains under this project's `runs/`; rendered media is ignored by Git.


## Videos and reproducibility

Finished comparisons: [low-noise step comparison](../exports/oracle-steps-v001/step-comparison/preview.mp4), [higher-noise step comparison](../exports/oracle-steps-v001/high-comparison/preview.mp4), [all four](../exports/oracle-steps-v001/all-four/preview.mp4).

| Variant | Interpolated 24 fps | Raw recurrent/warp diagnostic | All paintings |
| --- | --- | --- | --- |
| 0.4 / 3 | [Video](../exports/oracle-steps-v001/low3/cadence-24/interpolated/preview.mp4) | [Raw](../exports/oracle-steps-v001/low3/cadence-24/preview.mp4) | [Sheet](../exports/oracle-steps-v001/low3/cadence-24/review/anchors.png) |
| 0.4 / 9 | [Video](../exports/oracle-steps-v001/low9/cadence-24/interpolated/preview.mp4) | [Raw](../exports/oracle-steps-v001/low9/cadence-24/preview.mp4) | [Sheet](../exports/oracle-steps-v001/low9/cadence-24/review/anchors.png) |
| 0.6 / 3 | [Video](../exports/oracle-steps-v001/high3/cadence-24/interpolated/preview.mp4) | [Raw](../exports/oracle-steps-v001/high3/cadence-24/preview.mp4) | [Sheet](../exports/oracle-steps-v001/high3/cadence-24/review/anchors.png) |
| 0.6 / 1 | [Video](../exports/oracle-steps-v001/high1/cadence-24/interpolated/preview.mp4) | [Raw](../exports/oracle-steps-v001/high1/cadence-24/preview.mp4) | [Sheet](../exports/oracle-steps-v001/high1/cadence-24/review/anchors.png) |

The source runner is [oracle_steps.py](oracle_steps.py), with the frozen prompt pair and complete per-repaint graph stored in each case and run. [oracle_steps_review.py](oracle_steps_review.py) reuses the existing review/finishing harness. Run from `apps/deforum/`:

```bash
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/oracle_steps.py low3
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/oracle_steps_review.py build-raw
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/oracle_steps_review.py prepare
```

Generation requires the private deployment configuration and live ComfyUI. Finishing uses the unchanged `interpolate.py` with twelve source paintings at 1 fps and multiplier 24; inspect `--pair-only` before passing its manifest as `--validated-pair`. Then run the review helper's `finish` and `compare`. RIFE is applied after generation, never fed back. Between paintings it produces 23 in-between images; the final second follows the native settled path. Use a new export version before changing a completed experiment's recipe.


Measured median ComfyUI time per Oracle repaint: low3 5.18s, low9 13.45s, high3 5.23s, high1 2.51s. These exclude spatial warping, transport, video assembly and interpolation. Nine steps cost about 2.6 times the three-step graph time without a clear quality gain in this test. Mean absolute pixel change is retained in `metrics.json` as diagnostic evidence, not a semantic quality or flicker score.


## Finished-video review

All four final videos are 288 frames at 24 fps, 1536×1024, twelve seconds. Every sampled painting remains pixel-identical at its corresponding output frame. RIFE uses the same pinned 4.25 code, model weights and scale-1 settings as the prior benchmark. Full video decode and frame/provenance checks pass. The twelve timing/interpolation unit tests pass as well.

The first interpolated pair was visually checked for every case before full interpolation. Every painting was reviewed in a chronological sheet, with full-size selected endings. The video-review harness inspects six evenly spaced frames plus every frame in the high3 seed-to-face window at 4.4167–4.5833s and the low-noise comparison at 8.4167–8.5833s. These are sampled-frame findings, not an exhaustive real-time playback judgment.

In high3's transition window, the eye/face progressively overlays and replaces the amber seed; the intermediate image is soft and partly doubled, rather than a hard replacement at the painting boundary. Low-noise nine-step interpolation preserves the extra patchy texture; finishing does not restore lost sculptural depth. Prefer the three-step high-noise branch when judging arrival at the requested new subject, while retaining the one-step branch as an architectural alternative. The low-noise pair is primarily a diagnostic comparison.
