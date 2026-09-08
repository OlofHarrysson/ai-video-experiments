# Klein and Krea: first Pod audition

2026-09-08. Both modern recipes ran in native ComfyUI. Each generated its own opening and all subsequent repaints. Different prompts and editing mechanisms are intentional: this compares complete recipes, not checkpoints in isolation.

## Shortlist

**Krea 2 Turbo — scene description and partial repaint.** The more promising continuation candidate in the assistant's sampled-frame review: restrained palette, evolving porous architecture and cablework. The explorer changes proportions and details, and some imposed tilts are straightened. Consecutive-frame review shows double edges in some cadence intermediates where newly drawn shapes differ; Olof finds both models interesting but reports Krea is too jittery and often looks like two images at once; he has not selected a winner.

[Three-second Krea clip](../exports/audition-v001/krea/scene-d045/cadence/preview.mp4) · [motion only](../exports/audition-v001/krea/motion-only/preview.mp4)

**FLUX.2 Klein 4B distilled — native reference editing.** Retains the twist and scene layout closely; repeated requests grow branches around the flame. Fine texture softens and bright cyan/yellow colors accumulate. This is useful evidence for controllable layout, but not a finished animation recipe.

[Three-second Klein clip](../exports/audition-v001/klein/instruction/cadence/preview.mp4) · [motion only](../exports/audition-v001/klein/motion-only/preview.mp4)

## What was held and changed

Both use 1024×576, the same direct three-second twist, 12 source frames/second, cadence 3, and incrementing seeds. Twelve repainted anchors follow each model's opening. Intermediate frames warp both neighboring anchors to the output time and blend them; they never feed back into generation. Delivery is 24 fps with repeated source frames. No RIFE, optical flow, depth, regional masks or extra pixel noise.

Klein uses four steps, Euler, the Flux2 scheduler, CFG 1 and native reference-latent conditioning. Krea uses eight steps, Euler/simple, CFG 1 and partial img2img denoise 0.45. That denoise value is an experimental starting point for Krea, not a calibrated equivalent to SDXL's 0.45.

The [prompting sources and recipe adaptations](baseline.md#source-recipes) were read before execution. The exact executed graphs, prompts, input images, histories and PNGs are retained per run. Klein opening 0 uses the concise scene prompt; Krea opening 1 uses its more detailed description. Seeds are matched for the two openings within each model; later feedback increments the seed.

## Single-frame prompting comparison

Each pair starts from the same deliberately visible mid-twist image, with the same seed and settings within that model.

| Model | Scene description | Edit instruction | Decision |
| --- | --- | --- | --- |
| Klein | Preserves layout but raises orange saturation. | Preserves layout/palette more closely in one step, but branches escape the requested flame interior. | Extend instruction recipe; inspect cumulative drift. |
| Krea | Retains major content, but straightens the explorer. | Removes the explorer and converts architecture into flame/branch shapes. | Extend scene description; reject instruction wording for this recipe. |

The instruction was: “Add two fine branching ink strokes inside the existing orange flame. Keep the flame's outer silhouette. Keep every other contour, bent shape, tilted pose, object position, color and the framing exactly as in the reference image. Retain the same hand-inked illustration style.” Neither model reliably obeyed the small-region constraint. Krea's ordinary img2img graph is not a native reference-editing interface.

## All preserved samples

- Klein openings: [concise, selected](../exports/audition-v001/klein/opening-0.png), [detailed](../exports/audition-v001/klein/opening-1.png).
- Klein probe: [warped input](../exports/audition-v001/klein/probe-warp.png), [scene prompt](../exports/audition-v001/klein/probe-scene.png), [instruction](../exports/audition-v001/klein/probe-instruction.png).
- Krea openings: [concise](../exports/audition-v001/krea/opening-0.png), [detailed, selected](../exports/audition-v001/krea/opening-1.png).
- Krea probe: [warped input](../exports/audition-v001/krea/probe-warp.png), [scene prompt](../exports/audition-v001/krea/probe-scene-d045.png), [instruction](../exports/audition-v001/krea/probe-instruction-d045.png).

## Review and next step

Use the local review harness for evenly sampled progress, every displayed frame in a short interval, and timestamp-matched motion-only comparisons. Sampled frames locate drift and content changes; they do not settle human playback taste.

Next study: [remove cadence blending, then compare text-only and native reference generation](conditioning.md) for both models. Preserve the original FP8 Krea partial-img2img result as the baseline; investigate Klein color drift separately from guidance assumptions.

## Execution and archive

Official RunPod ComfyUI CUDA 12.8 Pod, RTX 4090. Actual ComfyUI 0.26.2, commit `b7ac98aafe41c8c8593b9f21238dab58a90424c6`, torch 2.10.0+cu128. Native model support was confirmed through real renders, without changing the installed core or adding custom nodes. All six pinned weights passed exact size and SHA-256 checks; see [model manifest](../../../serverless/modern-models.json).

The Pod was created at 19:20 UTC; the first Klein request was accepted at 19:26 UTC. No container build was needed. The two large Klein files downloaded and verified in about 156 seconds each, concurrently. All model downloads completed in roughly six minutes after their download process started. Prompt/setting changes reused the running installation.

Completed **32 generated PNGs**: four openings, four matched probes, and 24 feedback anchors. Both three-second clips and motion-only previews are local. The review harness sampled five overview times per clip, all seven displayed frames from 1.0–1.25 seconds, and matched motion-only pairs at 0, 1.5 and approximately 2.92 seconds. Krea partially resists the imposed twist by redrawing upright objects; Klein retains the layout more closely. Krea's changing geometry creates visible double outlines in blended intermediate frames.

Median warm feedback graph time: **Klein 5.10 seconds; Krea 13.41 seconds**. Median input upload: **7.89 and 7.32 seconds**, respectively, plus polling/output download. These are ComfyUI history spans and client upload timings, not isolated sampler benchmarks or a controlled SDXL cost comparison.

After the queue emptied, all **62 remote input/output files** were verified against local SHA-256 copies: 32 generated outputs, 28 uploaded inputs, plus the template's example image and empty placeholder. The owned Pod and its attached disk were deleted; follow-up inventories show zero Pods and network volumes. Serverless remains paused. The account refresh showed a $0/hour spend rate and approximately $44.69 balance; the observed balance change since this session's initial refresh was $0.37 and can settle later.

Private receipts live in `work/modern-pod-session/`, including model download logs, timing rows, archive verification and the closed deployment record. The 31 local tests passed with the experiment's Pillow/OpenCV dependencies; both native graphs were then verified through actual GPU generation. Olof’s explicit playback feedback is recorded above; the assistant shortlist does not establish a human preference.
