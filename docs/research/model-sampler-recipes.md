# Model and sampler recipes for feedback animation

Research checked 2026-09-08. **Treat the exact model version, sampler, noise schedule and guidance as a recipe.** Ordinary SDXL allows useful sampler experimentation; accelerated/distilled models can require quite different settings. A good still-image recipe is a starting point for animation, not evidence of stable repeated repainting.

The immediate [two-sampler experiment](../../apps/deforum/projects/motion-guide-study/experiments/samplers.md) keeps our model fixed. FLUX.2 Klein remains the later modern-model candidate from [models and cost](models-and-cost.md).

## What we have actually used

An inventory of literal `sampler_name` fields in archived project `runs/*/workflow.api.json` found only `dpmpp_2m`: 473 occurrences in motion-guide-study and 215 across the other projects. These count graph fields, not independent completed experiments, and do not describe opaque hosted APIs. We have not established a preferred sampler through a controlled comparison in this feedback recipe.

Current control: SDXL base 1.0 + `xl_more_art-full_v1.safetensors`, model/CLIP LoRA strengths 1.1, DPM++ 2M, Karras, 18 steps, CFG 4.5, denoise 0.45. Sampling seeds increment once per repaint. The opening and feedback use the same model combination. Cadence 3 and the twist stay unchanged.

## Creator evidence and exact versions

| Model / version | Creator recipe or inspected workflow | What matters for us |
| --- | --- | --- |
| **Our more-art v1 LoRA**, Civitai version **152309**, on SDXL base | Author recommends LoRA strength **0.8–1.0**, allowing higher strength for less detailed results. No mandatory sampler stated. Version gallery metadata includes Euler, Euler a, DPM++ 2S a Karras and DPM++ SDE Karras. | Our 1.1 is above the default recommendation, not inherently invalid. Test strength separately from samplers. Gallery images contain an older beta LoRA and extra finishing; they are not exact v1 recipes. [Creator page](https://civitai.com/models/124347?modelVersionId=152309), [version metadata](https://civitai.com/api/v1/model-versions/152309). |
| **DreamShaper XL Lightning DPM++ SDE**, version **354657** | **DPM++ SDE**, **Karras or Normal**, **3–6 steps**, **CFG 2**. Main description explicitly distinguishes it from **2M**. | Strong candidate for a later cheap artistic checkpoint audition. First use its own recipe, without our art LoRA; test feedback only after a native still works. [Exact version](https://civitai.com/models/112902?modelVersionId=354657), [author metadata](https://civitai.com/api/v1/models/112902). |
| **Juggernaut X**, version **456194** | DPM++ **2M Karras**, 30–40 steps, CFG 3–7; VAE included. | A conventional SDXL reference recipe, not the same as its accelerated relatives. [Version](https://civitai.com/models/133005?modelVersionId=456194). |
| **Juggernaut XI**, version **782002** | Civitai version description: DPM++ **2M SDE**, 30–40 steps, CFG 3–6; scheduler unspecified there; four inspected gallery examples use Exponential at 30 steps/CFG 4.5. RunDiffusion's XI guide instead gives **2M Karras**, 25–40 steps, CFG 4–6. | Both are first-party recommendations. Preserve the disagreement; do not turn either into a universal requirement or silently equate the samplers. [Version](https://civitai.com/models/133005?modelVersionId=782002), [RunDiffusion guide](https://www.rundiffusion.com/prompt-guide-for-juggernaut-xi-and-xii). |
| **Juggernaut XI Lightning**, version **920957** | DPM++ **SDE**, 4–6 steps, CFG 1–2; scheduler unspecified in version text; four inspected gallery examples use Karras at six steps/CFG 2. | Model-family name alone is insufficient. Do not carry XI's 30–40 steps/CFG across. [Version](https://civitai.com/models/133005?modelVersionId=920957), [author metadata](https://civitai.com/api/v1/models/133005). |
| **ByteDance SDXL-Lightning**, official 4-step full checkpoint | Official ComfyUI graph: **Euler + sgm_uniform**, **4 steps**, **CFG 1**, denoise 1. Separate 2/4/8-step weights must match their step count. | Even “Lightning” does not identify one universal sampler recipe: this differs from DreamShaper Lightning. Diffusers example says guidance 0; its no-CFG convention differs from this ComfyUI graph's CFG 1. [Model card](https://huggingface.co/ByteDance/SDXL-Lightning), [actual workflow](https://huggingface.co/ByteDance/SDXL-Lightning/blob/main/comfyui/sdxl_lightning_workflow_full.json). |
| **FLUX.2 Klein 4B distilled**, official ComfyUI editing template | **Euler**, **Flux2Scheduler**, **4 steps**, **CFGGuider 1**; Qwen3 4B encoder and Flux2 VAE. Reference images enter through `ReferenceLatent`. | A different conditioning and scheduling system. Start from the native editing graph; our SDXL partial-denoise loop is not a drop-in equivalent. Distilled and base Klein are separate recipes. [ComfyUI guide](https://docs.comfy.org/tutorials/flux/flux-2-klein), [inspected template](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_flux2_klein_image_edit_4b_distilled.json), [BFL card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B). |

The table is a compatibility/starting-point map, not a model quality ranking or a claim that older SDXL models are the newest available. No new checkpoint was installed for this research.

## What the sampler names conceal

The **sampler** decides how to take each denoising step; the **scheduler** chooses the noise levels at which those steps occur. ComfyUI separates these fields. An A1111 label such as “DPM++ SDE Karras” contains both.

| Source label | ComfyUI sampler | ComfyUI scheduler |
| --- | --- | --- |
| DPM++ 2M Karras | `dpmpp_2m` | `karras` |
| DPM++ SDE Karras | `dpmpp_sde` | `karras` |
| DPM++ 2M SDE Karras | `dpmpp_2m_sde` | `karras` |
| Euler a | `euler_ancestral` | Not specified by this name |
| Euler | `euler` | Not specified by this name |

This is a name mapping, not bit-identical cross-application reproduction. The pinned [ComfyUI sampler dispatch](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/samplers.py) and [sampling implementation](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/k_diffusion/sampling.py) keep these methods distinct. Euler ancestral introduces fresh latent noise during sampling; ordinary Euler with its default zero churn does not add that per-step noise. Both still start from the supplied noisy latent. Ancestral noise is separate from our optional pre-encode pixel noise. More internal randomness may affect evolving texture; it does not guarantee better morphing or worse continuity.

Equal steps do not always mean equal model evaluations or runtime. KSampler's denoise 0.45 also means a shortened noise schedule, not 45% new pixels. The [pinned parameter audit](feedback-parameters.md) explains the implementation. A four-step distilled txt2img example at denoise 1 does not validate four steps at denoise 0.45 in a recurrent loop.

## Civitai findings that change how we read examples

The more-art version endpoint returned ten gallery entries, nine with generation metadata: four Euler, three Euler a, one DPM++ 2S a Karras and one DPM++ SDE Karras. Those nine identify `sd_xl_base_1.0_0.9vae`, 20–70 initial steps and CFG 7–8. They also record high-resolution passes of 30–120 steps, upscale factors 1.35–1.5, a named upscaler and token-merging settings. Their LoRA metadata points to `xl_more_art-full-beta3_1_0.5`, hash `fe3b4816be83`, rather than our verified v1 hash. Thus copying the visible sampler and base step count would omit substantial parts of the showcased process. This is a small curated gallery, not a sampler comparison.

There is another documentation mismatch: Lykon's [Hugging Face card](https://huggingface.co/Lykon/dreamshaper-xl-lightning) demonstrates four steps and guidance 2 but constructs `DPMSolverMultistepScheduler` from a stored Euler scheduler config. That stored config has `use_karras_sigmas: false`. It does not establish the Civitai recipe's exact DPM++ SDE/Karras behavior. Prefer the explicit exact-version Civitai recipe for a ComfyUI audition and preserve the discrepancy rather than guessing from a Python class name.

For a new model, record its version/hash, recommended native workflow, sampler/scheduler, guidance, resolution, VAE, LoRA strength/trigger words, and any second pass. Treat a required distilled schedule differently from a creator's preferred artistic setting. Never assume a generic clip-skip value, an SD1.5 LoRA or a screenshot's negative prompt transfers to a different architecture.

## Small next tests

1. **Current model, Euler/Karras**, retaining 18 steps, denoise 0.45 and CFG 4.5. Ask whether it changes contour retention and repaint jumps relative to DPM++ 2M.
2. **Current model, Euler ancestral/Karras**, otherwise matched. Ask whether noise added inside the sampler produces useful evolution without the grain we saw from extra pixel noise.

These are controlled local comparisons, not recreations of Civitai's high-resolution gallery settings. Keep LoRA 1.1 for both; test 0.9 separately if repaint pressure remains a problem. Do not simultaneously add a new checkpoint, high-res fix and CFG changes. For the later modern-model audition, use Klein's official four-step graph and generate its own opening before trying repeated edits; compare the complete recipe, not equal numeric settings across architectures.

The two sampler alternatives are now [rendered and reviewed](../../apps/deforum/projects/motion-guide-study/experiments/samplers.md). Ordinary Euler stays closer to the control in sampled frames; ancestral changes structure/texture more. Neither result establishes a universal best sampler, and human playback preference is pending.

## Evidence archive

Public API JSON and downloaded official workflow/config snapshots are preserved locally in ignored `apps/deforum/work/sampler-session/research/`. The [source manifest](sources/sampler-models-2026-09-08/index.json) records URLs, file hashes and selected model identities without copying gallery prompts into Git. Civitai's normal webpage was unavailable through the web extraction tool; its public API supplied the author descriptions and version metadata. This research does not claim that Civitai artwork or any unexecuted model recipe was visually benchmarked.
