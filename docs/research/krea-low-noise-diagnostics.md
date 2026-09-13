# Krea Turbo: low-noise repaint and nearby-noise diagnostics

Research checked 2026-09-13. Source inspection and a proposed test design only; no inference or implementation. This note is the sole edited file. GPU execution and integration belong to the main agent.

**Recommendation:** the main agent's prepared stationary sigma0.10/0.20/0.60 and VAE-only controls address the practical question. If a low-noise branch visibly degrades, add one matched direct-latent diagnostic before attributing that degradation to the sampler. Keep the optional opening-noise demonstration separate from recurrent filmmaking.

## Main-agent handoff

The main agent reports preparing 15 recurrent updates per branch, including a Heun control. No result is implied by that preparation. The four-cycle design below is an economical screening alternative, not a request to replace that prepared plan. Within the 15-update runs, inspect cycles 1, 4, 8 and 15 to distinguish early stability from accumulated drift.

For Heun, match its starting level and exact intermediate levels to an Euler branch. At three intervals ending in zero, the pinned implementation takes five model evaluations versus Euler's three: 75 versus 45 over 15 repaints. A difference tests sampler recipes; greater numerical accuracy need not improve this distilled model's imagery. [Pinned Heun implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/k_diffusion/sampling.py#L243-L272).

The proposed four-opening test is useful: native full-eight-step baseline, exact advanced-sampler parity using the same noise, one correlated-noise opening at `rho=0.98`, and a fresh `seed+1` opening. Hold text, schedule, model, latent dimensions and precision fixed; verify actual supplied tensors through the existing recorded-noise path. Stop interpreting perturbation effects if native/advanced parity fails. Four openings cost 32 denoiser evaluations, excluding any retry.

Construct the correlated tensor as `ε' = 0.98 ε + sqrt(1 − 0.98²) η`, with independent Gaussian `η`. The innovation coefficient is about 0.199, and expected RMS displacement from the baseline is `sqrt(2 − 2 rho) = 0.20` per standard-normal coordinate. Thus rho0.98 is a meaningful nearby-noise example, but not an infinitesimal perturbation. Large image differences would not disprove continuity at smaller distances. A fifth, closer point is only worth considering if that ambiguity matters. The fresh-seed opening is an independent-noise comparison, not another nearby-noise level.

These openings are independent diagnostics of a known generation start. Even successful same-noise replay does not imply that re-encoding its output and adding that same noise will preserve it recurrently. No inversion or new temporal architecture follows from the demonstration.

## What is established here

These findings come from the repository's recorded experiments and their linked verification artifacts. This research pass read the reports and relevant graph builders; it did not independently replay inference or re-review the archived videos.

| Local evidence | Established finding | Limit on interpretation |
| --- | --- | --- |
| [Repaint diagnosis](../../apps/deforum/projects/modern-model-study/experiments/repaint-diagnosis.md) | Twenty-four stationary RGB feedback cycles lost contrast and material depth. VAE-only recurrence produced reconstruction artifacts, including without intermediate PNG conversion. PNG save/load alone preserved uint8 pixels. | The old `denoise=0.10` was a schedule-selection fraction, **not starting sigma 0.10**. The report cannot establish current-recipe low-sigma behavior. |
| [Latent feedback](../../apps/deforum/projects/modern-model-study/experiments/latent-feedback.md) | Encoding once and carrying sampled latents directly still flattened under the older eight-update recipe. First-cycle RGB and latent outputs matched exactly. | Repeated VAE encoding is not necessary for that failure. Initial encoding and observation decoding remain; the relative contribution of reconstruction in RGB feedback is unresolved. |
| [Turbo schedule](../../apps/deforum/projects/modern-model-study/experiments/turbo-schedule.md) | At the same start, sigma 0.3109010756, one Euler interval retained more broad shading than eight subdivided intervals after repeated latent feedback. Both degraded. | More evaluations were not automatically better for this checkpoint. This changed step count and intermediate levels together; it did not isolate distillation as a cause. |
| [Correlated noise](../../apps/deforum/projects/modern-model-study/experiments/correlated-noise.md) | Current sigma0.60/three-interval city feedback still changes roofs with unchanged text. Noise correlation 0.85 produced a liked mosaic style but poorer preservation. Noise amplitude stayed near one; first paintings matched. | One scene and correlation setting. Increasing noise–input-latent correlation is consistent with reinforcement, not proof of its cause. |

The [current continuity note](noise-and-latent-continuity.md) correctly distinguishes opening generation, encoded previous-image initialization, random noise and sampled state. Literal sigma0.10/0.20 with today's proportional three-interval schedule remains untested in the evidence reviewed here. Historical denoise labels must not be reused as literal sigma results.

## Why sigma 0.10 does not imply flattening

For the pinned ComfyUI flow mixing rule, in model-normalized latent coordinates:

`xσ = (1 − σ) z + σ ε`, so `x0.10 = 0.90 z + 0.10 ε`.

This specifies an initial latent mixture, not an image flattening operator, a visible-pixel retention percentage or an instruction to reduce depth. It also changes the starting point of sampling. Smaller perturbations are a reasonable preservation hypothesis, not a guarantee. [ComfyUI CONST implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_sampling.py#L77-L90).

The local pipeline repeatedly applies a reconstruction and generation map. Neither the VAE round trip nor the complete repaint map is constrained here to return the same roof geometry, preserve contrast or improve quality on every application. Small biased changes can accumulate; a model may also redraw detail rather than blur it. These are mechanism hypotheses, not a demonstrated explanation of every local artifact.

With ordinary Euler and churn disabled, sampling introduces no further Gaussian draws inside a painting. The model predicts an update from the current noisy state, sampling level and conditioning. Determinism therefore does not make repainting the identity operation. [Pinned Euler implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/k_diffusion/sampling.py#L168-L190).

**Model-specific boundary:** Krea recommends Turbo for eight-step text-to-image generation with guidance disabled and shift 1.15. That recommendation does not validate recurrent partial-noise editing, nor establish that low sigma must fail. [Official settings](https://github.com/krea-ai/krea-2#turbo-oss_turbo).

Krea's technical report now provides more specific primary evidence than the older latent-feedback note: it describes simultaneous guidance/timestep distillation using **Trajectory Distribution Matching (TDM)**. That supports schedule sensitivity as a reasonable question; it does not prove distillation caused our flattening, identify a minimum usable sigma, or show that the proportional low-noise schedule is a trained operating point. The report's separate discussion of flat-background artifacts during pretraining is likewise not evidence for the cause of this recurrent failure. [Technical report, timestep distillation section](https://www.krea.ai/blog/krea-2-technical-report).

## Why identical text can change roofs

The prompt specifies plausible scene content, not exact roof coordinates and window identities. Each repaint supplies a newly encoded image and a new Gaussian draw; its starting state changes even when text stays fixed. Spatial image cues remain, but this interface supplies no explicit correspondence constraint requiring a particular roof to survive. The pinned Krea image adapter processes image tokens; its singleton temporal dimension does not provide a history of preceding frames. [Krea adapter](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/ldm/krea2/model.py#L263-L295).

ComfyUI CFG1 still uses the positive text prediction; it removes additional classifier-free amplification. Turning off extra guidance does not turn off the prompt. [CFG implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/samplers.py#L537-L568).

Fine architectural details may have fewer robust surviving cues than broad masses, making alternate interpretations easier. That is plausible, but neither an object-size law nor an isolated finding from our tests. Fresh-noise perturbation, reconstruction errors and the learned update can interact. Avoid claiming that the model deliberately decides a roof needs improvement.

## Small staged experiment for the main agent

### A. Four recurrent cycles per branch

Use the exact saved city opening and unchanged prompt from the correlated-noise experiment. Each branch starts from that same RGB file; each subsequent cycle consumes **its own immediately preceding output**. Disable all motion, reference conditioning and blending. Keep Krea Turbo assets, runtime, precision, resolution, Euler and CFG1 fixed. Keep independent noise across cycles and use the same actual noise tensor at matching cycle indices across the three sampler branches.

Scale the entire current sigma list by `start / 0.6`, as in the existing [proportional-schedule helper](../../apps/deforum/projects/modern-model-study/experiments/prompt_noise.py). Rounded values below are for review; preserve full evaluated values in execution receipts.

| Branch | Exact operation / displayed sigma list | Four-cycle work |
| --- | --- | --- |
| VAE-only | Previous uint8 RGB → same VAE encode → decode → same uint8 PNG checkpoint | 4 VAE round trips; zero denoiser evaluations |
| Literal 0.10 | `[0.10, 0.085474014282, 0.051816845934, 0]` | 4 repaints; 12 denoiser evaluations |
| Literal 0.20 | `[0.20, 0.170948028564, 0.103633691867, 0]` | 4 repaints; 12 denoiser evaluations |
| Current 0.60 | `[0.60, 0.512844085693, 0.310901075602, 0]` | 4 repaints; 12 denoiser evaluations |

This screen is **12 generated repaints plus 4 reconstruction cycles**, ordinarily 16 single-cycle requests on the current PNG-feedback path, and 36 denoiser evaluations. Do not describe a bundled graph as reducing inference work. In particular, chaining float IMAGE nodes to save requests would change the intended RGB checkpoint control.

For fewer new requests, reproduce the first archived independent-noise sigma0.60 repaint. Only if pixels, graph settings, opening and noise match, reuse its archived cycles 2–4 as the historical control: **9 fresh repaints plus 4 VAE cycles**, 13 requests and 27 denoiser evaluations. If parity fails, use all four fresh control cycles; do not diagnose quality against a mismatched runtime. Archived VAE controls use a different cathedral input and cannot replace the city control.

Review original and cycles 1–4 directly: fixed roof/window crops for geometry, broad arches/dunes for shading, palette and overall composition. Report shape replacements separately from softened edges, contrast loss and checker artifacts. RGB difference and contrast statistics can support those observations; high-frequency energy alone can reward ringing or noise.

Four cycles are a one-second recurrence screen at four paintings/sec, not evidence of long-term stability. If a candidate is promising or inconclusive, extend only that candidate, sigma0.60 and VAE control to cycle 8; extend further only for a stated unresolved question. A branch should not win merely because it freezes detail while losing shading. Review raw paintings first; any playback remains 24 fps, with RIFE afterward and never in feedback. State the final hold explicitly when including opening plus four repaints.

### B. Separate reconstruction from sampling when needed

VAE-only is a **round-trip reconstruction control**, not an encoder-only measurement. It includes decoding, finite precision and the production uint8 checkpoint. Differences between it and the sampled RGB branch are not additive causal percentages: their inputs diverge and their errors interact.

If a low-sigma RGB branch degrades, use one additional four-cycle **direct sampled-latent chain** at that same sigma. Encode the identical opening once, match the four noise tensors and schedule, and decode only copies for review. This preserves recurrent generated-state feedback as a diagnostic; it adds no motion or production architecture. The old [latent graph](../../apps/deforum/projects/modern-model-study/experiments/latent_feedback.py) provides the existing core-node pattern. It is a design reference, not a runner to invoke unchanged with its old denoise settings.

This costs four more repaints / 12 model evaluations, potentially in one chained request. Require the first decoded repaint to match the RGB branch before interpreting later divergence.

- If both RGB and direct-latent chains flatten, repeated encode/decode is unnecessary for that observed failure. Sampling/model dynamics remain implicated, with the initial encode and inspection decoder still present; this does not isolate numerical integration from the learned model or prove a distillation cause.
- If direct-latent feedback retains shading while RGB fails, repeated reconstruction or its interaction with sampling matters at this recipe. That supports a targeted representation investigation, not a production latent-warp change.
- If VAE-only develops similar artifacts, reconstruction is a demonstrated contributor candidate. It still cannot explain how much of the sampled branch's failure it causes.

If tensors are already captured, compare each sampled latent with its decode→uint8→re-encode result in consistent latent units. This measures a round-trip residual; it does not identify encoder loss alone. Avoid adding capture infrastructure merely to complete the first screen.

## Optional: same opening noise versus nearby noise

This is a useful bounded demonstration of **local generator sensitivity**, not a fix for recurrent repainting. A true text-to-image opening starts from noise and text; recurrent repaints instead start from the encoded previous painting mixed with noise. Keep those two questions visibly separate.

Use the same Krea Turbo checkpoint, prompt, dimensions and runtime, with its full eight-step opening schedule. Preserve one actual Gaussian tensor `ε0` and one independent direction `η`. Define:

`εα = (ε0 + α η) / sqrt(1 + α²)`.

For independent standard Gaussians this preserves the marginal variance. Its expected correlation with `ε0` is `1 / sqrt(1 + α²)`; no empirical renormalization, clipping or smoothing is needed. Use one direction for both perturbations so their magnitudes are comparable.

Generate **four openings**: `ε0`, an exact repeat of `ε0`, `ε0.01`, and `ε0.05`. This is 32 denoiser evaluations at eight steps, ordinarily four requests. First check repeatability; if the unchanged-input pair differs materially, stop interpreting smaller changes until that confound is understood. Record actual tensor hashes, correlation and RMS displacement after the runtime's dtype conversion. The two expected correlations are approximately 0.99995 and 0.99875; these are noise statistics, not predicted image similarity scores.

An integer seed increment selects another pseudorandom draw; adjacent integers do not specify nearby tensors. Use the actual tensors, not `seed + 1` as the perturbation. [ComfyUI noise construction](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/sample.py#L8-L34).

Inference from the finite Euler computation: nearby starting arrays can yield nearby outputs, but nonlinear amplification and finite precision can make the useful perceptual scale narrow. The test measures that scale for one opening and one direction. It does not establish semantic control, monotonic change in roof shape or stable behavior under repeated RGB feedback. Krea's official sampler starts from Gaussian noise and performs conditioned Euler updates; it supplies no recurrent-preservation guarantee. [Reference sampler](https://github.com/krea-ai/krea-2/blob/main/sampling.py).

If reusing an archived opening, first verify that its exact generation inputs are available; a PNG and a seed alone do not establish cross-runtime parity. Reusing a recorded **partial-noise repaint** start is an alternative three-interval diagnostic, not text-to-image: hold its original encoded parent fixed and perturb its recorded noise. Reusing that noise with the newly encoded output changes the start and will not replay the same image. No inversion is required for either known-start probe.

Keep the opening demonstration optional and bounded. Proceed with the low-sigma recurrent screen first if the practical question is whether unchanged backgrounds can hold their geometry and shading. None of these proposed checks selects a new production setting or authorizes runner changes.
