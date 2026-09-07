# BonsAi motion: short baseline and 3D reveal

Date: 2026-09-07. Status: creative scope accepted; preparation, not rendered results. Preserve P3 + RIFE as the earlier creative baseline.

Olof accepted 8–10 seconds inspired by Evolve Zoom Slow, then a quick move into more interesting 3D transformations. He subsequently chose to continue with ComfyUI and defer A1111/Forge. The [motion-guide walkthrough](../../motion-guide-study/README.md) now demonstrates the isolated warp/repaint stages using two artworks; it does not complete the full animation. Keep the later video review to two distinct clips. The [channel research](../../../../../docs/research/bonsai-effect-workflow.md) contains settings, pinned sources and original guide assets.

## First: approach and morph

Target a readable central subject that evolves while the viewpoint approaches it. Start from the author's 12 FPS timeline, cadence 1, fixed seed with constant subseed blend, moderate repainting, fresh depth and circle-guide optical flow. Preserve the guide's timing rather than squeezing its full 30 seconds into eight seconds. The opening 8–10 seconds uses retention strength 0.42, corresponding to denoise 0.58 at the inspected WebUI adapter.

The circle is a separate motion reference. Its measured movement displaces the previous artwork before diffusion; guide pixels are not composited into the artwork. Forward depth-based camera movement is another part of this preset.

Before rendering, record the actual renderer, model and all deviations. Our current Difforum loop lacks an external-guide-flow input and an explicit noise-mixture input, and it reuses its starting depth. Copying settings into that loop is insufficient. Continue with a ComfyUI adaptation, with separately verified flow/noise integration and camera conventions. An isolated original-Deforum reference run is deferred.

Review subject readability, gradual transformation and detail through the approach. Inspect evenly spaced frames and an every-frame interval around any abrupt change. Preserve raw and interpolated versions.

## Second: pass a foreground object and turn

Use the same visual recipe for a short sideways camera move with a slight turn. Compose three depths: a close branch or carved arch edge, a subject beyond it, and a distant architectural background. Aim for the foreground to pass across the subject while revealing new space.

Preview camera/depth warping before repainting. Check movement direction, subject framing and exposed gaps. Prefer depth estimated from the current artwork over reusing stale starting depth. Disable ring-driven deformation here so the depth-camera contribution is legible.

Classic-3D-Motion is the next source reference for coordinated translation and rotation. Its full recipe also changes cadence, seed behavior and finishing, so a full-preset test is not a controlled camera-only comparison. Check camera units before transferring settings between renderers.

Review whether near and far elements move differently, whether the subject stays framed during the turn, and how newly exposed regions develop. Perfect rigid geometry is not the artistic target; a legible changing viewpoint matters.

## Human review

Show both videos directly in chat with one sentence explaining the change and one specific thing to watch in each. Screen the frames first. Move into the 3D test promptly; further zoom variations need a concrete question from a result.
