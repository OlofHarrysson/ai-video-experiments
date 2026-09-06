# E03: depth pullback

Question: does depth translation along Z give useful movement with less lateral disocclusion than the previous strong sideways move?

Same anchor and rendering settings as E02. Depth Anything V2 small FP32 estimates initial depth; Difforum 3D camera, Z .02 per step, X/Y zero, FOV 45, near 1/far 10, translation scale 1. Initial depth is reused. This is a single-image depth warp and repaint experiment, not a reconstructed 3D scene.

Apparent travel is not matched to E02. Preserve all frames and timed reviews; inspect foreground deformation, composition and texture drift. Covered by the authorized learning balance.

Observed direction: positive Z transforms scene points away from the camera, giving a pullback. The frozen run ID retains its original `depth-push` name; it does not describe the observed direction. Six timestamped samples from 0 to 4.958 seconds show a shrinking lantern, increasingly jagged foreground branches and strong late smoothing. E06 tests negative Z instead. Source: pinned [warp.py](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/warp.py).

## Completed result

The six sampled frames show a pullback: the nearby lantern shrinks more visibly than the distant dome. Foreground branches develop jagged contours, and late frames lose detail. Positive Z transforms scene points away; the run ID was frozen before this direction was visually verified.

[Video](../exports/e03-depth-push-v001/preview.mp4) · [Frozen run](../runs/20260906T231721485708Z-e03-depth-push-40f/workflow.api.json) · [Timestamped review](../exports/e03-review/v001/contact-sheet.jpg). 40 source frames / five seconds / 24 FPS delivery repeats the 8 FPS source. Review evidence is sampled decoded frames, not a full-playback quality judgment.
