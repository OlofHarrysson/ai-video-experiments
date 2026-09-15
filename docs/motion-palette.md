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

## Choosing the next motion

1. Inspect the actual latest painting. Identify the focal form, available space, useful curves and crowded edges.
2. Choose one main movement for the next passage and one supporting deformation. Change the main family between passages: spiral push → lateral bank → pullback, for example.
3. Keep the image travelling while other movement speeds rise/fall. Overlap phrases or add cruise; avoid synchronized zeros at every scene boundary.
4. Preview the sheet without diffusion. Check net screen-space movement throughout the shot, direction reversals, edge exposure and scale accumulation. A nonzero numerical speed is not proof that the final film feels continuous.
5. Inspect generated paintings and dense interpolated frames around slowdowns. Repainting may resist the prescribed warp; RIFE may soften or redistribute its motion. Adapt the next passage to the artwork rather than forcing the original storyboard.

Work and delivery remain 24 fps. Recent faster editions present source time at 1.5×: motion and prompt events both arrive faster while all diffusion paintings are preserved. RIFE frames are presentation only. After the last painting, continue actual spatial warps instead of holding the final frame.

## This hour's trials

[Continuous motion](../apps/deforum/projects/modern-model-study/experiments/continuous-motion-hour/README.md) tests cruise plus plane turns, waves, shear and existing regional spirals. These are candidate recipes, not new global diffusion defaults. Olof requests continuous slow-to-fast movement, greater variety and fewer repetitive stops; artwork quality is already promising. Storage optimization is deferred until disk pressure returns.
