# SDXL regional composition: first experiment proposal

Prepared 2026-09-10. **Proposed, not executed.** This note makes the next modeling choice reviewable; research and folder setup do not establish a working GPU graph.

## Question

Can we place two distinct objects deliberately and produce a coherent scene using background/object/finishing stages? Compare two useful interpretations: unfinished latent assembly and incremental painting on a completed background.

## Scene and controls

Draft scene: a painterly mountain meadow at golden hour, a small red tin robot on the left and a blue glass tree on the right. Objects are deliberately different in shape, material and color so leakage is easy to see. This is a proposed diagnostic subject, not an accepted creative direction.

- Canvas: 1024×1024.
- Left region: x=64, y=384, width=384, height=512.
- Right region: x=576, y=384, width=384, height=512.
- Shared prompt context: painterly fantasy illustration, warm light from upper left, coherent perspective, grassy ground plane.
- Background prompt: distant mountains, open meadow, golden sky, shared context.
- Left prompt: one small red tin robot standing on grass, full body, shared context.
- Right prompt: one blue glass tree rooted in grass, translucent branching canopy, shared context.
- Negative prompt: text, watermark, duplicate objects, cropped objects.

Use SDXL base 1.0 with the repository's pinned hash, no LoRA, 28 steps, Euler / normal, CFG 6.5. These are **initial experiment settings**, not a tuned recommendation. Euler keeps the split test simple because it does not require carrying a multistep sampler's history through composition. Seeds: background 21001, robot 21002, tree 21003. Freeze them and record each node's value; matching seeds across different shapes/workflows does not make their noise tensors identical.

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
- Present a small panel: A final, B before finish, B after finish. If either approach is promising, repeat with a second fixed seed set before calling it reliable.
- Download and hash-check all outputs, confirm the queue is empty, delete owned compute and retain the authorized model volume.

Success means recognizable positional control with an acceptable seam/identity tradeoff. Exact silhouette control, pose control, regional LoRAs, modern models, upscaling and animation are later questions.
