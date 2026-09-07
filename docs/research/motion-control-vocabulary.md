# From a motion request to a rendered image

Living vocabulary, started 2026-09-07. Pair each term with a motion-only preview and a repainted result. A familiar word is a starting hypothesis; use the preview to align on its visual meaning before making a longer clip.

## The pipeline we can inspect

**Description → motion recipe → displacement/projection → warped preceding artwork → diffusion repaint → next frame.**

There are two current ways to specify the motion recipe. Camera settings directly specify rotations and translations. Guide footage requires an additional estimation step: optical flow guesses which locations correspond between two guide frames. Black and white are visible features for that matching; they do not directly mean “move right” or “keep still.” These guides are not inpainting masks. Some other presets separately composite their guide into the artwork; the three studies here do not.

The preceding artwork is the content being moved. The guide is a source of motion. The model and prompt determine how the moved artwork is repainted. Keep those three roles distinct.

## A small working vocabulary

| Everyday request | Control and visual meaning | Boundary |
| --- | --- | --- |
| Slide the picture right | Give all locations the same positive horizontal displacement. | This is image translation; it is not evidence that a camera or object moved in 3D. |
| Top left, bottom right | Horizontal displacement changes with image height, with no required vertical displacement: shear. | Different from rigid rotation, which also changes vertical positions at the sides. |
| Roll or bank | Rotate the image around its center, or use camera Z rotation. | This tilts the composition; it does not reveal the side of an object. |
| Turn the view sideways | Camera yaw, with optional sideways translation. Depth changes the projection when translation is present. | Camera yaw is not the same as an object turning around its own center. An orbit also needs a target and a position path. |
| Move closer | Camera advance with depth, or a uniform image zoom. | A depth-based advance can change near/far scale differently; a uniform zoom cannot. |
| Expand around this point | Outward displacement relative to a chosen center, optionally localized to a band. | An expanding-ring guide produces an estimated field; it does not guarantee uniform radial movement everywhere. |
| Pinch, stretch or unfold regions | A spatially varying field, such as the preset's kaleidoscope-guide flow. | The field can distort recognizable objects and does not preserve rigid scene geometry. |
| Make it breathe | Vary expansion strength and direction over time. | This request still needs a center, region, amplitude and rhythm; it is not yet a tested named recipe here. |

The first session implementing this vocabulary is [three spatial effects](../../apps/deforum/projects/motion-guide-study/experiments/motion-effects.md). These terms describe controls, not an endorsement of every output or proof that Olof knows the terminology.

## Enough mathematics to make the controls concrete

Let `p = (x, y)` be an image location, and `u(p)` its desired displacement. In a forward description, `p_next = p + u(p)`.

- Translation: `u(p) = (a, b)` everywhere.
- Horizontal shear: `u_x = k(y − center_y)`, `u_y = 0`.
- Uniform expansion: `u(p) = a(p − center)`; positive `a` expands.
- In-plane rotation: `p_next = center + R(angle)(p − center)`.
- Local expansion: multiply the expansion field by a spatial weight `w(p)`. A soft band around a ring concentrates the motion there. This is an explicit mathematical construction, distinct from estimating optical flow from ring footage.

Our OpenCV feedback loop fills each output location by sampling `previous(p − u(p))`. This matches the inspected Deforum convention, but negating a spatially varying forward field is only an approximate inverse. Large deformations can produce resampling artifacts; repeated small steps can still stretch and soften details. Border reflection supplies texture at boundaries and is not a reconstruction of an unseen scene.

For depth-based motion, infer a relative distance `z` for each pixel, unproject it into 3D, apply `P_next = R P + T`, then project it back to the image. Difforum applies this transform to scene points. Its positive Z translation moves those points away; verbal camera direction must account for this sign convention. Its depth distances and translation scale in our study are relative units, not meters. Pure rotation about the viewing origin does not itself create depth-dependent translational parallax.

Schedules describe increments per generated frame, not final positions. Repeated steps accumulate. Changing generation FPS without adjusting increments changes speed. A cosine schedule can slow a turn, reverse it, and return it; a constant increment keeps moving in the same direction.

## Overall drift versus deformation

Any dense field can be written as its spatial average plus a remainder:

`u(p) = mean(u) + (u(p) − mean(u))`.

The first term is a uniform translation. The remainder has zero spatial mean, but can still contain rotation, expansion and local distortions. Subtracting the mean would remove average input displacement; it would not lock a particular subject in place or stop the model from changing composition. A future subject anchor would need its own explicit definition and validation.

The previous wave test measured rightward displacement at about 98% of pixel/frame locations. That describes the **estimated field actually applied**, not the creator's intention or uniquely correct correspondence. A [local diagnostic](../../apps/deforum/projects/motion-guide-study/exports/wave-diagnosis-v001/README.md) found fresh DIS still gives 96.7–98.0% rightward on six selected pairs, so warm-starting is not the main cause. Boundary ripple shapes travel right while tracked checker junctions remain in bounded regions. About 76% of the cropped image is away from edges, where matching is weakly constrained; those regions dominate the all-pixel percentage. The evidence supports following travelling wave shapes and extending their motion into flat regions, without establishing unique material motion. “Send a ripple right” and “slide the whole picture right” are distinct requests.

## How to direct the next short test

A useful request is: “Keep the center roughly still, bend the sides outward, then reverse halfway, with a gentle amount of repainting.” Translate it into an anchor, region, direction, amplitude and timing. If those are unclear, make a motion-only preview and discuss the visible result. Then repaint and compare against that preview. Avoid building a general natural-language motion engine until a few such recipes are reliable.

Source basis: Safety Marc's [Move-Around](https://github.com/S4f3tyMarc/Deforum-Studio-Presets/blob/bb8ce2fb0fd693319087460c8b21c13e19864be5/Deforum-Presets/Move-Around-30s.txt) and [Evolve-Zoom-Slow](https://github.com/S4f3tyMarc/Deforum-Studio-Presets/blob/bb8ce2fb0fd693319087460c8b21c13e19864be5/Deforum-Presets/Evolve-Zoom-Slow-30s.txt); local archived WebUI `hybrid_video.py` at `5d63a339dbec8d476657a1f672a4eeb6dc79ed37`; Difforum `core/camera.py`, `core/warp.py`, `nodes/warp_nodes.py` at `1d750efd3c1d1dda792b8ef6c14b06a14a69f879`. See the [source study](bonsai-spatial-motion.md) for the mechanism trace. The mappings above combine inspected implementation with mathematical explanation; proposed controls are marked as such.


## Missing coverage is not the same as dark artwork

The [camera-gap diagnosis and probes](../../apps/deforum/projects/motion-guide-study/experiments/motion-effects-2.md) verify a practical distinction. Difforum's warp output mask is **white for covered positions and black for holes**, despite an output name suggesting occlusion. A ComfyUI repair/noise mask uses white for the area to regenerate, so invert coverage before sampling. Preserve valid pixels with compositing before the global repaint. The subsequent unmasked repaint can still change everything.

A hole mask only describes this step. Once a black gap has been repainted into dark image content and carried forward, it can have valid coverage on later steps. Black ink, shadows, intentional backgrounds and inherited empty-looking borders cannot be separated by that mask alone. Fresh inferred depth may even treat a black band as nearby geometry.

In the matched probes, full-strength noise restricted to new holes barely improved the broad dark band. Removing exterior-black prompt clauses helped modestly; neither test solved it. Increasing denoise is therefore not a demonstrated general remedy. The saved evidence is a starting point for a future outpainting/background-continuation test with an explicit spatial target.

The [second effect round](../../apps/deforum/projects/motion-guide-study/experiments/motion-effects-2.md) also demonstrates two concrete knobs: multiply the same displacement field by four for a stronger effect, or compose an in-plane rotation with the preferred regional warp. Repainting may resist or reinterpret either operation; compare the motion-only preview with the final frames.
