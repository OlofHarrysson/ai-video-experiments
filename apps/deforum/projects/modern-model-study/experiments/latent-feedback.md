# No-motion latent feedback

Olof approves retaining sampled latents between repaints and selects Lanczos for future RGB warps. This experiment isolates repeated sampling from repeated VAE encoding. Keep Krea Turbo, the accepted cathedral opening, prompt, incrementing seeds, eight Euler/simple updates and CFG 1. Compare 24 cycles at denoise 0.10 and 0.30 against the preserved no-motion PNG-feedback controls.

Encode the opening once. Wire each KSampler LATENT output directly to the next KSampler's latent initialization. Decode each cycle for inspection only; decoded images never feed generation. There is no spatial motion, reference conditioning, blending, RIFE or depth in this diagnostic. This is a controlled test, not a production animation pipeline or a latent-warp implementation.

Verify the full requested/executed graphs, seed sequence, model/runtime versions, opening and saved output hashes. Compare cycle 1 with the earlier RGB-feedback branch as a reproducibility check. Review cycles 0, 1, 4, 11 and 24 and short consecutive-frame windows. Save every generated state and show matched playback comparisons. Metrics indicate change and contrast, not aesthetic quality.

## Hypothesis

The user's larger-step training hypothesis is plausible: [progressive distillation](https://arxiv.org/abs/2202.00512) teaches a student sampler to approximate more teacher steps with fewer evaluations. [Krea's official repository](https://github.com/krea-ai/krea-2) identifies Turbo as an eight-step distilled checkpoint and RAW as undistilled. This does not establish the exact distillation method used by Krea, or that all modern models are distilled.

The sampler does not decide that an image is aesthetically finished and skip work. It follows its supplied timestep/noise schedule. Our low-denoise use of a longer schedule's tail differs from the official full-generation eight-step recipe. Sensitivity to that usage, and recurrent distribution drift, remain hypotheses. This experiment changes representation reuse, not distillation or the schedule, so it cannot establish a causal distillation effect.

## Spatial default

New RGB warps use app-level `spatial_warp.remap_rgb`: Lanczos4 with the existing reflected border. Historical bilinear experiments retain their original behavior so old controls remain reproducible. The accepted Lanczos runner now uses the shared helper with identical output pixels.

## Results

**Direct latent feedback does not solve the main degradation.** Both 24-cycle branches completed. Their first repaint matches the corresponding preserved RGB-feedback control exactly in all decoded RGB pixels. This supports equivalent initial conditions before the feedback paths diverge.

![RGB feedback left; latent feedback right; 0.10 above and 0.30 below](../exports/latent-feedback-v001/comparison/preview.mp4)

At 0.10, both paths gradually lose contrast and rich shading, becoming flatter patterned illustrations. The latent path changes some textures and colors but does not retain the opening's material depth. At 0.30, latent feedback also simplifies and rearranges the architecture; it retains somewhat more contrast than the RGB path at cycle 24, but does not preserve the original fine architecture. This is not an accepted replacement animation recipe or a human taste ranking.

| Grayscale standard deviation | Opening | RGB feedback, cycle 24 | Latent feedback, cycle 24 |
| --- | --- | --- | --- |
| Repaint 0.10 | 56.15 | 33.78 | 32.34 |
| Repaint 0.30 | 56.15 | 40.60 | 43.47 |

This is a contrast diagnostic, not a quality score. Full-size crops and decoded video samples establish the visible flattening. Reviewed cycles 0, 1, 4, 11 and 24, final detail crops, and each displayed frame in a matched 1–1.5-second window for 0.10. Diagnostic playback shows four cycles per second, with repeated delivery frames and no interpolation.

The result excludes repeated VAE encoding as a sufficient explanation of the whole failure. It does not establish how much VAE error contributes when sampling interacts with reconstructed images, nor that distillation is the cause. The initial VAE encode and final observation decode remain; decoded outputs are never fed back. Raw latent tensors are retained inside each graph, not exported as continuation checkpoints.

## Recommended next comparison

Test the end of Turbo's actual eight-step schedule against our current subdivided low-noise schedule, with feedback intact. The previously verified full eight-step schedule's last nonzero sigma is about 0.311; our 0.10 recipe instead uses eight updates beginning at about 0.260. These are different trajectories, not merely different amounts of repaint. A controlled follow-up should match the starting noise coefficient where possible and change the update schedule explicitly. Neither full-schedule tails nor their suitability for repeated image editing are guaranteed by the official text-to-image recipe.

Keep latent-motion integration deferred while the no-motion sampler still loses quality. An undistilled Krea RAW comparison remains a later option, with its own opening and verified settings. This test does not justify a general old-versus-modern model conclusion.

## Execution and archive

Two successful core-node jobs, 24 samplers each, **48 generated states**. Full graph, seed, opening, output-hash and lineage verification passed. The requested/executed graphs each contain exactly one VAEEncode and 24 direct KSampler latent links. Both first-cycle RGB differences are zero. Source and comparison videos are local; all **52 remote input/output files**, including two bundled files, are hash-verified and preserved. [Runner](latent_feedback.py), [review and verification](latent_feedback_review.py).

ComfyUI commit `12d5279438bfefc058a269eae805ceab6047777f` / 0.34.0, PyTorch 2.10.0+cu128, L40S 48 GB, unchanged pinned Krea Turbo FP8/encoder/VAE assets and prompt. The graphs took 270.60 and 325.21 seconds, including decoding/saving. That differs from per-repaint warm timing and excludes setup/download/transfer time.

Both owned Pods and attached storage are deleted. Final account checks show no Pods, no network volumes and zero hourly spend. Observed balance change **$0.44**, leaving **$42.06**; these are account snapshots, not a final itemized invoice. Private receipts, startup logs, the verified archive and cleanup evidence are under `apps/deforum/work/latent-feedback-session/`.

## Verification notes

The shared Lanczos helper produces exactly the old Lanczos formula's pixels on the same local runtime. Three comparisons against archived Linux-generated warped inputs differ by at most one intensity unit in only 2–3 of 4,718,592 channel values; do not claim cross-platform byte identity. Historical bilinear controls are unchanged.

The initial Pod had an empty CLI-generated PUBLIC_KEY. Repairing its environment restarted it during workspace initialization; it then repeatedly failed on a missing Python environment. The Pod was deleted before inference and replaced with the same image and an explicitly supplied existing public key. Interrupted initialization is a suspected cause. Central incident: AF-20260909-220029. The replacement completed initialization before the pinned runtime update. The slow encoder transfer was completed through byte ranges of the same pinned file and verified against its complete expected SHA-256 before sampling.
