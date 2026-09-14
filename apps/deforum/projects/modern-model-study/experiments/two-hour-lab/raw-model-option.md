# Small Krea 2 RAW versus Turbo diagnostic

Research checked **2026-09-14, 16:23–16:28 UTC**. **NO-GO for this session; defer the download and diagnostic.** Native compatibility looks practical, including FP8 on the existing 32 GB GPU, but RAW requires another **13.14 GB** of weights. Free retained-volume space, transfer throughput and RAW execution time are unverified. Preserve the current ComfyUI/Torch runtime and complete the ongoing comparisons and films. This is a scheduling/storage decision, not evidence that RAW cannot run.

Only public primary-source text/metadata and local files were read. No weight payload, GPU job, infrastructure operation, installation, resize or runtime change was performed. This note is the only file written. Proposed settings below have **not** been executed.

**Exact weight candidate**

Use Comfy-Org's repackaged **`diffusion_models/krea2_raw_fp8_scaled.safetensors`**, retaining FP8 for both model arms. The official model repository identifies the RAW and Turbo originals and their common encoder/VAE layout. The pinned Hugging Face API confirms:

| Field | Value |
| --- | --- |
| Repository | `Comfy-Org/Krea-2` |
| Revision | `e5ea8b4dd7f38f348b138eb0fe29f92c0e367e96` |
| Exact size | **13,141,730,784 bytes** = 13.142 GB / 12.239 GiB |
| Published LFS SHA-256 | `48cd5d6c100297968349b41a8e77c6591d1dac18a215807f5f25f59e5c54cd61` |
| ComfyUI destination | `models/diffusion_models/krea2_raw_fp8_scaled.safetensors` |

[Pinned download URL](https://huggingface.co/Comfy-Org/Krea-2/resolve/e5ea8b4dd7f38f348b138eb0fe29f92c0e367e96/diffusion_models/krea2_raw_fp8_scaled.safetensors), [pinned size/hash metadata](https://huggingface.co/api/models/Comfy-Org/Krea-2/revision/e5ea8b4dd7f38f348b138eb0fe29f92c0e367e96?blobs=true), [publisher's file layout](https://huggingface.co/Comfy-Org/Krea-2/blob/e5ea8b4dd7f38f348b138eb0fe29f92c0e367e96/README.md). The hash is publisher metadata, **not a locally verified download**. This is the same repository revision already pinned in `apps/deforum/serverless/modern-models.json` for Turbo and its dependencies.

BF16 is also published at this revision: `diffusion_models/krea2_raw_bf16.safetensors`, **26,283,332,608 bytes**, SHA-256 `f99bb0ff8e362b77342bc4994e0c50906fe7ef7074864b181b7d48d2fa6d03d7`. Its additional storage and memory demands make it unsuitable for this small session diagnostic. No third-party quantization or new quantization node is needed for the FP8 candidate.

**Native runtime path**

Keep ComfyUI **0.34.0 / `12d5279438bfefc058a269eae805ceab6047777f`**, Torch **2.10.0+cu128**, CUDA 12.8. The local session's `system-stats.json` confirms the version/Torch/GPU snapshot; the supplied source pin was inspected upstream. This was not a fresh remote health or free-memory check.

The pinned implementation detects Krea by its tensor keys, uses the same `Krea2`/`SingleStreamDiT` family, and already handles scaled FP8 in the native diffusion loader. Krea's own inference code likewise loads either checkpoint into one architecture. Therefore native compatibility is strongly supported by source, although loading this particular RAW file remains untested. [Model detection](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_detection.py#L970), [scaled-FP8 loader](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/sd.py#L2258), [official common architecture](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/inference.py).

| Component | Frozen/native setting |
| --- | --- |
| Diffusion loader | `UNETLoader`, RAW filename above, `weight_dtype="default"` |
| Text encoder | Existing `qwen3vl_4b_fp8_scaled.safetensors`; `CLIPLoader(type="krea2", device="default")` |
| VAE | Existing `qwen_image_vae.safetensors`; `VAELoader` |
| Conditioning | `CLIPTextEncode` for the unchanged positive and separately encoded empty-string negative |
| Repaint input | `LoadImage → VAEEncode`; previous output from the same arm |
| Sampling | `KSamplerSelect("euler") → SamplerCustom`, `add_noise=True`, explicit `ManualSigmas` |
| Full-generation sanity input | Native `EmptySD3LatentImage`, 1024×1024, batch 1; 16 latent channels |
| Finishing | `VAEDecode → SaveImage`; inspect paintings before any interpolation |

[Native loaders](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/nodes.py#L982), [sampler nodes](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_custom_sampler.py), [16-channel empty latent](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_sd3.py#L40), [official dependency downloads](https://docs.comfy.org/tutorials/image/krea/krea-2#model-downloads).

**Guidance and scheduling: a necessary distinction**

Official RAW recommends **52 full denoising intervals, CLI CFG 3.5, 1024×1024**; Turbo recommends **8, guidance disabled, fixed `mu=1.15`**. [Official recommendations](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/README.md).

Krea computes `conditional + g*(conditional−unconditional)`; ComfyUI computes `unconditional + k*(conditional−unconditional)`. Hence RAW **Comfy CFG 4.5** and Turbo **Comfy CFG 1.0** translate those conventions, assuming identical branch predictions. RAW needs the encoded-empty negative used by the official sampler; the current zeroed branch is a different input. This is one fixed recipe per model, not another negative/CFG sweep. [Krea sampling implementation](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/sampling.py), [Comfy CFG equation and CFG1 optimization](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/samplers.py#L592).

Source-derived RAW schedule at 1024²: latent compression 8, patch 2, image-token count 4096; endpoint counts 256 and 6400 from the official 256/1280 resolution bounds. Thus `mu = 0.5 + 0.65*(4096−256)/(6400−256) = 0.90625`. Apply `exp(mu)/(exp(mu)+(1/t−1))` to a uniform 53-point grid from 1 to 0. The native Krea configuration instead defaults to **1.15**; the generic `ModelSamplingFlux` node's default interpolation endpoints also differ. Simply changing the model filename and setting 52 steps does **not** reproduce the RAW recommendation. [Official VAE dimensions](https://github.com/krea-ai/krea-2/blob/db3984fbc6e13b34c0064990fc2d95ac64d00058/autoencoder.py), [native Krea defaults](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/supported_models.py#L1928), [Flux patch-node endpoints](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_model_advanced.py#L161).

For a future diagnostic, calculate and archive the official float32 grid once, then supply it through existing `ManualSigmas`. This bypasses the shift-default mismatch and `simple` scheduler's 10,000-point table subsampling. There is no runtime patch or scheduler installation. Mathematical schedule/CFG alignment does not establish pixel parity with the official BF16 implementation. [Native schedule table](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_sampling.py#L406), [simple scheduler](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/samplers.py#L645).

**Memory, storage and time feasibility**

Arithmetic from published sizes: RAW FP8 + cached Qwen3VL FP8 + VAE totals **18.638 GB / 17.358 GiB** of serialized weights. This makes a batch-one 1024² run on the recorded **33,685,504,000-byte GPU** plausible. Serialized bytes are not peak VRAM: activations, casts, attention workspaces and CFG batching add memory. No measured RAW peak or speed is available. Both diffusion models plus encoder/VAE total **31.780 GB** before that overhead; execute model arms sequentially under ordinary ComfyUI memory management, only after the ongoing jobs finish. BF16 RAW alone is 26.283 GB, leaving much less headroom.

On disk, the three Krea files plus RAW total **31.780 GB**. If all six files in the canonical Krea/Klein manifest remain, adding RAW totals **47.912 GB**, before runtime, caches, media and scratch. These are conditional sums, not a measurement of the retained 50 GB volume. Require free bytes exceeding the 13.142 GB payload **plus at least 5 GB working reserve**, with no duplicate download cache. Do not resize or delete cached models to force this experiment into today's session.

A 13.142 GB transfer takes about **2.2 minutes at sustained 100 MB/s or 10.95 minutes at 20 MB/s**, excluding hashing/load time; these are arithmetic scenarios, not observed throughput. Any later run needs a measured first RAW repaint and a fresh shared-session budget check. The local session records $0.72/hour: a 20-minute compute reservation is $0.24 before storage, but that is an estimate within the shared $10 cap, not posted billing or permission to add time/resources.

**Bounded future design — maximum 14 image jobs**

Question: *Does RAW under its appropriate recipe show a useful difference in early recurrent partial-repaint degradation compared with Turbo?*

1. After storage/availability checks and the existing work finishing, run one 1024² full-generation sanity image per model with the settings above. Stop on load failure, invalid output, OOM, a required install/restart or excessive offloading. Do not troubleshoot by changing the working runtime. These two images check basic execution, not quality superiority.
2. Select one existing detailed city painting and preserve a single identical 1024² crop as both arms' initial image. Freeze its descriptive prompt, six paired seeds, resolution, VAE path and **zero motion**. Reuse the Turbo-generated source deliberately as an incumbent-preservation screen; acknowledge its possible bias toward Turbo. Each arm produces **six recurrent repaints** from its own previous decoded PNG. No prompt transition, reference LoRA, text blend, noise sweep or step-placement sweep.
3. Fix starting sigma **0.60** in both arms, so the initial mixture is the same `0.4*z + 0.6*noise` for the shared first input. Use the same actual first noise tensor, or verify paired noise equivalence. Later inputs diverge by design. RAW's proposed partial schedule is `[0.60]` followed by the strictly lower points of its official 52-interval grid, including zero: **20 intervals** at 1024². Turbo retains the recorded `[0.6, 0.512844085693, 0.310901075602, 0]`: **3 intervals**. This RAW tail is an experimental img2img adaptation, not an official recurrent recipe. Do not force RAW into three intervals merely to equalize cost. [Native flow initialization](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy/model_sampling.py#L86).
4. Inspect all twelve repaints at full frame and fixed roof/shading crops. Record adjacent change separately from accumulated deviation from the common source, plus retained geometry, edge detail and metallic shading. Smaller numerical change alone is not better preservation or less flicker. Archive exact sigma arrays, conditioning definition, weights/hash, source/parent hashes, seeds/noise evidence, timing and failures. Skip RIFE for the decision; a later playback may hold each painting for 12 frames at 24 fps.
5. Cap execution at **20 minutes**, allowing archival before the governing deadline, with no expansion beyond 14 jobs. Six RAW tails need 240 conditional/unconditional prediction-equivalents, versus 18 for six Turbo tails; RAW's full sanity adds 104, Turbo's adds 8. CFG may batch predictions, so these are work counts, not wall-clock ratios. Proceed beyond the first RAW repaint only if measured time and remaining shared budget support finishing. Otherwise retain the partial evidence and stop.

Interpretation must stay narrow. Krea identifies RAW as the base before further post-training and Turbo as additionally fine-tuned and distilled. This comparison changes checkpoint, recommended guidance and integration grid; matching FP8 format does not eliminate quantization effects. It can motivate a larger RAW study, **not establish that distillation caused the observed Turbo degradation**. Six repaints from one image/seed path cannot establish general stability, convergence of RAW's numerical integration, or better moving/prompt-changing films. [Official model-family description](https://huggingface.co/krea/Krea-2-Raw#model-family-and-release-checkpoints).
