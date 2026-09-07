# Feedback parameters: what this version actually does

Source audit, 2026-09-07. Applies to **Difforum `1d750efd3c1d1dda792b8ef6c14b06a14a69f879`** and **ComfyUI `v0.34.0`** (tag resolved to `12d5279438bfefc058a269eae805ceab6047777f`). These are implementation semantics, not universal animation settings or a new runtime verification. The worker runbook targets this ComfyUI version; individual render diagnostics remain the authority for the deployed runtime.

The [Brain Entity study](../../apps/deforum/projects/brain-entity-study/experiments/style.md) supplies the practical question: v002 is closer to Olof's intention, but loses too much midpoint detail. Its documented recipe uses SDXL base plus the art LoRA, DPM++ 2M/Karras, 30 steps, CFG 7, denoise 0.82, image noise 0.025, sharpen 0.35, LAB coherence 0.25, incrementing seed 7301 and cadence 1. These describe a comparison baseline, not recommended defaults. Model, LoRA, prompt, guide, starting artwork, resolution and camera motion all affect the useful parameter range.

## The two important distinctions

**Image-space noise is explicitly seeded.** The sampler passes `seed + f`; the helper constructs a dedicated CPU generator with `manual_seed(int(seed) & 0x7FFFFFFF)`. It draws a Gaussian `[batch, height, width, 1]` field, shares that field across RGB, scales it by `noise`, adds it to the image and clips to `[0,1]`. This is reproducible random input for the same seed, absolute frame, shape and compatible runtime—not an unseeded source invalidating earlier comparisons. [`add_noise`, lines 44–61](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/detail.py#L44-L61).

There are two seed schedules:

| `seed_mode` | Diffusion noise seed | Image-space noise seed on a diffusion frame |
| --- | --- | --- |
| `fixed` | Base seed | `(base seed + absolute frame) & 0x7FFFFFFF` |
| `increment` | Base seed + absolute frame | `(base seed + absolute frame) & 0x7FFFFFFF` |

Thus `fixed` does **not** freeze all noise between frames. The two fields also have different shapes and purposes; an equal numerical seed does not make them the same tensor. ComfyUI creates the initial latent noise on CPU using `torch.manual_seed(seed)` and passes the seed onward to sampling. [Difforum seed selection](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py#L173-L180), [ComfyUI noise preparation](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/sample.py#L9-L37).

**Same seeds do not prove bit-identical complete renders.** Pin weights, inputs, graph, runtime, precision and device/backend, then measure repeat renders. PyTorch does not guarantee reproducibility across versions or platforms. Difforum's effect runner can also switch from GPU to CPU after an error; preserve that log. Once frames diverge, feedback compounds the difference. This is a reason to measure reproducibility, not evidence that the previous videos were random or invalid. [PyTorch reproducibility](https://docs.pytorch.org/docs/2.14/notes/randomness.html), [Difforum effect device](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/fx.py#L27-L45).

**Previous-frame feedback is not an explicit alpha blend.** The path is previous image → camera warp → optional symmetry → sharpening → image noise → VAE encode → img2img sampling → VAE decode → color correction → next image. There is no control that mixes a percentage of the old frame's pixels into the new frame. Color coherence blends the newly decoded image with a statistics-corrected version of itself; it does not overlay the anchor's objects. [Feedback implementation](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py#L153-L226), [color blend](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/color.py#L63-L91).

## Denoise and steps are different controls

Difforum clamps `strength_schedule.at(f)` to `[0,1]` and passes it directly as ComfyUI `denoise`. It is not an inverted image-retention percentage. In this ComfyUI version, for `0 < denoise <= 0.9999`, KSampler builds a schedule for `int(steps / denoise)` steps, then retains its last `steps + 1` sigma values. Higher values use the full schedule. [Denoise forwarding](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py#L192-L219), [KSampler schedule selection](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/samplers.py#L1431-L1441).

For the study's DPM++ 2M/Karras path:

| Steps | Denoise | Schedule built for | Retained sampling intervals |
| --- | --- | --- | --- |
| 30 | 1.00 | 30 steps | 30 |
| 30 | 0.82 | 36 steps | 30 |
| 30 | 0.55 | 54 steps | 30 |
| 15 | 1.00 | 15 steps | 15 |

Lower denoise selects a lower-noise starting region while retaining the requested interval count. Fewer steps change numerical resolution and work. Therefore 30 steps at denoise 0.5 is not 15 steps at denoise 1.0. At fixed denoise, changing steps also changes the discretized sigma positions; integer truncation means small denoise adjustments can produce the same schedule. These interval counts are not a universal count of model evaluations for every sampler. [Schedule calculation and sampler dispatch](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/samplers.py#L1399-L1441).

Practical interpretation: lower denoise often preserves more of the current input, including its existing simplification; higher denoise gives the model more opportunity to reinterpret it. More steps cannot guarantee recovery of lost linework. Neither parameter means a literal percentage of new pixels. At denoise zero, ComfyUI returns the input latent, but Difforum still performs its warp, effects, VAE round trip and enabled color correction on diffusion frames; zero denoise is not a pixel-identity bypass. [Empty-schedule behavior](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/samplers.py#L1276-L1278).

## Other controls and their practical limits

| Control | Verified behavior | What to look for in this artwork |
| --- | --- | --- |
| `cfg` / `cfg_schedule` | Per-frame schedule overrides the scalar. Standard CFG extrapolates from the negative-conditioned prediction toward the positive-conditioned prediction. CFG 1 uses the positive prediction without the usual negative branch; model patches can change this formula. | Prompt influence, line character and composition can change together. Higher CFG is not a dedicated detail slider. [CFG implementation](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/samplers.py#L592-L629). |
| `noise` | Seeded Gaussian pixel perturbation before VAE encoding, only on diffusion frames. Separate from latent diffusion noise and denoise. The feedback node uses the helper's Gaussian default; its plasma mode is not exposed here. | Can supply texture to repaint, but cannot guarantee meaningful detail. Clipping matters near the study's black/white regions. [Detail helper](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/detail.py#L44-L61). |
| `sharpen` | Unsharp masking with default radius 2 before encoding: amplify the difference from a blurred image, then clip. Applied on every advancing frame, including cadence intermediates. | Accumulated halos or harsh edges may resemble detail without restoring engraved structures. [Sharpen helper](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/detail.py#L19-L28). |
| `cadence` | Diffuses when the absolute frame index is divisible by cadence. Other frames only advance the warped/effected feedback; no VAE, added noise, ControlNet or color match on those frames. | Reduces diffusion work but may introduce visible repaint jumps. It is neither optical flow nor a blend between two generated keyframes. [Cadence branch](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py#L151-L190). |
| `color_coherence` / `color_mode` | Matches channel means/stds to the initial image in LAB or RGB, then blends toward that corrected image. Zero or `none` bypasses correction. | Stabilizes broad palette/brightness, not outlines or object identity. It may resist an intended lighting change. [Color implementation](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/color.py#L54-L91). |
| ControlNet | Positive strength enables conditioning on both positive and negative branches. Hint is the external guide at `f % guide_count`, otherwise the warped image. Strength zero skips this added ControlNet. This does not strip any ControlNet already embedded upstream in conditioning. | A guide can steer structure while competing with desired illustrated complexity; strength is not guide-pixel opacity. Disabling it does not disable previous-frame feedback. [Conditioning attachment](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/nodes.py#L953-L980), [feature scaling](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/controlnet.py#L190-L210). |

The feedback node hardcodes ControlNet's diffusion range to `0.0–1.0`; it exposes no start/end controls or control-strength schedule. The study's still graph uses an end of 0.85, so its ControlNet timing differs from animation. An external guide is resized and selected, not automatically transformed by the feedback camera or converted into an edge/depth map. [ControlNet call](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py#L200-L211), [study graph builder](../../apps/deforum/projects/brain-entity-study/experiments/render.py).

The supplied initial image is output unchanged apart from resizing; sampling begins at the next frame. Continuations retain absolute schedule/seed/cadence indices, but reset the color anchor to their supplied starting image. Consequently a continuation with coherence enabled need not match the corresponding uninterrupted suffix, even with the correct starting pixels. [Initialization and range](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py#L128-L151).

## Applying this in the current study

The subsequent [architecture comparison](deforum-architecture-comparison.md) incorporates Olof’s playback feedback: P06 has clarity but insufficient temporal continuity. It compares missing intermediate-frame synthesis, noise continuity and classical cadence. This parameter guide describes control semantics, not a complete temporal workflow.

The [parameter study](../../apps/deforum/projects/brain-entity-study/experiments/parameters.md) records executed clips and their results. Keep prompts, weights, input files, resolution and camera fixed for each parameter comparison, preserve every result, and judge normal-speed playback alongside matched timestamps. Values below are local contrasts around v002, not transferable defaults.

1. **Guide ablation:** P01 uses the exact archived v002 graph with only `control_strength: 0.4 → 0`. Compare linework, figure retention and flat-region growth near the midpoint. This isolates the graph change; a changed runtime remains a possible confound. v001 versus v002 did not isolate it because denoise also changed.
2. **Repeatability control:** render the same short 12–16-frame prefix twice with actual recomputation, using the same graph/input and runtime. Compare decoded RGB pixels, not MP4 bytes or PNG metadata. Equality establishes repeatability for that tested setup; divergence should be investigated before attributing subtle differences to parameters. Frame zero alone is not a useful check because it is copied from the input.
3. **One-axis repaint test:** from a selected baseline, compare denoise 0.82 with 0.70 at 30 steps, holding everything else fixed. Use the same short interval for both; extend only if useful. This tests the detail-versus-reinterpretation balance. Do not simultaneously change steps, noise, sharpening or CFG. If using a continuation, compare both branches from the same anchor and absolute frame, rather than treating either as an exact v002 suffix.

## Evidence retained

Official source downloads are in ignored `apps/deforum/work/brain-parameters-session/research/`. The downloaded pinned `nodes/sampler_nodes.py` is byte-identical to the existing `apps/deforum/work/ten-experiments-session/upstream-sampler.py`; SHA-256 `95359aa0794243551b087a770edccc973c5b8d3116702edb4c167e21f9150699`. Other inspected files: Difforum `core/detail.py`, `core/color.py`, `core/fx.py`; ComfyUI `nodes.py`, `comfy/sample.py`, `comfy/samplers.py`, `comfy/controlnet.py`. Current official documentation was cross-checked through Context7; exact behavior above comes from pinned source. No claim of measured GPU determinism or newly reviewed playback is made.
