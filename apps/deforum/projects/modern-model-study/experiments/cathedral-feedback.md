# Cathedral repaint comparison

Approved 2026-09-09: animate both accepted cathedral openings with the same twist and cadence 3, testing two repaint strengths per model. Judge four short clips against motion-only previews before choosing a human shortlist.

## Fixed controls

Use the original 1536 × 1024 opening PNGs and their exact cathedral prompt from [opening artwork](opening-art.md). Keep their model weights, encoder and VAE; Krea uses the plain FP8 recipe without LoRA. Each branch begins at the same model's opening. Every subsequent diffusion starts from VAEEncode of that branch's warped previous generated anchor. Increment seeds from 491731 once per repaint.

Three seconds, 12 source fps, cadence 3: 36 source frames with 11 repaints per branch. The shared encoder repeats each source frame twice for a 72-frame, 24 fps MP4; this adds no interpolated motion. The two intervening source frames only warp the preceding anchor; no temporal blending, RIFE, reference conditioning, regional masks, extra image noise, depth or optical flow. The direct center twist eases toward one radian over three seconds. Use explicit image dimensions in the shared coordinate mapping to preserve the 1536 × 1024 canvas.

| Model | Gentler repaint | Stronger repaint | Held fixed |
| --- | --- | --- | --- |
| Krea 2 Turbo FP8 | denoise 0.30 | denoise 0.45 | 8 Euler/simple updates, CFG 1 |
| Klein 4B distilled | last 4 intervals of a 40-interval Flux2 schedule | last 4 intervals of a 24-interval Flux2 schedule | 4 Euler updates, CFG 1 |

These are experimental partial-noise feedback adaptations, not manufacturer-validated animation recipes. Klein's normal four-step schedule is intended for generation from noise; using a longer schedule's tail gives four actual updates from a lower noise level. The two models' controls are not numerically noise-matched. Compare strengths within each model first. Verify actual sigma arrays on the deployed runtime.

References: [Krea official recipe](https://docs.comfy.org/tutorials/image/krea/krea-2), [Klein author card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B), and [earlier initialized-feedback source inspection](additive_reference.md#recipes-and-limits).

## Execution and review

Run the same Python orchestration beside ComfyUI on the temporary Pod to avoid internet uploads per frame. Archive source/warped input/output hashes, graphs, seed, versions and receipts. Copy completed exports and runs to the Mac, then verify all generated media before deleting owned compute and attached storage.

Runner: `cathedral_feedback.py prepare`, then `cathedral_feedback.py MODEL STRENGTH`. Inspect evenly spaced frames from every clip plus consecutive-frame windows around repaint boundaries. Review for scene retention, blur/grain, distortion retention, sudden redraw and interesting evolution; frame metrics locate problems but do not establish artistic success.

## Results and human shortlist

All four clips completed. **Assistant candidate: Krea at denoise 0.45**, with 0.30 as the meaningful comparison. The stronger repaint produces clearer white arches and more newly resolved miniature structures; the gentler version becomes softer and less distinct. Both retain the central seed and imposed twist, but repaint boundaries remain visible. This is progress toward a useful recipe, not smooth morphing solved or a user-approved model selection.

![Krea: denoise 0.30 left, 0.45 right](../exports/cathedral-feedback-v001/comparisons/krea/preview.mp4)

| Variant | Observed result | Full-size clip |
| --- | --- | --- |
| Krea 0.30 | Recognizable composition and twist, little grain; progressively softer architectural detail and changed lighting. | [Gentler repaint](../exports/cathedral-feedback-v001/krea/gentle/preview.mp4) |
| Krea 0.45 | Clearer arches and more expressive rebuilding, with larger discrete redraws at cadence boundaries. Preferred candidate in this review. | [Stronger repaint](../exports/cathedral-feedback-v001/krea/stronger/preview.mp4) |
| Klein lower noise | Strong layout retention and twist, but grain accumulates and the seed becomes noisy. | [Gentler repaint](../exports/cathedral-feedback-v001/klein/gentle/preview.mp4) |
| Klein higher noise | Similar overall trajectory, with persistent grain and harsher fine texture; does not fix the weakness of the lower-noise branch. | [Stronger repaint](../exports/cathedral-feedback-v001/klein/stronger/preview.mp4) |

![Klein: lower starting noise left, higher right](../exports/cathedral-feedback-v001/comparisons/klein/preview.mp4)

Motion before diffusion: [Krea](../exports/cathedral-feedback-v001/krea/motion-only/preview.mp4) · [Klein](../exports/cathedral-feedback-v001/klein/motion-only/preview.mp4). These previews retain the original artwork and isolate the deformation. The reflected outer edges are an artifact of the selected border handling, not generated camera content.

The review used six evenly spaced samples per clip, then every displayed frame around 1.90–2.17 seconds. At the 2-second boundary, Krea changes architecture and lighting in addition to the warp. Full-size ending and comparison frames confirm the softer 0.30 versus clearer 0.45 distinction. Klein shows noisy detail around the seed and throughout the architecture in both strengths. These are sampled-frame findings; Olof's playback preference remains authoritative and pending.

**Next recommendation:** get Olof's reaction to the Krea pair before extending the shot. Retain the 0.45 candidate if he likes its evolution, then investigate the abruptness of repaint transitions separately. Do not diagnose Klein as an incapable image model: this result concerns our four-update partial-noise feedback recipes without reference conditioning.

## Execution evidence

- Native ComfyUI 0.34.0 (`12d5279438bfefc058a269eae805ceab6047777f`) on one L40S, $1.09/hour. Two 4090 create attempts returned unavailable capacity with no Pod created. The L40S used the same CUDA 12.8 template; its observed image digest was `sha256:498e3c4ac7ef5071214badb1681d82ab3a8f922b1055742ae692fa02cd3b59ff`.
- All six files in the opening study's pinned model manifest passed size/SHA-256 verification. A slow Qwen3VL download was stopped, its process exit verified, and that exact partial file resumed successfully in 33.5 seconds. The initial download log contains the deliberate termination; the separate resume log records successful verification.
- Runtime-derived sigma starts at 1536 × 1024: Klein **0.331687 / 0.471836**; Krea **0.583973 / 0.737355**. Complete arrays: [sigmas.json](../exports/cathedral-feedback-v001/sigmas.json). These establish that the nominal strengths are not matched noise levels across model families.
- 44 successful diffusion jobs, no regenerated opening and no replacement inference jobs. A missing `runs/` directory stopped the first orchestration before submission; creating it resolved that setup error. Median ComfyUI execution was 2.37 seconds per Klein repaint and 9.34 seconds per Krea repaint. Total recorded job execution was 272 seconds; this excludes provisioning, downloads, orchestration, transfers and local review. The two Krea orchestrators overlapped independent CPU work; ComfyUI executed their GPU jobs sequentially.
- [Lineage verification](../exports/cathedral-feedback-v001/verification.json) checks every graph, seed, parent/input/output hash, 1536 × 1024 output, and all 144 source frames against archived hashes. No feedback sampler uses an empty latent; none has ReferenceLatent or a reference adapter. First/middle/last source warps were recomputed locally per branch, and a cadence boundary plus neighboring frames was checked.
- Mac/Linux warp recomputation differed in at most 12 of 4,718,592 channels per inspected warp, with maximum difference 2/255, consistent with minor numerical/interpolation rounding. Those checks use a small explicit tolerance; file transfers and archived input/output hashes require exact equality. See [platform comparison](../exports/cathedral-feedback-v001/warp-platform-comparison.json).
- The old convenience warp wrapper defaults to a 1024 × 576 canvas. This experiment supplies dimensions explicitly and asserts shape, preventing a silent resolution/geometry change. Central record `AF-20260909-185323`; not established as the cause of earlier poor clips.

All 90 remote input/output files (44 generated frames, 44 warped inputs and two bundled files) matched local SHA-256 hashes. Four full-size clips, two motion-only previews, labeled comparisons, raw frames and run histories are local. Owned Pod and attached storage deleted; final Pod and network-volume lists empty, spend rate zero. Observed balance change was **$0.37** ($43.7582 to $43.3916); billing may settle after that snapshot. Private deployment/log/archive receipts remain in `work/cathedral-feedback-session/`.

Reproduce local verification/comparisons with `uv run --with pillow==12.1.0 --with opencv-python-headless==4.12.0.88 python projects/modern-model-study/experiments/cathedral_review.py` from `apps/deforum`. The comparison uses the existing Pillow-label/FFmpeg-encode approach; the local FFmpeg has no drawtext filter.

## Human feedback and follow-up

Olof selects Krea, pauses Klein and finds the cathedral animation still too flickery. The [lower repaint study](krea-low-repaint.md) compares 0.10/0.18/0.24 against the preserved 0.30 clip. The earlier assistant recommendation of 0.45 was not selected by Olof.
