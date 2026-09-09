# Does repeated repainting degrade the picture?

Olof observes that the cathedral loses quality over time and asks whether repeatedly diffusing an unchanged picture should improve it. Test that directly before choosing a remedy. Keep Krea; preserve all earlier generations.

## Controlled comparisons

Use the accepted Krea cathedral opening at 1536×1024 and its unchanged prompt. Run 24 cycles, saving every cycle. Inspect cycles 0, 1, 4, 11 and 24. The first eleven cycles match the repaint count of the earlier three-second animation.

1. **No movement, repaint 0.10:** output PNG becomes the next input unchanged; same Euler/simple, eight updates, CFG 1, incrementing seeds.
2. **No movement, repaint 0.30:** same test at the earlier higher strength. This distinguishes very-low-noise behavior from a somewhat stronger repaint.
3. **VAE only:** repeatedly encode/decode with the same VAE and PNG checkpoint, without sampling, text or noise. This isolates reconstruction plus 8-bit quantization losses, not the VAE in unlimited precision.
4. **Local spatial controls:** eleven repeated three-frame warps versus a single warp from the original to each matched endpoint. Compare both to the preserved full warp/repaint 0.10 clip. This is a diagnostic, not removal of feedback from the animation recipe.
5. **PNG control:** repeated PNG save/load must preserve the original 8-bit RGB pixels exactly. Lossless PNG storage does not make float-to-8-bit quantization lossless.

There is one opening and one seed sequence per repaint branch. Results can establish behavior of this recipe on this image, not a theorem about every diffusion model or asymptotic convergence. Difference, edge and color metrics describe specific changes; they are not aesthetic scores. Aesthetic drift is distinct from blur and from desired morphing.

Runner: [repaint_diagnosis.py](repaint_diagnosis.py). All controls and the matched animation are complete and archived locally.

## Adaptive follow-up

The local controls show substantial bilinear resampling blur. [warp_resampling_probe.py](warp_resampling_probe.py) compares Lanczos with identical coordinates, and [resampling_feedback.py](resampling_feedback.py) tests that one change in an eleven-repaint, cadence-3, 0.10 twist against the preserved bilinear clip. Existing animation runners remain unchanged.


## What happened

**The user's observation is reproduced for this Krea recipe, even with no motion.** After 24 repetitions, 0.10 loses substantial contrast and becomes hazy; 0.30 rebuilds the scene into flatter, simplified decorative shapes. Neither returns toward the original rich shading and fine architecture. This does not establish that every diffusion model, prompt or recipe must degrade, nor does it establish asymptotic convergence.

![No movement: original, VAE-only, repaint 0.10 and repaint 0.30](../exports/repaint-diagnosis-v001/comparison/preview.mp4)

Read left to right: top row is the unchanged original and VAE-only recurrence; bottom row is repaint 0.10 and 0.30. Playback advances four complete cycles per second, showing cycles 0–24. There is no spatial motion or temporal interpolation in these diagnostic clips.

| Control | Observation | Evidence |
| --- | --- | --- |
| Repaint 0.10, no motion | Gentler early changes still accumulate; contrast and color fall, shading becomes flat and a hazy patterned surface develops. | [Clip](../exports/repaint-diagnosis-v001/repaint010/preview.mp4) |
| Repaint 0.30, no motion | Larger redraws simplify architecture and change the seed and surrounding shapes. More clearly resolved than 0.10 at the end, but markedly flatter than the opening. | [Clip](../exports/repaint-diagnosis-v001/repaint030/preview.mp4) |
| VAE + PNG recurrence | Initially close to the source; after 24 cycles, colored/blocky reconstruction artifacts and rough texture are visible. | [Clip](../exports/repaint-diagnosis-v001/vae-only/preview.mp4) |
| VAE with float IMAGE feedback | Artifacts persist and brightness drift is stronger. Removing intermediate PNG conversion is not a sufficient fix. | [Matched final images](../exports/repaint-diagnosis-v001/vae-float/comparison.png) |
| Repeated bilinear warp | Small structures visibly blur without any diffusion. | [Exact crop](../exports/repaint-diagnosis-v001/warp-review/detail.png) |
| Repeated Lanczos warp | Retains substantially more fine structure in the no-diffusion control; ringing is a potential tradeoff. | [Exact crop](../exports/repaint-diagnosis-v001/warp-lanczos/detail.png) |
| PNG save/load, unchanged uint8 pixels | All 24 cycles retain identical RGB pixels. | `exports/repaint-diagnosis-v001/local-controls.json` |

The float probe uses only core ComfyUI nodes: the decoded IMAGE tensor directly feeds the next VAEEncode. It saves diagnostic snapshots at cycles 1, 4, 11 and 24 after the recurrence; saved PNGs do not feed back. [Graph runner](vae_float_probe.py), [verification](vae_float_review.py). The first cycle exactly matches the PNG branch, as expected; subsequent differences establish the storage-path control.

## Matched animation remedy probe

Only the resampler changes from bilinear to Lanczos. Same accepted opening, 0.10 denoise, incrementing seeds, eight Euler/simple updates, CFG 1, direct twist, twelve source fps, cadence 3 and eleven repaints. The previous generated image remains the initialization throughout. No blend, reference conditioning, masks or RIFE were added.

![Current bilinear left; Lanczos right](../exports/resampling-feedback-v001/comparison/preview.mp4)

The full-size frame review finds more retained fine texture with Lanczos, but the overall animation still changes in contrast and appearance. The improvement is much less decisive once repainting is active than in the motion-only test. It does not solve the whole quality problem. [Last-frame crop](../exports/resampling-feedback-v001/comparison/detail-last.png). Existing shared runners remain unchanged; the isolated probe is preserved for a human playback decision.

## Interpretation and next step

A single render completing its denoising schedule and repeatedly restarting from its own output are different operations. Our loop repeatedly reconstructs through a VAE and starts another noisy sampling trajectory. Neither operation is guaranteed to preserve all detail or monotonically improve aesthetic quality. The experiments establish separate reconstruction and resampling failure modes, plus a substantially different drift when sampling is added. They do not assign an additive percentage of degradation to each stage or isolate the sampler from its interaction with VAE errors.

**Recommended next diagnostic:** keep the sampled latent as the next repaint's initialization, encode the accepted opening only once, and decode copies for inspection. Initially leave motion off and hold the prompt, schedule and seed sequence fixed. This separates repeated VAE encoding from repeated sampling while preserving feedback. If it helps, test how to retain useful spatial control; moving a latent grid is not automatically equivalent to warping RGB pixels. If latent-only repainting still drifts, prioritize the Turbo low-noise sampling recipe and supported timesteps before another strength sweep. Both remain hypotheses, not implemented fixes.

## Measurements and limits

For no-motion 0.10, grayscale standard deviation falls from **56.15 to 33.78** across 24 cycles, consistent with the visible contrast loss. For 0.30 it ends at **40.60**. VAE-only with PNG ends at **58.92**, despite visible reconstruction artifacts: contrast alone would miss that failure. The float VAE path shifts mean grayscale from **80.93 to 95.21**; the PNG path ends at **82.05**. Neither is an aesthetic score.

Eleven repeated bilinear warps have whole-image Laplacian variance **23.80**, compared with **269.39** for one warp to the endpoint and **324.49** for repeated Lanczos. This measures high-frequency energy, including aliasing/ringing; it is not a percentage measure of sharpness or perceived quality. The matched crops, not the metric alone, establish the visible blur difference.

Reviewed decoded video frames at cycles 0, 1, 4, 11 and 24 for each no-motion clip, full-size final comparisons and crops, plus matched animation overviews and every displayed frame around 1.9–2.17 seconds. Source PNGs and all requested/executed graphs are preserved. [Main review](repaint_diagnosis_review.py), [animation review](resampling_feedback_review.py). Each of the 25 diagnostic source images is repeated six times in its 24 fps MP4; no new intermediate images are synthesized.

## Execution and cleanup

**84 verified successful jobs:** 48 no-motion repaints, 24 PNG/VAE cycles, eleven Lanczos feedback repaints and one 24-cycle float VAE graph returning four snapshots. All **173 remote input/output files** matched local archived hashes before deletion. The graph/lineage checks cover all 84 jobs; the spatial feedback probe also verifies sampled warp reconstruction and cadence boundaries. Core ComfyUI 0.34.0, PyTorch 2.10.0+cu128, the same pinned Krea FP8/encoder/VAE assets and L40S 48 GB. Median job execution across the mixed workload was 9.74 seconds.

Owned Pod and attached storage are deleted. Final checks show no Pods, no network volumes and **zero hourly spend**. Observed balance change at cleanup was **$0.42**, leaving **$42.58**; this account snapshot is not a final itemized invoice. Private receipts are under `apps/deforum/work/repaint-diagnosis-session/`. The main archive and the supplementary float-control archive are verified locally; no media was discarded.

A central workflow lesson was recorded as **AF-20260909-210644**: isolate repeated warp/reconstruction/repaint losses before broad parameter sweeps. This is not a claim that earlier visual exploration was valueless.
