# Spatial motion palette

Use this lookup when planning a scene or continuation. [Interactive sheet browser](../apps/deforum/motion_catalog.html) shows 22 direct effects without repainting; [the original preset research](research/bonsai-spatial-motion.md) provides historical context. These are image transforms, not a promise of a physical 3D camera.

Current recurrent implementation: [warps.py](../apps/deforum/src/deforum_lab/image/warps.py). Coordinates and distances use image-height units: at 1152×768 the viewport is x=0…1.5, y=0…1. Positive x/y move artwork right/down. Prompt descriptions still determine what the model paints into the moving composition.

| Intent | Renderer controls | When to use it | Watch for |
| --- | --- | --- | --- |
| Travel sideways or diagonally | `travel: [x,y]`, broad phrase | Follow a bridge, open space, distant light or horizon | Moving artwork left reads as the viewpoint travelling right |
| Keep drifting through a transition | `kind: cruise`, `velocity`, `roll_rate`, `log_zoom_rate` per source second | Carry movement across another effect's slowdown or reversal | Other transforms can cancel this; inspect net motion |
| Push into / pull away from a feature | `zoom` positive / negative, `center` | Enter a window or reveal a surrounding world | Negative zoom must stay above -1; prolonged push crowds objects |
| Roll the entire image | `turn`, large `radius` (e.g. 6) | Bank through an arch or tilt a horizon | Large radius is approximately global roll; cruise roll is exactly global |
| Form a local spiral | `turn`, smaller `radius`, chosen `center`, optionally `zoom` | Coil a ribbon, garden or cloud around a visible opening | Prolonged twisting can destroy a useful silhouette |
| Turn sideways / tilt backward | `kind: plane`, `tilt: [x_degrees,y_degrees]`, `distance` | Change relative size/speed of opposite sides, tip a flat composition | A projective flat sheet; no hidden object surfaces are revealed. Stay away from its projective horizon |
| Slide top and bottom differently | `kind: shear`, `amount`, `center_y` | Lean architecture or stretch a passage diagonally | Strong shear distorts proportions |
| Send a bend across the scene | `kind: wave`, `axis`, `amplitude`, `wavelength`, `cycles` | Flowing water, cloth, clouds or a less rigid transition | Short wavelengths visibly wobble straight architecture |

A standard phrase also needs `start` and `duration`. Its amount eases from zero to its final value; the resulting transform persists after the phrase finishes. A wave instead fades in/out during its interval. Cruise continues at its specified rates. Phrase order matters; all inverse transforms are applied in reverse order for correct image resampling.

The browser additionally shows local expansion/pinch, radial ripples and unfolding. Those have historical experimental implementations, but are **not all exposed by the shared recurrent renderer**. Do not silently map an unknown `kind` to an unrelated transform or claim every browser effect is already connected. A regional expansion is the same effect wherever its center is placed; it is not named after a sun, house or other background object.

## Families and reference recipes

The [Safety Marc comparison](research/bonsai-spatial-motion.md#current-palette-comparison--2026-09-15) separates four mechanisms. Deforum's menu labels alone do not make this distinction: all 95 saved presets select `3D`, including 45 with depth disabled.

| Family | What determines the movement | Current Krea loop |
| --- | --- | --- |
| Flat image transforms | Pan, zoom, roll, shear and local coordinate deformations | Available |
| Perspective on a flat sheet | Project a sheet tilted around its horizontal/vertical axes | Available through `plane`; different from depth parallax |
| Depth-based camera movement | Assign different distances to image regions, then move/project them; near and far regions can travel differently | Historical trials exist; deferred in the current recipe |
| Guide-derived deformation | Estimate motion between guide frames and apply it to the artwork | Historical Move-Warp trials exist; deferred in the current recipe |

Add **motion recipes** above those individual controls. These candidates adapt the reference's timing ideas; they are not exact preset reproductions or newly validated renderer options.

| Recipe to develop | Reference | How to construct a direct version | Status / omitted mechanism |
| --- | --- | --- | --- |
| Floating drift | `Move-Float-30s` | Phase-offset horizontal/vertical travel, slower rocking roll, gentle forward scale change. Keep travel active as roll reverses. | Existing controls can approximate it; a continuous periodic path is not yet a named renderer primitive. Original adds turbulent guide flow. |
| Travelling look-around | `Look-Around-30s`, `Classic-3D-Motion` | Continue sideways/upward travel while a slower plane tilt turns toward a focal region; counter-turn before the framing becomes too skewed. | Direct approximation possible now. Exact reference uses depth, and Look-Around also adds guide flow. This is not a target-locked 3D orbit. |
| Advancing spiral with a release | `Fly-Through-Spin-30s`, `Revolve-30s` | Combine travel, roll and a regional spiral; overlap a pullback before the subject fills the image. Carry lateral drift through the push/pull reversal. | Existing controls. The release is our adaptation for Olof's crowding/repetition feedback; the references additionally use depth and guide flow. |
| Uneven push–pull journey | `Classic-3D-Motion-2/3/4-30s`, `Move-Around-30s` | Vary translation, scale and rotation on different timescales, with a few broader accelerations. Avoid equal-duration repeated cycles and simultaneous full stops. | Existing phrases can approximate the choreography. Original narrow motion pulses may conflict with Olof's preference for fluent movement; exact schedules need validation and recalibration. |

Start with **floating drift** and **travelling look-around** as motion-only previews on one artwork, then repaint a selected route. Retain the accepted diffusion recipe. Add depth later when near/far separation is the artistic purpose, and guide flow when a particular guide's regional motion is wanted.

Reference presets mostly describe per-frame movement at 12 fps. Our renderer composes time-based mappings and uses image-height units, so their numeric amplitudes and frame numbers are not drop-in parameters. Convert timing to seconds, calibrate motion strength visually, and inspect the relative warp between consecutive times. The name `Dolly-Zoom-Out` is also insufficient evidence of a cinematic dolly zoom: its inspected preset disables depth and keeps field of view constant.

## Choosing the next motion

1. Inspect the actual latest painting. Identify the focal form, available space, useful curves and crowded edges.
2. Choose one main movement for the next passage and one supporting deformation. Change the main family between passages: spiral push → lateral bank → pullback, for example.
3. Keep the image travelling while other movement speeds rise/fall. Overlap phrases or add cruise; avoid synchronized zeros at every scene boundary.
4. Preview the sheet without diffusion. Check net screen-space movement throughout the shot, direction reversals, edge exposure and scale accumulation. A nonzero numerical speed is not proof that the final film feels continuous.
5. Inspect generated paintings and dense interpolated frames around slowdowns. Repainting may resist the prescribed warp; RIFE may soften or redistribute its motion. Adapt the next passage to the artwork rather than forcing the original storyboard.

Work and delivery remain 24 fps. Recent faster editions present source time at 1.5×: motion and prompt events both arrive faster while all diffusion paintings are preserved. RIFE frames are presentation only. After the last painting, continue actual spatial warps instead of holding the final frame.

## This hour's trials

[Continuous motion](../apps/deforum/projects/modern-model-study/experiments/continuous-motion-hour/README.md) tests cruise plus plane turns, waves, shear and existing regional spirals. These are candidate recipes, not new global diffusion defaults. Olof requests continuous slow-to-fast movement, greater variety and fewer repetitive stops; artwork quality is already promising. Storage optimization is deferred until disk pressure returns.
