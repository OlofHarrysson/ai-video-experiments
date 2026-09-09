# Repeated repainting and accumulated image loss

Research and controlled validation, 2026-09-09. [Experiment](../../apps/deforum/projects/modern-model-study/experiments/repaint-diagnosis.md).

## Why a restart is different from more sampling steps

The current loop is: previous 8-bit PNG → optional pixel warp → VAE encoding → fresh sampling noise → partial denoising under the prompt → VAE decoding → next 8-bit PNG. Each repaint completes its own schedule. Restarting adds noise again; it does not continue an unfinished denoising trajectory. A stable-looking endpoint is also not necessarily a high-quality endpoint.

[SDEdit, the authors' explanation](https://sde-image-editing.github.io/) describes noising an input and running a reverse generative process to balance faithfulness and realism. This supports the mechanism, not a guarantee of monotonic improvement under repeated reuse. A denoiser models a generative distribution rather than an image-specific scalar aesthetic objective. With new noise each cycle, there is no reason to expect a single fixed picture; even a hypothetical ideal stationary distribution would not mean every sample improves on the previous one. This last distinction is a mathematical interpretation, not a claim that our practical loop samples an exact stationary distribution.

## Candidate sources of degradation

- **Resampling:** interpolation when repeatedly moving pixels can remove high-frequency detail, especially under local shrinkage. A single warp of the original to the final coordinates does not compound the same interpolation losses, but cannot replace the evolving feedback image without changing the animation concept.
- **Encoding/decoding:** latent representations reconstruct images approximately. The [latent diffusion paper](https://arxiv.org/abs/2112.10752) explicitly studies the tradeoff between compression and detail preservation. Our actual Qwen VAE must be tested; this paper does not measure its error.
- **Repainting drift:** the model is asked to reinterpret each altered/noised picture. The prompt does not specify every original contour or pixel, and small structural, color and texture changes can feed into the next cycle.
- **Low-noise recipe suitability:** [Krea's official repository](https://github.com/krea-ai/krea-2) describes Turbo as an eight-step distilled checkpoint for fast text-to-image. The [official ComfyUI tutorial](https://docs.comfy.org/tutorials/image/krea/krea-2) uses eight steps for full generation. These sources do not validate repeatedly applying the tail of a longer schedule to self-generated images. Distillation or schedule mismatch is a hypothesis to test, not an established cause.
- **Storage precision:** PNG is lossless relative to its stored 8-bit pixels. Decoding a float tensor, converting it to 8-bit and encoding it again can still lose information. Do not describe this as JPEG-like compression.

## Remedy decision order

First measure the no-motion repaint and VAE controls, then compare repeated warps. If resampling dominates, improve resampling/coordinate handling while retaining the generated anchor. If VAE round trips dominate, consider retaining latent/float state or fewer conversions; latent-space motion is a separate experiment and does not automatically match pixel-space deformation. If denoising dominates, verify schedule/timestep support and test a suitable Krea recipe before another broad denoise sweep. A non-distilled Krea checkpoint is one potential comparison, requiring its own opening and controls; it is not proven superior for animation.

Finishing/upscaling and external reference conditioning may help final appearance, but do not by themselves diagnose or fix accumulated feedback errors. Neither is added to the current diagnostic. A workflow that maintains appealing detail across many repaints remains the practical objective; no setting can guarantee aesthetically good output on every frame.

## Pinned implementation checks

At ComfyUI commit `12d5279438bfefc058a269eae805ceab6047777f`, [Krea configuration](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/supported_models.py#L1928) sets shift 1.15. [KSampler](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/samplers.py) builds `int(steps / denoise)` intervals and takes the last `steps + 1` sigmas. Executing that schedule on the Pod gives start sigma **0.259758** for denoise 0.10 and **0.583973** for 0.30, with eight actual intervals in each. These are latent noise coefficients, not percentages of visible image replacement. The longer schedule's low-noise tail is distinct from simply continuing a finished render.

[SaveImage](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/nodes.py#L1692) scales the decoded float image by 255, clips and casts to uint8 before PNG storage. Our VAE control therefore includes that quantization. [OpenCV's transformation documentation](https://docs.opencv.org/4.13.0/da/d54/group__imgproc__transform.html) distinguishes bilinear interpolation from Lanczos interpolation over a larger neighborhood. Local comparison demonstrates different accumulated detail retention; a larger edge metric alone does not prove better quality and can also reflect ringing.


## Controlled findings

The [completed experiment](../../apps/deforum/projects/modern-model-study/experiments/repaint-diagnosis.md) confirms visible degradation in this recipe without motion. Repaint 0.10 loses contrast and becomes hazy across 24 cycles; 0.30 simplifies the scene into flatter decorative shapes. VAE-only recurrence develops artifacts too. A core-node float-tensor VAE control still develops artifacts and brightens more, so 8-bit PNG conversion is not a sufficient explanation or the obvious remedy.

Repeated bilinear warps visibly blur fine structure independently. Lanczos preserves more in the local control, but the matched repainting animation shows only a partial improvement. The subsequent latent diagnostic carries sampled latents between repaints with no motion, encoding the opening once and decoding for observation only. It preserves feedback and removes repeated VAE encoding, but the main flattening persists; see the follow-up below. No latent-motion or model replacement has been implemented.


## Distillation hypothesis and accepted follow-up

Olof selects Lanczos for future spatial warps and approves the [no-motion latent-feedback diagnostic](../../apps/deforum/projects/modern-model-study/experiments/latent-feedback.md). His suggestion that few-step training may affect recurrent repainting is plausible and remains untested as a causal explanation. [Progressive distillation](https://arxiv.org/abs/2202.00512) demonstrates learning fewer sampler evaluations from a teacher; this is relevant background, not evidence that Krea uses that exact method. [Krea's official model description](https://github.com/krea-ai/krea-2) distinguishes its eight-step Turbo checkpoint from undistilled RAW. Modern architecture and distillation are separate choices.

The model does not perform an explicit aesthetic-completeness check and skip scheduled work. Noise/timestep conditioning and the sampler determine the updates. Low-noise reuse of a distilled recipe may behave differently from its supported full-generation trajectory, but the current representation-reuse test cannot establish whether distillation is responsible. Repeated VAE and resampling artifacts already measured are separate evidence.


The [completed latent comparison](../../apps/deforum/projects/modern-model-study/experiments/latent-feedback.md) reproduces flattening without repeated VAE encoding. Both first repaints exactly match the RGB controls. The next proposed comparison targets the sampler schedule: the verified eight-step full schedule ends with sigma 0.311 then zero, whereas our 0.10 recipe starts at 0.260 and makes eight updates below that. Compare schedule construction with a matched starting noise coefficient before attributing the result to distillation or building latent-space motion. This remains an unexecuted proposal.
