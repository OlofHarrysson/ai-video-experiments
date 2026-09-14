# Settle promptly after the city appears

Approved plan, recorded before inference on 2026-09-14. Olof likes the low-hold shot but finds frames 105–132 too flickery after the successful city reveal.

Preserve all nine paintings through frame 96 from `hold-transform-v001/low-hold`. Change only the subsequent noise schedule: starting noise 0.25 at painting 108 (4.5s), then 0.10 at paintings 120–180 (5–7.5s). Keep prompts, seed sequence, three Euler intervals, CFG1, time-based Lanczos warps, two paintings per second and 24 fps unchanged. Each new painting consumes its own warped previous result. No adaptive detector, masks, latent mixing or reference adapter is introduced.

Replay the original frame-108 repaint from its saved input before the new branch. Check pixel equality against the archived original as a runtime control. Seven new recurrent paintings plus this diagnostic are expected. If replay differs, report and resolve that discrepancy before attributing differences to the noise schedule.

Finish with the established RIFE 4.25 scale 1. The delivered PNG timeline through frame 96 must match the previous video exactly. RIFE frames 97–107 change because they interpolate toward the new painting 108. The shell-to-city reveal before frame 96 is deliberately preserved. Inspect native paintings and selected consecutive frames around 105–132; measure repaint difference against the warped input, without treating it as a quality score.

Present the previous liked version on the left and early settling on the right. Preserve all attempts locally, verify their lineage and delivery, and remove only the owned short-lived Pod and temporary media. Retain the authorized model volume. Target less than $0.50 incremental cost within the existing experiment budget.

## Results

The seven new paintings preserve the city architecture much more closely after the reveal. The frame-96 circular arch, right-hand rectangular tower, gold railing, triangular roofs and orange patina persist while the programmed counter-turn continues. The old branch replaces and enlarges parts of this architecture over frames 108–132. The new branch also keeps the original narrower city vista: stopping redesign earlier prevents the later, wider opening. That is an artistic tradeoff, not an execution failure. Human playback preference is pending.

The original frame-108 control reproduced its pixels exactly on the new A100 session. All eight new jobs passed input/output hashes, execution history, model graph checks and the PNG's input fingerprint. Every generated branch input was recomputed from the previous painting with the correct absolute-time Lanczos warp and matched pixel-for-pixel. All nine prefix paintings are unchanged.

| Painting | Previous noise | New noise | Previous redraw magnitude | New redraw magnitude |
|---|---:|---:|---:|---:|
| 108 / 4.5s | 0.780 | 0.250 | 0.08881 | 0.01770 |
| 120 / 5.0s | 0.744 | 0.100 | 0.06862 | 0.00970 |
| 132 / 5.5s | 0.676 | 0.100 | 0.05424 | 0.00931 |

Mean redraw magnitude across these three paintings is 82.7% lower. This is normalized absolute RGB difference from the warped initialization; it is not percentage of flicker removed or a perceptual quality score. Surface shading remains readable in the inspected short ending, with fewer changing structures. Longer low-noise recurrence may still degrade fine detail.

Consecutive delivery crops at frames 103–108 and 115–120 support the source-painting finding: the right-hand tower, staircase and roof retain their identities with less doubled interpolation detail. The old version introduces new openings, balconies and domes across the same intervals. These bounded visual samples support improved preservation in the reported section, without establishing a general flicker score.

[Delivery verification](../exports/early-settle-v001/delivery-check.json) passes: eight seconds, 192 frames at 24 fps, all sixteen anchors retained, 165 RIFE intermediates and eleven final hold frames. PNG timeline frames 0–96 are byte-identical to the previous finished sequence. The standalone and comparison MP4s fully decode. The dedicated Chrome reviewer displays both frames and controls together at a 1456×858 viewport; painting stepping advances both from 108 to 120 and playback reaches frame 191 in both. It is paused at frame 96 for comparison and remains running through Devrun at http://localhost:3028/.

The assistant recommends earlier settling when the frame-96 composition is the desired destination. An automatic completion detector remains deferred: this run tests the value of a human-selected completion point first. The earlier shell-to-city morph remains unchanged and can still show RIFE ghosting during its large transformation.

### Viewing and resources

- [Synchronized reviewer](http://localhost:3028/): previous low-hold version left; earlier settling right.
- [Comparison video](../exports/early-settle-v001/comparison.mp4).
- [New standalone video](../exports/early-settle-v001/early-settle/section-016/rife/preview.mp4).
- [Paintings and detail crops](../exports/early-settle-v001/review/), [generation checks](../exports/early-settle-v001/generation-check.json).

All 288 archive files are local and SHA-256 verified. The owned A100 Pod, sixteen owned remote media files and session scratch were removed; the authorized model volume remains. Conservative estimated round cost is **$0.22**, including a disk allowance, not posted billing. No new model or node installation was needed.

## Human feedback and deferred direction — 2026-09-14

Olof observes that the earlier-settling ending essentially stops transforming and does not look very different from what he expects warping alone would produce. He considers keeping low noise potentially useful for subtle additional movement, but its value over warp-only motion is not established. He proposes using diffusion when change is wanted and pausing it otherwise, and explicitly parks these experiments while we improve the codebase. This is not a completed warp-only comparison or a selection of a universal noise/cadence default. The [refactor plan](../../../../../docs/refactor-plan.md) preserves this future question while keeping current behavior unchanged.
