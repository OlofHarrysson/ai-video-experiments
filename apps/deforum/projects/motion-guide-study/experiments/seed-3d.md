# B's repaint recipe with a small 3D camera move

2026-09-07. Olof rejected the fixed-seed result and selected B for a small 3D experiment. Keep incrementing seeds because they are simple and reproducible; no need to introduce unrecorded randomness.

## Shot and controls

Start with the exact same SDXL/art-LoRA opening as B. Move the viewpoint sideways past the nearby portal rim with a slight compensating turn, aiming to retain the person and central light near the middle. The rim should move more than the distant scene. Preview actual depth reprojection before repainting.

Existing ComfyUI nodes only: Depth Anything V2 Small, Difforum camera/guide builder/feedback sampler. Model, LoRA, prompt, negative prompt, 18 steps, CFG 4.5, DPM++ 2M/Karras, denoise 0.58, seeds 7301–7348, no extra pixel noise/sharpening/colour matching remain B's recipe. Replace B's 2D zoom with 3D motion: per-step scene-point translation X = -0.004, Y rotation = +0.035 degrees, 45-degree FOV, relative near/far 2/10. Frame zero is identity. These scene transforms correspond approximately to a viewpoint moving right and turning back left; they are not calibrated metres or a reconstructed scene.

Two six-second outputs (48 source frames at 8 FPS): camera-only preview and diffusion repaint. The guide reprojects the initial image at cumulative poses. Feedback warps the preceding repaint by each camera delta. Depth is estimated from the opening and reused in this short existing-node loop; it does not track newly generated objects or remain aligned indefinitely. The upstream 3D warp rounds projected points to integer pixels, so small per-step motion can quantize; its repeated feedback warp is not pixel-equivalent to the guide's one-shot cumulative projection. Re-estimating/reprojecting depth is a future improvement if this limitation becomes visible.

Comparison caveat: preserved B has an 8-bit PNG checkpoint after frame 3; the new repaint runs continuously. This is a creative camera test with matched sampling settings, not a perfectly isolated geometry-only benchmark. No interpolation or edge crop is applied, so errors remain inspectable.

## Review

Inspect the depth map, identical frame-zero pixels, initial/final guide and coverage masks. Distinguish expected out-of-view borders and newly revealed surfaces from repaint artifacts. Review paired timestamps against B and consecutive frames around any major change. Preserve every output and show the rendered video directly in chat.

## Results

Completed: [3D repaint](../exports/seed-3d-v001/repaint/preview.mp4) and [depth-only camera preview](../exports/seed-3d-v001/guide/preview.mp4), both six seconds. Same opening pixels, 48 source frames / 144 delivery frames each. No interpolation, crop or smoothing has been applied. All source frames and archives are local.

Assistant first-pass assessment: the repaint keeps the portal/person composition recognizable and fills the preview's obvious missing pixels. The camera contribution remains subtle compared with the generated morphing. It is a useful short depth-warp test, not yet a strong cinematic move or evidence of a stable reconstructed scene. Olof's playback judgment is pending.

- **Geometry:** the depth estimate places the outer portal rim and person closer than the central light. Approximate projection of selected saved-depth landmarks gives outer-left rim X shift -25 px, inner-left rim -9 px, person -13 px and central light +10 px by frame 47. Translation and compensating yaw combine, so not every near landmark has greater absolute motion than every distant one. The relative displacement establishes parallax in the guide. These values come from recorded camera matrices and quantized saved depth, not optical-flow feature tracking. [Depth](../exports/seed-3d-v001/guide/depth.png), [geometry measurements](../exports/seed-3d-v001/guide/geometry-review.json).
- **Guide defects:** newly exposed areas create gaps beside the person and a dark right border. The last raw validity mask has 9.82% unfilled pixels before the node's neighbour filling; this includes thin forward-splat gaps, not just a contiguous border. Frame zero has full coverage and matches the opening pixels exactly.
- **Repaint:** the sampled person remains a recognizable silhouette rather than the guide's broken silhouette. The central flame becomes a large orange/teal circular orb. A feature on the upper-left rim gradually becomes a planet; consecutive samples from 2.75–4.125 s show its development. The clouds/ground and rim also change. The result takes a different path from B's floating mask despite the same prompt and seed sequence: warped image inputs participate in the feedback trajectory.
- **Remaining limits:** the evolving orb becomes visually flat in some samples, and fine contours continue to change. The reused initial depth cannot represent newly created objects. Integer-pixel reprojection can suppress very small per-frame displacements. Do not attribute every apparent motion in the repaint to the camera or infer normal-speed smoothness from contact sheets alone.

Before increasing shot length, the next useful camera question is how to make parallax more legible while retaining this composition. A larger move would also stress exposed surfaces and stale depth more; it is a new experiment, not an established fix.

## Validation, timing and cleanup

The graph check verifies B's diffusion settings and model/conditioning remain unchanged and that a real depth input reaches the 3D sampler. Guide/repaint camera schedules match and begin at identity. Opening pixels and video dimensions/duration/counts were verified. [Validation](../exports/seed-3d-v001/validation.json).

Visually inspected: depth, full-size final guide and repaint, [guide overview](../exports/seed-3d-v001/reviews/v001/contact-sheet.jpg), [paired B/3D overview](../exports/seed-3d-v001/reviews/v002/contact-sheet.jpg), [first eight source-frame positions](../exports/seed-3d-v001/reviews/v003/contact-sheet.jpg), and [twelve consecutive planet-emergence positions](../exports/seed-3d-v001/reviews/v004/contact-sheet.jpg). Review sheets label decoded 24 FPS video frames; divide those indices by three for source-frame indices. Shared `video_review.py` produced all versioned reviews.

| Run | Queue/startup delay | Execution |
| --- | ---: | ---: |
| `20260907T183558357907Z-seed-3d-guide-48f` | 59.171 s | 28.686 s |
| `20260907T184350696640Z-seed-3d-repaint-48f` | 126.029 s | 174.410 s |

Both jobs completed on worker `rquge0ryf7r1be`, using the verified `f106834b7` image and installed nodes. The worker stopped after the 120-second idle window between preview and repaint, then restarted; the second delay is not warm inference time. A previously triggered GitHub build changed the endpoint's selected image to `9807c1924` while the old worker completed the repaint. No build was needed for this experiment's graphs, and no accepted job was duplicated. Preserve this distinction when diagnosing setup latency.

All **156 cloud objects / 97,841,851 bytes** were copied and verified against local files, including coverage/depth outputs. Endpoint min/max workers are zero; temporary storage was detached and deleted. Final worker/Pod/volume inventories and account state are verified in session cleanup. Observed account delta: $47.3139631299 → $47.1803930558, about **$0.1336**, with reported current spend rate zero. This is an account delta rather than an itemized invoice; delayed charges may settle later. Private receipts: `apps/deforum/work/seed-3d-session/`.

Runner: `seed_3d.py`, stages `check`, `guide`, `repaint` from `apps/deforum/` using `uv run --env-file .env --with pillow python projects/motion-guide-study/experiments/seed_3d.py STAGE`. Existing stages are immutable. Reconnect interrupted accepted jobs through the shared collector; do not resubmit uncertain jobs. Choose a new export version and a new temporary deployment for a fresh experiment, since this volume was deleted after verified collection.
