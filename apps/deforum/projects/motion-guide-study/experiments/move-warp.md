# Move-Warp guide in B's repaint loop

2026-09-07. Olof accepted a short Move-Warp-inspired experiment after studying Safety Marc's presets. He clarified that the opposed horizontal movement he saw lacked the complementary vertical movement expected from simple rotation; treat regional deformation as the hypothesis, without claiming the exact reference mechanism from appearance alone.

## Experiment

Use the actual archived `Wave-Warp-30s.mp4`, a bending checkerboard, to estimate a fresh spatial displacement between successive guide frames. Apply that field to the preceding artwork before every repaint. Start from B's exact opening and keep SDXL base + art LoRA 1.1, prompt, seeds 7301+frame, 18 steps, CFG 4.5, DPM++ 2M/Karras and denoise 0.58. No camera/depth warp, guide compositing, additional pixel noise, sharpening, color matching or final interpolation.

48 source frames at 8 FPS: six seconds. Use the guide's first 48 frames, originally 12 FPS, one guide step per artwork frame; this deliberately plays its movement at two-thirds of original speed while retaining B's generation cadence. Flow factor 0.55 is borrowed from the later portion of Move-Warp-30s. It is a constant here, not the full preset schedule. OpenCV DIS Medium, warm-started with the previous flow estimate after the first pair; remap uses grid minus scaled flow, bilinear sampling and reflection borders. These follow the reference mechanism with explicitly recorded implementation differences.

The Mac computes warps and orchestrates the loop; existing ComfyUI LoadImage → VAEEncode → KSampler → VAEDecode → SaveImage nodes perform each remote repaint. This avoids rebuilding the GPU image. Every output returns as an 8-bit PNG checkpoint, unlike B's mostly in-memory loop. It is a creative mechanism test, not an exact one-variable ablation or full preset reproduction. Transport overhead is separate from diffusion cost.

## Review and preservation

First inspect a warp-only video and displacement statistics. Then render a few feedback frames, inspect, and continue the same recorded sequence. Preserve every flow field, warped input, output frame, exact graph, seed and cloud receipt. A resumed stage collects accepted jobs rather than submitting duplicates. Inspect overview frames and short consecutive-frame windows. Show the finished repaint and warp-only preview in chat; Olof judges normal-speed quality.

Runner: `move_warp.py`, stages `prepare`, `render --until N`, `review`. Run from `apps/deforum/` with `uv run --env-file .env --with opencv-python-headless==4.12.0.88 --with pillow==12.1.0 python projects/motion-guide-study/experiments/move_warp.py STAGE`.

Outputs: `exports/move-warp-v001/`. Source settings and guide provenance: [spatial-control research](../../../../../docs/research/bonsai-spatial-motion.md). A generation completes only after local hash verification and owned cloud-resource cleanup.

## Completed result

- [Six-second repaint](../exports/move-warp-v001/repaint/preview-48f.mp4): 48 source frames, 144 delivered frames at 24 FPS using holds, no interpolation.
- [Warp-only comparison](../exports/move-warp-v001/warp-only/preview.mp4): identical opening and the same sequence of flow fields, applied recursively without repainting.
- [Matched overview](../exports/move-warp-v001/reviews/v001/contact-sheet.jpg), [consecutive source-frame positions at 3.5–4.875 seconds](../exports/move-warp-v001/reviews/v002/contact-sheet.jpg), and [validation](../exports/move-warp-v001/validation.json).

Assistant first-pass review: the pure warp clearly deforms different regions, but repeated resampling stretches the explorer into a smear and progressively compresses the scene. The repaint repeatedly restores recognizable forms while following a different visual trajectory: the explorer grows and shifts right, the portal opens into a landscape, and the flame becomes an orb and then a large floating mechanical head. The orange/teal illustration language remains recognizable. At 3.5–4.875 seconds, twelve consecutive generated-frame positions show the head forming over multiple steps, though proportions and details still change abruptly. This is selective frame evidence, not a normal-speed smoothness verdict; Olof subsequently said this looks much better and the movement is more interesting, while withholding judgment on whether this particular movement is right.

The test establishes actual guide-flow injection before every ComfyUI repaint. It does not establish exact object control or a full Move-Warp preset reproduction. Camera rotation and depth are disabled. The pure warp has no persistent 3D geometry, yet repainting produces a scene with strong depth cues. The visibly changed scale and composition should not be described as a calibrated camera move.

Applied flow's per-frame 95th-percentile magnitude is 14.47–14.94 pixels. This is displacement of the guide-derived field, not tracked object motion. Every flow array and warped PNG is preserved, making it possible to compare a future lower-strength pass without changing the art recipe.

## Execution, validation and cleanup

47 accepted jobs completed successfully on worker `j83s53vl6ukjhy`, using the previously verified `f106834b7` image. No model download/package change or container rebuild was introduced for this experiment. The first job waited **437.363 seconds** for capacity/startup. Worker inventory also showed two earlier workers throttled; only the final worker executed these jobs. Do not attribute that entire delay to model inference or infer billed time from queue delay.

Warm median job execution was **2.394 seconds**, with median queue delay **0.102 seconds**. Total reported execution across all 47 jobs was **120.920 seconds**. End-to-end warm frame delivery was roughly 7–8 seconds because each step includes transport, archive download and five-second collector polling. The local orchestration avoids a rebuild and preserves each step, at the cost of more round trips than one in-worker loop.

Verified identity warp, known translation direction, exact opening pixels, all 47 flow shapes, unchanged model/prompt/sampler settings and incrementing seeds. All 47 remote statuses are COMPLETED; each frame/input hash matches its receipt. Both full videos are 1024×576, six seconds, 144 delivery frames. First three feedback frames were inspected before continuing; every later frame continues from its immediately preceding saved PNG.

All **282 cloud objects / 84,619,437 bytes** were downloaded and verified against local files, including all inputs, graphs and diagnostics. Endpoint min/max workers are zero and idle timeout is five seconds; zero workers are confirmed. The owned temporary volume was detached, read back as detached, and deleted. Active deployment configuration was moved into private session receipts so the deleted volume cannot be reused accidentally.

Observed account balance: **$47.1704967225 → $47.0530544262**, a delta of about **$0.1174**, with reported spend rate zero. This is an account delta rather than an itemized final invoice; charges may settle later. Private receipts and full-copy verification: `apps/deforum/work/move-warp-session/`.

## Rightward drift diagnosis

Olof noticed the image shifting right. No separate camera pan, zoom or depth transform was used: the saved ComfyUI graph contains only model/text loading and img2img sampling around the locally warped input. Across all 47 saved flow fields after the 0.55 multiplier, mean horizontal displacement ranges from +6.71 to +7.81 pixels per source frame, averaging +7.35 pixels; 97.6% of pixel/frame positions point right. Mean vertical displacement is −1.20 pixels. See [global flow statistics](../exports/move-warp-v001/global-flow-statistics.json).

The applied field therefore combines a substantial uniform rightward component with local deformation. Repeated warping accumulates drift; these spatial means are not tracked object positions, and repainting also changes composition. This measures the estimated field we applied, not ground-truth motion of the repetitive guide pattern. A future controlled comparison could subtract each field's spatial mean vector before warping, separating overall translation from regional deformation; this has not been rendered and would not guarantee that diffusion preserves composition.

A subsequent [guide diagnosis](../exports/wave-diagnosis-v001/README.md) finds fresh DIS also strongly rightward. Travelling ripples along checker boundaries differ from the bounded motion of checker junctions; weakly constrained flat regions dominate the pixel percentage. Warm-starting contributes but does not explain the bias. This narrows the interpretation to estimated shape/phase motion, not uniform checkerboard translation.
