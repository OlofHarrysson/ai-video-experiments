# Spatial motion palette

Use this lookup when planning a scene or continuation. [Interactive sheet browser](../apps/deforum/motion_catalog.html) shows 22 direct effects without repainting; [the original preset research](research/bonsai-spatial-motion.md) provides historical context. These are image transforms, not a promise of a physical 3D camera.

Current recurrent implementation: [warps.py](../apps/deforum/src/deforum_lab/image/warps.py). Coordinates and distances use image-height units: at 1152×768 the viewport is x=0…1.5, y=0…1. Positive x/y move artwork right/down. Prompt descriptions still determine what the model paints into the moving composition.

## Primitives and composed shots

Choose individual moves from the table below, then handcraft their timing and combination around the actual artwork. A pan left, a pan right, another pan left and another pan right are **four moves**, not one reusable primitive. Longer reference recipes are examples to take apart, not default choreography to repeat across scenes.

Each move has a direction, amount, interval, speed profile and, where applicable, center or region. A shot combines those moves for a visible purpose: bring an opening into the center, follow a curved track, pass through an arch, or pull back to reveal a changed environment. Separate moves can overlap; dividing them into primitives must not introduce a pause between each one.

| Intent | Renderer controls | When to use it | Watch for |
| --- | --- | --- | --- |
| Travel sideways or diagonally | `travel: [x,y]` | Follow a bridge, open space, distant light or horizon | Moving artwork left reads as the viewpoint travelling right |
| Keep drifting through a transition | `kind: cruise`, `velocity`, `roll_rate`, `log_zoom_rate` per source second | Carry movement across another effect's slowdown or reversal | Other transforms can cancel this; inspect net motion |
| Replace a future move while carrying its incoming speed | `kind: continuation`, endpoint pan/log-scale/roll, `velocity_start`, `velocity_end` | Branch from a painting and ease toward a new framing; release forward zoom into lateral drift | Cubic curve can overshoot; regional incoming motion only admits an approximate pan/zoom/roll fit |
| Push into / pull away from a feature | `zoom` positive / negative, `center` | Enter a window or reveal a surrounding world | Negative zoom must stay above -1; prolonged push crowds objects |
| Roll the entire image | `turn`, large `radius` (e.g. 6) | Bank through an arch or tilt a horizon | Large radius is approximately global roll; cruise roll is exactly global |
| Form a local spiral | `turn`, smaller `radius`, chosen `center`, optionally `zoom` | Coil a ribbon, garden or cloud around a visible opening | Prolonged twisting can destroy a useful silhouette |
| Turn sideways / tilt backward | `kind: plane`, `tilt: [x_degrees,y_degrees]`, `distance` | Change relative size/speed of opposite sides, tip a flat composition | A projective flat sheet; no hidden object surfaces are revealed. Stay away from its projective horizon |
| Slide top and bottom differently | `kind: shear`, `amount`, `center_y` | Lean architecture or stretch a passage diagonally | Strong shear distorts proportions |
| Send a bend across the scene | `kind: wave`, `axis`, `amplitude`, `wavelength`, `cycles` | Flowing water, cloth, clouds or a less rigid transition | Short wavelengths visibly wobble straight architecture |

A standard phrase also needs `start` and `duration`. Its amount eases from zero to its final value; the resulting transform persists after the phrase finishes. A wave instead fades in/out during its interval. Cruise continues at its specified rates. Phrase order matters; all inverse transforms are applied in reverse order for correct image resampling.

The assistant's [motion-preview CLI](../apps/deforum/MOTION_PREVIEW.md) exposes the continuation curve on a selected painting and includes the original lead-in. Its four curve components are image translation x/y, natural-log enlargement and roll in radians; velocities use source seconds. The plan adapter converts playback seconds and viewpoint directions. After its endpoint, the curve continues at its specified ending velocity. Check the complete path, not just its destination or velocity fit; RIFE and repainting can still affect the perceived join.

The renderer already supports these controls individually and in combination. Set unused standard controls explicitly to zero: `zoom` and `turn` have nonzero historical defaults. For example, a translation-only phrase needs `zoom: 0`, `turn: 0` and its chosen `travel`. Pure scaling needs `turn: 0`, and a twist without scaling needs `zoom: 0`. A waveform is a deformation field, not an instruction to alternate whole-shot pans.

The browser additionally shows local expansion/pinch, radial ripples and unfolding. Those have historical experimental implementations, but are **not all exposed by the shared recurrent renderer**. Do not silently map an unknown `kind` to an unrelated transform or claim every browser effect is already connected. A regional expansion is the same effect wherever its center is placed; it is not named after a sun, house or other background object.

## Families and reference recipes

The [Safety Marc comparison](research/bonsai-spatial-motion.md#current-palette-comparison--2026-09-15) separates four mechanisms. Deforum's menu labels alone do not make this distinction: all 95 saved presets select `3D`, including 45 with depth disabled.

| Family | What determines the movement | Current Krea loop |
| --- | --- | --- |
| Flat image transforms | Pan, zoom, roll, shear and local coordinate deformations | Available |
| Perspective on a flat sheet | Project a sheet tilted around its horizontal/vertical axes | Available through `plane`; different from depth parallax |
| Depth-based camera movement | Assign different distances to image regions, then move/project them; near and far regions can travel differently | Historical trials exist; deferred in the current recipe |
| Guide-derived deformation | Estimate motion between guide frames and apply it to the artwork | Historical Move-Warp trials exist; deferred in the current recipe |

The following **composed examples** adapt the reference's timing ideas. Borrow a component when it suits a painting; do not apply an entire sequence merely to add variety. These are not exact preset reproductions or newly validated renderer options.

| Recipe to develop | Reference | How to construct a direct version | Status / omitted mechanism |
| --- | --- | --- | --- |
| Floating drift | `Move-Float-30s` | Phase-offset horizontal/vertical travel, slower rocking roll, gentle forward scale change. Keep travel active as roll reverses. | Existing controls can approximate it; a continuous periodic path is not yet a named renderer primitive. Original adds turbulent guide flow. |
| Travelling look-around | `Look-Around-30s`, `Classic-3D-Motion` | Continue sideways/upward travel while a slower plane tilt turns toward a focal region; counter-turn before the framing becomes too skewed. | Direct approximation possible now. Exact reference uses depth, and Look-Around also adds guide flow. This is not a target-locked 3D orbit. |
| Advancing spiral with a release | `Fly-Through-Spin-30s`, `Revolve-30s` | Combine travel, roll and a regional spiral; overlap a pullback before the subject fills the image. Carry lateral drift through the push/pull reversal. | Existing controls. The release is our adaptation for Olof's crowding/repetition feedback; the references additionally use depth and guide flow. |
| Uneven push–pull journey | `Classic-3D-Motion-2/3/4-30s`, `Move-Around-30s` | Vary translation, scale and rotation on different timescales, with a few broader accelerations. Avoid equal-duration repeated cycles and simultaneous full stops. | Existing phrases can approximate the choreography. Original narrow motion pulses may conflict with Olof's preference for fluent movement; exact schedules need validation and recalibration. |

The first [two motion-only previews](../apps/deforum/projects/modern-model-study/experiments/motion-recipe-previews/README.md) demonstrate floating drift and travelling look-around with the current controls. Each lasts ten seconds at 24 fps on the same artwork; [compare them](http://localhost:3028/motion-recipes). They expose reflected borders and preserve the initial artwork. Olof accepted these previews, then requested more deliberate, artwork-specific choreography after the storytelling films. Retain the accepted diffusion recipe. Add depth later when near/far separation is the artistic purpose, and guide flow when a particular guide's regional motion is wanted.

Reference presets mostly describe per-frame movement at 12 fps. Our renderer composes time-based mappings and uses image-height units, so their numeric amplitudes and frame numbers are not drop-in parameters. Convert timing to seconds, calibrate motion strength visually, and inspect the relative warp between consecutive times. The name `Dolly-Zoom-Out` is also insufficient evidence of a cinematic dolly zoom: its inspected preset disables depth and keeps field of view constant.

## Choosing the next motion

1. Inspect the actual latest painting. Identify the focal form, available space, useful curves and crowded edges. Record the source frame and visible target position; measure an opening's size as well as its center when planning entry.
2. State the purpose and destination composition before choosing effects. Record a short move list: **target → primitive(s) → timing/overlap → intended framing → what must remain recognizable → reveal**. Choose variety because the artwork calls for it, rather than cycling through a list of effects.
3. Keep the image travelling while other movement speeds rise/fall. Overlap the short moves; inspect any cruise component for unwanted drift. Avoid synchronized zeros and automatic left/right repetitions. Start the next useful move before the previous one has completely stopped.
4. Preview the sheet without diffusion. Check the target's path and size throughout the shot, direction reversals, edge exposure and scale accumulation. Translate viewpoint language into image displacement: panning the view down moves the artwork up. A nonzero numerical speed or a correct endpoint is not proof of a well-framed, fluent path.
5. Generate a short passage and inspect its actual paintings before committing the next movement. Repainting can relocate or reinterpret the target; RIFE can soften or redistribute motion. Adjust the center/path, or branch before the unwanted change. Preserve the theme and important motifs while adapting the route.

## A doorway as a story beat

Olof's [storytelling feedback](../apps/deforum/projects/modern-model-study/experiments/storytelling-lab/README.md#human-feedback--2026-09-16) gives a concrete next application: center the railway doorway and begin approaching it earlier, keep it a doorway, then reveal a different world as we cross. The previous film repeats whales and tracks on the far side, weakening the payoff.

Plan this as overlapping individual moves: **reframe toward the opening → push into it → carry movement through the threshold → reveal the new surroundings**. Keep the doorway legible during approach; coordinate new-scene descriptions and change strength with the crossing instead of spending the approach transforming it into a clock. Framing and prompt timing must be inspected together, since spatial transforms alone cannot preserve doorway identity or invent its destination. A recurring color, shape or object may connect the worlds without repeating the entire previous scene. The [doorway revision](../apps/deforum/projects/modern-model-study/experiments/doorway-revision/README.md) now tests this approach. The doorway and different destination are readable, but the first crossing creates a near harp that blocks the route. A large lateral continuation fails; a rewind and push through the measured gap gives a clearer train/meadow ending. Plan the visible passage as well as the target point, and remeasure after repainting. These are findings from this scene, not a universal motion preset.

Work and delivery remain 24 fps. Recent faster editions present source time at 1.5×: motion and prompt events both arrive faster while all diffusion paintings are preserved. RIFE frames are presentation only. After the last painting, continue actual spatial warps instead of holding the final frame.

## Earlier continuous-motion trials

[Continuous motion](../apps/deforum/projects/modern-model-study/experiments/continuous-motion-hour/README.md) tests cruise plus plane turns, waves, shear and existing regional spirals. These are candidate recipes, not new global diffusion defaults. Olof requests continuous slow-to-fast movement, greater variety and fewer repetitive stops; artwork quality is already promising. Storage optimization is deferred until disk pressure returns.
