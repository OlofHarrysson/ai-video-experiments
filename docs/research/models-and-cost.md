# Image models and recurring cost

Researched 2026-09-06. Recommendation: keep SDXL as the workflow control, then benchmark self-hosted FLUX.2 Klein 4B distilled as the first modern-model candidate. No new model was installed or rendered during this research.

## Compare the actual loop

The [first session](../../apps/deforum/results/2026-09-06.md) averaged 144.66 seconds per five-second clip after the initial image was cached. At the observed all-in running rate of $0.768/hour, that is approximately $0.0309 per 40-frame clip, or $0.00079 per newly diffused frame (39 feedback iterations). The $0.24 session balance difference also includes setup/review and smoke tests; it is not a per-clip price.

At that measured rate, one pass over 30 seconds is roughly $0.19, one minute $0.37, and five minutes $1.85. These are linear warm-runtime estimates, excluding startup, extra depth processing, interpolation, downloads, idle time, retries, and rejected creative attempts. They are not quotes or long-run benchmarks. The first image of each fresh scene also costs inference time.

Olof wants similar economics and rules out a pipeline around 3× as expensive. Use the measured SDXL recurring cost as the comparison, rather than amortizing all candidates against an arbitrary setup session. Aim near 1×; reaching about $0.093 per comparable five-second clip is a stop-and-reconsider point. Track total spend and cost per accepted second as well: cheap rejected footage is still wasted budget.

## Shortlist

| Candidate | Why test it | Integration and cost uncertainty |
| --- | --- | --- |
| Existing SDXL base | Known working feedback loop and cost reference. | Test detail and flicker separately; Olof found 0.30 too smooth and 0.50 too flickery. |
| FLUX.2 Klein 4B distilled | Four-step generation/editing; Apache 2.0 weights. Official ComfyUI generation and editing workflows exist. | Uses its own diffusion model, Qwen text encoder and VAE. Benchmark a native workflow, then one feedback step. Neither 4090 speed nor temporal quality is established here. |
| SDXL + DMD2 | A small change of model components within an already working family; official four-step SDXL UNet and LoRA examples. | Requires the appropriate distillation schedule/guidance. Reducing ordinary SDXL to four steps is not the same experiment. Recurrent img2img quality is unverified. |
| Krea 2 Turbo | Eight-step distilled checkpoint; a second candidate for visual character if Klein is disappointing. | Native integration, low-denoise behavior, memory and license suitability need checking for the chosen weights. Keep it behind the first modern-model benchmark. |
| Seedream through fal | Useful for reference images, scene keyframes, and deliberate edits. | Hosted editing is an instruction-conditioned API, not access to the SDXL latent sampler. Per-frame pricing is much higher than our measured recurring baseline. |

Sources: [Klein model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B), [ComfyUI Klein workflows](https://docs.comfy.org/tutorials/flux/flux-2-klein), [DMD2 implementation](https://github.com/tianweiy/DMD2), [Krea 2 implementation](https://github.com/krea-ai/krea-2).

BFL's model card quotes roughly 13 GB VRAM for Klein 4B; ComfyUI reports a smaller footprint and fast times for its tested 5090 workflow. These are configuration-specific upstream measurements, not predictions for our 4090 Pod. Measure the complete pipeline, including text encoder, VAE, transfers and depth. Four sampling steps do not imply seven times our current speed. [Model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B), [ComfyUI guide](https://docs.comfy.org/tutorials/flux/flux-2-klein)

## Hosted price comparison

On the research date, fal lists Seedream 4.5 editing at $0.04/image and Seedream 5.0 Lite editing at $0.035/image. Forty calls would be $1.60 or $1.40, respectively, roughly 52× or 45× our warm SDXL five-second cost. Resolutions and capabilities differ, so this is an economic illustration, not a matched-quality benchmark. An occasional keyframe can still be worthwhile. Seedream 4.5 is a priced reference, not a claim that it is the newest version. [4.5 edit pricing](https://fal.ai/models/fal-ai/bytedance/seedream/v4.5/edit), [5.0 Lite edit pricing](https://fal.ai/models/bytedance/seedream/v5/lite/edit)

BFL lists Klein API pricing from $0.014/image: even that minimum is $0.56 for 40 calls, before any higher-resolution/reference charges. Self-hosting is the relevant Klein comparison for this project. Recheck prices before execution. [BFL pricing](https://docs.bfl.ai/quick_start/pricing)

## Small benchmark protocol

1. Preserve the SDXL control. Keep resolution, initial reference, camera path and generated frame count comparable. Use each model's appropriate sampler and conditioning; do not copy numeric denoise settings blindly.
2. Run the candidate's official native example, then test one warped-image redraw. Verify that it retains intended structure and produces non-black output.
3. Render eight feedback frames; record wall time, peak VRAM, model/node versions, and the full graph. Stop early on a major cost or integration failure.
4. Extend to 40 only if useful. Compare playback flicker, detail loss, structural drift and controllability separately. Add depth/interpolation as separate experiments so their costs remain visible.

A native reference-edit workflow may condition on an image while initializing sampling differently from partial img2img. Decide which behavior the experiment needs and inspect the actual graph. A generic `MODEL` socket or “model-agnostic” README is insufficient evidence of compatible conditioning, latent shape, sampling or continuation.

The current client and installer are SDXL-specific: checkpoint validation, graph node IDs and the recorded model hash assume the existing recipe. Integrating another model must update those together; a new graph alone must not inherit a false SDXL provenance receipt.
