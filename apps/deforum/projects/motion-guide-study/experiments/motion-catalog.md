# Spatial effect selection

2026-09-08. First build a motion-only effect browser: one recognizable drawing, effect selector, play/pause/replay and time scrubbing. Frame zero is the original image. No diffusion, cloud compute or separate original-image panel. Olof chooses the movement before it becomes an artwork experiment.

The archived Safety Marc library contains 95 variants, including 77 with optical-flow motion and 50 with inferred depth. Many are combinations of camera schedules, guide motion, compositing and generation settings; they are not 95 independent transforms. Olof selected **direct effects now; original mechanisms later**. This browser therefore contains 22 direct examples, not reproductions of all 95 presets. Related-source links associate motion ideas; they do not claim equivalent schedules, strength, guide fields or output.

## Delivered browser

Canonical source: [motion_catalog.html](../../../motion_catalog.html). It is a self-contained inline visualization fragment; the host supplies theme/control styles. A frozen [local copy](../exports/spatial-effects-v002/spatial-effects.html) and [manifest](../exports/spatial-effects-v002/manifest.json) preserve this version. The browser is surfaced in chat with a single drawing, grouped selector, six-second playback and time scrubbing. Choosing an effect resets time to zero and pauses. Playback is manual and stops at the end; Replay starts again.

| Group | Selectable effects |
| --- | --- |
| Local reshaping | Expand region; Pinch region; Make a region breathe; Open the center sideways; Send a ripple outward |
| Move the whole sheet | Slide left; Slide right; Slide up; Slide down; Float around a loop |
| Scale and rotate | Zoom in; Zoom out; Zoom in, then back out; Rotate the whole sheet; Rock from side to side; Zoom and rotate together |
| Bend and twist | Top left, bottom right; Wave from top to bottom; Wave from left to right; Twist around the center |
| Perspective on a flat sheet | Turn the flat sheet sideways; Tilt the flat sheet backward |

Effects are independent of the drawing content. Center, radius, strength and timing describe where and how a transform acts; changing the center does not create a new effect. The current local expansion, pinch and breathing previews use normalized center (0.5, 0.5) and a falloff radius of 0.225 times image height. These values are code parameters; this browser does not yet expose position or radius controls.

Every effect defines a time-dependent coordinate mapping directly. The grid and drawing share that mapping; all effects have exactly the same geometry at frame zero. Local scaling uses a smooth spatial falloff. Waves use sinusoidal displacement, and perspective projects a rotated flat plane without estimating image depth. Timing is six seconds with smoothstep easing. These are absolute mappings of the original drawing over time; a future feedback renderer must derive the per-step transformation between successive states, rather than repeatedly applying the absolute transform and multiplying its strength accidentally.

This is a vector-geometry preview, not a raster quality test: it does not simulate accumulated resampling blur, border reconstruction, guide compositing, diffusion or object-aware deformation. Drawing content can move outside the fixed viewport. A local expansion can alter neighboring objects inside the falloff; it does not semantically isolate a selected object.

## Verification

In the preserved [v001 browser](../exports/spatial-effects-v001/spatial-effects.html), all 23 selections were exercised at frame zero and 1.5, 3, 4.5 and 6 seconds. Initial geometry matches across every effect, all geometry is finite, and each effect changes at a nonzero intermediate sample. All related-preset links resolve to files in the pinned local source archive. Screenshots of every effect were inspected; breathing/rocking were sampled at 1.5 seconds because their midpoint returns to the neutral pose. Browser checks cover play/pause/replay, backward scrubbing, switching effects during playback, the six-second stop, and manual-start behavior under reduced-motion preference. Light/dark at 736 and 360 pixels and the initial 320-pixel view have no observed horizontal overflow or clipped controls. Private QA receipts and screenshots are in `apps/deforum/work/motion-catalog/`. No cloud compute, diffusion, depth prediction or guide-flow estimation ran.

Version 002 merges the two expansion targets into one generic effect and centers expansion, pinch and breathing independently of the artwork. The updated selector has 22 entries with no object-specific names. These three changed transforms were checked at an intermediate time for finite geometry; the centered expansion was visually inspected. No browser errors were observed. Private receipts are in `apps/deforum/work/motion-catalog-v002/`.

## Following this selection

Olof requests cadence 3 and an interpolation comparison after selecting a motion. Cadence 3 should reduce the number of diffusion evaluations to roughly one per three animation frames, but setup, warping, transport and finishing still take time. Reduced repaint frequency may help or hurt continuity; it is a test, not an established stabilization method.

Keep classic Deforum's endpoint-based cadence distinct from the installed Difforum node's warp-only skipped frames. Before rendering, name which cadence is being tested and preserve the same shot duration and motion per second across the control and variant. Do not accidentally triple the motion rate or shorten the clip by changing only the diffusion count or export FPS.

Interpolation is a separate matched comparison on preserved frames (with versus without RIFE), at the same duration. Prior Brain Entity RIFE experiments already exist; the next comparison should apply it to the newly selected motion. These rendering tests are requested next, not executed during this browser-building task. Depth estimation and new optical-flow machinery are deferred unless Olof chooses to include them in the scope clarification.
