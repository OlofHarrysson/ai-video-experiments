# Previous-image feedback plus optional image conditioning

2026-09-08. Olof explicitly keeps the Deforum feedback loop. This study adds a reference input to that loop; it does not compare independent redraws with reference-only generation.

## Quality diagnosis and human feedback — 2026-09-09

Olof finds Klein more consistent than SDXL in some respects but less interesting and compelling than the SDXL results and original Deforum references. He rejects Krea, including its first image. This supersedes the assistant's creative shortlist below; those earlier observations remain as the experiment history.

Verified findings:

- The latest Krea opening used the style-reference LoRA at strength 1 with TextEncodeQwenImageEditPlus but **no reference image**. Keeping this fixed across opening/branches controlled the additive comparison, but did not establish a validated default for opening generation. The adapter author describes training with one or two reference images; the official ComfyUI normal text-to-image template defaults to no LoRA. Its effect on the poor opening is a hypothesis, not isolated proof. [Adapter card](https://huggingface.co/ostris/krea2_turbo_style_reference), [official workflows](https://docs.comfy.org/tutorials/image/krea/krea-2).
- The earlier FP8 Krea opening without this adapter also used a flat ink-illustration treatment. It has more pronounced orange/black contrast than the latest opening in direct image inspection, but checkpoint format, encoder path and adapter changed between studies. Those images cannot isolate the adapter or quantization as the cause.
- Our prompt explicitly requests flat screen-printed colors, pale stone, a tiny explorer and broad quiet areas. That is a narrow authored art direction, not an artist-proven recipe. Natural-language detailed prompting follows the author's general advice, but does not establish that this particular prompt or selected output meets the user's aesthetic target. Official examples use 2K; our 1024×576 test is also below their example resolution. Resolution alone is not a demonstrated explanation or fix. [Author prompting guide](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md).
- The successful local SDXL recipe included the **More-art LoRA** and prior style/parameter iteration; it was not plain SDXL versus otherwise equivalent modern models. This describes our local recipe, not an assertion about the checkpoints used by every reference-video artist.
- Klein's partial-noise four-update adaptation deliberately retains much of the previous image. Greater continuity with little invention is consistent with that recipe. Both modern feedback recipes remain experimental; correct executed graphs and weight hashes do not validate their artistic behavior or establish a model's limits. No specific core ComfyUI defect has been identified as the cause of the poor opening.

The assistant over-weighted continuity and successful pipeline execution when recommending continuation, and extended a weak Krea opening into more video. Central record: **AF-20260909-002949**.

**Next recommendation, not a new render authorization:** first run an unchanged official still-image recipe with its published example prompt/settings to check the installation, then audition a small set of reference-led opening images. Judge the starting art before the animation. Once a convincing opening exists, retain the same-model warped-image feedback loop and separately test expressive evolution. A good stock still with a poor custom still points toward prompt/style choices; a good opening that deteriorates in feedback points toward the animation recipe. A poor reproduced control calls for implementation/checkpoint investigation before declaring the model unsuitable. Model preference remains a separate artistic judgment.

## Data flow held fixed

1. Take the previous generated anchor and apply the direct spatial twist.
2. Encode that warped image as the sampling initialization and partially noise it.
3. Denoise using the model-specific text prompt; decode and preserve the result.
4. Feed that result into the next iteration. Cadence 3 supplies two warp-only intermediate frames, without blending or RIFE.

The reference-enabled arm additionally conditions on the previous generated anchor **before warping**. The baseline receives no reference-image conditioning. This choice could reinforce appearance but resist the imposed motion; that is a hypothesis to inspect. Each branch uses its own previous output once their trajectories diverge. Single-step probes first use identical starting pixels and seeds.

## Recipes and limits

Both models use their own opening, the same prompt/seed sequence within each pair, 1024×576, 12 source fps, cadence 3 and a two-second twist. Openings start from noise; all later sampling starts from the warped previous image. No regional masks, extra pixel noise, color correction, depth, optical flow, explicit image blending or copyback.

- **Klein 4B distilled:** four actual Euler updates, CFG 1, with the final four intervals of a 40-interval Flux2 schedule. Starting sigma is approximately **0.426681**, so previous-image initialization remains present. The ordinary four-step schedule starts at sigma 1 and even its final nonzero point is about 0.739; merely attaching an initial latent there would be a poor mild-repaint control. This lower-noise schedule is an experimental adaptation, not a vendor-recommended Klein animation recipe. Optional conditioning uses ReferenceLatent separately from the initialized sampling latent.
- **Krea Turbo INT8:** eight Euler/simple updates, CFG 1, BasicScheduler denoise 0.45 and ModelSamplingFlux 1.15/0.5. Both arms and the opening use the same style-reference LoRA at strength 1. Both encode text through TextEncodeQwenImageEditPlus; only the optional image changes. This controls for the adapter/prompt-encoder changes present in the previous study. The adapter's usefulness without a reference and with partial-noise initialization is experimental. Denoise 0.45 is not a claim of equivalent noise to Klein's schedule.

The deployed Krea schedule starts at sigma **0.674571**, followed by 0.620139, 0.559908, 0.492899, 0.417765, 0.333238, 0.237266, 0.127356 and zero. The initialized signal is therefore still present, but the starting noise is stronger than Klein's. Compare reference on/off **within** each model; these are not noise-matched tests of model quality. Schedule values were computed from the deployed ComfyUI implementation without loading another model.

Weights: [pinned model manifest](conditioning-models.json). Runtime: ComfyUI v0.34.0, required for native Krea reference latents. Use the official prebuilt Pod, update the core before inference and archive the deployed version.

## Verification before judging the art

Assert that every feedback sampler takes its latent from VAEEncode of the warped input; no empty latent remains in these graphs. Within each pair, assert identical sampler settings, model/adapter settings and prompts. The extra reference must have its own input and archive hash. Inspect identical-source probes before extending seven repaint anchors per arm. Record failed probes and any subsequent setting changes explicitly.

Source evidence: [ComfyUI sampling nodes](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy_extras/nodes_custom_sampler.py), [flow-model noise initialization](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/model_sampling.py), [separate reference conditioning](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy_extras/nodes_edit_model.py), and [Krea model conditioning](https://github.com/Comfy-Org/ComfyUI/blob/v0.34.0/comfy/model_base.py). Source support establishes a possible graph; GPU execution and visual usefulness remain to be tested.

## Klein results

Both two-second branches are complete, with their fourteen feedback anchors verified against saved inputs, outputs and executed graphs. The common single-step probes retain the warped scene in both versions. In timestamp-matched overview frames and the every-frame window at 1.15–1.30 seconds, both retain the arch, explorer and flame while following the twist. The reference-enabled branch retains cleaner, more coherent linework toward the end; the baseline develops more broken, grainy detail. The reference benefit is modest and does not establish long-shot stability or Olof's playback preference.

**Current candidate:** Klein with added reference, followed by a longer test before changing more parameters. The mild recipe produces relatively little invention; useful morphing remains a separate creative tuning question.

![Klein: feedback with text at left; added reference at right](../exports/additive-reference-v001/comparisons/klein/preview.mp4)

[Baseline full size](../exports/additive-reference-v001/klein/baseline/preview.mp4) · [Added reference full size](../exports/additive-reference-v001/klein/reference/preview.mp4) · [Matched probes](../exports/additive-reference-v001/klein/probe-review.jpg) · [Frame review](../exports/additive-reference-v001/klein/comparison-review/v001/review.json) · [Lineage verification](../exports/additive-reference-v001/klein/lineage-verification.json)

## Krea results

Both single-step probes execute with initialized feedback. In each, the arch is substantially reshaped and the tiny explorer disappears; the additional reference does not prevent this at the tested settings.

Both two-second sequences are complete and their fourteen feedback anchors pass the same lineage checks as Klein. Krea produces stronger structural morphing: the organic opening becomes a constructed circular ring and the explorer is repeatedly redrawn and repositioned. In the matched late frames, adding the reference retains a more defined inner ring and a clearer, larger figure; it does not lock the original geometry or subject scale. Both branches lose some fine ink detail and flatten the palette. This is an interesting morphing alternative, not yet a reliable preservation recipe.

**Recommendation:** take Klein with added reference into a longer controlled-motion test first. Keep Krea with added reference as the more adventurous morphing alternative. If continuing Krea, a lower starting noise level is a useful next isolated test; it is not a demonstrated fix for the fading. No new playback preference has been inferred for Olof.

![Krea: feedback with text at left; added reference at right](../exports/additive-reference-v001/comparisons/krea/preview.mp4)

[Baseline full size](../exports/additive-reference-v001/krea/baseline/preview.mp4) · [Added reference full size](../exports/additive-reference-v001/krea/reference/preview.mp4) · [Matched probes](../exports/additive-reference-v001/krea/probe-review.jpg) · [Frame review](../exports/additive-reference-v001/krea/comparison-review/v001/review.json) · [Lineage verification](../exports/additive-reference-v001/krea/lineage-verification.json)

The assistant inspected same-source probes, evenly spaced clip frames and short every-displayed-frame windows across repaint boundaries. This supports the reported changes in structure/detail; sampled frames do not establish the human playback experience. All four full-size clips and both synchronized comparisons are preserved and the two comparisons are surfaced in chat.

## Execution notes

Seven pinned model assets passed exact size and SHA-256 checks. ComfyUI v0.34.0 is running. Two slow Krea transfers were interrupted and resumed from their partial files, then verified. Two Python HTTP uploads timed out before any prompt submission; queue/history checks confirmed that no duplicate inference was submitted. Failed attempts remain archived. Direct HTTP upload from inside the Pod worked, while the public upload route and an SSH tunnel from the Mac were slow or timed out; the underlying network cause is unresolved.

For this session, image uploads explicitly use SSH file transfer with remote SHA-256 verification; prompt submission, status and output collection still use the same ComfyUI HTTP API. This is a transport change only. It is configured explicitly, with no automatic fallback or automatic resubmission. Transfer latency remains variable. Central friction record: **AF-20260908-235706**. Private runtime, deployment and transfer receipts live in `work/additive-reference-session/`.

ComfyUI's recorded prompt execution totals were about **48 seconds for Klein** and **248 seconds for Krea**, across 17 images each; the medians were 2.23 and 20.07 seconds. These include each prompt's executed conditioning/model work, not upload, download, local orchestration or initial Pod preparation. The roughly 35-minute Pod session therefore should not be read as 35 minutes of diffusion compute: setup, transfer failures, repeated frame transfers and review/orchestration accounted for much of the elapsed time.

## Validation and cleanup

Completed **34 diffusion images**: two openings, four matched probes and 28 feedback repaints. The four clips and two comparison videos each decode fully to **48 displayed frames at 24 fps, two seconds**. The underlying source is 12 fps with cadence 3; delivery repeats frames and adds neither RIFE nor blending.

The executed graphs match their declared recipes apart from uploaded filenames. Each first feedback pair uses byte-identical warped input; subsequent repaints use their own branch's output. Every intermediate frame is verified pixel-for-pixel against its warp-only construction. Uploaded input, optional reference and generated-output hashes match the preserved archives.

The queue was empty before cleanup. **All 88 remote input/output files have matching local SHA-256 copies**, including failed-upload inputs and bundled template files. The owned Pod and its attached storage were deleted. Post-cleanup inventories contain no Pods or network volumes, and account spend is **$0/hour**. The observed balance change was approximately **$0.44**, leaving approximately **$43.96**; billing can settle later. The active deployment receipt was renamed `deployment-closed.json` to prevent accidental reuse.

Reproduction entry points: [runner](additive_reference.py), [archive and comparison checks](additive_review.py), [shared Pod transport](../../../pod_client.py), and [pinned model manifest](conditioning-models.json). Rendering requires a new live session configuration; all review artifacts work locally after cleanup.
