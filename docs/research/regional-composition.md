# Regional prompting and layered painting

Researched 2026-09-10. Primary-source documentation, an embedded example workflow and pinned ComfyUI code were inspected. No GPU was allocated and no new output quality was tested. Project: [regional composition](../../apps/comfyui/projects/regional-composition/README.md).

## Recommendation

Use **ordinary SDXL and built-in ComfyUI nodes** for a small comparison of noisy latent composition and successive masked inpainting. These address two parts of Olof's intent: arranging several subjects before finishing the scene, and adding objects to an existing image. Keep regional prompting as a distinct control rather than calling all three methods the same thing.

The closest older reference is ComfyUI's [Noisy Latent Composition example](https://comfyanonymous.github.io/ComfyUI_examples/noisy_latent_composition/): separately begin the background and subjects, paste the partly denoised subjects into the background, then continue joint diffusion. The supplied workflow has a 16-step schedule split after step 4, with feathered composition and no fresh noise injection on continuation. That is a continuation of unfinished sampling, not a low-strength repaint of a finished collage. The author reports strong placement control but limited fine-detail control. The original uses WD1.5 beta 3 illusion; an SDXL version would be an adaptation, not an exact reproduction.

## Three related mechanisms

| Method | What the regions control | Best use | Main limitation |
| --- | --- | --- | --- |
| Area or mask prompting | Where each text conditioning contributes during one sampling run | Lay out a whole scene with several prompts | Does not lock existing pixels or guarantee object count/contours |
| Noisy latent composition | Where partly formed background/subject latents are placed before joint completion | Assemble a new scene with positional control | Later diffusion can change subjects; all pieces need compatible noise levels |
| Successive masked inpainting | Which part of an existing image is repainted at each stage | Add or replace objects one at a time | Order matters; lighting, seams and interactions can need repair |

The official [area-composition examples](https://comfyanonymous.github.io/ComfyUI_examples/area_composition/) use `ConditioningSetArea` and demonstrate adding foreground conditioning over other areas. Their later global pass also illustrates attribute leakage: the subjects' hair colors become less distinct. A finishing pass can improve coherence while weakening the deliberate differences between objects. It is an experiment to compare with the pre-finish image, not a guaranteed cleanup operation.

The official [inpainting examples](https://comfyanonymous.github.io/ComfyUI_examples/inpaint/) support painted masks and demonstrate both dedicated inpainting checkpoints and ordinary checkpoints. This gives us a native starting path without adopting a custom node pack.

## Mapping the layer-by-layer workflow

For incremental painting:

1. **Background:** generate the complete canvas with environment, perspective and lighting. Leave room for foreground objects.
2. **Object A:** repaint a rectangle or mask with an object-specific description plus shared scene/style context. Save and inspect the result.
3. **Object B:** repeat from the accepted A image. Include room for feet, cast shadows or nearby interaction; a mask cannot affect geometry outside its editable region.
4. **Finish:** compare the unchanged composite with a gentle full-image repaint. If only a seam is wrong, a local repair can preserve more of the successful scene.

Use shared style/light phrases in each object prompt, while keeping object-specific colors and attributes local. “Background prompt” should not insist that the foreground remain empty during object insertion.

For noisy composition, the first three blocks prepare unfinished pieces and the last block completes their common sampling schedule. There is no finished background to preserve exactly. Compose all pieces at the same schedule boundary; do not mix a clean latent with a noisy one and assume the remaining steps will fix the mismatch.

## Native ComfyUI implementation boundaries

Inspected against the previously verified runtime commit `12d5279438bfefc058a269eae805ceab6047777f` (0.34.0), not a claim about the currently running account environment.

- `ConditioningSetArea` provides rectangles; `ConditioningSetMask` provides masked conditioning. Combine these with global conditioning through `ConditioningCombine`.
- A conditioning mask chooses **where a prompt applies**. `SetLatentNoiseMask` chooses **where sampling edits**. They have separate responsibilities.
- `VAEEncodeForInpaint` clears masked input pixels and builds a noise mask. Ordinary `VAEEncode` plus `SetLatentNoiseMask` retains the underlying image as initialization; these are different starting conditions.
- `KSamplerAdvanced` exposes start/end steps, noise injection and leftover-noise retention. Together with `LatentComposite`, it provides the classic noisy-composition path. Rectangle placement uses multiples of eight for this SDXL latent workflow.

Source: [pinned core nodes](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/nodes.py).

After an inpainting pass, `ImageCompositeMasked` can copy the generated patch over the previous image while retaining pixels outside the composite mask. This matters because encoding and decoding alone can alter nominally protected pixels. Keep the sampling mask and the composite mask explicit: enough editable margin for generation, and a soft transition for compositing. Built-in `FeatherMask` fades the **outer edges of the mask canvas**; it does not automatically soften every arbitrary shape inside a full-canvas mask. For rectangles, feather a local white mask before placing it. For painted shapes, use a prepared soft-contour mask or a verified contour-blur operation. [Pinned mask nodes](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_mask.py).

`DifferentialDiffusion` is a possible later refinement: it makes mask values affect when regions participate in denoising. This is different from final RGB feathering and should be tested separately. [Pinned implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_differential_diffusion.py).

## Older ecosystem and alternatives

- **Regional Prompter** is a WebUI extension with attention and latent modes, region matrices and masks. Its base prompt and common prompt have different meanings. It is useful historical evidence, but its graphs/settings are not ComfyUI imports. Its September 2026 README also describes model-specific Forge Neo support; that does not establish equivalent ComfyUI support. [Maintainer repository](https://github.com/hako-mikan/sd-webui-regional-prompter).
- **Attention Couple** separates conditioning inside attention layers. The original ComfyUI repository was archived in March 2024 and points to a successor; its SDXL pooled-conditioning and regional-LoRA limitations make blindly installing the old node a poor baseline. [Original repository](https://github.com/laksjdjf/attention-couple-ComfyUI).
- **Impact Pack RegionalSampler** runs base and regional samplers during each step, with overlap and outside-mask restoration controls. It is relevant when regions need distinct sampling settings. It introduces more dependencies and behavior than the first native-node experiment needs. [Maintainer documentation](https://github.com/ltdrdata/ComfyUI-Impact-Pack#regional-sampling).
- **MultiDiffusion** coordinates region-conditioned diffusion paths into one result. It is background for joint regional generation, rather than a synonym for finishing a pasted image. [Author project and paper](https://multidiffusion.github.io/).

## What transfers from our Deforum work

The [Pod runbook](../../apps/deforum/POD.md) and [retained-volume trial](../../apps/deforum/projects/modern-model-study/experiments/persistent-model-volume.md) are the relevant infrastructure owners. Reuse the official image, persistent runtime and authorized 50 GB EU-RO-1 volume. Inspect current Pods, ownership, model inventory, free space and GPU availability before allocation. Keep existing work and the retained volume intact.

The trial populated Krea assets. Prior SDXL execution does **not** prove SDXL is present on this volume. Verify or add the existing [pinned SDXL base checkpoint](../../apps/deforum/README.md#versions-and-provenance), rather than running the Krea-only preparation command and declaring this experiment ready. Avoid copying the legacy installer wholesale: it also installs animation dependencies.

Our [E10 masked repair](ten-experiments-session.md) already demonstrated sampling masks plus RGB copyback, preserving outside-mask pixels while inventing unwanted content inside. That establishes a useful preservation mechanism, not successful regional object prompting. The [existing graph helper](../../apps/deforum/projects/redraw-lab/experiments/masked.py) is a reference for this distinction.

Archive actual graph inputs and every intermediate image, verify local downloads, and delete the experiment's owned Pod after the queue is empty. Do not infer current account spend or resource state from historical cleanup notes.

## Modern-model path

Keep the scene, rectangles/masks, prompts and evaluation criteria portable. Rebuild model-specific graph sections when changing families; do not carry over SDXL CFG, schedulers, VAE encodings or attention patches by assumption.

For later **masked editing**, FLUX.1 Fill has an official ComfyUI workflow with dedicated fill weights, encoders and VAE. It is a documented migration candidate, not a claim that it is the newest or best model now. [Official guide](https://docs.comfy.org/tutorials/flux/flux-1-fill-dev). Reassess modern candidates when that experiment starts. Existing Krea availability alone does not validate regional conditioning or noisy composition with its distilled schedule.

Next: [bounded SDXL comparison](../../apps/comfyui/projects/regional-composition/experiments/baseline.md). The key learning to preserve is the distinction between prompt placement, editable pixels and continued denoising; no portable methodology change is needed from this research alone.
