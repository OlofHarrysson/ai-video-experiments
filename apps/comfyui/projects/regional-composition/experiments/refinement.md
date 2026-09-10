# Regional composition followed by global refinement

Authorized 2026-09-10: test stages one and two of the [ControlAltAI reference](../references/controlaltai-area-composition.md), using supported built-in nodes. Skip Ultimate SD Upscale and any third generation stage. This is a mechanism comparison using our diagnostic robot/tree scene, not an exact reconstruction of the video's artwork or old extension.

**Completed:** seven successful ComfyUI jobs, all 16 PNGs and 12 latent files local and verified; owned Sweden Pod deleted. **2048 at denoise 0.60 is the assistant's candidate from this small test**, with human preference pending. It produces clean detail on both starting images, while changing object design. At 2048, 0.30 and 0.45 leave conspicuous blur and horizontal artifacts. The 1024/0.45 control is clean, so do not transfer the stronger setting to a no-upscale workflow without testing.

![Matched starting images and 2048 global refinement](../exports/refinement-selected-v001/comparison.png)

The comparison uses equal display sizes: left is the actual first-stage input in this session, right is the 2048 result at 0.60. View [all first-seed controls](../exports/refinement-seed21001-v001/seed21001-comparison.png), [matched foreground details](../exports/refinement-seed21001-v001/seed21001-details.png), and the [second-seed control](../exports/refinement-seed21101-v001/seed21101-comparison.png). Full-resolution files and hashes are indexed in [the run inventory](refinement-run-inventory.json).

## Findings

| Condition | First-pass visual assessment |
|---|---|
| Regional starting image, 1024 | Already coherent and painterly; establishes the broad layout |
| Latent enlarged to 2048, decoded without sampling | Strong artifacts; latent interpolation alone is not equivalent to resizing the finished RGB image |
| Global 2048, denoise 0.30 | Blurred, simplified forms and fine horizontal artifacts |
| Global 2048, denoise 0.45 | Some shape recovery, but still blurred and visibly striped |
| Global 2048, denoise 0.60 | Clean, more intricate tree/robot detail on both seeds; robot features, branches, clouds and terrain are redrawn |
| Global 1024, denoise 0.45 | Clean refinement with changed robot/branch details; no large latent-enlargement artifacts to repair |

The two-stage mechanism preserves approximate composition while allowing a new global prompt to rebuild the scene. It does not lock exact object identity or boundaries. Neither selected result convincingly turns the tree into glass. The original regional images were already reasonably integrated, so this is stronger evidence for refinement and enlargement behavior than for repairing severe seams. No condition keeps regional prompts in stage two, so this test does not isolate the benefit of replacing regional conditioning with one global prompt from the benefit of adding another sampling pass.

The enlarged variants share the exact same first-stage latent tensor and refinement seed at 2048. The 1024 control has the same seed integer but a different noise tensor shape. Denoise changes the starting noise level and schedule segment. These limits matter when interpreting the differences as an algorithm experiment.

## Design before execution

Reproduce the saved masked-regional SDXL base images for seeds 21001 and 21101, saving their original generated latents as well as PNGs. Compare decoded pixels against the archived first-stage images before calling the starts matched. Recreating the latent avoids adding a PNG-to-VAE encoding round trip to the refinement path. Keep original and reproduced images if there is a difference.

Use the same checkpoint hash, ComfyUI image digest, Euler/normal, 28 steps and CFG 6.5 as the baseline. Stage one retains background strength 0.25, separate foreground prompt strengths 1.0 and feathered masks. Stage two has one positive prompt describing all objects, the environment and the shared style; it has no regional conditions. Keep the original negative prompt. Stage two initializes from the stage-one latent, enlarges it using native `LatentUpscale` with bislerp, then uses ordinary KSampler img2img denoising. This is a new partially noised refinement pass, not continuation of an unfinished stage-one schedule.

Primary seed-21001 comparisons:

- Original 1024 regional generation.
- 2048 latent-upscale decode without sampling, a diagnostic for enlargement alone.
- 2048 global refinement at denoise 0.30, 0.45 and 0.60, using one fixed refinement seed 21004.
- 1024 global refinement at denoise 0.45, with no latent resizing, to distinguish refinement from enlargement.

Repeat the most useful 2048 setting on seed 21101 using refinement seed 21104. Retain all settings and outputs, including unattractive results. Use the same decoder mode for comparisons within a resolution; record any memory-related decoder changes. The pixel-upscaled original is a display control, not a generation stage.

Review placement, robot identity/count, tree shape/material, ground contact, blending and texture at matched display size, then inspect selected full-resolution details. Changing denoise also changes the starting noise/schedule segment, so this is a practical strength comparison, not a fixed-noise step-count experiment. Two first-stage seeds do not establish reliability.

## Execution and resource scope

Use a short-lived Sweden A40 with the previously verified pinned official ComfyUI image, listed at $0.49/hour plus temporary storage. Live catalog: A40 HIGH stock in EU-SE-1; the country-filtered RTX A6000 read for US/Ireland/Germany returned LOW availability. No Pods existed at preflight. Preserve the separately retained Romania network volume. Add only the verified SDXL checkpoint, collect and hash-check all owned outputs, confirm the queue empty, and delete this experiment's Pod and temporary disk when done.

Private receipts belong to `apps/comfyui/work/regional-refinement/`. Actual per-job graphs, prompts, node schemas, runtime, lineage, history and output hashes belong to this project's ignored `runs/` folders. Export tested editable graphs and a comparison with the final result note.

## Starting-image check

The first recreated seed-21001 image retains the original composition but differs in fine details: mean absolute RGB difference 2.223/255, maximum channel difference 247. Identical graph settings, checkpoint hash and runtime versions do not establish bitwise reproduction across these sessions; the exact cause was not isolated. The initial strict check caught this before any refinement. Preserve both images, use the new first-stage latent as the common parent for this experiment, and retain strict pixel equality for all within-session refinement comparisons. Cross-session similarity is reported separately from within-session lineage.

Seed 21101 did reproduce the archived regional image pixel for pixel. Every refinement run matched its within-session parent's decoded pixels **and original latent tensor bytes, dtype and shape** exactly. The run graphs connect the first sampler directly to stage two; no intermediate PNG encoding or external image editing feeds generation. Safetensors metadata differs by graph, so latent comparisons use tensor payloads rather than whole-file hashes.

## Executed recipe and reproducibility

The global prompt is: “one small red tin robot standing on grass on the left, full body, one blue glass tree rooted in grass on the right, translucent branching canopy, distant mountains, open meadow, golden sky, painterly fantasy illustration, warm golden light from upper left, coherent perspective, grassy ground plane”. The negative prompt remains “text, watermark, duplicate objects, cropped objects”.

Model/runtime: SDXL base 1.0, SHA-256 `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`; ComfyUI 0.26.2 at `b7ac98aafe41c8c8593b9f21238dab58a90424c6`; PyTorch 2.10.0+cu128; A40. Image digest matches the [baseline](results.md). Download plus checksum took 121.5 seconds. All decoding used ordinary `VAEDecode`; no tiled fallback was reported or needed. Native `LatentUpscale` used bislerp with crop disabled, 1024→2048. Both samplers use Euler/normal, 28 steps, CFG 6.5.

The [editable two-stage graph](../workflows/regional-global-refinement-sdxl.json) and [API graph](../workflows/regional-global-refinement-sdxl.api.json) are exact copies of the executed seed-21001, 2048/0.60 workflow. API execution, live schema validation and graph-export equality were verified; this new graph was not separately opened or rendered through the frontend. Diagnostic SaveImage/SaveLatent branches preserve intermediate evidence.

```sh
uv run --script apps/comfyui/projects/regional-composition/experiments/run_refinement.py run \
  --deployment ACTIVE_RECEIPT.json --mode base --size 1024

uv run --script apps/comfyui/projects/regional-composition/experiments/run_refinement.py run \
  --deployment ACTIVE_RECEIPT.json --mode refine --size 2048 --denoise 0.60 \
  --parent-run PATH_TO_VERIFIED_BASE_RUN
```

Add `--seed-offset 100` to both stages for the second starting image. The full graph makes the first stage cacheable while preserving direct latent lineage. `collect --deployment ... --folder EXISTING_RUN` resumes collection of a recorded prompt ID. The archived deployment is closed and cannot be reused.

The two historical base-run folder names include `d0.45`, the unused refinement CLI default at the time. Their executed first samplers use denoise 1.0. The runner now labels base-only runs with their actual 1024/1.0 values; historical receipts and graphs remain unchanged.

## Verification and cleanup

All seven remote jobs succeeded. The first local base-run command reported a failed cross-session equality check after its two outputs had been successfully collected; that is not a failed generation. All 28 files matched remote SHA-256 values and the complete owned output inventory. PNGs were fully decoded. The queue was empty before deletion. Every first-stage and final image was visually reviewed, including the no-refinement enlargement control.

Warm 2048 jobs took approximately 31–33 seconds in server execution, including diagnostic output nodes and cached first-stage work. The 1024 refinement took 6.8 seconds. These exclude download/collection and startup time; they are not timings for two uncached sampling stages. The owned Pod existed from 10:10:49 to 10:26:29 UTC, at listed compute $0.49/hour plus temporary storage. Its deletion was verified; its temporary 30 GB Pod disk is removed. The retained Romania volume remains. A separate active Deforum Pod was observed and left untouched, so account-wide compute spend was not zero. The observed account balance change includes other work and is not attributed to this experiment.
