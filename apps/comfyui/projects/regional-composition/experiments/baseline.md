# SDXL regional composition: experiment design

Completed 2026-09-10: [results and comparisons](results.md). Olof authorized all three methods with SDXL and built-in ComfyUI nodes. Execution resumed in Sweden (EU-SE-1), using an A40 and temporary Pod storage. The first owned Pod in EU-RO-1 was deleted at Olof's request before image submission; the separately authorized retained volume was preserved.

## Question

Can we place two distinct objects deliberately and produce a coherent scene using background/object/finishing stages? Compare regional prompting in one pass, unfinished latent assembly and incremental painting on a completed background.

## Scene and controls

Draft scene: a painterly mountain meadow at golden hour, a small red tin robot on the left and a blue glass tree on the right. Objects are deliberately different in shape, material and color so leakage is easy to see. Use this diagnostic subject for the authorized comparison; it does not establish a broader creative direction.

- Canvas: 1024×1024.
- Left region: x=64, y=384, width=384, height=512.
- Right region: x=576, y=384, width=384, height=512.
- Shared prompt context: painterly fantasy illustration, warm light from upper left, coherent perspective, grassy ground plane.
- Background prompt: distant mountains, open meadow, golden sky, shared context.
- Left prompt: one small red tin robot standing on grass, full body, shared context.
- Right prompt: one blue glass tree rooted in grass, translucent branching canopy, shared context.
- Negative prompt: text, watermark, duplicate objects, cropped objects.

Use SDXL base 1.0 with the repository's pinned hash, no LoRA, 28 steps, Euler / normal, CFG 6.5. These are **initial experiment settings**, not a tuned recommendation. Euler keeps the split test simple because it does not require carrying a multistep sampler's history through composition. Seeds: background 21001, robot 21002, tree 21003. Freeze them and record each node's value; matching seeds across different shapes/workflows does not make their noise tensors identical.

## R: regional prompting in one pass

Combine the shared background conditioning with two `ConditioningSetArea` object prompts at the rectangles above, strength 1.0. Generate the whole canvas from one empty latent at denoise 1.0, seed 21001. Save the result and an exact region overlay. This is prompt localization, with no staged image compositing or inpainting.

## A: unfinished latent assembly

Adapt the [official reference](../references/README.md), using the SDXL canvas and object dimensions above.

1. Sample background and two object latents through step 7 of the same 28-step schedule, retaining leftover noise.
2. Compose the object latents at their rectangle positions with 32-pixel feathering.
3. Continue the combined latent from step 7 through 28, with fresh noise injection disabled and full final denoising enabled. Use shared scene conditioning plus the two regional object prompts.
4. Decode and save the finished image; save the pre-completion latent if supported by the validated graph. A decoded noisy intermediate is a diagnostic, not finished artwork.

Compared with the original example, the model, prompts, dimensions, sampler, schedule and final regional conditioning change. Treat this as reproduction of the mechanism. If subjects are lost, first compare a later split at step 14 while holding the other settings fixed.

## B: incremental masked painting

1. Generate and save the complete background at denoise 1.0.
2. Insert the robot with a rectangle mask, `VAEEncodeForInpaint`, initial denoise 0.85, and its scene-aware prompt. Composite the decoded patch onto the input image. Save the result.
3. Insert the tree into that result the same way. Save the pre-finish composite.
4. Branch from that exact composite into a full-image finishing pass at denoise 0.15, using global scene and regional object conditioning. Keep the pre-finish image as the control.

Prepare explicit sampling and soft composite masks; start with 32-pixel inward feathering on local rectangle masks, then place them on the canvas. Inspect the mask previews before sampling. White means editable/copied from the generated patch. Leave enough spatial margin for ground contact and shadows.

If insertion is too weak, change only its denoise toward 1.0 and retry from the same parent. If the finish damages object identity, keep the pre-finish result and investigate local seam repair. Do not spend the session on a broad parameter grid.

## Preflight and evidence

- Inspect existing Pods and ownership; follow the [retained-volume runbook](../../../README.md#runpod-reuse). Verify actual SDXL files, hashes, free space and live `/object_info` before queueing.
- Validate the adapted graph against the live node schemas and run one small real request before the full comparison. Start from the archived official workflow and existing inpainting examples, not an invented API schema.
- Save UI-editable and executed API workflows, exact masks, seeds, checkpoint/runtime versions, prompt IDs, errors, intermediate images and hashes. Outputs and receipts belong to this project/session.
- For B's object passes, verify outside-composite-mask pixels match the parent. Do not apply that invariant to the full-image finish or A's joint completion.
- Review object presence/count, position, attribute separation, scene lighting, ground contact, rectangle seams and detail retention. Report visual judgments separately from mask/pixel checks.
- Present a small panel: R regional prompting, A noisy composition, B before finish and B after finish. If either approach is promising, repeat with a second fixed seed set before calling it reliable.
- Download and hash-check all outputs, confirm the queue is empty, delete owned compute and retain the authorized model volume.

Success means recognizable positional control with an acceptable seam/identity tradeoff. Exact silhouette control, pose control, regional LoRAs, modern models, upscaling and animation are later questions.

## Bounded follow-up during execution

The seed-21001 regional and split-7 noisy results are landscape-dominated: foreground attributes and silhouettes are weak or absent. Test background conditioning strength 0.25 (from 1.0) during combined regional sampling, keeping prompts, seeds, regions and schedules fixed. Background-only and object-only preparation remain unchanged. This tests prompt competition; it is not a different model or composition architecture. Preserve both controls. If noisy composition still loses its subjects, use the planned split-14 comparison.

Reducing background influence exposes hard rectangular artifacts in both area-conditioned variants. Next compare native `ConditioningSetMask` with the same rectangles, 32-pixel soft edges and `set_cond_area=default`, at background strength 0.25. This keeps full-canvas sampling context instead of the cropped area-conditioning windows. It changes mask edge weighting and conditioning context together; treat this as a practical recipe probe, not proof of a single cause.

The initial pixel check found eight one-level RGB changes at corners inside object A's rectangle. The float composite mask is positive there, but its saved 8-bit preview rounds tiny values to zero. The corrected check uses the binary rectangle as the exact support of the soft mask. Pixels outside that support remain the preservation criterion; do not use a quantized preview to infer exact float-mask zeros.

Full-canvas masked conditioning at background strength 0.25 produced recognizable subjects without hard rectangular panels in both regional prompting and split-7 noisy composition. Repeat all three working recipes with seed offset +100 (21101/21102/21103), using the same masked conditioning for the staged finish as well. The split-14 retry is unnecessary because subjects now survive. Glass material remains a review criterion rather than an assumed success.
