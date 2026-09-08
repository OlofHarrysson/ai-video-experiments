# Repaint controls on the same short twist

2026-09-08. Olof accepts the cadence setup, values motion-only previews, and prioritizes unwanted repainting over black-border repair. He requested denoise testing plus a simple combined regional-mask/additional-noise example. No object tracking, explicit feedback alpha blend, or image-space copying of protected pixels over the result.

## Before rendering

Use exactly the first three seconds of [twist, turn and ripple](spatial-sequence.md): same opening, direct twist, 12 animation FPS, cadence 3, 18 steps, CFG 4.5, art LoRA 1.1, prompt and incrementing seed sequence. Keep endpoint warping/blending for cadence, as accepted. Deliver at 24 FPS by repeating the cadence frames, without RIFE, which Olof found difficult to distinguish in the previous comparison.

1. Compare global denoise **0.35 / 0.45 / 0.58**. Reuse the preserved 0.58 anchors and motion-only frames; render the two lower settings from the same opening. Keep all outputs and show a compact comparison.
2. Choose a lower-denoise candidate after first-pass review. From the same opening, run one additional branch with that denoise, a bottom-left sampling-protection region and top-right pixel noise. Both controls change together; this is an illustration of the combined controls, not an attribution test of each one.

Regions use image coordinates and stay fixed on screen. Across a 64-pixel feather, the sampling mask transitions from 0 (bottom-left interior) to 1 elsewhere. ComfyUI's existing `SetLatentNoiseMask` constrains the sampler in latent space; no final pixel copyback is used. A mask value is not a calibrated local denoise value, and a VAE round trip can change protected pixels. [Pinned sampler implementation](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/samplers.py#L570).

The top-right receives Gaussian image-space noise before VAE encoding: standard deviation 0.06 on RGB [0,1], one noise field shared across channels, seed 524001 + repaint index, clipped then quantized to PNG. This is additional pixel noise, separate from KSampler's usual diffusion noise. All other regions have zero extra noise except the feather transition. Mask and noise previews are archived alongside exact input PNGs and graphs.

Twelve new endpoint repaints per new branch; 36 new jobs total plus the reused baseline. The terminal endpoint at 3 seconds supports the final cadence interval. Each final clip is 36 cadence frames / 12 FPS = 3 seconds, or 72 delivery frames at 24 FPS.

Runner: [repaint_controls.py](repaint_controls.py). Media: `../exports/repaint-controls-v001/`. Review astronaut/portal changes, disappearing background details, mask-boundary behavior and retained detail. Preserve the raw controls even if the combined result is not aesthetically better.

## Completed results

All four three-second branches are preserved. Each has 13 generated anchors including the opening and terminal support frame, 36 cadence frames and 72 delivery frames at 24 FPS. No RIFE was applied.

- [Denoise comparison](../exports/repaint-controls-v001/denoise-comparison.mp4): left 0.35, middle 0.45, right 0.58.
- [Regional comparison](../exports/repaint-controls-v001/regional-comparison.mp4): uniform 0.35 versus the same setting with bottom-left sampler protection and top-right added noise.
- Full-size clips: [0.35](../exports/repaint-controls-v001/d035/cadence/preview.mp4), [0.45](../exports/repaint-controls-v001/d045/cadence/preview.mp4), [0.58](../exports/repaint-controls-v001/d058/cadence/preview.mp4), [regional](../exports/repaint-controls-v001/regional/cadence/preview.mp4).
- [Motion only](../exports/repaint-controls-v001/motion-only/preview.mp4) and [region locations](../exports/repaint-controls-v001/region-preview.png).

**Assistant recommendation: uniform 0.35 for the next creative test.** Five evenly spaced samples per branch, consecutive-frame windows and a full-size regional anchor show that 0.35 retains the astronaut silhouette and portal structure more closely while still bending the flame and composition. At 0.45 the portal develops more detail and the flame becomes more elaborate. At 0.58 the flame becomes a rounded disc and background moons appear. Lower denoise reduces these changes; it does not freeze the image or establish long-clip stability. Olof's playback preference remains unconfirmed.

The regional branch uses 0.35. Its protected corner changes less on the first repaint, but repeated warping and VAE round trips leave soft, stretched detail at bottom-left by the end. The top-right develops conspicuous grain that spreads with subsequent motion. This illustrates the controls but is not the recommended clean result. The fixed screen mask does not follow the astronaut. Extra input noise and the sampling mask change together, so their separate contributions are not isolated.

A small diagnostic compares the first output against its clean warped input, excluding feather boundaries. Mean absolute RGB change (0–255 units) falls from **11.45 to 4.75** in bottom-left and rises from **8.72 to 12.35** in top-right. These values support the intended regional intervention, not a claim of better visual quality or unchanged protected pixels. The later grain and smear are visible in full-size anchor 33. Review images and the decoded, timestamp-matched every-frame window at 2.25–2.50 seconds are preserved under `../exports/repaint-controls-v001/reviews/v001/`.

## Execution, validation and cleanup

The 36 new animation jobs and one reference probe all completed: 37 jobs, 121.33 seconds of reported execution, median 3.041 seconds per job. Initial queue delay reached 624.646 seconds while workers reported pending image pulls. A newer completed image was selected during diagnosis, but **all jobs actually ran on the older worker `fqom8899qiq0k1`, image `2d7cda891`**. The switch did not establish that the newer image solved startup. Runtime: ComfyUI 0.34.0, PyTorch 2.11.0+cu128, Python 3.12.3, RTX 4090. Worker code/model definitions were unchanged between the two image commits.

The extra reference probe reproduced the earlier 0.58 frame exactly, including its PNG hash, using the identical archived input and graph. This supports reusing the previous baseline under the serving runtime. It does not verify the newer configured image, which served none of these jobs.

Local checks confirmed matched graphs, quadrant orientation, sampler-only masking, deterministic added noise, preserved opening and all generated-anchor hashes. All four individual movies and two labeled comparisons have the expected three-second duration and frame counts and fully decode. Twenty existing interpolation/review tests passed. FFmpeg here lacks `drawtext`; comparison labels were rendered with Pillow before normal video encoding.

All **222 cloud objects / 66,295,384 bytes** were byte-verified against local copies. The endpoint is paused at min/max zero, no workers or Pods remain, and the temporary volume was detached and deleted. Spend rate returned to zero. Observed balance reduction was **$0.0552**, leaving about $46.19; this is an account observation, not an itemized invoice. Private job receipts, validation, copy verification and commands remain in `work/repaint-controls-session/`.

## Human playback feedback

Olof prefers **0.45**, finding 0.35 blurry and 0.58 too changeable. He rejects protected-region artifacts; noisy top-right remains interesting. His preference supersedes the assistant recommendation above. [Next test](noise-steps.md): 18 versus 36 sampling steps at 0.45, with and without top-right noise, without protection.
