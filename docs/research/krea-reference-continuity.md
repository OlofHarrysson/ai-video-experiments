# Extra reference conditioning for recurrent Krea 2 Turbo

Source audit: 2026-09-13. Research only; no inference, remote-resource inspection, weight downloads, installs, or shared-code changes. Current repository files and public primary sources were inspected. Recommendations below are proposals for the main agent, not validated animation results.

## Recommendation

**Krea 2 Turbo can receive an extra reference image while retaining VAE-encoded previous-image initialization.** The smallest existing-core experiment uses the Ostris style-reference LoRA, `TextEncodeQwenImageEditPlus`, and `FluxKontextMultiReferenceLatentMethod(index_timestep_zero)`. ComfyUI v0.34.0 already implements the reference-token path. No custom-node installation, Python dependency, or warm-process restart is inherently required for this graph.

However, the retained-volume receipts verify only the current three base assets, not the adapter. The style LoRA is pinned in the earlier experiment manifest, and was available during that experiment; this is not evidence that it survived on the retained volume. A main-agent check of its actual availability is needed before a no-download render is possible.

**Expected value:** a small style/reference-continuity audition, with low confidence for background geometry preservation. For a later deliberate-edit investigation, `conradlocke/krea2-identity-edit` v1.2 is more relevant than style transfer or face ReID, but requires its matching custom nodes and a restart. Do not add those to the current bounded diagnostic. None of the reviewed sources establishes a solution to repeated flattening in our three-interval recurrent loop.

## Decision for the main agent's current RTX 4090 session

The main agent is preparing city branches for sigma 0.1/0.2/0.6, VAE-only and Heun 0.6. **A small reference branch fits the existing graph architecture, conditionally on adapter availability and measured memory fit.** Use the Euler 0.6 arm as the reference control; do not pair the new conditioning with Heun or a lower sigma. Keep the same current city opening as a fixed reference.

For the smallest screening test, run A0 versus C on identical input/seed once. If C visibly damages the image, stop. If it offers a useful improvement, run the A1 and B single-step controls below before attributing the effect, and only then consider a 15-repaint C trajectory alongside the already-planned A0 trajectory. Two-arm playback alone establishes the whole recipe's effect, not a reference-image benefit separated from LoRA/template changes.

The additional reference sequence and Qwen3VL vision encoding consume memory and execution time; RTX 4090 fit and runtime are not verified here. Fixed prompt/reference inputs may benefit from Comfy node caching, but do not budget on guaranteed cache reuse across separately submitted graphs. No extra dependencies or restart are needed for the native route. If the 457 MB LoRA is absent, obtaining it is a main-agent scope decision; this audit's no-download permission does not authorize fetching it.

## What the previous tests establish

Local audit targets: [conditioning.py](../../apps/deforum/projects/modern-model-study/experiments/conditioning.py), [additive_reference.py](../../apps/deforum/projects/modern-model-study/experiments/additive_reference.py), and [additive_reference.md](../../apps/deforum/projects/modern-model-study/experiments/additive_reference.md).

- `conditioning.py` alone is **not** the current feedback baseline: its sampler starts from `EmptyLatentImage`. Its reference branch adds the LoRA and replaces the text-encoding route simultaneously. Reference images are carried as conditioning, not sampler initialization. The text-only sequence therefore performs independent redraws, despite constructing warp files locally.
- `additive_reference.py` corrects this: it deletes the empty latent and connects `VAEEncode(anchor.png)` to the sampler. Its extra `reference.png` is the previous painting before warping; each branch subsequently consumes its own prior output. Both branches and their common opening carry the style LoRA at strength 1 and use the same Qwen Edit Plus encoder.
- That comparison controls reference presence **within an adapter-enabled recipe**. It does not isolate the adapter's effect relative to today's ordinary FP8 baseline. Its no-reference opening is outside the adapter author's stated one/two-reference usage.
- Historical Krea uses INT8 ConvRot, 1024×576, eight updates starting near sigma 0.674571, spatial twist, and a two-second sequence. Today's FP8 diagnostic uses stationary images, three explicit intervals from 0.6, and 4 paintings/sec. Historical observations cannot be transferred as matched results.
- The recorded Krea results already show the limitation: reference conditioning did not prevent disappearance of the small explorer or reshaping of the arch; late frames retained some ring/figure definition, but both branches flattened. These are historical, sampled-frame observations, not a fresh visual review or a demonstration that every Krea reference method fails.

## Three distinct image paths

```text
Previous RGB painting -> VAEEncode ---------------------> sampler.latent_image
                                                           |
Fresh independent Gaussian noise + unchanged sigmas --------+-> new painting
                                                           ^
Extra reference RGB -> Qwen3VL vision + prompt -> conditioning|
                   -> Qwen Image VAE -> clean reference tokens
```

The initialized target latent remains the thing being denoised. Reference latents are a separate attention context; they are not blended into that latent or copied onto output pixels. Feeding a fixed earlier artwork as reference can expose detail no longer present in the previous painting, but recovery is a hypothesis. Reusing each latest painting as the reference supplies another representation of an image already drifting; it is not a stable memory of the opening.

In the audited core, `Krea2.extra_conds` maps `reference_latents` into model inputs after latent-format processing. `SingleStreamDiT` appends reference image tokens with separate positional indices, gives them timestep zero for `index_timestep_zero`, and returns only target-image predictions. This is separate from the nonzero starting sigma of the target. [Core conditioning](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/model_base.py), [Krea transformer](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/ldm/krea2/model.py).

## Exact smallest graph change

Keep the current FP8 UNET, Qwen3VL FP8 encoder loaded with `type=krea2`, Qwen Image VAE, stationary initialization, fresh Gaussian noise, CFG1, output dimensions, seed sequence and all three Euler intervals. Preserve `[0.6, 0.512844085693, 0.310901075602, 0.0]` literally. Keep 24 fps and RIFE as finishing only.

Apply this graph delta to [ten_dollar.repaint_graph](../../apps/deforum/projects/modern-model-study/experiments/ten_dollar.py), whose current `SamplerCustom` path is the recorded native control. This is documentation code only; it does not submit anything:

```python
# g = an existing fresh repaint_graph(prompt, seed, SIGMAS)
# node() is the existing class_type/inputs constructor.
g['60'] = node('LoraLoaderModelOnly', model=['1', 0],
               lora_name='krea2_style_reference.safetensors', strength_model=1.0)
g['61'] = node('LoadImage', image='reference.png')
g['62'] = node('TextEncodeQwenImageEditPlus', clip=['2', 0], vae=['3', 0],
               prompt=prompt, image1=['61', 0])
g['63'] = node('FluxKontextMultiReferenceLatentMethod', conditioning=['62', 0],
               reference_latents_method='index_timestep_zero')
g['5']['inputs']['conditioning'] = ['63', 0]
g['9']['inputs'].update(model=['60', 0], positive=['63', 0], negative=['5', 0])
assert g['9']['inputs']['latent_image'] == ['24', 0]
assert g['24']['class_type'] == 'VAEEncode'
```

For the explicit `SamplerCustomAdvanced` form, make the equivalent model/positive/negative edits on its **CFGGuider**, leaving the sampler's noise input, sigma input and `latent_image=['24',0]` unchanged. Do not reintroduce the deleted experimental correlated-noise node. Use the main agent's independent Gaussian noise path.

This is the conditioning route in Comfy's current official style-reference template. That template selects INT8 ConvRot; **our FP8 adaptation is intentionally a separate feasibility probe**, not a claim of reproducing the complete official template. Both are Krea Turbo, but a successful INT8 workflow does not by itself verify FP8 adapter loading or identical behavior. Do not switch checkpoints to make an otherwise confounded comparison. [Pinned official template](https://github.com/Comfy-Org/workflow_templates/blob/aaac56dd5cc5497533d92cbe50edc35ea660e587/templates/image_krea2_turbo_int8_image_style_reference.json), [official Comfy guide](https://docs.comfy.org/tutorials/image/krea/krea-2).

No extra CLIP-Vision/IPAdapter checkpoint is used. Connect **both** the VAE and reference image to the conditioning encoder. Omitting VAE tests vision-language conditioning alone, not the full trained reference route. Adding `ReferenceLatent` alone to ordinary text likewise omits the vision-language half. Neither omission is a substitute control for the complete adapter.

## Native core versus the Ostris author recipe

The author pairs `krea2_style_reference.safetensors` with `TextEncodeKrea2OstrisEdit` and `Krea2OstrisEditModelPatch`. The style adapter is trained for one or two style images and needs no trigger phrase. This is aesthetic guidance, not training evidence for retaining the same buildings or dune contours. [Adapter card](https://huggingface.co/ostris/krea2_turbo_style_reference/blob/269e1e4266b89bbabdc64a4f8cebfa0b7254078a/README.md).

There are two important source distinctions:

1. The Ostris README says stock Krea ignores reference latents. That statement is stale **for v0.34.0**, whose implementation above consumes them. The cached `object_info-models-ready.json` also records the two required core conditioning nodes and `index_timestep_zero`. Do not install a patch merely to overcome a missing capability that core already has. [Ostris README](https://github.com/ostris/ComfyUI-Krea2-Ostris-Edit/blob/7756566160c4a1b24bb1bd9f0ff3ced1a83d7547/README.md).
2. The native encoder is not text/preprocessing-identical to Ostris's encoder. Native `TextEncodeQwenImageEditPlus` uses an edit-oriented system template, normalizes VLM images to 384² area and reference latents to approximately 1024² area, rounding dimensions to 8. Ostris uses `KREA2_TEMPLATE`, downscales without intentionally enlarging small inputs, and snaps VAE reference sizes to 16. Thus native success is useful; native failure does not refute the author's exact recipe. [Native encoder](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy_extras/nodes_qwen.py), [Krea template](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/text_encoders/krea2.py), [Ostris encoder code](https://github.com/ostris/ComfyUI-Krea2-Ostris-Edit/blob/7756566160c4a1b24bb1bd9f0ff3ced1a83d7547/nodes.py).

For ordinary Ostris style/edit training, leave `kv_cache=False` in the author path. Some newer adapters require isolated reference attention and `kv_cache=True`; this is a training-dependent attention rule, not a freely interchangeable speed setting. Core `index_timestep_zero` does not establish that isolated-attention contract.

Installing the author pack would require a warm Comfy restart to register nodes, but its README specifies no additional Python dependencies. It is outside the current no-install experiment. Do not stack its forward replacement onto native core without checking revision compatibility; the current smallest proposal uses core alone.

## Controlled experiment and inference limits

Use an existing approved opening, with no new opening generation. Start with the same stationary city used by the diagnostic; add a second existing detailed artwork to test whether a result is scene-specific. Freeze the reference to that branch's **common starting artwork**, and keep the same prompt in every arm. A previous-output reference policy would be a later, separate test.

The requested baseline/LoRA/no-ref/LoRA/ref comparison needs one additional encoder control to avoid a hidden text-template confound:

| Arm | Model | Conditioning encoder | Reference | What the comparison establishes |
|---|---|---|---|---|
| A0 | Current FP8, no LoRA | Current `CLIPTextEncode` | None | Exact current baseline |
| A1 | Current FP8, no LoRA | Qwen Edit Plus | None | A1−A0 measures encoder/template route change |
| B | Current FP8 + style LoRA 1.0 | Qwen Edit Plus | None | B−A1 isolates adapter loading without reference |
| C | Current FP8 + same LoRA | Same Qwen Edit Plus | Fixed starting artwork | C−B measures addition of the full image-conditioning bundle |

For A1/B omit `image1` and the reference loader; the latent-method setter can remain. Keep the VAE input consistently wired. For A1 omit the LoRA or use its verified zero-strength bypass. A0 remains literally unchanged. B is a diagnostic ablation, not a recommended production setting for a reference-trained adapter.

First run matched one-step probes: two artworks × two seeds × four arms = 16 repaints. Stop on adapter mismatch warnings, failed conditioning, obvious flattening, or major background redesign; archive the failure rather than improvising a new encoder/checkpoint. Check whether C changes output relative to B; equality warrants investigating ignored inputs, not declaring perfect preservation.

Only if C offers useful detail/structure retention should the main agent extend matched recurrent branches to 15 repaints plus the shared opening: 4 seconds at 4 paintings/sec, 96 delivery frames at 24 fps. Every branch must initialize from its own previous painting after the first step. Keep all anchors for review before applying identical RIFE finishing.

Judge the intended outcomes separately: persistence of named buildings/dune edges; surface crispness; depth and shading; palette/contrast; accumulation of drift; and unwanted redesign. Low pixel difference can reward a blurred image, while high-frequency energy can reward noise. Use matching crops and full paintings alongside any simple difference measurements. A fixed source can also pull later camera motion backward or resist a requested transformation; the stationary test cannot establish either behavior.

C−B changes both VLM image information and clean reference tokens. It does not isolate their contributions. Recurrent branches rapidly diverge, so late-frame comparisons describe trajectories, not identical-input causal effects. An improvement at this sigma/three-interval recipe is useful local evidence; failure cannot establish that a normally eight-step reference adapter is universally ineffective. Do not silently switch to eight steps, strengthen CFG, change prompts, or add sharpening to rescue this test.

## Other available reference adapters

These are author claims and source-audited interfaces, not local tests. None was found in the inspected retained-base manifests or old reference-ready node inventory.

| Candidate | Exact matching route | Relevance and limitations | Runtime cost of adopting |
|---|---|---|---|
| **Identity Edit v1.2** | `krea2_identity_edit_v1_2.safetensors` → `LoraLoaderModelOnly` 1.0 → `Krea2EditModelPatch`; `Krea2EditGroundedEncode` with Qwen3VL `type=krea2`. Its shipped example uses our FP8 model/encoder and Qwen Image VAE. | Best semantic fit for editing while preserving surrounding content; author admits local edits can still alter other areas. Turbo recommendation is 8–12 steps/CFG1. Three-interval recurrent use remains untested. | New pack, restart, adapter weight; no extra Python dependencies per pack. |
| **ReID rank32** | `krea2_reid_rank32.safetensors` + `TextEncodeKrea2OstrisEdit` + `Krea2OstrisEditModelPatch(kv_cache=True)`. Its example uses **BF16 Qwen3VL**, INT8 Turbo and Qwen Image VAE. | Learns subject identity while releasing pose, clothing and **background**. Poor fit for preserving the whole stationary city. Do not run through ordinary non-isolated style-reference attention. | New pack/restart, adapter; author-example encoder is an additional 8.88 GB asset not evidenced in retained cache. |
| **Konoko reference v1** | `krea2_reference_v1.safetensors` + `TextEncodeKrea2Reference` + `Krea2ReferenceLoraLoader`, suggested `strength_text_fusion=1`, `strength_dit_body=0`; author requests BF16 Qwen3VL. | Vision-token character/style addressing; a distinct conditioning approach. Author warns of cloning, franchise leakage and partial two-reference behavior. No exact scene-lock evidence. | New pack/restart, LoRA and BF16 encoder. Weight revision/hash not resolved from its README, which names the file without an exact download repository. |
| **Detail enhancer edit** | Published `krea-detail-enhancer-exp.safetensors`; author points to Ostris encode/model-patch nodes. | Targets microdetail, but explicitly admits altered images, lighting/color changes and horizontal-aspect failures. Its workflow names a different `exp-v2` weight and changes VAE, model quantization and sampler. Not an exact reproducible drop-in preservation recipe. | At least new weight/pack/restart for author workflow; resolve file/workflow mismatch before considering an audition. |

Sources: [Identity Edit card](https://huggingface.co/conradlocke/krea2-identity-edit/blob/89e9e7a09ee2e5c9331e952063d79b1b8a703280/README.md), [Identity node contract](https://github.com/lbouaraba/comfyui-krea2edit/blob/86f886dac23013d88996e3a2e99093ba44d322fb/README.md), [Identity workflow](https://github.com/lbouaraba/comfyui-krea2edit/blob/86f886dac23013d88996e3a2e99093ba44d322fb/workflows/krea2_identity_edit.json), [ReID card](https://huggingface.co/yijunwang2/krea2-reid/blob/121fb0183944f1befeb712d92e9ca07d0e282088/README.md), [ReID workflow](https://huggingface.co/yijunwang2/krea2-reid/blob/121fb0183944f1befeb712d92e9ca07d0e282088/workflow/krea2_reid_comfyui.json), [Konoko nodes](https://github.com/KonokoAz/ComfyUI-Krea2-Reference/blob/bae20b3e0316e5b13fea94aa8a502c33fd2063ca/README.md), [enhancer card](https://huggingface.co/reverentelusarca/krea2-detail-enhancer-edit-lora/blob/5f905aa5994b30a3d104e707046dab5312289210/README.md), [enhancer workflow](https://huggingface.co/reverentelusarca/krea2-detail-enhancer-edit-lora/blob/5f905aa5994b30a3d104e707046dab5312289210/workflow-comfyui-krea2-detail-enhancer-edit-lora.json).

If Identity Edit is considered later, preserve our initialization by feeding `VAEEncode(previous painting)` to both sampler `latent_image` and patch `target_latent`. Feed the extra reference to patch `source_latent`, and to `Krea2EditGroundedEncode.image`. At matching source/output size, the documented latent path needs no geometry resampling. For its pixel path, connect `vae`, `source_image` and `target_latent` so reference encoding happens before sampling; otherwise its author describes model offloading during sampling. Its `fit` geometry, grounding resolution and `ref_boost` are additional choices to align separately, not changes for today's test.

Older vision-only nodes such as [ethanfel's encoder](https://github.com/ethanfel/ComfyUI-Krea2TextEncoder) can condition through image-aware language hidden states without VAE reference tokens. Their claims that Krea core never consumes `reference_latents` predate the audited core. Neither those claims nor their FP8 vision warnings should override the precise official FP8 encoder workflow and our archived execution evidence. Conversely, official FP8 success does not verify every third-party node's FP8 path.

## Weight provenance and cached availability

All byte sizes and hashes below are metadata, not freshly computed checksums of downloaded files. Public Hugging Face model API responses were read with `blobs=true`; no weight bytes were fetched. An LFS SHA-256 is the weight-file hash, not the repository revision or Git blob ID.

| Asset | Exact bytes | Revision | SHA-256 |
|---|---:|---|---|
| Ostris `krea2_style_reference.safetensors` | 457111760 | `269e1e4266b89bbabdc64a4f8cebfa0b7254078a` | `f50df5a9e62e4be8aa926a63dd5bb1a64770c4004f763c1208007ae13daa82b8` |
| ReID `krea2_reid_rank32.safetensors` | 228587752 | `121fb0183944f1befeb712d92e9ca07d0e282088` | `a80349faee4a2d80eff9a83820cd523c74cd0bbc6039cee21fa34b084d967944` |
| Identity Edit `krea2_identity_edit_v1_2.safetensors` | 1828256432 | `89e9e7a09ee2e5c9331e952063d79b1b8a703280` | `6adf9a69cc9502d286db7b69964d37da7e9cfe4b05b4d004bc275f087d3fd3cf` |
| Identity Edit `krea2_identity_edit_v1_2_r128.safetensors` | 914159744 | same Identity revision | `f53db0bb4b081d638f196865cbc9f055379704fafb788336784fc1ccde18d825` |
| Identity Edit `krea2_identity_edit_v1_2_r64.safetensors` | 457111048 | same Identity revision | `f794b47142555c929cf536a2f1e4f335174b9aedbb08572b07d45814d4242423` |
| Enhancer `krea-detail-enhancer-exp.safetensors` | 228587824 | `5f905aa5994b30a3d104e707046dab5312289210` | `237d764223b43f9680b237802014d3954262f23f9b77a7a3897abbbc8d26fba7` |
| Comfy Qwen3VL `text_encoders/qwen3vl_4b_bf16.safetensors` | 8875719384 | `e5ea8b4dd7f38f348b138eb0fe29f92c0e367e96` | `36f3ff447ef59201722e8f9ce6020c9819fdcfba6aa2608c4e09b1c0ce114e34` |

Metadata sources: [Ostris API](https://huggingface.co/api/models/ostris/krea2_turbo_style_reference?blobs=true), [ReID API](https://huggingface.co/api/models/yijunwang2/krea2-reid?blobs=true), [Identity API](https://huggingface.co/api/models/conradlocke/krea2-identity-edit?blobs=true), [enhancer API](https://huggingface.co/api/models/reverentelusarca/krea2-detail-enhancer-edit-lora?blobs=true), [Comfy Krea API](https://huggingface.co/api/models/Comfy-Org/Krea-2?blobs=true). Revision-pinned file pages above provide stable provenance if `main` later changes.

Local evidence checked:

- [conditioning-models.json](../../apps/deforum/projects/modern-model-study/experiments/conditioning-models.json) pins the style LoRA with the identical revision, size and hash above, plus the historical INT8/FP8-encoder/VAE combination.
- [modern-models.json](../../apps/deforum/serverless/modern-models.json) pins today's FP8 model (13,141,730,784 bytes), FP8 Qwen3VL encoder (5,242,467,968 bytes) and Qwen Image VAE (253,806,246 bytes). The manifest has no reference adapter.
- Ignored local `apps/deforum/work/persistent-model-volume/eu-1-models.json` and `eu-2-models.json` record verified installation/reuse of those three assets only. These are historical receipts, not a live file listing.
- Ignored `apps/deforum/work/additive-reference-session/object_info-models-ready.json` lists the style LoRA and native core nodes during the old session; neither Ostris custom node is present there. That old session's note records deletion of its owned storage.
- [prepare_pod_models.py](../../apps/deforum/prepare_pod_models.py) with `--krea-only` filters to exactly three `Comfy-Org/Krea-2` assets; it does **not** prepare the Ostris LoRA. `--verify-only` should not be confused with proving an asset omitted by that filter.

Consequently, a warm native experiment needs only an already-readable style LoRA and ordinary model loading, **if the main agent independently confirms that file exists**. Loading or switching a LoRA can incur memory/offload latency, but is not a Comfy process restart. If the file is absent, the current no-weight-download scope leaves a documented recipe rather than a runnable reference test.
