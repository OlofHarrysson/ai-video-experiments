# Krea 2 Turbo controls for gradual recurrent transitions

Research checked 2026-09-13 against official Krea source/cards, ComfyUI commit `12d5279438bfefc058a269eae805ceab6047777f`, and current project code/notes. This note records source inspection and theoretical recommendations. The separate [transition-ramp experiment](../../apps/deforum/projects/modern-model-study/experiments/transition-ramps.md) records execution and visual evidence.

**Keep ComfyUI CFG 1. Use the completed noise-ramp study to choose pacing, then test descriptive intermediate scene prompts.** External CFG is executable but outside the recommended Turbo recipe; it is not an established way to make these transitions gradual. Manual sigmas already specify our sampling times, so changing a schedule-shift setting alone would not change this runner's numerical path.

## Exact recipe and scope

The official Turbo recommendation is eight steps, external CFG disabled, and fixed timestep-shift `mu=1.15`. The CLI example uses `--checkpoint oss_turbo --steps 8 --cfg 0.0 --mu 1.15`. Turbo is distilled; this recommendation is for image generation, not a validated recurrent partial-noise animation recipe. [Official repository](https://github.com/krea-ai/krea-2), [official Turbo card](https://huggingface.co/krea/Krea-2-Turbo/blob/main/README.md).

Our [repaint graph](../../apps/deforum/projects/modern-model-study/experiments/ten_dollar.py) uses the existing Krea Turbo FP8 model, Qwen3VL encoder and Qwen Image VAE. Each previous RGB painting is spatially warped, VAE-encoded and supplied to `SamplerCustom` as `latent_image`. Euler, CFG 1 and a fresh reproducible seed accompany each repaint. Three intervals use

`S(p) = (p / 0.6) × [0.6, 0.512844085693, 0.310901075602, 0]`.

This is a custom partial-noise schedule, not the official eight-step run. A new painting arrives every 0.5s; 24fps delivery has eleven RIFE intermediates between paintings. RIFE never feeds generation. Changing sampling intervals within a repaint is different from adding recurrent repaints.

The [completed journey](../../apps/deforum/projects/modern-model-study/experiments/dynamic-journey.md) records a liked film and an assistant preference for the first four new-prompt repaints at 0.60, 0.64, 0.68, 0.70, then 0.64. It does not establish Olof's ranking of the three probes or a universal ramp optimum. The [Oracle comparison](../../apps/deforum/projects/modern-model-study/experiments/oracle-steps.md) found clearer subject development at 0.6/three intervals; nine intervals at 0.4 did not convincingly restore depth. Preserve these as scene-specific evidence.

## Why CLI CFG 0 equals ComfyUI CFG 1

Let `c` and `u` denote positive and negative/unconditional predictions at the same latent and noise level.

| Implementation | Guidance expression | Positive-only value |
| --- | --- | --- |
| Krea reference sampler | `c + g(c − u)` when `g > 0`; otherwise `c` | CLI `g = 0` |
| Ordinary ComfyUI CFG | `u + k(c − u)` | `k = 1` |

Thus `k = 1 + g` translates the **convention**, assuming identical predictions. ComfyUI CFG 0 selects the negative prediction; it does not reproduce Krea CLI CFG 0. Values between 0 and 1 mix toward that negative prediction rather than adjusting previous-image retention. The pinned ComfyUI sampler skips the negative evaluation at CFG 1 unless an extension disables that optimization. [Krea sampler, pinned revision](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/sampling.py), [ComfyUI CFG implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/samplers.py).

This is not a claim of pixel equivalence between frameworks: quantization, encoding, negative conditioning and schedules can differ.

**Our negative branch is explicitly zeroed.** Node 5 in [modern_workflows.py](../../apps/deforum/modern_workflows.py) is `ConditioningZeroOut` applied to the positive conditioning; `repaint_graph` retains it. This zeros the conditioning tensor and supported auxiliary values while retaining other metadata. Zero tensors are not the same as encoding an empty prompt, and a zero-conditioned model prediction is not necessarily zero. At CFG 1 this branch has no ordinary guidance influence. [Pinned zero-out implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/nodes.py).

Krea's reference sampler instead encodes an empty string by default when external guidance is enabled. Consequently, raising our CFG against the zeroed branch is not a complete reproduction of Krea's guided path. [Official sampler](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/sampling.py).

**External CFG is mechanically meaningful, but its benefit on Turbo is unproven here.** ComfyUI accepts it and evaluates both branches; CFG above 1 extrapolates away from the negative prediction. That adds model work and may increase prompt pressure, but does not guarantee literal compliance, smoother change or retained shading. The author recommends disabling it for Turbo. A future small CFG audition would therefore be experimental, with the negative-conditioning definition frozen and documented. Do not transplant RAW/SDXL guidance ranges or describe Turbo as unable to execute CFG. [SamplerCustom inputs and execution](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_custom_sampler.py), [Turbo recommendation](https://huggingface.co/krea/Krea-2-Turbo/blob/main/README.md).

There is also no separate FLUX-style guidance-value conditioning input in the inspected Krea wrapper. A generic guidance-metadata node is not evidence of an effective Krea control. [Pinned Krea model wrapper](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_base.py).

## Controls that must stay distinct

**Starting noise/sigma controls the repaint's initial state.** Krea uses ComfyUI's `CONST` flow parameterization. With its default noise scale, the model-space starting latent is `x_p = (1 − p)z + pε`, where `z` is the processed VAE latent and `ε` is seeded Gaussian noise. It is not simply `z + pε`. Moving from 0.6 to 0.7 reduces the latent coefficient from 0.4 to 0.3 and raises the noise coefficient from 0.6 to 0.7. These are latent coefficients, not percentages of pixels replaced. At 1, the initialization loses its previous-image term; keep proposed recurrent ramps below 1. [Flow initialization and sampling class](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_sampling.py), [Krea class selection](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_base.py).

**A ramp is indexed by repaint, not by internal denoising step.** Start, peak, number of ramp paintings and ramp shape determine the sequence of `p` values. Each `p` rescales all three intervals; it changes initialization and integration boundaries together. Within each repaint sigmas still decrease to zero. A longer ramp can preserve readable intermediates but can also delay the new scene or accumulate degradation. For N paintings 0.5s apart, first-to-last sample spacing is `(N−1)×0.5s`; record their actual timestamps as well as the count. A smooth mathematical ramp does not imply a smooth semantic response.

**Sampling shift redistributes denoising times.** Krea's fixed `mu=1.15` shifts a uniform grid via `exp(mu)/(exp(mu)+(1/t−1))`; its sampler notes that Turbo was trained at this fixed value. The pinned Krea configuration also sets shift 1.15 and selects `ModelSamplingFlux`, whose timestep conversion returns sigma directly. This is not `ModelSamplingDiscreteFlow`'s differently parameterized shift. [Official timestep schedule](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/sampling.py), [Krea configuration](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/supported_models.py), [Flux sampling class](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_sampling.py).

**ManualSigmas bypasses schedule generation.** The node parses the supplied float list; `SamplerCustom` forwards it to sampling. With this graph's fixed arrays, no conditioning ranges or extra patches, changing only the model's shift leaves those sampling times and initialization unchanged. A real schedule experiment must change the emitted sigma array, preferably preserving its starting value, zero endpoint and interval count to isolate internal spacing. [ManualSigmas/SamplerCustom](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_custom_sampler.py). Euler uses those adjacent sigma differences and defaults to no stochastic churn; ordinary Euler does not add another independent noise draw at every internal interval. [Pinned Euler implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/k_diffusion/sampling.py).

**Prompt guidance selects the destination; conditioning blends vary that destination.** Descriptive bridge prompts could progress from shell with buildings, to a hollow architectural shell, to a city passage while keeping material/light language stable. This follows the author's natural-language guidance, but the particular bridge is a project hypothesis. Freeze all text; avoid automatic per-frame prompt expansion. [Official prompting guide](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/docs/prompting.md), [project prompting notes](prompting-for-feedback.md).

An embedding blend `(1−a)E_old + aE_new` differs from CFG extrapolation, changing sigma, concatenating prompts or blending decoded images. Krea exposes twelve Qwen layers flattened into a three-dimensional conditioning tensor; basic arithmetic blending is structurally plausible. It has not been validated for semantic pacing. [Pinned Krea encoder](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/text_encoders/krea2.py). `ConditioningAverage` mixes by token position, truncates/pads unequal lengths and retains destination metadata. Tokens are not semantically aligned; endpoint equivalence, shapes and relevant metadata need checking before relying on this node. [Pinned averaging node](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/nodes.py).

**Correlated noise changes randomness across repaints.** Incrementing an integer seed does not create a gradual noise interpolation. A theoretical unit-variance construction is `ε_n = ρ ε_(n−1) + sqrt(1−ρ²)η_n`, with independent standard Gaussian innovations and `0≤ρ<1`. Under these assumptions adjacent noise fields have correlation ρ; sigma can remain unchanged. This is a proposed controlled variable, not implemented by the current integer `noise_seed` input. Reusing one seed is the fully fixed endpoint, not a general temporal-consistency solution.

PYoCo provides primary evidence for correlated noise in a video model that was trained with such priors, not proof of benefits in Krea Turbo recurrent img2img. [Paper](https://openaccess.thecvf.com/content/ICCV2023/html/Ge_Preserve_Your_Own_Correlation_A_Noise_Prior_for_Video_Diffusion_ICCV_2023_paper.html). For this project, reduced random variation might help continuity or might suppress desired evolution. Correlation on a fixed pixel grid does not follow moving material; warping Gaussian noise with RGB interpolation also changes its statistics. Defer this added machinery until simpler controls are evaluated.

## Practical order and decision evidence

| Priority | Candidate | Useful question and limit |
| --- | --- | --- |
| 1 — completed first sweep | Ramp start, peak, count and shape; settling level remains untested | Can recognizable intermediate forms appear without the first repaint replacing the scene? Hold prompts, seeds, motion, intervals and cadence fixed. |
| 2 | A few frozen descriptive bridge prompts | Can the whole environment change while preserving material depth? Compare with the same selected ramp; do not simultaneously change CFG. |
| 3 | Prompt-conditioning blend | Potential continuous destination control. Requires endpoint/shape checks and a short visual probe; a 50% embedding blend is not a promise of a 50% transformed scene. |
| 4 | Small external-CFG audition near 1, if needed | Could target recognition improve at fixed noise? Explicitly define zeroed versus encoded-empty negative; account for the extra branch. Turbo guidance-free remains the control. |
| 5 | Internal sigma spacing / interval count | Might change reconstruction quality; prior extra-step tests did not recover depth. Compare fixed start/end, not different native tails with different starting noise. |
| Later | Correlated noise | Test only if random repaint variation is the remaining problem. Preserve innovation/noise tensors for reproducibility; do not infer correlation from neighboring seed numbers. |

Compare branches from the exact same saved painting and timestamp. Evaluate painting-level target recognition, intermediate forms, material depth and framing first, then identical RIFE playback for jumps/softness. More prompt compliance with flattened surfaces is not automatically a win. Keep the same model, VAE, recurrent initialization, half-second cadence and finishing while answering one control question at a time.
