# Moving the feedback loop to a modern image model

2026-09-08. Recommendation: audition **FLUX.2 Klein 4B distilled** next, with **Krea 2 Turbo** as the artistic alternative. Preserve SDXL as an archived control. This is a researched proposal, not an implemented migration or a demonstrated quality improvement. No weights, packages or cloud resources were installed during this audit. The subsequent approved [execution attempt](../../apps/deforum/projects/modern-model-study/experiments/baseline.md) built a new worker but stopped during model preparation before inference; owned resources are cleaned up. The audit below describes the pre-audition deployment.

Olof finds the two Euler variants insufficiently different and wants progress toward newer models, while retaining reliable motion tooling. More SDXL sampler sweeps are lower priority. [Prompting for feedback](prompting-for-feedback.md) records model guidance and concrete draft prompts.

## Our actual dependency boundary

The latest [sampler experiment](../../apps/deforum/projects/motion-guide-study/experiments/samplers.md) submits **nine node instances, eight unique node types**. All are standard ComfyUI nodes:

`CheckpointLoaderSimple → LoraLoader → two CLIPTextEncode nodes`

`LoadImage → VAEEncode → KSampler → VAEDecode → SaveImage`

Model/conditioning/VAE connections join those paths. There are **zero Difforum, depth, ControlNet, optical-flow or RIFE nodes** in this graph. Evidence: the archived `exports/samplers-v001/euler/manifest.json`, [samplers.py](../../apps/deforum/projects/motion-guide-study/experiments/samplers.py), and the [graph builder](../../apps/deforum/projects/motion-guide-study/experiments/move_warp.py). Historical scripts import one another as helpers; that does not execute all their older graph variants.

The Mac takes the last generated PNG, applies the scheduled direct spatial warp, sends it for one repaint, and preserves the returned image as the next anchor. Cadence intermediates are built afterward from the two warped generated endpoints and never enter feedback. [Spatial implementation](../../apps/deforum/projects/motion-guide-study/experiments/spatial_sequence.py), [cadence implementation](../../apps/deforum/projects/motion-guide-study/experiments/repaint_controls.py).

| Component | Current dependency | Migration consequence |
| --- | --- | --- |
| Spatial controls / previews | Local NumPy/OpenCV transforms; RGB images | Reuse twist, expansion, ripple, plane turn and scrubbing. They do not require an SDXL latent format. |
| Repainting | SDXL checkpoint, SDXL art LoRA, CLIP conditioning, SDXL VAE, partial img2img schedule | Replace as one model-specific recipe. Our LoRA and denoise numbers do not transfer automatically. |
| Cadence / review / archive | Local generated-frame files, Pillow/FFmpeg; exact frame manifests | Keep the behavior. Record new dimensions/timing explicitly. |
| Serverless transport | Generic graph plus one source image; archive adapter expects main `SaveImage` node **11** | A native Klein graph needs an API graph export and this output contract, not a rewritten transport. Current client directly supplies one source image, sufficient for the first single-reference test. |
| Reproducible GPU image | Dockerfile adds **two** custom packs: Difforum and DepthAnythingV2; also bundles SDXL, its art LoRA, QR ControlNet and depth weights | The packs/unused weights are installed but unused in this experiment. For a new model worker, package the needed components rather than accumulating old and new weights indefinitely. Preserve the old recipe. |
| Legacy generic CLI | `experiment.py` assumes checkpoint node 1 and records hardcoded SDXL/Difforum provenance in its direct-Pod path | Do not route a new model through that unchanged path. The latest experiment uses `serverless_client.submit`, which accepts arbitrary graphs and has no such SDXL preflight. |

The last completed render reports ComfyUI **0.34.0**. Inspection of that exact release's source finds Flux2/Klein, Krea2 and Z-Image model support, the `flux2` and `krea2` encoder types, and `Flux2Scheduler`. This supports feasibility; it is not a live import test, VRAM benchmark or proof that every node in today's template works in the worker. [Pinned core model support](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/supported_models.py), [encoder loader](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/nodes.py), [Flux nodes](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy_extras/nodes_flux.py).

The original Deforum and our installed Difforum package are distinct projects. The installed Difforum revision is dated **2026-08-04**; calling this particular package a frozen 2023 dependency would be inaccurate. Its recent commit does not prove universal model compatibility, either. [Pinned commit](https://github.com/chillithebillis/Difforum/commit/1d750efd3c1d1dda792b8ef6c14b06a14a69f879). The custom-pack count above describes this Dockerfile's additions, not a complete inventory of everything bundled in RunPod's base image.

## Shortlist and tradeoffs

| Candidate | Evidence for trying it | Remaining question |
| --- | --- | --- |
| **FLUX.2 Klein 4B distilled — first feedback audition** | Official four-step image generation/editing workflows; separate Qwen3 4B encoder and Flux2 VAE. Native editing graph uses `ReferenceLatent`, Euler, `Flux2Scheduler`, CFG 1. | Will repeated edits respect the warped layout and preserve texture while allowing interesting morphing? Reference conditioning is different from our current partial-noise latent initialization. Four steps do not prove lower total cost. |
| **Krea 2 Turbo — artistic alternative** | Author emphasizes stylistic exploration; natural-language prompting guide, eight-step native ComfyUI workflow and optional artistic LoRAs. Official text-to-image template uses Euler/simple, CFG 1, Krea2 encoder mode and Qwen Image VAE. | Its style-reference workflow adds specific weights/LoRA and influences aesthetics; it is not evidence of layout-preserving img2img. Recurrent repainting and warm 4090 cost need testing. |
| **Z-Image-Turbo — reserve** | Official ComfyUI support and efficient distilled generation. Inspected current template uses eight steps, CFG 1, `res_multistep`/simple, its model-sampling patch and proper encoder/VAE. | Native generation support alone does not establish the desired reference-editing feedback behavior. Avoid confusing Turbo generation with the separate Z-Image-Edit capability. |

Sources: [Klein ComfyUI workflows](https://docs.comfy.org/tutorials/flux/flux-2-klein), [BFL Klein card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B), [Krea author implementation](https://github.com/krea-ai/krea-2), [Krea ComfyUI guide](https://docs.comfy.org/tutorials/image/krea/krea-2), [Z-Image ComfyUI guide](https://docs.comfy.org/tutorials/image/z-image/z-image-turbo), [Z-Image author card](https://huggingface.co/Tongyi-MAI/Z-Image-Turbo).

Klein 4B is the bounded compute/integration candidate within the project's recurring-cost constraint, not a claim that it is the strongest available model. Its larger 9B relative can be considered if the editing mechanism succeeds but 4B's artwork quality limits the result. Avoid testing both sizes before the loop's main uncertainty is answered. Existing hosted FLUX experiments used FLUX.1 dev; they were not Klein feedback tests. Keep [earlier economics](models-and-cost.md) separate from any new measured cost.

## The workflow change that matters

Current img2img uses the warped image's latent as the starting canvas, adds controlled noise, and denoises it. The inspected Klein editing template instead starts an **empty output latent** and supplies the input as **reference conditioning**. There is no directly equivalent “reuse 55% of the old image” setting. A new `denoise: 0.45` field on the old graph would not faithfully reproduce the native edit workflow.

Start with the official editing path. Give it the already-warped frame and an instruction describing the small repainting change. Do not also ask it to rotate the scene; the spatial transform has already happened. If it straightens the deliberate distortion, replaces the subject, adds borders or redesigns everything, the first feedback probe has failed even if the image is attractive. An older model's looseness may sometimes produce better surreal morphing; newness does not settle that aesthetic question.

## Proposed small audition

1. **Two opening stills with Klein's native generation recipe**, using one concise and one more descriptive version of the same scene brief. Keep settings/seed matched. Select a useful opening through assistant screening; do not start its loop from an SDXL-generated anchor.
2. **One warped-frame edit**, checking that the intended displacement survives and that one tiny local change can be requested without a global redesign. Show input, warp and output together.
3. **Eight advancing anchors**, then extend to the familiar three-second/cadence-3 twist only if the short feedback chain retains useful motion and detail. Keep interpolation, depth, masks and automatic per-frame prompt expansion out of this first audition.

Record exact weights/hashes, actual conditioning text, full graph, runtime, warm inference, round-trip time, preserved warp and cumulative drift. Reuse motion and review tools. Do not build a generalized multi-model framework yet. Keep model packaging separate from the public research notebook's ordinary document edits so a future deployment design can avoid unnecessary image rebuilds; this is an operational proposal, not changed configuration.

## Evidence

Audited local checkout at commit `1a5cbf7`. Official templates inspected at `7c25a3c586484601f94b7e8f8b14c23b2c95a096`; source support checked at ComfyUI `12d5279438bfefc058a269eae805ceab6047777f` (v0.34.0). Raw source/API responses remain in ignored `apps/deforum/work/modern-model-research/`; the [source index](sources/modern-models-2026-09-08.json) records URLs and hashes. No live worker inventory or new-model execution is claimed.
