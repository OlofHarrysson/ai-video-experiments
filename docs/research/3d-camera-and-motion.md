# 3D camera, depth, and temporal motion

Researched 2026-09-06. Recommendation: first prove a small depth-based dolly and lateral move with the existing SDXL setup. Keep learned stabilization and interpolation as separate comparisons.

## What each component does

| Component | Role | What it cannot establish alone |
| --- | --- | --- |
| Camera transform | Specifies viewpoint movement. | Hidden surfaces or scene geometry. |
| Depth estimator | Estimates distance ordering from an image, or temporally consistent depth from video. | Complete geometry behind visible objects. |
| Depth reprojection | Moves visible points according to depth and camera; can create parallax. | Correct newly exposed surfaces. |
| Optical flow | Estimates pixel correspondence between observed frames; can support alignment/stabilization. | An intentional 3D camera path or a complete scene. |
| Frame interpolation | Generates intermediate frames between existing ones. | Repair of every semantic jump or recovery of lost detail. |
| Image/video model | Synthesizes or reinterprets appearance and missing content. | Guaranteed camera or object consistency without validation. |

RAFT and SEA-RAFT are learned optical-flow methods; modern ML and optical flow are not opposing categories. RIFE estimates intermediate motion for frame interpolation. An LLM could help author shot instructions, but it is not required to estimate pixel motion. [RAFT](https://github.com/princeton-vl/RAFT), [SEA-RAFT](https://github.com/princeton-vl/SEA-RAFT), [RIFE](https://github.com/hzwer/ECCV2022-RIFE)

## Current Difforum source audit

Inspected the same pinned commit used for our render: `1d750efd3c1d1dda792b8ef6c14b06a14a69f879`.

- `DifforumFeedbackSampler` calls `warp_3d` only when camera mode is `3d` **and** a depth image is supplied. Without depth it takes the 2D path.
- Depth is resized before the feedback loop and reused. It is not re-estimated from each generated frame or reprojected into a new depth map. This limits confidence in extended motion as image content and viewpoint change.
- `warp_3d` performs forward reprojection and returns a coverage mask. It fills small gaps locally; the feedback sampler discards the mask and redraws the full warped image. This is not a tested mask-directed disocclusion-inpainting pipeline.
- `DifforumFlowStabilize` uses OpenCV Farneback flow. It is an available inexpensive baseline, not RAFT or a learned video-consistency model.
- The upstream `difforum_parallax_fluid.json` combines depth, DMD2, camera keys, stabilization, cadence and RIFE. Treat it as a source of wiring examples: copying all of it would change too many variables for our next test. Its claim that this solves convergence is not evidence for our scene.

Sources: [feedback sampler](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py), [warp](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/warp.py), [flow](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/flow.py), [parallax workflow](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/examples/advanced/difforum_parallax_fluid.json).

## Depth choices

Start with Depth Anything V2 Small for a short monocular experiment. Small's weights are Apache 2.0; the larger variants use non-commercial licenses. The architecture predicts relative depth, so scale, near/far mapping and depth direction must be checked against a known foreground/background arrangement. Its official repository also provides metric-depth variants; relative depth must not be presented as measured meters. [Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2)

Video Depth Anything explicitly targets consistency across video frames. Its Small model is Apache 2.0; Base/Large are non-commercial. It is a useful later option for guide footage or a completed clip, but it does not automatically solve an online generative feedback loop whose future frames do not yet exist. [Video Depth Anything](https://github.com/DepthAnything/Video-Depth-Anything)

## First camera experiment

Use a scene with a nearby column or plant, a middle doorway, and a distant background. Inspect the depth map and make a short camera-only preview before spending on diffusion. Confirm that nearby landmarks travel farther than distant ones under lateral translation, verify the direction of a dolly, and inspect holes near occlusions. Keep movement small; single-view depth is closer to a 2.5D representation than a complete navigable world.

Then add the existing SDXL redraw for eight frames at a time. Hold model and detail controls constant. Do not label the test successful merely because the output moved: check differential parallax, reversed depth, border stretch, holes and scene drift. A 40-frame extension follows only after the short move is convincing.

For a future depth-update comparison, measure static depth against refreshed or transported depth, with explicit alignment and scale handling. This may require a different existing loop graph or a small custom component. No such architecture is implemented or approved by this research.

## Interpolation and stronger scene representations

Apply stabilization or RIFE to a preserved copy of a completed clip. Compare normal playback and occlusion frames; flow blending can introduce ghosting and smooth away wanted texture. Interpolation changes delivery motion but does not reduce already rendered compute. Lowering generated FPS later is a separate cost/quality experiment. [RIFE](https://github.com/hzwer/ECCV2022-RIFE)

SHARP reconstructs a 3D Gaussian representation from a single photograph for nearby-view rendering. It is a promising future camera experiment, not proof that arbitrary long travel or object editing will work. Its code and model have separate license files to review before adoption. Keep authored simple 3D scenes and reconstruction as distinct approaches. [Apple SHARP](https://github.com/apple/ml-sharp)
