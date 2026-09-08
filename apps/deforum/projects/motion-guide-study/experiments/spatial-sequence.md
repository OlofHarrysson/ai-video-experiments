# Twist, turn and ripple with cadence 3

2026-09-08. Olof selected three direct spatial effects and asked for one combined video plus a matched comparison with and without RIFE.

## Before rendering

Nine seconds, 1024×576, one continuous feedback sequence. Twist grows from 0–3 seconds; a flat-sheet sideways turn grows from 3–6 seconds; a ripple travels outward from 6–9 seconds. Completed twist and turn remain applied. The ripple naturally subsides at the end. Same formulas as the effects browser, in normalized preview coordinates; no guide video or estimated depth.

Use the preserved same-model opening and B repaint recipe: SDXL base 1.0, art LoRA 1.1, 18 steps, CFG 4.5, denoise 0.58, DPM++ 2M/Karras, unchanged prompt, seed increment per repaint. Effects are independent of artwork content. Reflection supplies samples beyond the image boundary; it can duplicate edge content and does not reconstruct hidden scenery.

**Cadence 3:** 12 animation FPS, repaint every three frames (4 repaints/second). Generate endpoints at indices 0,3,…,108; index 0 is the preserved opening, with 36 new GPU repaints. The terminal endpoint at 9 seconds supports the final in-between frames; presentation remains exactly 108 frames / 12 FPS = 9 seconds. Native SaveImage jobs are single stills; their transport preview FPS does not define this sequence's timing.

Between generated endpoints, warp both to the current time and blend with weights 1−alpha and alpha. This follows the two-endpoint warp/blend idea in [classic Deforum](https://github.com/deforum/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/render.py#L295), using exact direct coordinate mappings and explicit endpoint timestamps. It is not the original renderer's indexing or Difforum's warp-only skipped-frame behavior. No cadence optical flow. Incremental source lookup is F_source(F_target_inverse(pixel)); never repeatedly apply the whole absolute transform to a previous frame.

**Finishing comparison:** no-RIFE repeats the 12 FPS cadence frames at 24 FPS. RIFE inserts one midpoint between those same frames, also delivered at 24 FPS. All cadence frames remain unchanged anchors, with an explicit final hold to preserve duration. RIFE uses its own learned motion internally; this does not add guide-flow or depth estimation to generation. This pair isolates RIFE, not cadence 3 versus cadence 1.

First inspect the motion-only sequence, validate coordinate inverses and schedule boundaries, then render. Inspect evenly sampled artwork frames and denser windows around effect transitions. Preserve opening, generated endpoints, warped diffusion inputs, cadence frames and both final videos. Record actual outcomes below after execution.

Runner: [spatial_sequence.py](spatial_sequence.py). Media: `../exports/spatial-sequence-v001/`.

## Local validation and setup

The coordinate forward/inverse check passes across all 109 endpoint times with maximum round-trip error under 0.000004 preview pixels. Mappings remain finite and continuous at the 3/6-second effect boundaries. The motion-only overview shows visible twist and perspective turn; reflection repeats edge artwork during the turn. This boundary behavior is retained for the test. The existing 31-test suite passes, including the new 108-to-216-frame timing test.

The shared RIFE adapter now accepts explicit source frame count, source FPS and integer multiplier, retaining its previous 48-frame, 8-to-24 FPS defaults. This experiment uses 108, 12 and 2. Model, padding, inference and preservation checks are unchanged.

RunPod initially replaced the selected tested image with an automatic GitHub build from the preceding documentation/UI commit. The tested image was restored after the build completed, with the original queued job retained. This is an infrastructure startup issue, separate from changing diffusion settings. No new worker build was requested for these effects.

## Completed results

- [Cadence 3 without RIFE](../exports/spatial-sequence-v001/cadence/preview.mp4): 108 motion/blend frames at 12 FPS, repeated for 24 FPS delivery.
- [Cadence 3 with RIFE](../exports/spatial-sequence-v001/rife/preview.mp4): the same 108 anchors plus 107 learned midpoints and one final hold.
- [Motion only](../exports/spatial-sequence-v001/motion-only/preview.mp4): direct transforms of the preserved opening without repainting.

All three are 1024×576, 216 delivery frames and exactly nine seconds, and fully decode. Every cadence frame is preserved byte-for-byte at the corresponding even RIFE output index. The 36 displayed generated endpoints match their archived PNGs; the 37th endpoint at 9 seconds is retained to construct the final cadence interval. Opening and older experiments are unchanged.

**First-pass visual review:** nine evenly distributed samples plus early/middle generated anchors establish the development from a flame in a portal to a sun-like disc, tree and more circular portal. The twist bends the flame and rim visibly. Repainting partly resists the flat-sheet shape, keeping the explorer upright and the portal rounded, although the composition eventually narrows and leaves a large black area on the right. The ripple is clearer in motion-only footage than in the repainted scene. This is a successful pipeline test with unresolved motion fidelity and border handling, not a finished shot.

Timestamp-matched every-frame windows at 4.50–4.75 and 7.50–7.75 seconds show small RIFE changes between unchanged anchors. The cadence blends already provide intermediate imagery, so this finishing difference is modest. Some overlapping explorer/contour detail is present in cadence blends and remains after RIFE; interpolation does not repair that or the black boundary. Review pages are in `../exports/spatial-sequence-v001/reviews/v001` (motion), `v002` (artwork overview), and `v003` (28 matched samples across four pages). These are sampled-image findings; human playback preference is still pending.

**Execution:** 36 completed serverless jobs, no failed/retried jobs in the endpoint health readback. The first job waited 358.635 seconds; total reported execution was 153.859 seconds, with median job execution 3.731 seconds and roughly 7–8-second warm round trips. All 36 jobs ran on the already-starting worker from image tag `2d7cda891`, even though the endpoint was subsequently restored to `f106834b7`: changing endpoint configuration did not prevent that stale worker from serving queued work. Runtime reports ComfyUI 0.34.0, PyTorch 2.11.0+cu128, Python 3.12.3 and RTX 4090. Future sessions must inspect actual worker/job provenance, not infer the serving image from endpoint settings.

RIFE 4.25 completed locally on MPS in 17.98 seconds including model load, interpolation, encoding and checks; interpolation/output took 12.45 seconds. The first-pair result was inspected before the full pass. All 31 local tests passed, as did separate movie-duration, frame-count, original-anchor and full-decode checks.

**Cleanup:** 216 cloud objects / 66,265,398 bytes were verified against local copies. The endpoint is paused at min/max zero, all jobs completed, no workers or Pods remain, and its volume is detached and deleted. Account spend rate returned to zero; the observed balance reduction was $0.0951 (billing observation, not an itemized invoice). Private receipts, commands, validation and timing data are in `work/spatial-sequence-session/`. REST detachment required an explicit User-Agent header; without it urllib received HTTP 403. MCP's empty volume list again left the attachment unchanged, so readback remains necessary.

The comparison isolates RIFE on one cadence-3 render. It does not establish that cadence 3 improves quality over cadence 1. Next decisions should follow playback feedback, with border handling and how strongly repainting preserves the chosen deformation as the main open issues.
