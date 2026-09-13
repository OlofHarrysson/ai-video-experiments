# Noise, sampling steps and continuity between paintings

Checked 2026-09-13 against the recorded correlated-noise experiment, its executed workflow, pinned ComfyUI source and targeted inversion papers. This is an explanation and research proposal; no new inference or architecture change was performed.

Olof likes the [correlated result's mosaic colors](../../apps/deforum/projects/modern-model-study/experiments/correlated-noise.md) as a possible future effect. He agrees it misses the present aim: preserve incidental detail more closely during unchanged prompts, while allowing deliberate transformations.

## The current loop

```text
previous painting (RGB)
  → spatial warp when enabled
  → VAE encoder → clean image latent z
  → mix with initial noise ε at the selected starting level
  → three Euler updates, conditioned on the text
  → VAE decoder → next painting (RGB)
  → repeat using this new painting
```

The stationary comparison disables the spatial warp. It has four paintings per second, three model/sampler updates inside each new painting, and a 24 fps delivery. RIFE supplies intermediate delivery images afterward and never feeds the generator. A warp-only or interpolated video frame does not trigger another noise draw.

The current feedback connection already passes through latent space: the previous painting's encoded values initialize sampling. What is not carried directly between paintings is the sampled latent tensor or its entire denoising trajectory. Those are decoded to RGB, saved, and re-encoded for the next painting. The single-image model does not receive a sequence of earlier frames or persistent temporal hidden state.

## Three tensors with the same shape, different meanings

| Symbol | Meaning | How we obtain it |
| --- | --- | --- |
| `z` | Encoded image content | VAE encoding, followed by the model's latent normalization |
| `ε` | Initial random perturbation | Gaussian pseudorandom samples, or the tested correlated sequence |
| `xσ` | Noisy sampling state | Initial image/noise mixture, then successive model-driven updates |

An image latent is not a noise code. These arrays can have matching dimensions without representing the same thing. Likewise, a seed is a compact instruction for reproducing a pseudorandom draw; it is not an image description or a separate model input carrying meaning.

For the 1536×1024 city paintings, the [actual recorded noise](../../apps/deforum/projects/modern-model-study/exports/correlated-noise-v001/diagnostics/independent/0000.json) has shape:

```text
[batch, channels, temporal slots, height, width]
[    1,       16,              1,    128,   192]
```

That is **393,216 values**. The spatial grid is eight times smaller along each image dimension. The 16 channels are learned latent features, not RGB colors, named objects or independent editable layers. Spatial positions relate to image regions, but decoding mixes features and neighboring positions; a latent cell is not an isolated 8×8 pixel tile. The singleton temporal axis is a tensor-format detail here, not memory of previous paintings.

The baseline noise generator draws approximately independent `N(0,1)` values across this array. Values can be negative or positive and are not restricted to [-1,1]. Mean zero and standard deviation one describe the distribution, not exact requirements for each finite draw. [Pinned noise-generation source](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/sample.py).

The displayed noise movies show **actual channel-zero slices**, enlarged and mapped to grayscale: -3 is black, 0 is middle gray, +3 is white. Values outside that range are clipped only for display. They are real noise values, but show only one of the sixteen channels. The separately decoded noisy-latent images are approximate diagnostic visualizations; decoding a noisy latent does not reveal a literal picture that the denoiser sees. See [diagnostic construction](../../apps/deforum/projects/modern-model-study/experiments/correlated_noise_review.py).

## Randomness is introduced once per painting in our Euler path

Our Krea adapter uses ComfyUI's `CONST` flow parameterization. With its default noise scale, initialization is:

`xσ = (1 − σ) z + σ ε`

At the tested starting level, `x0.6 = 0.4 z + 0.6 ε`. Here `z` means the model-normalized latent, not the raw array saved for diagnostics. These are latent coefficients, not percentages of visible pixels retained or destroyed. Increasing the starting level changes both the mixture and where sampling begins. [Pinned mixing rule](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_sampling.py), [Krea adapter](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_base.py).

Our [executed recipe](../../apps/deforum/projects/modern-model-study/experiments/correlated_noise.py) uses:

| Update | Sampling level before → after | Fresh random noise inside this update |
| --- | --- | --- |
| 1 | 0.600000 → 0.512844 | None |
| 2 | 0.512844 → 0.310901 | None |
| 3 | 0.310901 → 0 | None |

Euler asks the model for a prediction from the current state, text and sampling level, then advances the state. In this flow convention that prediction supplies a velocity: `x_next = x + (σ_next − σ) v`. The predictions change as the state and level change. They are not newly sampled Gaussian vectors, and the original ε is not freshly pasted into each update. Its influence is already in the evolving state.

The selected ordinary Euler sampler has default `s_churn=0`; the branch that injects extra random noise is inactive. Ancestral/SDE samplers can inject additional noise during sampling, so the once-per-painting statement is specific to this workflow. [Pinned Euler implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/k_diffusion/sampling.py#L168-L190).

## What the correlated test changed

Index `n` below means a new painting, not an internal Euler update:

`ε_n = 0.85 ε_(n−1) + sqrt(1 − 0.85²) η_n`

`η_n` is a fresh independent Gaussian array; its multiplier is approximately 0.527. This is not an 85%/15% arithmetic blend. The squared coefficients sum to one, preserving marginal variance under the stated independent-innovation assumptions. Both cases start from the same ε and reproduce the same first painting.

The [recorded result](../../apps/deforum/projects/modern-model-study/experiments/correlated-noise.md) verifies adjacent-noise correlation near 0.85, versus approximately zero in the control. Noise standard deviation remains near one. However, added noise also becomes correlated with the current image latent, which was produced using earlier noise. A flattened diagnostic correlation rises to approximately 0.14; the control stays near zero. This is an observation consistent with recurrent reinforcement, not a demonstrated cause of the mosaic appearance. Marginal Gaussian statistics alone do not establish the correct relationship between image and noise.

Smoothly changing one input does not guarantee smooth perceived output. The starting image changes too, and the model's response to that image, the text and the noise is nonlinear. Even unchanged text specifies a family of plausible buildings; it does not impose exact correspondence for each roof or window. Olof's fine-detail ambiguity hypothesis is plausible. Dominant structures often have more surviving cues, but size is not a guarantee of preservation, and this experiment does not isolate object size as the cause.

## Can we tailor the noise?

Yes, at the sampler interface. The question is whether the resulting states remain useful to this model.

| Control | What it changes | Current judgment |
| --- | --- | --- |
| Starting level | Image/noise mixture and sampling interval | Already tested; lower levels preserve more but can lose visual richness |
| Correlation across paintings | Temporal evolution of the initial ε | Tested at 0.85; liked mosaic effect, unsuccessful preservation |
| Spatial noise strength or frequency | Where perturbations act, or their spatial scale | Possible, but changes the prior and is not a direct semantic control; earlier regional-mask artifacts remain relevant |
| Direct sampled-latent feedback | Avoids repeated RGB decode/encode in the feedback path | Previously tested with an older sampler recipe; insufficient by itself |
| Reuse a recorded noisy starting state | Establishes the trajectory that produced a known painting, before perturbing it | Cheapest first diagnostic for our own unmodified generated paintings |
| Inversion | Finds an image-dependent noisy state with a reconstruction objective | Relevant when the original trajectory is unavailable or the image has been warped; requires a Krea-specific feasibility check |

For ordinary generation, use compatible tensor dimensions, model normalization, noise level and a prior close to the expected standard Gaussian. Arbitrary clipping, blur or channel bias changes that prior. Normalizing the mean and variance afterward does not repair all covariance or image-dependence changes. More tailored noise is possible through deliberate optimization or inversion, but is not guaranteed to encode an instruction such as “keep these exact roof shapes.”

A simple blend of two independent Gaussian noise arrays also changes amplitude: a 50/50 blend has standard deviation about 0.707, not one. A normalized mixture can avoid that particular confound. This does not solve perceptual correspondence or recurrent drift. Our tested recurrence already accounted for the marginal-variance issue.

## Encoding, retaining latents and inversion

**Encode the previous image, add some noise, repaint:** this is already our core loop. The encoder returns image features, not the particular noise that generated the image.

**Retain the sampled latent directly:** our [earlier no-motion latent-feedback comparison](../../apps/deforum/projects/modern-model-study/experiments/latent-feedback.md) encoded the opening once and connected 24 sampler outputs directly to subsequent samplers. Both latent and RGB paths still flattened, and Olof saw no large difference. That used an older eight-update low-denoise recipe, not today's three-interval schedule. It neither proves direct latent storage useless nor supports calling it the missing connection that will fix animation. A revisit is possible, but a pure representation swap is a lower-priority hypothesis.

**Recover a noisy state that reconstructs this image:** this is image inversion. It usually uses the generative model, a numerical inversion procedure and sometimes optimization, rather than just one VAE encoder pass. The result need not be the historically original random draw, and exact reconstruction is not guaranteed. A useful inversion establishes a reconstruction baseline before testing small perturbations or text edits.

**Reuse a known generation start:** for our own paintings we can sometimes avoid inversion entirely. Each recorded repaint has its input latent, ε, prompt, sigma schedule and executed graph. Those identify the noisy starting state that generated the output. Replaying that state with the same deterministic sampler and runtime should reproduce that output. This is different from reusing ε with the newly encoded output: the latter changes `xσ` even if ε stays fixed. It is also different from the earlier experiment that retained only the clean sampled latent. Exact repeatability must be checked in the new runtime, not assumed across devices or versions.

A controlled perturbation around a recorded starting state can test local image sensitivity. It is a single-painting diagnostic, not yet a recurrent movie recipe. Reusing one start forever would freeze the frame; using only that start and ignoring subsequent outputs would change the feedback architecture. Do not silently replace the existing previous-painting initialization. Once the output has been spatially warped, the unmodified recorded trajectory no longer reconstructs the desired warped image; inversion or another explicit adaptation would be needed.

Targeted research, not a comprehensive method ranking:

- [RF-Inversion](https://arxiv.org/html/2410.10792v1), ICLR 2025 work, inspected through its initial preprint's introduction, algorithm and evaluation (**partial-full-text**). It constructs image-dependent starting states and controlled sampling for FLUX editing. Its experiments concern image editing and stroke-to-image tasks, not our recurrent Krea animation. It supports the distinction between random corruption and reconstruction-oriented inversion; it does not provide a validated Krea integration.
- [ReNoise](https://arxiv.org/html/2403.14602v1), ECCV 2024 work, inspected through method, convergence discussion, experiments and limitations (**partial-full-text**, initial preprint). It refines approximate inverse steps using repeated model evaluations, with demonstrations on few-step SDXL Turbo and LCM. It also describes a reconstruction/editability tradeoff and model-specific tuning. Its sampler mathematics should not be copied unchanged into Krea's flow sampler.

[Krea's official repository](https://github.com/krea-ai/krea-2) describes Turbo as an eight-step distilled text-to-image checkpoint. Neither the reviewed papers nor that recommendation establishes that our three-interval partial-noise use can be accurately inverted. Inversion can cost extra model evaluations; do not assume one encoder pass or a free new control.

**Interpolate latent states:** potentially useful, but distinguish random ε, clean z and intermediate xσ. Compare compatible states at the same sampling level. Directly blending clean VAE latents may still produce overlapping forms or softened detail; latent space is not automatically a semantic morphing space. Better endpoint reconstruction and correspondence can help make a latent path useful, but smooth numerical changes alone are insufficient. This is separate from RIFE's image interpolation and does not justify removing the feedback loop.

## Proposed next experiment

Status after Olof's follow-up: keep this replay proposal available while comparing simpler options below. Olof prefers to defer mathematical inversion unless its value justifies the complexity. No experiment is selected or started by this discussion.

The earlier proposal is a **single-painting replay and perturbation test**. We already know a sampling state that produced one of the recorded city paintings. That gives a cheaper controlled starting point for Olof's idea than building an inverter.

1. Reproduce one recorded painting from its saved input latent and ε, with its exact model, prompt and three-interval schedule. This is a zero-change control. Keep the independent-noise repaint of that painting as the existing comparison. If supplying a pre-mixed noisy state directly, account for model normalization and avoid applying the initial mixing rule a second time.
2. Perturb the known start by a few small amounts along one fixed direction, with unchanged text. Inspect roof/window crops, palette, shading and composition as well as numerical differences. This asks whether controlled latent changes give useful nearby images; it does not establish a semantic direction or temporal stability over many recurrences.
3. If useful, align on how to carry that information between actual recurrent repaints before making a movie. Keep each preceding painting as the feedback source; any additional trajectory state and its relationship to the spatial warp must be explicit. No fixed-anchor redraw sequence should be presented as a replacement Deforum loop.
4. Keep inversion as the next feasibility question for reconstructing arbitrary or warped previous paintings. Audit a candidate against Krea's velocity prediction and schedule, test reconstruction before editing, and include a VAE-only control. Do not silently import a FLUX-specific node, switch models or expand tooling to make it run. Useful reconstruction and useful editability must both be demonstrated before longer recurrent tests.

This is a proposed experiment awaiting alignment, not an implementation commitment. Preserve the existing independent-noise recipe and liked mosaic branch. The practical unknown is whether preserving and carefully changing a generation trajectory gives useful control with Krea Turbo—not whether arrays in latent space can be connected at all.

## Follow-up: samplers, temporal slots and very low noise

Checked 2026-09-13 in response to Olof's annotated questions.

**Opening versus later paintings.** Our normal opening starts from random noise and text. Every subsequent recurrent painting starts from the VAE-encoded previous painting, after the configured spatial warp, plus initial noise and text conditioning. Image initialization is the content being repainted. Optional reference-image conditioning supplies additional guidance through a separate model/adapter path. It is not required for image initialization. Olof explicitly says he had not realized we encoded the previous image; do not infer that earlier explanations were understood. Communication record: AF-20260913-225854.

**Sampler history and official preference.** The completed [alternative-sampler comparison](../../apps/deforum/projects/motion-guide-study/experiments/samplers.md) used SDXL: DPM++ 2M, Euler and Euler ancestral. The Krea experiment runners and reports checked here use Euler; no completed alternative-sampler audition with the current Krea recipe was found. Step-count and sigma-schedule tests are not sampler comparisons. [Krea's reference sampler](https://github.com/krea-ai/krea-2/blob/main/sampling.py) implements Euler, and its [recommended Turbo settings](https://github.com/krea-ai/krea-2#turbo-oss_turbo) are eight steps, guidance disabled and shift `mu=1.15`. Disabled guidance means ComfyUI CFG1. Our partial three-interval recurrent use remains an experimental adaptation.

ComfyUI exposing other samplers does not make them vendor-endorsed Turbo recipes. A bounded deterministic Heun audition is possible at the adapter level: it corrects an Euler prediction using a second model evaluation. At our three intervals ending in zero, the inspected implementation uses five model evaluations versus Euler's three. Greater numerical accuracy does not guarantee better artwork from a distilled checkpoint. Euler ancestral has a flow-specific implementation but adds stepwise randomness, so it is a lower-priority preservation hypothesis. These are source-level candidates, not verified Krea renders. [Pinned sampler implementations](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/k_diffusion/sampling.py#L215-L272).

**A second temporal slot is not video memory.** The pinned Krea adapter's `_forward` reshapes a five-dimensional input from `(B,C,T,H,W)` into a four-dimensional batch before the image transformer. It does not create attention across successive frames as a video sequence. Its official sampling path uses ordinary spatial image latents. Simply increasing T is not a supported way to condition a repaint on two previous frames, and other tensor dimensions/conditioning may cease to match. An extra image can instead enter through a compatible reference-conditioning pathway; our [earlier adapter experiment](../../apps/deforum/projects/modern-model-study/experiments/additive_reference.md) tried that with a weaker opening and older settings, so it is not evidence for current-recipe improvement. [Pinned adapter](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/ldm/krea2/model.py#L263-L295).

**Literal starting sigma 0.1.** Initialization becomes `0.9 z + 0.1 ε`, with stronger retention of the encoded signal. Smaller visible changes are a reasonable expectation, not a guarantee of exact detail preservation. The mixing formula does not inherently flatten the image. Repeated encoding/resampling and repeated model reinterpretation can accumulate errors; earlier direct-latent results show VAE conversion is not the sole explanation. Low-noise partial sampling of Turbo is also outside the official full-generation recipe. Which mechanism dominates remains unresolved.

The old [denoise 0.10 study](../../apps/deforum/projects/modern-model-study/experiments/krea-low-repaint.md) used an eight-update schedule selected through ComfyUI's denoise fraction; it was not literal starting sigma 0.10. The later [explicit sigma sweep](../../apps/deforum/projects/modern-model-study/experiments/prompt-noise.md) reached 0.30. Do not present either as a completed current-recipe sigma-0.10 test. A new very-low-sigma test must scale the remaining schedule too, keeping all intervals descending; setting only the first point below 0.512844 would be incorrect.

**Spatial interpretation.** Olof withdraws the idea that non-spatial noise explains the redraws. The noise array does have spatial height/width. This does not settle his separate hypothesis that fine details have fewer surviving cues after corruption; that remains plausible, with no guarantee that large objects stay fixed.

**Current options, not an approved run:**

1. First establish whether literal sigma0.10/0.20 can preserve a short unchanged-prompt scene with today's three-interval recipe, alongside the sigma0.60 control. Keep Euler, CFG1, repaint frequency and independent noise fixed. If useful, test raising noise only when a prompt transition is intended. Earlier ramps explored this principle at higher holding values; very low holding values remain untested here. This is the assistant's preferred practical next step after the new questions.
2. A matched Euler/Heun audition at the current noise schedule. Report both quality and extra evaluations; do not imply it is officially preferred or expected to fix temporal consistency.
3. The saved-state replay/perturbation diagnostic above, if the priority is understanding local latent sensitivity. It does not yet supply a recurrent motion recipe.

Defer inversion and any video-model/temporal architecture change. Olof asks to reconsider the options before proceeding; no new generation or workflow change occurred.
