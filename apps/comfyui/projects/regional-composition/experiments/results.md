# SDXL composition results — 2026-09-10

All three methods ran in Sweden using SDXL base 1.0 and built-in ComfyUI nodes. **Regional prompting is the current starting recommendation:** both final seeds placed recognizable subjects in a coherent landscape. Noisy composition produced the strongest single first-seed layout, but the second seed rendered the tree inside a picture frame. Staged inpainting offered exact preservation outside each insertion rectangle, while leaving conspicuous patches. Its gentle finish did not repair them. Two seeds are a screening test, not a reliability estimate, and none convincingly achieved a glass tree.

## Compare the final recipes

First seed set, 21001/21002/21003:

![First seed comparison](../exports/masked-seed21001-v001/comparison.png)

Second seed set, 21101/21102/21103:

![Second seed comparison](../exports/masked-seed21101-v001/comparison.png)

| Method | Observed result | Practical implication |
|---|---|---|
| Regional prompting | Red robot and blue-trunked tree in both images; naturally integrated, but the first tree reaches inward and has orange foliage | Good starting point for approximate prompt placement; masks do not enforce exact object boundaries or materials |
| Noisy latent composition | First image separates a small robot and blue-canopy tree clearly; repeat contains a conspicuous framed tree | Interesting alternative, with unresolved seed sensitivity and patch integration |
| Incremental masked painting | Robot insertion works; tree becomes a blue shrub or hazy patch, with rectangular tonal changes | Good edit-boundary control, poor integration in this initial SDXL base recipe |
| Full-image finish | Denoise 0.15 changes texture slightly but leaves the patch visible in both seeds | A finishing pass is not an automatic seam-removal operation |

Layer construction for the first seed:

![Background, robot insertion, tree insertion and finish](../exports/masked-seed21001-v001/layered-stages.png)

The [second seed stages](../exports/masked-seed21101-v001/layered-stages.png), every original output and failed visual control are preserved. Human creative preference is pending; these rankings are the assistant's visual review.

## What was actually tested

The [design note](baseline.md) preserves the initial plan and bounded follow-up decisions. All full-size runs use 1024×1024, Euler/normal, 28 steps, CFG 6.5, no LoRA. Rectangles are `(64,384,384,512)` and `(576,384,384,512)` in x/y/width/height order. Prompts and every node value are in the [tested workflows](../workflows/README.md).

- **Original controls:** area-conditioned prompts with background strength 1.0 lost the subjects in regional and noisy generation. Lowering background strength to 0.25 exposed hard rectangular artifacts.
- **Final conditioning:** `ConditioningSetMask`, full-canvas context (`set_cond_area=default`), object strength 1.0, background strength 0.25. Build each local rectangle, feather inward by 32 pixels, then place it on the full mask canvas. This changes both context and edge weighting relative to the area control; it does not isolate a single cause.
- **Regional:** sample the whole canvas once with combined background and masked object prompts.
- **Noisy:** sample background and two smaller object latents through step 7 of the same 28-step schedule, feather-composite the unfinished latents, then resume at step 7 with fresh noise disabled. Save the composite latent plus decoded diagnostic images. This adapts the official mechanism to SDXL; it is not a pixel reproduction of its older-model example. The planned split-14 probe was not needed to recover subjects and was not run.
- **Layered:** generate a background, then perform two masked `VAEEncodeForInpaint` insertions at denoise 0.85 and mask growth 6. Copy each decoded insertion back through its feathered rectangle. Finish the resulting image at denoise 0.15 with the final combined conditioning. The finish seed is background seed +3.

Full-image conditioning masks control prompt influence. Inpainting noise masks control what is resampled. RGB copyback enforces preservation of pixels outside the insertion support. These are separate controls.

The six final runs use two seed sets. Matching a seed across different latent shapes or workflows does not imply matched noise. Early controls and the smoke request bring the total to **12 successful jobs**, yielding **55 PNGs and four latent files**; the PNG count includes masks and intermediates, not 55 finished artworks. See [run inventory](run-inventory.json). Early submission receipts predate the optional conditioning fields; their frozen graphs retain the exact values.

## Runtime and verification

- Official image: `runpod/comfyui:cuda12.8@sha256:498e3c4ac7ef5071214badb1681d82ab3a8f922b1055742ae692fa02cd3b59ff`.
- ComfyUI 0.26.2, commit `b7ac98aafe41c8c8593b9f21238dab58a90424c6`; frontend 1.45.19; Python 3.12.3; PyTorch 2.10.0+cu128. The image includes additional packs, but the executed graphs use only built-in nodes. No runtime upgrade or custom-node installation was needed.
- SDXL checkpoint `sd_xl_base_1.0.safetensors`, Hugging Face revision `462165984030d82259a11f4367a4eed129e94a7b`, 6,938,078,334 bytes, SHA-256 `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`. Download and hash verification took 312.5 seconds.
- A40 in EU-SE-1, listed compute rate $0.49/hour plus temporary storage. Pod creation-to-deletion was about 27 minutes, including startup, download, inference, collection and review. This interval is not an itemized billing receipt. Final-job execution times were about 12 seconds regional, 14–15 seconds noisy, and 33–34 seconds layered; these exclude local round trips and setup.
- Graphs passed checks against live node schemas and completed through the API. All three exported UI graphs opened in ComfyUI without missing-node/model dialogs; no second render was submitted through the frontend.
- Every PNG was fully decoded locally. All 59 files matched remote SHA-256 values; the complete remote output inventory matched the local archive. The queue was empty before cleanup.
- Both object insertions in both final seed sets preserve every pixel outside their rectangle exactly. The float feather mask has small positive corner values that round to zero in an 8-bit preview; the check therefore uses the binary rectangle as its exact support. This does not assert preservation through the full-image finish.

## Infrastructure outcome and next step

The initial Romania Pod was deleted at Olof's request before image submission. Its failed local preflight was a proxy HTTP 403 with the default Python user agent; the project client now uses an explicit user agent. No inference was queued there. The successful Sweden Pod was deleted after verified collection, including its temporary 30 GB Pod disk. A fresh list returned no Pods. The separately authorized 50 GB `deforum-models` network volume remains in EU-RO-1 and continues to incur storage cost; no volume migration was performed.

Prefer larger regions with deep live inventory for future experiments, with Sweden/Iceland acceptable when inventory supports them. The existing cache location must not silently determine a new project's region.

Continue from masked regional prompting for simple layout work. For the requested layer-by-layer process, the next useful experiment is improving the insertion and seam-repair recipe on the same saved background, with an explicit before/after control. A broader sweep or modern-model transition has not been run in this session.
