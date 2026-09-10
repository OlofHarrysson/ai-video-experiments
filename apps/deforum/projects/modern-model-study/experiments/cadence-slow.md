# Slower repaint cadence: 3, 7, 10 and 15

## Plan recorded before rendering

Olof still finds the artwork changing too frequently and requests cadence 3 as the baseline plus 7, 10 and 15. Defer interpolation until after this comparison. Keep the accepted three native Turbo sampling intervals, same opening, prompt, motion and per-repaint seed progression. Reuse the preserved cadence-3 raw clip. RIFE remains the preferred finishing option, but these deliveries intentionally expose the underlying generation and warp timing.

Use the same three-second continuation, source clock 12 fps, delivered at 24 fps by duplication. Cadence 7 repaints every 0.583 seconds (five new repaints), cadence 10 every 0.833 seconds (three), and cadence 15 every 1.25 seconds (two). Cadence 3 repaints every 0.25 seconds (eleven). The cadence-15 clip is a short diagnostic with only two repaint events; it does not establish long-duration behavior.

Each branch starts from the same preserved global frame 36. Warp the previous generated image to each scheduled repaint, sample it with the unchanged model recipe and an incrementing seed, then feed that result into the next iteration. Intermediate frames warp the preceding generated anchor. No RIFE, image crossfade, pixel protection, additional noise or independent redraw. Fewer repaints alter cumulative diffusion updates and seed assignment over time.

Deliver one synchronized four-panel comparison and preserve individual raw clips, all anchors and provenance for later interpolation. Inspect overview frames and the intervals surrounding repaint events. Higher cadence should reduce event frequency; it does not necessarily reduce the size of a single redraw.

## Results

All three branches are complete. **Cadence 10 is the assistant's tentative next interpolation candidate:** it gives each painting about 0.83 seconds while retaining more opportunities for structural evolution than cadence 15. This is a pacing hypothesis for human playback, not a proven smoothness ranking. Cadence 7 is the less extreme alternative; cadence 15 makes the long hold followed by a redraw especially clear.

The main finding is that longer cadence reduces the number of redraws, but the remaining redraws can still change a lot of structure. At 2.50 seconds, cadence 10 and 15 both repaint: arches, small windows and the central flame change noticeably at once. Cadence 15 also has a visible rebuilding event at 1.25 seconds. Motion continues between those moments; the image is not a held still. Larger cadence also means more spatial deformation has accumulated before each repaint. It is not equivalent to slowing playback of the cadence-3 result.

All clips preserve the warm cream, teal and orange palette, the central flame-like form and the architectural spiral. Cadence 3 accumulates more intricate structural revisions by the end. The larger-cadence branches remain closer to the opening over much of the shot. None of these observations establishes that less frequent repainting alone solves smooth morphing.

![Cadence 3, 7, 10 and 15 without interpolation](../exports/cadence-slow-v001/comparison/preview.mp4)

| Panel | Cadence | Time between repaints | New repaints in three seconds |
| --- | ---: | ---: | ---: |
| Top left | 3, reused baseline | 0.25 s | 11 |
| Top right | 7 | 0.58 s | 5 |
| Bottom left | 10 | 0.83 s | 3 |
| Bottom right | 15 | 1.25 s | 2 |

Individual raw clips: [3](../exports/turbo-transitions-v001/tail-3/preview.mp4), [7](../exports/cadence-slow-v001/cadence-7/preview.mp4), [10](../exports/cadence-slow-v001/cadence-10/preview.mp4), [15](../exports/cadence-slow-v001/cadence-15/preview.mp4). There is **no RIFE or crossfade** in this comparison, including the reused baseline. This differs from the previously accepted cadence-3-plus-RIFE delivery. All original anchors and timing remain preserved for the later interpolation experiment. Cadence 15's source anchor rate is 0.8 fps; the follow-up below extends and verifies the interpolation runner for this rate.

## Verification and execution

- All ten requests succeeded. Checked every requested/executed graph, previous-output/warped-input/new-output hash chain, every reconstructed anchor warp, all source-frame hashes and selected between-repaint frames. The recurrent feedback algorithm is unchanged.
- The same three-interval Krea Turbo tail, Euler/simple, CFG 1, shift 1.15, prompt and increment-per-repaint seed policy remain in use. Fewer calls necessarily change which seed is used at a given time. The original cadence-3 graph equals the new graph. Its earlier GPU was an L40S; new variants use RTX 5090, so this is a practical recipe comparison rather than a bitwise controlled hardware study.
- All four individual previews and the comparison contain 72 decoded frames, 24 fps, exactly three seconds. Source motion runs at 12 fps with duplicated delivery frames. No anchors are shifted in time. The last cadence-7 repaint appears only in the final source frame; cadence 10 and 15 finish with half a second from their last generated anchor.
- Visual review: five evenly spaced comparison samples, every delivered frame from 2.416667 to 2.583334 seconds, full-size comparison frames before/after the 2.50-second redraw, plus cadence 15's overview and every frame across 1.166667–1.291667 seconds. The opening was also inspected at full resolution. This is sampled temporal inspection; human playback judgment is pending.
- Reused the retained ComfyUI 0.34.0 runtime and pinned model cache with no installations or model downloads. Model verification took about 29.5 seconds. Container setup on the allocated host took several minutes despite cached weights. The whole rendering batch took 183.17 seconds including warps, transport and encoding. First graph execution took 11.26 seconds; subsequent calls were approximately 2.96–3.08 seconds.
- Downloaded and hash-verified all 288 archive files, including 20 remote input/output images. Archive SHA256: `a542c3e9eade9c64b21690d9619f72f4c15c8f61d6474e9f9a29b0aac2dff525`. All generations, intermediate frames and receipts are local. Verified an empty queue, deleted the owned GPU Pod, and verified the live Pod list is empty. The authorized 50 GB model/runtime volume remains.

[Runner](cadence_slow.py), [comparison and verification](cadence_slow_review.py), shared [feedback loop](turbo_smoothing.py) and [cadence verification](cadence_spacing_review.py). Private cloud receipts: `apps/deforum/work/cadence-slow-session/`.

## Interpolation follow-up: plan

Olof requests RIFE on all four cadences with the previously used settings. Reuse the accepted cadence-3 RIFE delivery and interpolate the preserved 7/10/15 anchors locally using RIFE 4.25, full-scale float32 MPS inference and 24 fps delivery. Do not regenerate diffusion frames. Anchor source rates are 12/7, 12/10 and 12/15 fps; multipliers 14, 20 and 30 preserve the original repaint instants exactly. Allow positive source rates below 1 fps in the existing runner and verify actual timing.

As before, preserve the original warp-only interval after the final generated anchor: 0.25 seconds for cadence 3, 1/12 second for 7, and 0.5 seconds for 10/15. No future endpoint exists there for RIFE. Retain raw versions, first-pair checks and source hashes. Deliver all four at equal duration in one synchronized comparison and inspect transitions before claiming an improvement.

The timing relationship is `repaints/second = source-motion fps / cadence`; `seconds/repaint = cadence / source-motion fps`. Delivery FPS is separate. Duplicating 12 fps motion frames into a 24 fps file preserves time and adds no motion samples. RIFE adds inferred display samples while preserving the diffusion anchors' timestamps. Merely relabeling the same frame sequence with a different FPS changes speed and duration; our assembly does not do that. Future experiment descriptions should state seconds per repaint, source-motion FPS and delivery FPS together. Olof identifies perceived update rhythm as important; his proposed too-busy/too-uneventful thresholds remain hypotheses, not settled preferences.

## Interpolation follow-up: results

All four finished versions are available with **RIFE 4.25 and the same non-timing settings as the accepted baseline**. No new diffusion frames or cloud resources were needed. Cadence 3 reuses the existing accepted delivery; 7, 10 and 15 interpolate the exact preserved generation anchors. The raw comparison remains intact.

![Cadence 3, 7, 10 and 15 with RIFE](../exports/cadence-slow-v001/comparison-rife/preview.mp4)

Individual finished clips: [3](../exports/turbo-smoothing-v001/interpolation/preview.mp4), [7](../exports/cadence-slow-v001/cadence-7/interpolated/preview.mp4), [10](../exports/cadence-slow-v001/cadence-10/interpolated/preview.mp4), [15](../exports/cadence-slow-v001/cadence-15/interpolated/preview.mp4).

| Cadence | Diffusion anchors per second | Seconds per repaint | Delivery FPS | RIFE images between anchors |
| --- | ---: | ---: | ---: | ---: |
| 3 | 4 | 0.25 | 24 | 5 |
| 7 | 1.714 | 0.583 | 24 | 13 |
| 10 | 1.2 | 0.833 | 24 | 19 |
| 15 | 0.8 | 1.25 | 24 | 29 |

The temporal windows show the intended change: before the cadence-15 anchor at 1.25 seconds, the RIFE version has already moved toward its new arches and details, while the raw version retains the prior painting until the anchor. At the anchor, the two versions meet exactly. The same applies around the 2.5-second redraw in cadence 10/15. First-pair midpoint images have some translucent/doubled architectural lines and softened ornaments; temporal smoothing does not establish perfect correspondence. Cadence 10 remains a useful middle-ground audition, with 15 the slower alternative, but Olof has not judged these finished versions yet. Do not promote an assistant still-frame assessment to a human playback verdict.

Verification: checked all output hashes against RIFE receipts, preserved source hashes/mtimes, exact anchor pixels at their original timestamps, identical pinned model/code/weights and non-timing settings versus the accepted baseline, and each finished video's 72 decoded frames at 24 fps for exactly three seconds. The baseline's 72 saved display frames also match their original manifest. Nine timing/inventory tests pass, including the sub-one-fps anchor case. Actual first-pair runs validated all three source rates, including cadence 15's 31-frame pair at 24 fps. Full RIFE inference took 20.33, 17.81 and 18.03 seconds for 7/10/15, excluding setup and encoding. Raw interpolation exports include final holds; final assembly preserves the original three-second endpoint and replaces the final interval with the existing warp-only frames as planned.

Visual checks: all three first-pair midpoint images at full size; five evenly spaced comparison samples; every display frame from 2.416667–2.583334 seconds; matched raw/RIFE cadence-15 frames across 1.166667–1.291667 seconds. Source and result PNGs, both comparison videos, individual previews and review receipts remain local. No GPU Pod was created for this follow-up.

Reproduce from `apps/deforum/`: run `interpolate.py` using `work/rife-session/.venv/bin/python`, the preserved `cadence-N/rife-sources`, `--source-frames` 6/4/3, `--source-fps 12/N` and `--multiplier 2N`. Use a new output directory, inspect `--pair-only` output, then supply its manifest with `--validated-pair` for the full run. The existing receipts record exact commands. Assemble using `uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/cadence_slow_review.py --interpolated`.
