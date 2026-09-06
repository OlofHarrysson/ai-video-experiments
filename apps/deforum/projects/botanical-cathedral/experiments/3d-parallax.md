# Intentional 3D camera

Status: proposed; not rendered. [Research and source audit](../../../../../docs/research/3d-camera-and-motion.md).

## Question

Can a short dolly/lateral move create correct differential parallax without unacceptable depth artifacts?

## Comparison

Keep the existing SDXL model and detail controls. Use a layered scene/reference, inspect Depth Anything V2 Small output, and preview the camera warp without diffusion first. Add an eight-frame redraw only after foreground/background motion is correct. Verify that depth is connected; mode `3d` by itself is insufficient.

## Evidence to collect

Near landmarks move more than distant ones for a lateral move; dolly direction is correct; holes/border artifacts remain inspectable; the camera-only and repainted versions share the intended motion. Record depth direction/range, transform convention and static-depth limitation. Test refreshed depth as a separate future change.

## Cost boundary and result

Use short SDXL runs, record additional depth overhead, and compare against recurring baseline cost. No allocation or paid resource is active. Result and run links: pending.
