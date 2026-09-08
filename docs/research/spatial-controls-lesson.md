# Seeing spatial controls before diffusion

2026-09-08. Olof requests an educational pause: animated spatial deformation, how guide footage produces motion, alternative ways to author that motion, and a brief account of depth. These examples isolate deformation. They are not new generated art or reproductions of a complete Deforum preset.

## Two local interactive examples

Next step: the [spatial effects browser](../../apps/deforum/projects/motion-guide-study/experiments/motion-catalog.md) expands the drawing-based approach to 23 direct controls on one image, with frame zero serving as the original. Olof selected direct effects now and deferred original guide/depth mechanisms.

- [Stretchable sheet](../../apps/deforum/projects/motion-guide-study/exports/spatial-controls-lesson-v001/stretchable-sheet.html): six-second local expansion, translation, horizontal shear and local twist. Grid, drawing and two neighboring dots share the same coordinate mapping. Play/pause/replay, mode selection and time scrubbing. Motion starts only when requested and does not loop automatically.
- [Guide to motion](../../apps/deforum/projects/motion-guide-study/exports/spatial-controls-lesson-v001/guide-to-motion.html): an animated monochrome pattern, estimated next-step arrows and a different drawing carried by those movements. The arrows are displayed six times larger for visibility; applied displacement has factor one. The grid can be hidden. At the final frame there is no next frame, so no arrows are shown.

These are inline visualization fragments with theme utilities supplied by Codex; they are also surfaced directly in the conversation. Local browser QA wrappers and screenshots are in ignored `apps/deforum/work/spatial-controls-lesson/`. All lesson media is local; no cloud resources were provisioned.

## What the sheet explains

Movement and stretching are not separate pixel operations. When neighboring locations move by the same displacement, their spacing stays the same. When their movements differ, their spacing or relative orientation changes: expansion, compression, shear or twisting. A moving grid reveals those relationships more clearly than arrows alone. The two dots make one spacing relationship easy to follow.

The direct example expands around the sun with a smooth falloff. Nearby house geometry bends as well: this control selects a spatial region, not the semantic object “sun.” It does not demonstrate independent object editing. A real raster implementation resamples colors between pixels; enlarged detail is interpolated until a later generative step adds or changes it. The vector drawing deliberately avoids blur and diffusion so the geometry stays legible.

## What the guide explains

A guide is an ordinary sequence of images. Optical flow compares adjacent frames and estimates image-location displacements. Those displacements can then move unrelated artwork at corresponding locations. The guide's colors do not directly encode movement directions or denoise strength. White is not inherently “grow,” and black is not inherently “stay still.” A single white circle has no unique implied motion; its change over time is what gets analyzed.

Black, gray and white can indeed be represented numerically as brightness near 0, 0.5 and 1. Subtracting those values at the same coordinates tells us how brightness changed there, not where a feature moved. To estimate motion, compare a small neighborhood with nearby neighborhoods in the next image and find the displacement that best aligns their patterns. Brightness differences can score candidate alignments; the chosen horizontal and vertical offsets become the arrow. This is a high-level account of correspondence, not a claim that every estimator exhaustively searches patches. In this lesson, gray dots add matching detail rather than encoding half-strength motion. Uniform areas lack distinctive matches; repeated checker patterns also create ambiguity.

The lesson uses a procedural travelling horizontal deformation of a checker pattern with gray dots. DIS Medium actually estimates motion from 73 rasterized frames at 12 FPS; this is not a hand-authored field labeled as a measured one. The known construction lets us check the estimator: median per-frame interior median endpoint error is about 0.048 pixels. This easy synthetic result does not establish accuracy on arbitrary footage or Safety Marc's guides.

[Generator](../../apps/deforum/projects/motion-guide-study/experiments/guide_lesson.py) and [manifest](../../apps/deforum/projects/motion-guide-study/exports/spatial-controls-lesson-v001/manifest.json) preserve method and hashes. For the small interactive payload, measured flow is sampled on a 17×11 lattice and used to advect vector vertices. The visible guide is an SVG reconstruction of the same pattern/deformation; its side margins exclude the raster border-fill region. This is an educational visualization of the mechanism, not a bit-for-bit playback of our backward-remapped PNG feedback loop. No guide pixels are composited into the drawing, and no diffusion is run.

## Ways to author movement

1. **Specify a transformation directly.** Choose center, affected radius, direction, strength and timing. Equations produce the field without an estimation step. This suits requests such as “expand this area gradually” or “top left, bottom right.” The first visualization demonstrates this route.
2. **Manipulate a mesh or draw motion strokes.** An authoring tool can turn moved handles or strokes into a smoothly varying deformation. A soft mask can control where the effect fades out. Such a mask is a spatial weight, not guide footage; this authoring interface is a possible next tool, not one already implemented here.
3. **Animate or supply a guide video.** Create patterns in an animation editor, generate them procedurally, render a simple 3D scene, or use existing footage. Estimate its motion and transfer the field. It need not be monochrome. High-contrast patterns provide visible matching features, but flat regions, repeated patterns and occlusion still create ambiguity. Existing artist guides are useful because they preserve motion designs we can study; recreating a guide from equations and then re-estimating its known movement is optional.
4. **Use depth and a camera transform.** Estimate relative distances in the artwork, place image samples in approximate 3D, move the viewpoint and project back. This can create near/far parallax and expose missing content. It is another route to moving image locations; it is not required by the purely two-dimensional guide method.

Depth cannot reveal the real hidden side of a depicted object. Gap filling or generative repainting has to supply newly exposed content. Color/detail adjustments can be added around the feedback loop; frame interpolation is a separate finishing step that adds intermediate frames. None of those steps is needed to understand where the guide-driven deformation comes from.

Recommended next learning interaction: compare slide and grow, watch dot spacing, then scrub the guide example and relate the changing arrows to bending in the drawing. Ask Olof what remains unclear; showing these materials does not establish understanding. See [motion vocabulary and pinned implementation sources](motion-control-vocabulary.md).

## Verification

Checked all four modes, start/middle/end scrubbing, play/pause/replay, mode changes during playback, the guide grid toggle and both six-second endpoints. Light/dark layouts at 736 and 360 pixels, plus the guide at 1024, have no observed horizontal overflow or clipped controls. Sampled screenshots confirm that the grid and artwork deform together and that the guide appearance remains separate. A first-frame animation-timestamp edge case was fixed and playback rechecked. These checks establish interactive behavior and geometry presentation, not a subjective video-quality judgment.

## Where the other Deforum processes fit

The backbone is **previous artwork → spatial deformation → image preparation → diffusion repaint → saved next artwork**. Repeat from the new artwork. A first image is generated or supplied before this loop. Optional features branch into this sequence; classic Deforum is not a requirement to run every available algorithm on every frame.

| Stage | Purpose and optional components |
| --- | --- |
| Read this frame's controls | Evaluate camera/motion, prompt, seed, denoise and other schedules. Scheduling changes controls over movie time; it is not another image model. |
| Obtain motion information | Direct transforms can supply coordinates immediately. Optional depth estimation supplies relative near/far distances for 3D reprojection. Optional optical flow estimates 2D movement from guide-frame pairs. Camera and guide motion can be combined. |
| Deform the previous artwork | Move/resample its image content with the chosen transforms. Handle borders or uncovered regions according to the warp implementation. This does not recover unseen scene detail. |
| Prepare the image | Optional color matching, contrast, sharpening and extra image-space noise. Separate image noise from the latent noise inside diffusion. Optional hybrid compositing blends actual guide pixels and is distinct from transferring guide motion. |
| Repaint with diffusion | Encode the prepared image, sample using prompt/seed/denoise settings, then decode. Optional masks or ControlNet can constrain where or how generation changes the image; ControlNet guides sampling rather than moving pixels directly. |
| Save and feed back | Preserve the result and use it as the next input. Depending on settings/implementation, color matching or guide compositing can also occur after generation. |

Two timing mechanisms sit alongside this simplified loop. **Classic cadence** spaces out diffusion-generated endpoints and constructs intervening frames using warps/blending, optionally optical flow. This is not identical to our Difforum sampler's warp-only skipped frames. **Final frame interpolation**, such as RIFE/FILM, runs on generated images to add intermediate frames before export. It is separate from cadence and from guide motion.

Optical flow is a reusable motion-estimation operation, not one fixed stage: classic code uses it for hybrid guide motion, optional cadence, and an optional extra-generation/warp redo. A separate flow-based stabilizer in the rewrite aligns and blends history to reduce changes; it should not be attributed to the classic guide path. These optional details can be taught individually after the basic map is clear.

Source: locally rechecked classic WebUI [renderer](https://github.com/deforum/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/render.py), especially lines 295–399 (cadence), 415–468 (warp, hybrid motion/compositing, color, contrast/sharpening/noise), 542–593 (optional redo, generation and post-generation processing). See [architecture comparison](deforum-architecture-comparison.md) for depth and interpolation sources and the differences from our executed ComfyUI graphs. The table is an educational grouping, not a literal universal execution order.
