# Sampling steps and accumulated input noise

2026-09-08. Olof selects denoise **0.45**: 0.35 looked blurry, 0.58 repainted too much. He rejects bottom-left protection artifacts and requests testing whether more diffusion iterations can reduce top-right grain while retaining useful noise-driven changes.

## Before rendering

Same three-second twist, opening, incrementing seed sequence, cadence 3, model, LoRA, CFG and sampler as [repaint controls](repaint-controls.md). No protection mask, pixel copyback, feedback composite or RIFE. Top-right remains a fixed screen region with a 64px feather. Gaussian image noise is added before VAE encoding, separately from the sampler's normal latent noise.

A small 2×2 comparison holds denoise at 0.45:

| Branch | Sampling steps | Extra top-right pixel noise, standard deviation on [0,1] |
| --- | ---: | ---: |
| clean18 | 18 | 0 |
| clean36 | 36 | 0 |
| noise18 | 18 | 0.06 |
| noise36 | 36 | 0.06 |

Reuse the prior 0.45 clean baseline, with a fresh identical-input probe to validate the serving runtime. Render 12 new repaints per other branch. Every branch feeds its own generated frame into its next warp; playback intermediates never enter feedback. If 36 steps leaves conspicuous grain, add one branch at 36 steps with half the input noise (0.03), preserving all other settings.

More steps refine the sampling trajectory; they do not grant a larger denoise strength. In [ComfyUI 0.34.0 KSampler](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/samplers.py#L1297), denoise below one builds a longer schedule and retains the requested number of final steps. Both runs already finish at zero sampler sigma; 36 is not an extra cleanup pass appended after the 18-step output. Discretization also slightly changes the starting sigma, so this tests the ordinary steps control, not identical sigma trajectories. Pixel noise may survive as image texture after encoding; whether more steps removes it is an empirical question.

Review evenly spaced frames and matched every-frame windows, then a full-size top-right crop. Grain/detail measurements are diagnostics, not quality scores. Surface a short comparison and a recommendation in chat. Preserve every branch and exact input/graph; do not infer Olof's preference before playback.

Runner: [noise_steps.py](noise_steps.py). Media: `../exports/noise-steps-v001/`.

## Setup record

The initial EU-RO-1 attempt reported throttled workers, cached-image loading and LOW regional RTX 4090 availability. After roughly eleven minutes in the queue, all three accepted jobs were cancelled before any GPU output; their receipts and the empty-volume verification were preserved. The EU volume was detached and deleted. US-IL-1 reported HIGH availability for the same GPU, so this session moved its endpoint preference and fresh archive volume there, keeping the image/model/configuration unchanged.

Two requests immediately after unpausing in Illinois received explicit HTTP 409 `ENDPOINT_PAUSED` rejections while configuration propagated. They had no accepted job IDs. These folders are preserved under project `runs/rejected/`; new requests were submitted only after the definitive rejection was verified. The interrupted parallel caller may later report those earlier exceptions even while its accepted clean36 branch finishes; follow the individual job receipts and branch files for actual render status.

## Completed results

All five three-second variants are local. Each has 13 preserved generated anchors (including opening and terminal support frame), 36 cadence frames, and 72 delivery frames at 24 FPS.

- [Steps with added noise](../exports/noise-steps-v001/step-comparison.mp4): 18 versus 36 steps, both noise 0.06.
- [Noise amount](../exports/noise-steps-v001/noise-amount-comparison.mp4): 0.06 versus 0.03 noise, both 36 steps.
- [Steps without added noise](../exports/noise-steps-v001/clean-step-comparison.mp4): 18 versus 36 steps, no input noise.
- Individual full-size clips: [clean18](../exports/noise-steps-v001/clean18/cadence/preview.mp4), [clean36](../exports/noise-steps-v001/clean36/cadence/preview.mp4), [noise18](../exports/noise-steps-v001/noise18/cadence/preview.mp4), [noise36](../exports/noise-steps-v001/noise36/cadence/preview.mp4), [half36](../exports/noise-steps-v001/half36/cadence/preview.mp4).

**Assistant finding: reducing added noise helped more than doubling the steps.** Full-size late anchors retain conspicuous speckling with 0.06 noise at both 18 and 36 steps. The extra steps do not provide a convincing grain-removal benefit. Both noisy branches also change the scene substantially, adding stars/planets; noise36 introduces another partial explorer near the lower-left edge late in the clip. The clean 18/36 branches remain broadly similar, with smaller differences in flame and portal detail.

The adaptive **half36** branch keeps denoise 0.45 and 36 steps, reducing only the top-right pixel-noise standard deviation to 0.03. Its late-frame speckling is less pronounced and it retains some extra texture/morphing. Grain and scene changes are still present. This is the recommended noisy candidate for human playback; the user-selected clean18 remains the simpler baseline. This experiment does not establish that 36 steps are necessary at noise 0.03, since half-noise at 18 steps was not tested.

Evidence: five evenly spaced samples for each variant, consecutive cadence-frame windows, full-size anchors 15 and 33, and a decoded timestamp-matched every-frame comparison of noise36/half36 at 2.25–2.50 seconds. Review artifacts are under `../exports/noise-steps-v001/`, with the standard harness pages in `reviews/v001/`. Sampled visual findings do not replace Olof's playback preference, which remains pending.

## Validation, timing and cleanup

All five movies fully decode with correct dimensions/duration/frame count. Opening and every displayed generated anchor match archived PNG hashes. The first noisy inputs are byte-identical across the 18/36-step branches; graphs differ only in steps and output prefix. The added-noise map leaves the bottom-left interior unchanged before sampling. No sampling-protection or image-copyback node is present. A fresh clean18 reference probe is pixel-identical to the earlier baseline.

**49 accepted US jobs completed**: 48 new repaints plus one reference probe. All served the same image `2d7cda891` on RTX 4090 workers `9fybtvl18ijbkq` and `aespp1w9k0nikg`; runtime is ComfyUI 0.34.0, PyTorch 2.11.0+cu128 and Python 3.12.3. Reported execution totals 544.621 seconds, including a 141.794-second outlier on the second worker. The slow control job completed before a cancellation attempt could take effect; its existing result was collected and the branch resumed without duplicate GPU submission. No US job failed or was retried in the final endpoint readback.

Median execution was **3.856 seconds at 18 steps with noise**, versus **6.346 seconds at 36 steps with noise**; half36 was 6.171 seconds. These include handler work and are not pure kernel benchmarks. The longest initial US queue delay was 661.312 seconds. Logs later showed real multi-gigabyte image downloads/extraction: moving region improved access but did not eliminate cold setup. The earlier EU wait, US image setup, rejected submissions and one slow worker must remain separate from the added sampling work. Check regional Serverless stock before binding a new volume; a HIGH catalog rating is not an immediate-start guarantee. [RunPod worker states](https://docs.runpod.io/serverless/workers/overview).

All **294 cloud objects / 94,665,622 bytes** were verified against local copies. The endpoint is paused at min/max zero, its worker inventory is empty, and both temporary volumes are deleted. Account spend rate returned to zero. Observed balance decrease was **$0.378**, leaving about $45.77; billing can settle later, so this is not an itemized experiment invoice. Private logs, receipts and exact validation/comparison commands are in `work/noise-steps-session/`. No changes to the worker image were required.
