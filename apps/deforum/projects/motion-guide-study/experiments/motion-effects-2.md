# Stronger and combined spatial effects

2026-09-07. Olof selects radial unfolding as by far the best of the previous three clips. He requests more effects and a stronger ring. He values the amount of motion and subject repositioning in turn/bank but dislikes the large black empty region; adding noise is his hypothesis, not an established diagnosis.

Three initial six-second branches retain the selected opening and B's repaint recipe:

- **Strong ring:** reuse the exact ring displacement fields at four times their previous magnitude (factor 3.2 instead of 0.8), isolating strength.
- **Turbulent warping:** the actual `Turbulent-noise-30s.mp4`, DIS Medium at factor 2 from `Evolve-Slow-30s`, with camera and guide compositing disabled.
- **Rotating unfolding:** the preferred kaleidoscope fields at the same factor 0.8, preceded by 0.9 degrees of in-plane rotation per generated frame. This combines tested unfolding with a restrained version of the roll ingredient seen in `Revolve-30s`; it is not a full Revolve reproduction or a 3D orbit.

Preserve six-second motion-only versions and all warped inputs. All guide steps remain the first 48 consecutive 12-FPS guide frames, delivered at 8 generated FPS with 24-FPS holds. SDXL base/art LoRA, prompt, steps 18, CFG 4.5, denoise 0.58 and seed 7301 + frame remain unchanged. No interpolation or new model build.

Inspect an early repaint checkpoint before the full clips. Separately diagnose old turn/bank black pixels versus newly uncovered warp regions, then test the smallest relevant gap-repair change using existing ComfyUI nodes. Do not classify all black artwork as missing data or increase whole-image noise without evidence.

Runner: `motion_effects_2.py`; outputs: `exports/motion-effects-v002/`. Exact source hashes and executed graphs are preserved. All originals remain untouched.

## Video results

All three six-second clips completed. Olof's original radial unfolding remains the selected reference; his preference among these new versions is unconfirmed.

| Effect | Repaint and motion-only preview | Observed result |
| --- | --- | --- |
| Rotating unfolding | [Artwork](../exports/motion-effects-v002/rolling-unfold/repaint/preview-48f.mp4) · [Motion only](../exports/motion-effects-v002/rolling-unfold/warp-only/preview.mp4) | Builds on the preferred effect: the portal pinches into cavities containing planets while the surrounding terrain turns and the explorer changes position. Near the end, a cavity becomes a beaked profile. Strong structural change, but subject identity/count remains uncontrolled: a tiny extra figure briefly appears around 5.125 seconds. |
| Strong ring | [Artwork](../exports/motion-effects-v002/strong-ring/repaint/preview-48f.mp4) · [Motion only](../exports/motion-effects-v002/strong-ring/warp-only/preview.mp4) | Four times the previous displacement produces a much larger glowing orb, which becomes an alien face near the end. This is a clear strength comparison. The consecutive-frame window also exposes a second explorer appearing at 3.0 seconds; by 3.25 seconds one main figure remains. |
| Turbulent warping | [Artwork](../exports/motion-effects-v002/turbulent/repaint/preview-48f.mp4) · [Motion only](../exports/motion-effects-v002/turbulent/warp-only/preview.mp4) | The motion-only image becomes heavily wrinkled, but the repaint repeatedly returns to a circular portal and central flame. Rim and terrain change substantially without the other clips' larger compositional transformations. Less distinctive in the sampled review. |

Assistant recommendation: inspect rotating unfolding as the closest continuation of the favorite, and the strong ring as the more exaggerated alternative. Turbulence is retained as a useful example of the repaint resisting a guide's structural deformation. The prompt's causal contribution to that resistance has not been isolated.

Review used six evenly spaced timestamp-matched artwork/motion-only pairs per clip, followed by seven consecutive generated frames: strong ring 2.5–3.25 seconds, turbulence 3–3.75 seconds, rotating unfolding 4.5–5.25 seconds. Sheets are in each effect's `reviews/v001/` and `reviews/v002/`. These are sampled-frame findings, not a claim of normal-speed playback quality. All three videos are surfaced in chat for Olof's assessment.

The motion controls are explicit: ring displacement is exactly four times each of the previous 47 fields; turbulence uses a different source guide; rotation applies +0.9 degrees before the regional warp at every step. Rotation sums to 42.3 degrees over the clip, but the combined deformation and repaint do not constitute a rigid 42.3-degree camera turn. Rotation and guide remapping use two bilinear resampling operations with reflected borders.

## Execution and validation

[Validation](../exports/motion-effects-v002/validation.json) confirms 144 completed jobs: 141 feedback frames and three camera probes. Each artwork and motion-only video has 48 source frames at 8 FPS, encoded as 144 held frames at 24 FPS, 1024×576, six seconds. No RIFE or interpolated frames were added.

Total reported job execution was 376.231 seconds across two actual workers. Initial queue/startup delays were 139–153 seconds; subsequent median execution was 2.26–2.48 seconds per frame with median queue delays of 3.04–3.66 seconds. The existing worker image `f106834b7` was reused; these settings did not require a new build. Startup and queue overhead remain separate from warm inference time and account cost.

Local checks cover zero-flow identity, known positive translation direction, all 47 exact fourfold ring fields, graph references, and incrementing seeds. Hosted probe validation confirms mask area and exact preservation outside the repair mask before global repaint. Outputs, submitted graphs, warped inputs, flow fields, masks and diagnosis artifacts are preserved locally.

Cloud archive verification byte-compared all **877 objects / 269,421,104 bytes** against their local copies and confirmed an unchanged second listing. The endpoint is paused with minimum and maximum workers zero; live inventories show zero workers, Pods and network volumes after detaching and deleting this session's temporary volume. The stale active deployment file is archived as closed. Account balance moved from $46.741084278 to $46.348430352, approximately **$0.39** for the session at this readback, with reported current hourly spend zero. Private receipts remain under ignored `work/motion-effects-2-session/`.


## Camera diagnosis and matched probes

The [local diagnosis](../exports/turn-bank-diagnosis-v001/README.md) separates missing coverage from near-black color. At old frame 3, 4.26% of positions lack direct coverage and 1.70% remain empty after the warp's small neighbor fill; 95.07% of those still-empty positions remain near-black after repaint. At frame 16 no positions remain empty after that fill, yet the repaint is 30.11% near-black. Most of the large dark region is therefore inherited image content at that point, not a new hole in the current mask. Fresh depth also treats much of that dark band as near geometry. Near-black means maximum RGB channel ≤16, not missing data.

The old prompt asks for a black exterior/background. Its causal role is a hypothesis, tested with the same old frame-2 input and frame-3 camera/seed using three probes against the preserved original: repair only, changed exterior prompt only, and both.

Repair uses existing `VAEEncode → SetLatentNoiseMask → KSampler(denoise=1) → VAEDecode → ImageCompositeMasked`, then the original global 0.58 repaint. Invert Difforum coverage (white=valid) to get white=repair. No mask growth; growing its dense thin gaps could affect much of the image. Composite the original warped image outside the mask before the global repaint. Repair seed is 107301+frame; global seed remains 7301+frame. The ordinary encoder before the global sampler drops the repair mask. Preserve both pre-global repaired pixels and masks.

The prompt comparison changes only the two exterior-black clauses, retaining the central dark opening and black-ink style. Changed conditioning applies to both repair and final repaint. A full repaired clip, if the probe warrants it, starts at the original opening to test prevention of accumulation, rather than trying to repair all historical black pixels with a current-step coverage mask. This is a workflow test, not another motion effect.


### Probe result: useful diagnosis, unsuccessful fix

The same old frame-2 input and frame-3 camera/seed produced near-black fractions of **16.85% original**, **16.64% repair only**, **15.91% prompt only**, and **15.57% repair plus prompt**. The repair mask occupies 4.26% of the image. Both repair composites exactly preserve all pixels outside the mask before the global repaint, but around 64% of masked positions are still near-black immediately after repair. These percentages include legitimate dark artwork; they are not a semantic quality metric.

The [matched probe sheet](../exports/motion-effects-v002/camera-repair/probe-comparison.jpg) still shows a broad dark left band in all four results. This disproves the simple expectation that a full-noise pass in the current gaps will reliably solve the visible frame. It does not prove noise never helps or separate every prompt/conditioning effect. The combined probe makes a small change rather than a satisfactory repair. No full repaired camera clip was commissioned from this weak result. Main deliverables remain the three new motion studies; original turn/bank and all probes are preserved. [Probe validation](../exports/motion-effects-v002/camera-repair/probe-validation.json), runner `camera_repair.py`.
