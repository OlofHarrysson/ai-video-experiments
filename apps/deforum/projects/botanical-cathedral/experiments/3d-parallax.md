# Intentional 3D camera

Status: hosted experiment complete; see [session results](serverless-results.md) for outputs, timing, visual limits and cleanup.

## Question

Can a short dolly/lateral move create correct differential parallax without unacceptable depth artifacts?

## Comparison

Keep the existing SDXL model and detail controls. Use a layered scene/reference, inspect Depth Anything V2 Small output, and preview the camera warp without diffusion first. Add an eight-frame redraw only after foreground/background motion is correct. Verify that depth is connected; mode `3d` by itself is insufficient.

The prepared graph uses the selected continuation anchor, Depth Anything V2 Small FP32, near/far 1/10, FOV 45°, bright depth near, and no depth inversion. A +0.02 scene-X translation per frame moves points right, equivalent to camera translation left; zoom and rotation are disabled to isolate parallax. The guide uses cumulative poses on the original image. The repainted feedback test reuses initial depth while the image evolves, so it tests a short local move only.

## Evidence to collect

Near landmarks move more than distant ones for a lateral move; dolly direction is correct; holes/border artifacts remain inspectable; the camera-only and repainted versions share the intended motion. Record depth direction/range, transform convention and static-depth limitation. Test refreshed depth as a separate future change.

## Cost boundary and result

Use short SDXL runs, record additional depth overhead, and compare against recurring baseline cost. Guide and repaint runs are preserved locally. Parallax is measured; edge artifacts and static-depth limitations remain. The endpoint is paused and storage deleted; see [results](serverless-results.md).
