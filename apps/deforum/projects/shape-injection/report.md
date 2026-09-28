# Blending authored shapes into Krea's feedback loop

2026-09-28. Diagnostic study requested by Olof: control image structure even where no identifiable object exists. Paste an animated shape into the current painting, then let diffusion interpret it. This is distinct from object tracking, regional text conditioning and sampler repaint masks.

## Mechanism and controls

The initialization is the previous generated painting with a transparent Remotion SVG alpha-composited over it. The global text describes the beach and, in semantic arms, a volleyball, sandstone ring or kite. There is no additional reference-image conditioning, ControlNet, depth map, object detector or sampler mask. Camera movement is zero in this diagnostic, so it cannot explain guide-following behavior. SVG alpha controls compositing only.

We use the existing Krea 2 Turbo FP8 model through the repository's native ComfyUI graph, at 1024 × 576. This deliberately holds the current creative model constant. The opening uses eight Euler/simple steps and seed 7281. Single-step probes use seed 7282, CFG 1, and three Euler intervals with manual sigmas `[0.6, 0.512844085693, 0.310901075602, 0]`; the higher-noise arm scales that schedule by 0.85/0.6. This `noise` value is the initial sigma, not a portable generic denoise percentage.

The 18 probes cross flat-circle opacity 0, 0.45 and 0.8 with initial sigma 0.6 and 0.85, both with a generic beach prompt and a volleyball prompt. Shaded sphere, ring and triangle add paired no-guide/0.8 controls at sigma 0.6. The sphere/no-guide control intentionally repeats the circle/no-guide graph and seed; it is not independent evidence. All other comparisons also remain a small diagnostic, not a model-wide reliability benchmark.

The animation uses 16 generated paintings at four paintings per second. Each output becomes the next initialization; seeds are 7300–7315. The authored guide travels from (280,205) to (740,205), rises 45 pixels midway, and has a nominal circle radius of 74 pixels. Triangle and ring rotate; the ring also changes projected height. No video model or frame interpolation hides the individual repaints in the diagnostic exports.

## Single-step observations

Assistant visual screening, not human taste judgments:

- **Flat circle → volleyball:** at sigma 0.6, both opacity 0.45 and 0.8 place a large cream ball near the supplied circle. Diffusion adds curved seams and shading. The matched no-guide prompt produces a much smaller ball elsewhere. The 0.45 example looks more fully interpreted; 0.8 retains more of the flat guide.
- **Triangle → kite:** the 0.8 triangle becomes fabric with folds, a frame and a string, close to the authored silhouette. This is the clearest still-image example of useful reinterpretation.
- **Shaded sphere:** becomes a textured round form, but does not clearly improve volleyball identity over the flat circle.
- **Ring:** gains irregular shading and some stone-like surface. It is less convincing than the kite, and retains a translucent, graphic quality.
- **Generic beach prompt:** the faint circle disappears; the strong one survives largely as a flat disc. These samples do not support an automatic assumption that a circle will become a scene-appropriate object without useful semantic direction.
- **Higher noise:** sigma 0.85 erases the tested circles and permits the prompted ball to appear elsewhere. More repainting did not improve spatial control here.

Full input/output pairs are in `exports/probe-sheet-1.jpg` through `probe-sheet-3.jpg`, with individual cases under `exports/probes/`.

## Reference identification

The closest saved reference is [The BonsAi Effect's motion-preset examples, Shapes-Circles-30s at 19:12](https://www.youtube.com/watch?v=vmKePs6iHs4&t=1152s). Five extracted frames show large rings becoming eyes and mechanical/animal structures. This is a plausible match to Olof's recollection, not confirmed identification of the exact spinning donut.

Both saved `Shapes-Circles` presets enable Normal hybrid compositing at alpha 0.8 and optical-flow hybrid motion at factor 0.8. The [pinned original implementation](https://github.com/deforum-art/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/hybrid_video.py#L87) blends guide appearance into the painting. The separate Evolve Zoom Slow expanding-ring preset disables compositing and uses guide flow; the mechanisms must not be conflated. This experiment isolates image blending and does not reproduce the entire SDXL preset.

## Authored local movement comparison

After blend-only sequences left the first ball behind, a second arm adds a broad, smooth translation field before blending. Its displacement comes from successive guide coordinates. Pixels within 125 pixels of the current guide center receive the full translation; a smoothstep falloff reaches zero at 245 pixels. Bicubic inverse remapping moves the painting, then the same 0.8 circle is composited and the same diffusion seeds/sigmas are used.

This is an authored deformation field, not estimated optical flow, semantic object tracking or an inpainting mask. It can move whatever visual structure occupies that area. It also moves nearby background pixels, so it cannot promise an unchanged scene outside an object's exact boundary. The first painting is shared in content with the blend-only comparison; subsequent paintings test the additive deformation.

## Recurrent results and recommendation

Seven four-second clips preserve all 16 generated paintings each. Assistant screening covered sequence contact sheets, with denser inspection of the recommended moving-ball result. These are raw four-paintings-per-second diagnostic exports, not finished films.

| Comparison | Observed behavior |
| --- | --- |
| Circle, 0.45 blend | The still-image success is not reliable across seeds: the ball initially appears elsewhere, and later injected circles/clouds add more forms. |
| Circle, 0.8 blend | Establishes a large ball, then leaves it behind while the new guide becomes a separate disc. |
| Triangle, 0.8 blend | Becomes a kite with folds, struts and strings. The moving guide grows an extra fabric section; it does not rigidly carry the original kite. |
| Ring, 0.8 blend | Develops into a textured floating rock arch after several paintings. Later strong stamping leaves repeated literal rings. Useful evidence of transformation, not a clean spinning-ring animation. |
| Circle + local translation, 0.8 throughout | Follows the authored path without the abandoned-ball failure, but repeated strong stamping flattens/erases panel detail in the second half. |
| **Circle + local translation, 0.8 first / 0.15 thereafter** | **Most useful movement result:** a single large ball follows the path while retaining curved seams. Surface details and the surrounding beach still evolve. |
| No guide, same ball prompt/seeds | A small blue/yellow ball stays near its self-selected location in the left half; it does not follow the authored path or take the guide's large size. |

Recommended review: `exports/sequences/circle-flow-gentle/comparison.mp4` shows the authored guide, blended initialization and diffusion output side by side. `exports/kite-before-after.jpg` is the clearest compact still reinterpretation. The remaining clips are under `exports/sequences/`, including all failures. The full result does not establish long-sequence robustness, exact geometry, rigid identity, physical interaction or fracture.

For Deforum, treat the guide as a way to introduce and reshape visual structure. Use strong injection briefly, then reduce it while authored local deformation transports the painting. Shape pixels alone are not a reliable motion controller. A global prompt helps resolve what the structure becomes; geometry supplies a spatial suggestion rather than a semantic guarantee.

Next hypotheses, not tested here: broad ribbons/bands to organize emerging terrain or architecture; outline guides to preserve more existing texture; and ring expansion/rotation fields synchronized with short blending pulses. These can act on image regions without first identifying an object. Their artistic value should be judged in a surreal scene after this basic mechanism test.

## Execution, cost and cleanup

One A100 SXM4 80 GB Pod at $1.59/hour ran from 19:48:28 to 20:13:07 UTC: approximately **$0.65 compute**, including setup, model downloads, inspection and network idle time. Storage adds a small amount; this is an elapsed-rate estimate, not a settled invoice. It is below the $3 working limit. The retained EU model volume could not be used because no suitable GPU was available there; an A40 allocation also failed without creating a Pod. The owned temporary US Pod downloaded the three pinned Krea weights and verified their SHA256 values.

The 130 warm repaints had median server execution time 3.683 seconds, equivalent to approximately **$0.0016 compute per painting** at this GPU rate. This excludes startup, HTTP transfer and inspection overhead. The whole session averaged approximately **$0.005 compute per generated painting** across 131 paintings; neither figure is a fixed API price or a claim about display-frame cost.

All 131 remote output PNGs match their downloaded originals by SHA256. All 14 video exports fully decode and contain exactly 16 frames over four seconds. The three strong-circle arms have identical decoded pixels at painting zero, before their movement/blending policies diverge. Scoped Ruff and whitespace checks pass; all Remotion guides were actually rendered and used.

The queue was empty before cleanup. Deleting owned Pod `9cs6dqzu67ml2g` returned HTTP 204; subsequent Pod listing returned zero Pods. The retained model volume was not modified. See [session receipt](session.json); detailed hashes, histories and runtime receipts remain in local ignored evidence storage.

## Reproduction and preservation

Render guides from `apps/remotion/projects/watermelon-guides/` with `node scripts/render-injection.mjs`. From `apps/deforum/`, use `uv run --locked python projects/shape-injection/run.py --help` for generation. `screen.py` makes contact sheets; `finish.py NAME` makes guide / blended initialization / diffusion comparisons.

Every submitted painting keeps its original and executed graph, uploaded initialization, global text, seed, parent hash, ComfyUI history, output hash and PNG in `runs/`. The model/runtime verification and remote-output preservation receipt are retained with the session evidence. Generated media is ignored by Git and preserved locally, without an external backup. The production Deforum recipe is unchanged by this isolated study.
