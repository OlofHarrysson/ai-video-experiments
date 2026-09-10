# Cadence 4 and 5 with learned interpolation

## Human direction and experiment written before rendering

Olof finds RIFE substantially better: it makes flicker read more like morphing. Cadence 2 was worse. Preserve interpolation as an optional finishing step; use the un-interpolated version to diagnose the generated anchors and spatial controls. Do not confuse approval of RIFE with a request to feed interpolated frames back into diffusion.

Test the same three-second continuation at cadence 4 and 5, compared with the accepted cadence-3-plus-RIFE result. Same opening, timed twist/expansion, Krea model, prompt, three native sampling intervals, Euler/simple settings and seed increment per repaint. Cadence 4 has eight new repaints; cadence 5 has seven. Fewer repaint events necessarily assign seeds differently over time and reduce cumulative diffusion updates.

Deliver all comparisons at 24 fps, using the same RIFE 4.25 network and settings. Interpolate directly between generated anchors, preserve their original timestamps, and use original warp-only frames after the final generated anchor. The final interval is 1/3 second for cadence 4 and 1/12 second for cadence 5; do not invent an ungenerated endpoint or stretch the clip. Keep raw versions for diagnosis. No diffusion-noise or RIFE-model changes in this round.

## How interpolation works

Our installed RIFE 4.25 is already a learned interpolation model. Given two repaint images and a requested time between them, it estimates motion fields pointing into both source images. It refines those fields through five network blocks, warps both images, and combines the warped samples using a learned per-pixel mask. This can move a contour between endpoint positions rather than simply fade two stationary contours together. When diffusion adds or removes structure, the network must guess a transition; stretched ornaments, merging shapes or double edges remain possible. It does not understand our scene as persistent 3D objects.

The process is separate from generation: recurrent diffusion creates anchors, then RIFE makes display frames. Switching RIFE off retains every original generation. Our selected implementation uses full-scale motion estimation, float32 on MPS, five scales, and direct arbitrary-time predictions. The installed model does not implement the old ensemble/refinement switches, so those are not useful quality knobs here.

Possible later controls are output frame rate, motion-estimation scale, and a comparison with another trained interpolator. More frames do not guarantee better correspondences. The author's current README recommends 4.25 for most scenes and notes suitability of 4.24+ for diffusion-video processing, so retain this demonstrated model for the cadence comparison first.

Sources checked 2026-09-10: [Practical-RIFE](https://github.com/hzwer/Practical-RIFE), [original RIFE](https://github.com/hzwer/ECCV2022-RIFE), and the installed `train_log/IFNet_HDv3.py` pinned in our interpolation receipts. Outputs: `../exports/cadence-spacing-v001/`.

## Results

Both branches are complete. **Cadence 4 is the assistant's tentative candidate for a modest pacing change:** it retains intricate architecture and a recognizable flame with fewer rebuilding events than cadence 3. **Cadence 5 is the more distinct alternative:** broader forms and a more prominent flame develop, with fewer diffusion updates over the shot. Neither is an established improvement over Olof's accepted cadence-3-plus-RIFE baseline. Human playback judgment remains pending; sampled stills cannot establish a definitive smoothness ranking.

The same RIFE model connects all three versions. Each comparison places the accepted cadence 3 on the left and the new branch on the right.

![Cadence 3 versus 4, both with RIFE](../exports/cadence-spacing-v001/compare-4/preview.mp4)

![Cadence 3 versus 5, both with RIFE](../exports/cadence-spacing-v001/compare-5/preview.mp4)

| Cadence | Repaints per second | New repaints in this clip | RIFE frames between anchors |
| --- | ---: | ---: | ---: |
| 3, accepted control | 4 | 11 | 5 |
| 4 | 3 | 8 | 7 |
| 5 | 2.4 | 7 | 9 |

All deliveries are 72 frames at 24 fps and exactly three seconds. The final interval after the last generated anchor uses the original un-interpolated frames. Raw RIFE exports are also retained: cadence 5's default hold produces 80 raw frames, and the final assembly trims that hold to the original 72-frame duration. No source anchor is moved, replaced or interpolated back into the recurrent generation.

Individual finished videos: [cadence 4](../exports/cadence-spacing-v001/cadence-4/interpolated/preview.mp4), [cadence 5](../exports/cadence-spacing-v001/cadence-5/interpolated/preview.mp4). Diagnosis without RIFE: [cadence 4 raw](../exports/cadence-spacing-v001/cadence-4/preview.mp4), [cadence 5 raw](../exports/cadence-spacing-v001/cadence-5/preview.mp4).

## Verification and execution

- Reviewed both initial RIFE pairs, five overview samples from each comparison, every delivered frame in the selected 1.54–1.75-second window, and full-size matched frames at 1.667 seconds. Fine branches still change shape; interpolation is an inferred connection between redraws, not proof of object continuity.
- All 15 feedback requests completed with verified parent/input/output hashes, requested/executed graphs, every anchor's reconstructed spatial warp, source-frame hashes, selected cadence frames and output timing. All 17 generated anchors across the two branches remain pixel-identical at their original timestamps after RIFE assembly.
- Reused the retained ComfyUI 0.34.0 runtime and all three pinned model assets with zero model downloads or package installation. Weight verification took about 26.4 seconds. RTX 4090 stock was unavailable, an L4 allocation failed without creating a resource, and an RTX 5090 in EU-RO-1 was allocated at $0.99/hour. Earlier control generation used an L40S; this is a practical recipe comparison, not bitwise equivalence across GPU types.
- The sampler remains Euler/simple, CFG 1, shift 1.15, with the last three native Turbo intervals `[0.6545668244, 0.5128440857, 0.3109010756, 0]`, the same prompt and opening, and seeds incremented once per repaint. Median graph execution was 3.04 seconds for cadence 4 and 3.01 for cadence 5. RIFE ran locally on MPS in 17.12 and 20.58 seconds of inference respectively, excluding setup and encoding.
- The shared runner now accepts cadence as a parameter instead of duplicating the feedback algorithm. The interpolation runner accepts fractional source rates such as `12/5`. Its first eleven-frame timing check caught MP4 movie-timescale rounding: 0.458008 instead of 11/24 seconds. Encoding now uses a movie timescale aligned to the frame rate. Repeated pair frames were hash-identical; only container timing changed. Earlier checks and the failed pair receipt remain preserved. Eight local timing/inventory tests and both actual MPS pair checks passed.
- Downloaded and hash-verified all 327 archived files, including 30 remote input/output images. Archive SHA256: `8ab460805839c09e27c0c95490a8edfd078cd90181522f75acb86cca93385093`. The owned GPU Pod was deleted after archive and feedback verification and an empty queue. Live Pod listing is empty; the authorized 50 GB model/runtime volume remains. All generations, raw/interpolated frames, comparisons and receipts are local.

[Runner](cadence_spacing.py), [verification/assembly](cadence_spacing_review.py), shared [feedback runner](turbo_smoothing.py) and [interpolation runner](../../../interpolate.py). Private cloud and archive receipts: `apps/deforum/work/cadence-spacing-session/`.
