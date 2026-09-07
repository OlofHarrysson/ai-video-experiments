# Deforum architecture and temporal continuity

Research snapshot: 2026-09-07. Read-only source comparison; no new GPU render, installation or workflow migration. This document compares classic Deforum, the newer Difforum rewrite we use, the Deforum-organization ComfyUI nodes, and the XmYx implementation. It complements [parameter semantics](feedback-parameters.md), [current ComfyUI practices](comfyui-animation-practices.md), and the [YouTube tutorial study](comfyui-youtube-workflows.md).

Subsequent execution: the [continuity study](../../apps/deforum/projects/brain-entity-study/experiments/continuity.md) tests fixed versus incrementing seeds, separate pixel noise and Flow Stabilize. [Local RIFE finishing](../../apps/deforum/projects/brain-entity-study/experiments/rife-results.md) now preserves originals and generates intermediate frames. These results are separate from this source audit; interpolated noise tensors and denser diffusion timelines are still untested.

## Recommendation

Keep the current ComfyUI/SDXL setup as the comparison baseline. First test actual intermediate-frame synthesis on preserved P01/P03 footage, then test more gradual changes to the noise supplied during generation. Do not migrate the complete runtime or choose a new image model before these narrower comparisons establish what is missing.

The current loop implements the basic Deforum idea, but omits several temporal mechanisms present elsewhere. Its generated images are only eight frames per second, with full img2img repainting at every frame. The 24 FPS export repeats images; it does not invent transitional poses or morph states. Our selected sampler's higher cadence merely skips diffusion on some frames and advances the camera warp. It does not reproduce classic Deforum's two-endpoint tweening. There is no temporal model in this SDXL graph.

These are verified implementation differences. Their contributions to perceived quality remain experimental. Interpolation can make a transition easier to watch without making its underlying objects or narrative coherent.

## Creative evidence and scope

Olof's playback assessment supersedes the previous contact-sheet ranking. P06 is clear but feels like a slideshow. P01 has interesting morphing and better continuity, P03 is very good, and P04 is likely the clip described as “Before” and “really cool.” P02 has a good beginning and a boring ending; P05 shares the gradual-transition problem. This round is substantially closer to the desired art than earlier experiments. Preserve that look while improving the motion.

This separates three problems:

1. **Temporal sampling:** too few distinct visual states per second.
2. **Per-step change:** each repaint can replace too much scene content or texture at once.
3. **Creative progression:** the shot must keep evolving without flattening or becoming repetitive.

P06 helped diagnose the third problem's relationship to prompt travel, but failed the user's second criterion. Better middle-frame detail is not sufficient evidence of better video.

## Which project is which?

“Deforum” names several distinct implementations. Current GitHub metadata was read directly, including resolved repository names and default-branch commit dates. Dates below identify inspected code; they do not prove support responsiveness or compatibility with our environment. None of these repositories was marked archived at inspection.

| Project | Inspected head; commit date | Role and evidence |
| --- | --- | --- |
| [deforum/deforum-stable-diffusion](https://github.com/deforum/deforum-stable-diffusion/commit/03be26aebc4aec6e3a0298c8d3e271c672034f59) | `03be26a`; 2024-08-30 | Original notebook/local lineage. Historical mechanisms and terminology; not the current worker. |
| [deforum/sd-webui-deforum](https://github.com/deforum/sd-webui-deforum/commit/5d63a339dbec8d476657a1f672a4eeb6dc79ed37) | `5d63a33`; 2024-05-15 | Official A1111 extension; `deforum-art/sd-webui-deforum` redirects here. Main comparison for classic rendering and cadence. Repository push date is later than this default-branch commit. |
| [chillithebillis/Difforum](https://github.com/chillithebillis/Difforum/commit/1d750efd3c1d1dda792b8ef6c14b06a14a69f879) | `1d750ef`; 2026-08-04 | Independent rewrite and the nodes actually installed in our worker. Our pin already equals the inspected main branch. It is not the Deforum organization's node package. |
| [deforum/deforum-comfy-nodes](https://github.com/deforum/deforum-comfy-nodes/commit/5d2bb850d934e69a73ba79c2186a4a437e9c2ec2) | `5d2bb85`; 2026-05-14 | Deforum-organization native ComfyUI implementation. Generic graph loops, schedules, image/latent utilities and a FLUX example. Not installed or runtime-tested here. |
| [XmYx/deforum-comfy-nodes](https://github.com/XmYx/deforum-comfy-nodes/commit/d56b6cb39a471023ff027e03b7550935d5cfe017) | `d56b6cb`; 2026-06-01 | Separate integration with more classic machinery, including standalone cadence. Not simply another name for the organization package. |
| [XmYx/deforum-studio](https://github.com/XmYx/deforum-studio/commit/edf898d8325d6946aed0bed8a21ff03bb0510f04) | `edf898d`; 2026-05-30 | Backend selected by the current XmYx node installer; its setup declares Python 3.10–3.14 support. |
| [deforum-studio/deforum](https://github.com/deforum-studio/deforum/commit/f95533c84e997474e66b86ce867098f5f6d7ba44) | `f95533c`; 2024-07-11 | Separate older pipeline repository. Do not confuse its stale Python 3.10 instructions with the current XmYx backend. |

“Official” identifies provenance, not tested quality. Conversely, the existence of 2026 commits means a blanket claim that all Deforum development stopped in 2024 would be wrong. Difforum's promotional claims about solving flicker or model universality must be checked against the actual render path and compatible model recipe.

## What classic Deforum adds around img2img

### Starting model and seed continuity

Source rechecked 2026-09-07 after the motion-guide repaint review. In the original notebook lineage, `generate` uses the same `root.model` for sampling, prompt encoding and image encoding/decoding. It can generate the opening from noise or encode an external starting image. The animation renderer subsequently sets the transformed previous image as `init_sample`. Thus one loaded image model can generate both the opening and its continuation; the incoming image carries scene information between steps. [Pinned generator](https://github.com/deforum/deforum-stable-diffusion/blob/03be26aebc4aec6e3a0298c8d3e271c672034f59/helpers/generate.py), [pinned renderer](https://github.com/deforum/deforum-stable-diffusion/blob/03be26aebc4aec6e3a0298c8d3e271c672034f59/helpers/render.py).

The original renderer's `next_seed` supports fixed, iterated, ladder, alternate and random behavior. The WebUI extension also supports seed scheduling and optional checkpoint scheduling. Fixed seed and fixed checkpoint are available controls, not universal requirements enforced by Deforum. External-image support establishes that a source need not originate from the rendering model; it does not establish good preservation or aesthetic compatibility. [WebUI seed implementation](https://github.com/deforum/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/seed.py), [WebUI generator](https://github.com/deforum/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/generate.py).

A seed initializes randomness; it is not an image identity. Changing it during generation from noise can yield a different composition. During partial img2img sampling, the encoded previous frame is an additional input, so changing the seed does not necessarily replace the whole scene. Conversely, fixing the seed cannot guarantee preservation when the input, denoise or other settings change. Matching a seed across different models does not match their outputs, and incrementing integer seeds does not create gradually changing noise tensors.

For the next experiment, generate a fresh opening and every repaint with the exact same checkpoint, VAE, text encoders, LoRA files/weights, prompt and resolution. Start with a fixed seed to isolate repaint behavior, then investigate seed variation separately if useful. Keep the existing P3 + RIFE result as the creative comparison: the user's preference for that incrementing-seed animation prevents treating fixed seed as an established artistic optimum. The failed Seedream-to-SDXL marsh demonstration does not isolate model mismatch as the cause; using one model throughout removes that confound before a broader denoise sweep. See the [revised experiment](../../apps/deforum/projects/motion-guide-study/experiments/walkthrough.md#user-review-and-proposed-next-test).

The classic renderer keeps image history, camera and prompt schedules. In its cadence branch it retains two diffusion endpoints, advances them with camera transforms, and mixes their contributions to create intermediate output frames. Optional optical-flow cadence estimates correspondences between endpoints; hybrid footage can provide motion and compositing guidance. This is more than holding one frame until the next redraw. [Cadence implementation](https://github.com/deforum/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/render.py#L295-L399).

The warp stage can predict depth from the current image when needed. Its 3D camera conventions also differ from ours, including a fixed translation scale. Copying numeric camera values across implementations does not reproduce a shot. [Camera and depth handling](https://github.com/deforum/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/animation.py#L173-L230).

Classic seed behavior includes fixed, iterated, alternating and scheduled strategies, rather than only a fresh integer on every advancing frame. Incrementing the integer is not interpolation between the corresponding random tensors. [Seed behavior](https://github.com/deforum/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/seed.py#L19-L35).

There is also a separate output interpolation stage using RIFE or FILM. It operates on already generated images and has its own output-rate/slow-motion handling. This must be distinguished from cadence inside animation generation. [Interpolation dispatch](https://github.com/deforum/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/frame_interpolation.py#L85-L120).

Settings are not portable by label. In the inspected A1111 adapter, `denoising_strength = 1 - args.strength`. Difforum forwards its strength schedule directly as denoise. Our `0.82` is therefore aggressive denoising, not 82% image retention. [A1111 adapter](https://github.com/deforum/sd-webui-deforum/blob/5d63a339dbec8d476657a1f672a4eeb6dc79ed37/scripts/deforum_helpers/webui_sd_pipeline.py#L21-L50).

## Our exact graph versus the rewrite's capabilities

The six parameter runs were inspected from their saved API graphs and receipts, and their exports were checked with ffprobe. Every run has 48 source PNGs, six seconds of 1024×576 video, and 144 delivery frames. `DifforumAnimSetup.fps` and the receipt both say 8. The local encoder uses `fps=24` after reading images at 8 FPS. No motion interpolation filter or node occurs on that path. [Local encoder](../../apps/deforum/editing.py), [render recipe](../../apps/deforum/projects/brain-entity-study/experiments/render.py), [preserved experiment records](../../apps/deforum/projects/brain-entity-study/experiments/parameters.md).

| Capability | Current executed graph | What is missing or different |
| --- | --- | --- |
| Previous-image feedback | Warped image → effects/noise → VAE → SDXL img2img → decode → color match | Image feedback is present; there is no learned temporal memory. |
| Camera | 2D, zero translation/rotation, zoom 1.001 per update | Nearly all visible transformation is diffusion/prompt change. These clips do not test 3D reconstruction. |
| Denoise | 0.82; P02 uses 0.70 | Strong freedom to redraw. Reducing it preserved more structure but did not solve the entire artistic problem. |
| Seeds | `increment`, seed 7301 + frame | No interpolated noise tensor or seed-hold schedule. Same numerical proximity of seeds does not imply similar noise. |
| Prompt travel | Blended CLIP conditioning, keyframes 0/23/47, eased per frame; P06 constant | Already interpolates conditioning. Smooth embeddings do not guarantee smooth object transformations. |
| Cadence | 1, every advancing frame diffused | Raising the existing node's cadence would only create camera-warp-only frames between redraws. |
| Temporal finishing | None | No flow stabilization, RIFE/FILM, echo or temporal video module. |
| ControlNet | Off for P01–P06 | P01's ablation only tests removing the guide. It does not test a temporally richer guide. |
| Depth | Not connected in this study | Elsewhere our 3D sampler reuses the supplied depth; it does not recompute depth as the scene morphs. |

The pinned sampler has a single previous image and no future endpoint buffer. Its non-diffusion branch appends the warped image directly; its normal branch replaces that state with the decoded new image. This explains why its `cadence` input cannot be assumed to behave like classic cadence. It also fixes ControlNet to the full denoising range and discards the warp validity mask; no separate masked repair path is exposed in this sampler. [Sampler source](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py#L128-L226).

### Already available in Difforum, but omitted from our graph

The earlier [3D/motion source note](3d-camera-and-motion.md) already identified the parallax-fluid example and Farneback stabilizer. This audit connects those previously documented options to the actual P01–P06 graph and Olof’s playback feedback; they were not enabled in the parameter round.

Difforum's own **parallax-fluid** example connects its sampler to **Flow Stabilize**, then **RIFE VFI**, then video export. It specifies 24 source FPS, RIFE ×2 and 48 delivery FPS. It also changes model/LoRA, denoise, cadence and camera, so importing the whole graph would confound the experiment. Take individual mechanisms as hypotheses. [Exact example](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/examples/advanced/difforum_parallax_fluid.json).

Flow Stabilize uses OpenCV Farneback flow to align prior output with the current frame, then blends history according to local photometric agreement. It preserves the batch length. It is neither a learned video model nor an intermediate-frame generator. Large semantic redraws can fail the agreement test and receive little blending; increasing its strength cannot guarantee smooth morphs. It is available in our installed package, but untested in this study. [Flow implementation](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/flow.py#L19-L105).

Prompt Schedule encodes each keyframe, builds a per-frame blend plan and supplies those conditionings to the sampler. Its helper reconciles different token lengths by truncation/zero-padding to the destination shape; it also blends pooled conditioning. Unequal token lengths are worth checking in a controlled prompt study, but no tokenizer-shape measurement or causal claim about our artifacts has been established. [Prompt node](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/prompt_nodes.py#L24-L38), [blend helper](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/prompt.py#L98-L136).

### Documentation claims that need care

The rewrite's performance guide suggests that lowering strength directly reduces sampling work. That is not how our pinned ComfyUI KSampler behaves at a fixed step count: it constructs a longer sigma schedule and retains the requested number of intervals. Our measured 30-step denoise comparison also did not halve execution time. Prefer the [source-backed parameter audit](feedback-parameters.md) over that general performance claim. [Upstream performance text](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/PERFORMANCE.md#L79-L88).

The same package's “deluxe” example specifies 24 FPS in animation setup, RIFE ×2 and 16 FPS in VideoCombine. This is an apparent timing mismatch if interpreted as preserving setup duration. It may be a deliberate slow-motion recipe, but its labels alone are insufficient. Trace counts, durations and links in any imported example. [Deluxe graph](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/examples/advanced/difforum_deluxe_travel_controlnet_video.json).

## What the other ComfyUI implementations offer

### Deforum-organization nodes

The organization package implements graph expansion with loop state passed between iterations, making the internal sampling path more accessible than a monolithic feedback node. Its FLUX example exposes prompt/denoise/step/seed schedules and transformations. It remains an image-feedback workflow, not automatically a temporally trained generator. [Loop implementation](https://github.com/deforum/deforum-comfy-nodes/blob/5d2bb850d934e69a73ba79c2186a4a437e9c2ec2/flow_control.py), [author's workflow guide](https://github.com/deforum/deforum-comfy-nodes/blob/5d2bb850d934e69a73ba79c2186a4a437e9c2ec2/examples/deforum_flux_complex/README.md).

A particularly relevant node is **SeedInterpNoise**: it produces intermediate noise tensors between seeded endpoints using SLERP. This offers a third option between frozen noise and completely new noise each frame. However, its implementation hardcodes four latent channels and an eightfold spatial reduction. That matches an SDXL-shaped latent assumption, not every model family advertised by the package. It also needs a sampling path that actually accepts the generated noise; our feedback node only accepts a seed mode. [Seed interpolation implementation](https://github.com/deforum/deforum-comfy-nodes/blob/5d2bb850d934e69a73ba79c2186a4a437e9c2ec2/latent_nodes.py#L39-L133).

Do not blindly copy latent-noise injection formulas between model families or accidentally add noise twice. The package's PrepareLatentDenoise node explicitly separates noise preparation and sampling. Its correctness with a chosen model and our installed ComfyUI version requires a focused runtime check. [Preparation path](https://github.com/deforum/deforum-comfy-nodes/blob/5d2bb850d934e69a73ba79c2186a4a437e9c2ec2/latent_nodes.py#L138-L207).

### XmYx nodes and backend

XmYx contains a standalone cadence implementation with endpoint history, frame blending, optical flow and depth support. That is a useful reference for closing the classic-cadence gap, but importing the package also brings its backend and runtime assumptions. [Cadence source](https://github.com/XmYx/deforum-comfy-nodes/blob/d56b6cb39a471023ff027e03b7550935d5cfe017/deforum_nodes/modules/standalone_cadence.py).

Its README still says Python 3.10 is required, whereas its installer points to XmYx/deforum-studio and that backend now declares `>=3.10,<3.15`. This is a real documentation/code disagreement, not proof that the full node stack works with Python 3.12. Installation scripts also manage substantial dependencies. Test in isolation if selected; do not destabilize the working worker merely to investigate. [Node README](https://github.com/XmYx/deforum-comfy-nodes/blob/d56b6cb39a471023ff027e03b7550935d5cfe017/README.md), [installer](https://github.com/XmYx/deforum-comfy-nodes/blob/d56b6cb39a471023ff027e03b7550935d5cfe017/install.py), [backend setup](https://github.com/XmYx/deforum-studio/blob/edf898d8325d6946aed0bed8a21ff03bb0510f04/setup.py).

The separate 2024 deforum-studio/deforum pipeline also makes pre-generation, generation and post-generation stages explicit, including cadence and RIFE/FILM dispatch. It is useful architectural evidence; the current XmYx backend must be assessed by its own pinned code rather than assumed identical. [Older pipeline](https://github.com/deforum-studio/deforum/blob/f95533c84e997474e66b86ce867098f5f6d7ba44/src/deforum/pipelines/deforum_animation/pipeline_deforum_animation.py#L323-L385).

## What the parallel ComfyUI and tutorial studies add

The [official-source practices report](comfyui-animation-practices.md) confirms that our observed ComfyUI 0.34.0 remains the latest published release at this snapshot. Core upgrade alone is not a demonstrated fix. It distinguishes batched image sampling from temporal modules, sampling-time controls from movie-time schedules, and exact caching from approximate acceleration. Its RIFE inspection supplies the endpoint-count rule used below. AnimateDiff-SDXL, Wan and LTX remain conditional routes with family/version dependencies, not drop-in quality switches.

The [YouTube study](comfyui-youtube-workflows.md) screened 70 candidates and read 11 full available caption tracks covering about three hours of listed video duration. Six successful sources are from 2025–2026, five are older specialist foundations. Author workflow JSONs were inspected; no tutorial was visually reviewed or executed here.

- Latent Vision's author tutorials are useful for separating style/composition conditioning, evolving reference masks and actual noise-tensor mixing. Their older SD1.5 AnimateDiff animation example is not evidence for recurrent SDXL compatibility.
- Mickmumpitz's 3D-to-image example illustrates authored structure and stylization, but identifies Kling as the movement generator between poses. Do not attribute the final film's continuity to the SDXL still graph.
- Recent frame-I/O and RIFE tutorials reinforce explicit image counts and export timing. Their defaults and denoise metaphors still require source checks.
- A reference-guided handoff between two visual concepts is a later experiment if text/noise controls are insufficient. It can preserve style while directing subject change, but may resist the surreal morphing Olof wants.

These findings reinforce the mechanism-first test order below. The older 3D-blocking/stylization idea remains deferred; neither tutorial popularity nor a new video-model release justifies changing the current scope automatically.

## Proposed sequence of tests

These are research recommendations, not implementations or already generated results.

| Order | Test | Held fixed | What it can establish |
| --- | --- | --- | --- |
| 1 | Apply RIFE to original P01 and P03 PNG sequences; compare with repeated-frame exports at equal six-second duration | Exact diffusion frames, prompts, seeds, camera, style | Whether missing intermediate presentation frames explain enough of the abruptness. Inspect ghosting, contour tearing and wrong correspondences. |
| 2 | Compare raw versus Flow Stabilize, separately from interpolation | Same original frames and delivery rate | Whether motion-aligned history blending reduces texture changes without suppressing desired morphing. |
| 3 | Compare incremented, held and interpolated noise in one explicit sampling path | Same model, prompt schedule, denoise, camera and output timeline | Whether independent noise changes are a significant source of complete redraws. This requires a small workflow change; it is not a scalar setting exposed by our sampler. |
| 4 | Test a denser generation timeline with milder per-update changes | Same six-second shot and time-based camera/prompt intent | Whether genuine additional diffusion states create better morphs than output interpolation. Rebudget computation and tune denoise empirically. |
| 5 | If necessary, compare classic-style two-endpoint cadence or a temporally trained guided model | Same visual reference and explicit shot intent | Whether more substantial temporal machinery is worth its complexity, latency and effect on the artwork. |

The current transport receipt and encoder hardcode eight generated FPS; a denser-generation test first needs coherent FPS handling through graph, receipt, collection and export. Do not change only the FPS field. For a six-second 24-source-FPS test, allocate approximately 144 source frames, retime prompt endpoints by timestamp, and adjust per-frame transforms. For the current purely multiplicative zoom, preserving the zoom rate when tripling updates suggests `1.001 ** (1/3)` per update, rather than applying 1.001 three times as often. This mathematical adjustment applies to zoom only; denoise has no analogous proven conversion rule. Likewise, simply raising existing cadence may introduce held-image/repaint jumps rather than the desired intermediate morphs.

The inspected RIFE wrapper produces `(N−1)×multiplier+1` images, so 48 inputs at ×3 yield 142, not 144. Add two final-frame holds at 24 FPS to retain the six-second presentation; verify the actual output. See the [interpolation runbook details](comfyui-animation-practices.md#rife-and-film-current-evidence-and-duration-traps).

For review, select the most abrupt source-frame pair and examine its proposed intermediate frames as well as the whole clip. Keep clarity, gradual transformation, preserved visual anchors, interesting progression and camera motion separate. Olof's normal-speed playback verdict selects the winner; static detail metrics or contact sheets support diagnosis.

## Evidence archive and remaining uncertainty

Local source snapshots, repository metadata, resolved commit records, file trees and a download manifest are in ignored `apps/deforum/work/deforum-architecture-research/source/`. The initial fetch retained 234 selected source/example files across six repositories; the XmYx backend was inspected separately. `current-workflow-audit.json` records actual P01–P06 graph settings and ffprobe results. Full third-party sources remain local; this public note links to originals and summarizes findings.

No claim is made that alternate packages load in our worker, that interpolation can recover a semantically correct transition between arbitrary frames, or that any reference video's exact cadence/settings are known. A 60 FPS reference file does not reveal how many diffusion frames its creator generated. Prompt wording, stochastic sampling, LoRA, repeated VAE processing and depth/camera choices can still contribute; the research narrows the next tests rather than proving one universal fix.
