# Three spatial effects

2026-09-07. Test three visibly different motion mechanisms with the selected B opening and repaint recipe. Olof likes the stronger Move-Warp movement and wants examples that connect everyday descriptions to mathematical controls.

1. **Turn and bank**: adapt the camera-only component of Safety Marc's `Move-Around-30s`: sinusoidal pitch/yaw/roll and Y/Z translation. Consume 1.5 original 12-FPS steps per 8-FPS artwork frame; multiply angular increments by 1.5. Scale original translation units by 0.01 before this time adjustment, using Difforum relative depth 2–10 and 60-degree FOV. This is a unit-adjusted study, not a calibrated WebUI reproduction. Infer depth from each preceding repaint using the installed Depth Anything V2 Small node. Preserve a separate opening-depth camera preview.
2. **Radial unfolding**: isolate `Move-Around-30s`'s actual kaleidoscope guide, DIS Fine, factor 0.8, with all camera and compositing controls disabled.
3. **Expanding ring**: isolate `Evolve-Zoom-Slow-30s`'s circle guide, DIS Medium, factor 0.8, with all camera and compositing controls disabled.

All are 48 source frames at 8 FPS, delivered as six-second 24-FPS videos using holds. Same opening, SDXL base + art LoRA, fixed prompt, seed 7301 + frame, 18 steps, CFG 4.5, denoise 0.58. No RIFE. Flow guides use their first 48 consecutive 12-FPS frames, matching the prior wave test's two-thirds playback speed. Each diffusion frame passes through PNG; preserve every previous frame, warped input, exact graph and run receipt.

Use existing ComfyUI nodes, including `DifforumWarp` for one-step 3D projection. Reuse the Mac-side guide-flow loop for the two other effects. The camera reference uses fixed opening depth; the repaint uses fresh depth and cannot be expected to match that reference throughout.

Review: verify an obvious motion-only effect before full repainting, inspect four-frame checkpoints, then evenly spaced overview and short consecutive-frame windows. Present each result in chat with what changed and what to watch. Do not infer exact object motion or the user's preference from sampled frames.

Runner: `motion_effects.py`; output root `exports/motion-effects-v001/`. Source presets and guide hashes are captured in per-effect manifests. Reference collection pinned at `bb8ce2fb0fd693319087460c8b21c13e19864be5`.


## Completed results

All three six-second clips completed. Each uses 47 feedback jobs after the identical opening; a separate 48-frame 3D guide job brings the total to **142 completed jobs**. Exact saved graphs and source hashes were checked against all run receipts. All six videos (three repaint and three motion-only) have 144 delivered frames, 24 FPS, 1024×576 and six-second duration.

| Effect | Repaint | Motion only | First-pass findings |
| --- | --- | --- | --- |
| Turn and bank | [Play](../exports/motion-effects-v001/turn-bank/repaint/preview-48f.mp4) | [Play](../exports/motion-effects-v001/turn-bank/warp-only/preview.mp4) | The reference visibly turns, tilts and reverses direction. Repainting opens the portal toward a desert landscape; the central flame gains a teal globe and branching dark forms. The explorer remains readable. Large black edge areas and changing scene geometry limit camera fidelity; the upright figure shows how repainting can weaken the intended tilt. |
| Radial unfolding | [Play](../exports/motion-effects-v001/radial-unfold/repaint/preview-48f.mp4) | [Play](../exports/motion-effects-v001/radial-unfold/warp-only/preview.mp4) | Strong bilateral pinching turns the rim into two eye-like structures; the left becomes a helmeted face, while the right resembles a hovering eye/platform. The centered explorer gives scale. This is the assistant's preferred artistic continuation candidate, pending Olof's playback judgment. |
| Expanding ring | [Play](../exports/motion-effects-v001/ring-expand/repaint/preview-48f.mp4) | [Play](../exports/motion-effects-v001/ring-expand/warp-only/preview.mp4) | A more restrained centered composition: the flame acquires concentric teal/orange circles while the portal and explorer persist. The ring guide is never composited into the image; the circular appearance emerges during repainting of warped content. This single run does not prove the guide alone caused that shape. |

The source image, model/LoRA, prompt, seeds and denoise are held constant; this compares motion mechanisms rather than model quality. Fresh depth inference is an additional ingredient of the 3D branch, so it is not a one-parameter comparison against the previous static-depth test. The three effects also differ in displacement magnitude: median per-step 95th-percentile displacement is **14.12 px** for the kaleidoscope and **1.13 px** for the ring. Mean guide-flow drift is approximately **(+0.47, −0.02) px** and **(+0.002, +0.012) px**, respectively. Strong global rightward drift is therefore not inevitable for guide flow.

Review scope: six evenly spaced timestamp-matched repaint/motion-only pairs per effect, early source frames 1/3, intermediate frames 8/16/24/32 where available, then every displayed frame at **4.75–5.00 s** for turn/bank and unfolding and **3.75–4.00 s** for the ring. At 8 generated FPS, each 0.25-second inspection contains three distinct artwork positions plus repeated delivery holds. These windows retain related shapes but show visible proportion/detail changes. No RIFE interpolation or normal-speed smoothness verdict is claimed. Sheets are in each effect's `reviews/v001` and `reviews/v002`; `warp-review/v001` holds the earlier motion-only screening.

## Execution evidence

[Validation](../exports/motion-effects-v001/validation.json), [local checks](../exports/motion-effects-v001/local-validation.json) and [evaluated camera matrices](../exports/motion-effects-v001/camera-validation.json) are preserved. The first camera-only request queued for **7.981 s** and executed in **13.173 s**. The three feedback branches ran concurrently on two workers. Median per-job execution: 3D **2.893 s**, kaleidoscope **2.594 s**, ring **2.530 s**; median queue delays 105–108 ms. Total reported execution time across 142 jobs: **413.351 s**. This excludes local warp, uploads, archive collection, polling and idle/setup time.

The workers executing the jobs reported the existing `f106834b7` image. No model/node build was needed for this session. During the final pause, the endpoint configuration pointed at the automatically built `23d321f27` tag, while the completed workers still reported `f106834b7`; do not equate current endpoint configuration with the image that ran these jobs. Runtime diagnostics for each attempt remain in its archive.

The [motion vocabulary](../../../../../docs/research/motion-control-vocabulary.md) connects the observed effects to translation, shear, rotation, local expansion, camera projection and the repaint step. The [wave diagnostic](../exports/wave-diagnosis-v001/README.md) separates travelling ripple phase from bounded checker-junction movement and inferred flow in blank regions. User understanding and preferences for these three new clips remain unconfirmed.

## Archive and cleanup

Verified all **1,089 cloud objects (349,940,661 bytes)** against local files, including auxiliary depth, warped images, coverage masks, executed graphs and manifests. A second listing matched the first before deleting the temporary 10 GB volume. Endpoint min/max workers are zero, the volume is detached and deleted, and final inventories show zero workers, Pods and volumes. The active deployment file was moved to private closed-session receipts.

Observed account balance fell from **$47.0416801206 to $46.741084278**, approximately **$0.30**. This is the observed account delta, not a final itemized invoice. The account spend-rate field still showed $0.001/hour immediately after volume deletion despite empty resource inventories; treat that as an unsettled reporting field, not proof of a retained resource. Private verification and account receipts are in `apps/deforum/work/motion-effects-session/`. Every generation and intermediate remains on the Mac.
