# Spatial image control: learning from Safety Marc's presets

Execution update: the accepted [Move-Warp-inspired experiment](../../apps/deforum/projects/motion-guide-study/experiments/move-warp.md) now completes guide-flow feedback through Mac warping and existing ComfyUI img2img nodes. Six-second repaint and warp-only videos are preserved; no full preset reproduction or in-worker guide-flow node is claimed. The gap analysis below records the state that motivated the experiment.

2026-09-07. Olof wants the expressive movement in The BonsAi Effect's references. He found our latest 3D repaint nearly motionless and the guide too restrained. Literal camera realism is one possible technique; the current creative question is how to direct different regions of an evolving image.

## What the repository tells us

The [Deforum Studio Presets repository](https://github.com/S4f3tyMarc/Deforum-Studio-Presets) is a library of **settings**, with a separately linked archive of animated guide videos. The image-transform algorithms live in WebUI Deforum. Understanding an effect requires the preset, its guide, and the implementation that interprets it. These presets are not importable ComfyUI graphs.

We inventoried all **95 preset files** at commit `bb8ce2fb0fd693319087460c8b21c13e19864be5`: 77 enable optical-flow hybrid motion, 18 disable hybrid motion; 20 enable guide compositing (17 Normal, 3 Before Motion); 50 enable depth warping and 45 disable it. These are overlapping switches and include short/30-second variants, not 95 independent algorithms. The machine-readable inventory is preserved beside the archived presets as `preset-motion-inventory.json`.

The same `animation_mode: 3D` label appears in files with depth disabled. In the inspected WebUI implementation, disabling depth substitutes a constant-depth plane; it does not disable all perspective/camera transforms. A menu label is therefore insufficient to identify a depth-aware effect.

## Representative effects and their actual ingredients

Values below are the original settings, not directly transferable camera units for Difforum. Effect descriptions are source interpretations unless a reviewed output is identified.

| Preset | Spatial ingredients | Guide painted into image? | What we learn |
| --- | --- | --- | --- |
| [Classic-3D-Motion-30s](https://github.com/S4f3tyMarc/Deforum-Studio-Presets/blob/bb8ce2fb0fd693319087460c8b21c13e19864be5/Deforum-Presets/Classic-3D-Motion-30s.txt) | Depth plus time-varying translation and rotation on multiple axes; no hybrid motion; cadence 2. | No | Rich motion can come from a designed camera schedule, without an external flow guide. This differs substantially from our constant tiny lateral step. |
| [Evolve-Zoom-Slow-30s](https://github.com/S4f3tyMarc/Deforum-Studio-Presets/blob/bb8ce2fb0fd693319087460c8b21c13e19864be5/Deforum-Presets/Evolve-Zoom-Slow-30s.txt) | Depth/camera advance plus DIS Medium flow from `Circle-Zoom-30s.mp4`, factor 0.8. | No | Combines camera movement and expansion guided by a white ring. The ring itself is not an inpainting mask. |
| [Evolve-Slow-30s](https://github.com/S4f3tyMarc/Deforum-Studio-Presets/blob/bb8ce2fb0fd693319087460c8b21c13e19864be5/Deforum-Presets/Evolve-Slow-30s.txt) | Depth disabled; small oscillating Z; turbulent-noise guide, flow factor 2. | No | Spatially varying flow can drive the image without inferred scene depth. Seed-mixture scheduling also changes repainting. |
| [Move-Warp-30s](https://github.com/S4f3tyMarc/Deforum-Studio-Presets/blob/bb8ce2fb0fd693319087460c8b21c13e19864be5/Deforum-Presets/Move-Warp-30s.txt) | Depth enabled; scheduled Y rotation; `Wave-Warp-30s.mp4`; DIS Medium flow factor 0.35, changing to 0.55 at frame 181. | No | The guide is a bending black/white checker pattern. It supplies regional deformation alongside a turn. This is the most direct next study for Olof's current question. |
| [Move-Warp-2-30s](https://github.com/S4f3tyMarc/Deforum-Studio-Presets/blob/bb8ce2fb0fd693319087460c8b21c13e19864be5/Deforum-Presets/Move-Warp-2-30s.txt) | Same wave guide, depth disabled, scheduled Y rotation and Z translation, changing flow factor 0.2–1.2 at listed control points. | No | Even the closely named variant changes several mechanisms; it is not a simple strength toggle. |
| [Move-Around-30s](https://github.com/S4f3tyMarc/Deforum-Studio-Presets/blob/bb8ce2fb0fd693319087460c8b21c13e19864be5/Deforum-Presets/Move-Around-30s.txt) | Depth, oscillating translation/rotation and kaleidoscope-guide flow at 0.8. | No | Combines a time-varying viewpoint with nonuniform guide motion. |
| [Grids-30s](https://github.com/S4f3tyMarc/Deforum-Studio-Presets/blob/bb8ce2fb0fd693319087460c8b21c13e19864be5/Deforum-Presets/Grids-30s.txt) | All six camera schedules zero; block-guide DIS Fine flow at 1.2. | **Yes**, alpha 0.95, no composite mask | An effect can be driven by guide motion and guide appearance even with no camera travel. |
| [Shapes-Stars](https://github.com/S4f3tyMarc/Deforum-Studio-Presets/blob/bb8ce2fb0fd693319087460c8b21c13e19864be5/Deforum-Presets/Shapes-Stars.txt) | Depth disabled, Z 0.6; star-guide DIS Medium flow at 0.8. | **Yes**, alpha 0.75, no composite mask | Shape influence and motion influence are different controls. This row refers to the unsuffixed variant. |

Also inspected: Fly-Through-30s (strong Z advance, oscillating roll, kaleidoscope flow), Move-Float-30s (oscillating X/Y, roll, turbulent flow, depth off) and Revolve-30s (X travel, roll, grain-guide flow). These are combinations of shared mechanisms rather than entirely separate rendering engines.

## The actual feedback operation

Source trace: WebUI Deforum commit `5d63a339dbec8d476657a1f672a4eeb6dc79ed37`, [render.py](https://github.com/deforum-art/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/render.py), [hybrid_video.py](https://github.com/deforum-art/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/hybrid_video.py), and [animation.py](https://github.com/deforum-art/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/animation.py). This is inspected source, not proof of the exact artist runtime.

1. Transform the preceding artwork with the scheduled camera; infer depth from that image when enabled and no depth is supplied.
2. Read two successive guide frames, resize them to the artwork dimensions, and estimate their motion. The selected presets use DIS optical flow, not an LLM. The implementation can carry the preceding flow estimate forward.
3. Multiply the displacement field by the scheduled flow factor and resample the artwork using those offsets.
4. If enabled, composite the guide's actual appearance. `Normal` runs after hybrid motion; `Before Motion` runs before hybrid motion but after the camera warp in this source. Without a mask, the blend is directly between the current artwork and guide at the scheduled alpha.
5. Apply the remaining conditioning/image processing and diffusion repaint; carry the result into the next iteration. Cadence and final interpolation are separate operations.

Consequently, our earlier “the black and white pixels do not enter the artwork” explanation is correct for the circle walkthrough and Move-Warp, where compositing is None. It must not be generalized to all presets: Grids and Shapes deliberately blend guide content before repainting.

## Moving versus stretching

A vector field is a displacement instruction at each image location. Give every point in a region the same leftward displacement and it translates. Give adjacent points increasingly different displacements and the region stretches, compresses or bends. Opposing horizontal movement at the top and bottom can be shear; a simple rotation can also send the top and bottom in opposite directions. Appearance alone does not identify the source algorithm.

Image warping resamples pixel values onto a new grid; it does not physically enlarge individual pixels. Content can leave the frame, and newly exposed regions have no observed texture. Border filling and repainting supply those missing values rather than recover a hidden original scene. See [OpenCV geometric transforms](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html).

Depth plus camera projection is another way to calculate a 2D displacement map. A freeform wave or swirl need not correspond to a single camera moving through a rigid scene. Our current diffusion loop receives a 2D warped image, while depth is used externally; that does not imply the model has no learned spatial knowledge or that explicit depth conditioning is impossible.

## Visual evidence and new references

- The preset compilation's Evolve Zoom Slow was re-sampled at 565, 566, 568, 570, 572 and 574 seconds. The centered cybernetic face remains readable while its circuits and surrounding radial forms evolve. This alone cannot separate the ring and depth contributions.
- Move-Warp was sampled at original times **975, 977, 979, 981, 983 and 985 seconds**, using a preserved 974–986-second excerpt. The face changes position and orientation, background monitors change arrangement, and the composition bends/evolves. The visible result is consistent with combined mechanisms; it is not a flow-only ablation. [Watch chapter](https://www.youtube.com/watch?v=vmKePs6iHs4&t=974s).
- The actual Wave-Warp guide was inspected at 2–7 seconds: its checker cells bend and shift over time. It provides concrete moving structure for estimating local flow, not a semantic object layout. Circle and turbulent guides were inspected in the earlier study. Kaleidoscope, block and star guide files were additionally extracted and preserved; their appearances have not yet been reviewed here.
- [Child of the Moon](../../apps/deforum/projects/reference-studies/references/bonsai-child-of-the-moon.md): 12 overview samples and eight one-second samples of the winding-road sequence. Highly saturated graphic color, readable paths and changing curvature/composition. Creator confirms Cheyenne; description names SDXL/Forge, Filmora and Topaz. Exact motion recipe is undisclosed.
- [Echoes of a Thousand Years](../../apps/deforum/projects/reference-studies/references/bonsai-echoes.md): a softer blue/cream surreal visual language, with faces containing landscapes, stairs, clocks and floating architecture. See its review for sampling scope. The retrieved comments do not establish a motion preset or checkpoint.

These are selective frame reviews, not complete normal-speed audiovisual viewing. Both new 720p video-only study copies and all available comment replies are local. No paid generation or transcription was used.

## What is missing in our ComfyUI path

Our installed Difforum feedback node supplies 2D/camera-depth warping, repainting and seed schedules. The selected B recipe changes seeds reproducibly. The last 3D test used static opening depth and tiny camera deltas; it does not test Safety Marc's guide deformation.

The earlier local walkthrough estimates actual ring flow and warps an artwork, but applies only isolated still repaints. **External guide flow is not yet injected into each step of our running ComfyUI video loop.** The inspected node interface also does not reproduce guide compositing or the preset's scheduled seed mixtures. A node carrying the Deforum name is not evidence of feature equivalence.

**Recommendation:** study/adapt Move-Warp's actual wave guide next, using B's accepted same-model/changing-seed repaint recipe as the art control. First verify the field and a plainly visible warp-only preview, then a short guide-flow feedback clip, then add the preset's scheduled turn if needed. This would isolate an authentic reference mechanism while acknowledging that B's seed/conditioning recipe differs from the complete preset. Do not call it an exact preset reproduction.

Implementation remains a proposal pending alignment. Prefer an existing compatible warp node; if the current monolithic feedback sampler prevents inserting guide flow, scope one small explicit integration rather than a broad platform migration. Keep ComfyUI as requested. The next pass should resolve this concrete missing mechanism before another generic camera-strength sweep.
