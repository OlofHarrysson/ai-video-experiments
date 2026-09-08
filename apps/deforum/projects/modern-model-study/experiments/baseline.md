# Klein and Krea audition

## Question

Can either model preserve a locally warped drawing while adding interesting detail across repeated feedback? Does an explicit next-frame edit instruction help, or cause unwanted reinterpretation?

## Approach

Olof authorized both candidates, model-specific prompts, and same-model opening/feedback. Keep spatial motion independent of the generator. Do not transfer SDXL LoRAs, CFG, negative prompts or denoise values as universal defaults.

1. Generate two openings per model and inspect before choosing one.
2. Warp the selected opening and inspect a single repaint. Klein uses native reference-latent editing. Krea starts with conventional partial img2img and a full scene description; one instruction-worded probe tests a hypothesis, not documented native editing support.
3. Inspect eight feedback anchors, then extend viable runs to the familiar three-second, 12 fps, cadence-3 twist. Preserve motion-only previews and every generation.
4. Review overview frames and an every-frame interval. Surface one clip per model with a short explanation. No RIFE, depth, optical flow, additional pixel noise or regional masks.

## Source recipes

- [BFL prompt construction](https://docs.bfl.ai/guides/prompting_unified_building), [single-reference editing](https://docs.bfl.ai/guides/prompting_editing_single_reference), and [technical notes](https://docs.bfl.ai/guides/prompting_unified_technical): describe concrete visual attributes; specify what changes and what remains. Avoid generic quality filler.
- [Krea prompting](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md): use natural-language descriptions with concrete details. Automated prompt enhancement stays disabled so the saved prompt is the actual prompt.
- ComfyUI official templates at `7c25a3c586484601f94b7e8f8b14c23b2c95a096`: `image_flux2_klein_image_edit_4b_distilled.json` and `image_krea2_turbo_t2i.json`.
- Assets/revisions/checksums: [worker manifest](../../../serverless/modern-models.json). Klein uses verified BF16 distilled weights instead of the template's FP8 filename; this may affect memory and speed. Krea uses FP8 scaled weights.

Klein: four steps, Euler, Flux2 scheduler, CFG 1, reference conditioning for edits. Krea: eight steps, Euler/simple, CFG 1; full denoise for opening, partial denoise as an experimental feedback adaptation. Dimensions 1024×576 for both. These are model-and-workflow auditions; different editing mechanisms prevent an isolated checkpoint ranking.

## Execution

Prepared 2026-09-08. New models require a worker image build and cold download; settings/prompt changes thereafter reuse that image. Original SDXL container recipe is preserved as `serverless/Dockerfile.sdxl`. Actual runtime evidence and results will be added after execution.
