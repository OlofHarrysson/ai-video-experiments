# E06: approach with sparse repainting

Chosen after E03 shrank the foreground and E04 retained more detail than E02. The pinned [warp implementation](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/warp.py) transforms scene points: positive Z moves them away; negative Z approaches.

Use Z -.012 per frame, zero lateral translation/rotation, initial Depth Anything depth, and E04's cadence 3/.25 denoise/CFG 5/no noise or sharpening. 40 frames at 8 fps, 1280×720. Compare the foreground's expansion, exposed gaps and late-frame detail. This is an adaptive recipe combining direction, speed and cadence changes; it is not a one-variable comparison against E03.

Expected constraint: new geometry is still inferred from one initial depth image. Authorized session balance covers the render; preserve all source frames and versioned export.

## Completed result

Six overview frames show the approaching view changing foreground placement while retaining the distant dome and boardwalk. Compared with the earlier per-frame feedback pair, late frames retain more scene structure, but the nearby branches and lantern acquire broken contours and lose texture. The sparse-repaint recipe is useful for further tests, not a finished 3D shot. Depth remains tied to the first image.

[Video](../exports/e06-depth-approach-v001/preview.mp4) · [Frozen workflow](../runs/20260906T232405293622Z-e06-depth-approach-40f/workflow.api.json) · [Timed review](../exports/e06-review/v001/contact-sheet.jpg). Five seconds; 40 source frames repeated to 120 delivery frames. Sampled-frame review only.
