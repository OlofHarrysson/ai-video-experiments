# Krea: lower repaint strength

Olof selects Krea for further work and pauses Klein. He still finds the cathedral animation too flickery and requests lower repaint strengths.

Compare **0.10, 0.18 and 0.24** against the preserved **0.30** clip. Keep the accepted 1536×1024 Krea cathedral opening, prompt, incrementing seeds, Euler/simple, CFG 1, eight sampling updates, three-second twist, source 12 fps and cadence 3. Each branch generates eleven anchors from its own warped previous anchor. Intermediate frames only warp the preceding anchor. No blending, RIFE, reference conditioning, masks, extra image noise or depth.

This isolates denoise within this recipe. Lower denoise reduces the starting sampling noise; it is not a percentage blend of two images. Judge redraw jumps together with detail retention. A gentler setting can still soften across repeated VAE encoding and spatial resampling.

Runner: [krea_low_repaint.py](krea_low_repaint.py). All three clips completed and are archived locally.


## Results

**Assistant shortlist: 0.10 first, 0.18 as the alternative.** The 0.10 sequence retains more of the original fine architectural structure and makes smaller changes at the inspected repaint boundary. It still softens and changes texture/lighting over time. The stronger settings simplify the filigree into broader, flatter patterns. This is an assistant frame-based review; Olof's playback judgment is pending.

![Three lower strengths and the preserved control](../exports/krea-low-repaint-v001/comparisons/all/preview.mp4)

Top row: 0.10 and 0.18. Bottom row: 0.24 and the earlier 0.30 control. Every panel starts from the same opening and follows the same twist and seed sequence. No new 0.30 render was required.

| Denoise | First-pass finding | Video |
| --- | --- | --- |
| 0.10 | Smallest redraws; retains the original fine forms best in this group, with some accumulated softness/texture residue. First candidate for less flicker. | [Full size](../exports/krea-low-repaint-v001/d010/preview.mp4) |
| 0.18 | More rebuilding and simplified ornament; a middle alternative if 0.10 feels too restrained. | [Full size](../exports/krea-low-repaint-v001/d018/preview.mp4) |
| 0.24 | More distinct redraw and flatter decorative shapes; closer to the earlier recipe. | [Full size](../exports/krea-low-repaint-v001/d024/preview.mp4) |
| 0.30, preserved | Larger discrete redraws, including a visible restructuring of the white arch near two seconds. | [Earlier control](../exports/cathedral-feedback-v001/krea/gentle/preview.mp4) |

A [two-panel comparison](../exports/krea-low-repaint-v001/comparisons/lower-vs-control/preview.mp4) also preserves 0.18 against 0.30. All generations and run receipts remain indexed through each export's anchor records.

## Review and validation

Reviewed six evenly spaced decoded frames per new clip and the existing 0.30 overview, then all displayed frames around 1.9–2.17 seconds in matched pairs. These windows bracket a repaint boundary. The MP4 contains 72 frames at 24 fps, duplicating each of the 36 source frames; these duplicates do not add new motion. Contact sheets and timestamp metadata are beside the exports under `reviews/`.

Mean absolute pixel change between each already-warped input and its repaint was **7.45 / 9.73 / 11.98 / 14.23** channel levels out of 255 for 0.10 / 0.18 / 0.24 / 0.30. This supports smaller redraws at lower strengths, but includes lighting and texture differences and is **not a perceptual flicker score**. It does not establish that longer clips will remain clear or artistically interesting.

[krea_low_review.py](krea_low_review.py) verified all 33 requested/executed graphs, parent/input/output hashes, 108 source frames, sampled full-resolution warp reconstruction and cadence boundaries. All sampling initialized from the previous generated anchor after warping. Archived hashes match exactly; cross-platform remap checks allow the established tiny rounding tolerance. Pinned ComfyUI 0.34.0 (`12d5279438bfefc058a269eae805ceab6047777f`), PyTorch 2.10.0+cu128, official Krea FP8 weights from the existing pinned model manifest, L40S 48 GB. Eight actual Euler/simple updates per repaint, CFG 1.

## Execution and cleanup

The three independent feedback branches shared one ComfyUI queue. Median job execution was **9.79 seconds**; the Krea model download and checksum verification took **473 seconds**. Only the three Krea assets were downloaded; no Klein inference ran. All 68 remote input/output files matched local archived hashes before deletion. Queue was empty, the owned Pod and attached storage were deleted, and the final account showed no Pods or network volumes and **$0/hour** current spend.

Observed balance change at cleanup: **$0.31**, with **$43.07** remaining. This is an account snapshot, not an itemized final invoice. Private operational receipts are ignored under `apps/deforum/work/krea-low-repaint-session/`; media and verification artifacts are preserved in the project export/run directories. Code and notes are tracked in Git; media remains local and ignored.
