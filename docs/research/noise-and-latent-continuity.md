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

Prioritize a **single-painting replay and perturbation test**, before building an inverter, another noise-correlation sweep or a long movie. We already know a sampling state that produced one of the recorded city paintings. That gives a cheaper controlled starting point for Olof's idea.

1. Reproduce one recorded painting from its saved input latent and ε, with its exact model, prompt and three-interval schedule. This is a zero-change control. Keep the independent-noise repaint of that painting as the existing comparison. If supplying a pre-mixed noisy state directly, account for model normalization and avoid applying the initial mixing rule a second time.
2. Perturb the known start by a few small amounts along one fixed direction, with unchanged text. Inspect roof/window crops, palette, shading and composition as well as numerical differences. This asks whether controlled latent changes give useful nearby images; it does not establish a semantic direction or temporal stability over many recurrences.
3. If useful, align on how to carry that information between actual recurrent repaints before making a movie. Keep each preceding painting as the feedback source; any additional trajectory state and its relationship to the spatial warp must be explicit. No fixed-anchor redraw sequence should be presented as a replacement Deforum loop.
4. Keep inversion as the next feasibility question for reconstructing arbitrary or warped previous paintings. Audit a candidate against Krea's velocity prediction and schedule, test reconstruction before editing, and include a VAE-only control. Do not silently import a FLUX-specific node, switch models or expand tooling to make it run. Useful reconstruction and useful editability must both be demonstrated before longer recurrent tests.

This is a proposed experiment awaiting alignment, not an implementation commitment. Preserve the existing independent-noise recipe and liked mosaic branch. The practical unknown is whether preserving and carefully changing a generation trajectory gives useful control with Krea Turbo—not whether arrays in latent space can be connected at all.
