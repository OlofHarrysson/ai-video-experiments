# Opening artwork audition

Approved 2026-09-09. Establish a compelling opening before another feedback animation. Olof already knows these models can produce good artwork; the question is whether our recipe and art direction produce something he wants to develop.

## Scope

One Krea official-template control, followed by three visual concepts for Krea 2 Turbo and FLUX.2 Klein 4B: a porcelain cybernetic oracle, a living cathedral and a mechanical moth. Inspect the first output before completing each model’s remaining concepts; group inference by model to reuse loaded weights. Preserve every image and surface a small shortlist in chat. No animation, motion, reference-image conditioning or LoRA in this audition.

The BonsAi Evolve Zoom reference supplies composition lessons: a large focal face, material contrast, dense surrounding geometry, dark recesses and restrained bright accents. These prompts describe new images; they do not reproduce the reference frames or claim the creator's exact recipe.

## Recipe

- Pinned ComfyUI 0.34.0, commit `12d5279438bfefc058a269eae805ceab6047777f`; native nodes on a short-lived RTX 4090 Pod.
- Pinned weights and SHA-256 values: [`modern-models.json`](../../../serverless/modern-models.json).
- Krea: recommended FP8 checkpoint, Qwen3VL encoder, Qwen Image VAE, Euler/simple, 8 steps, CFG 1, denoise 1, no LoRA.
- Klein: 4B distilled checkpoint, Qwen3 encoder, FLUX.2 VAE, Euler, Flux2Scheduler, 4 steps, CFG 1.
- Official Krea control: published martini-glass illustration prompt and seed, 1024 square, default prompt enhancement enabled. Flatten only the active branches of the official template into the API graph; archive expanded text and source template.
- Authored artwork: 1536 × 1024, seed 491731, detailed natural-language descriptions. Krea enhancement disabled here to keep the authored text explicit; this is a documented workflow switch, not an untouched default. No negative prompt branch at CFG 1.

This changes several things from the rejected study (prompt, opening recipe and resolution). It is an art audition, not an experiment that can attribute improvement to a single parameter. Strong stills do not establish good feedback animation.

Run from `apps/deforum`: `uv run python projects/modern-model-study/experiments/opening_art.py CASE`, where CASE is `control`, `krea-oracle`, `klein-oracle`, or another case listed in the runner. Session deployment details stay in ignored `work/opening-art-session/`. Each case runs once; recovery collects an accepted job rather than submitting it again.

## Sources checked

- [Official Krea ComfyUI workflow and controls](https://docs.comfy.org/tutorials/image/krea/krea-2)
- [Krea author prompting guide](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md)
- [Official template source](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/image_krea2_turbo_t2i.json)
- [Klein 4B model card](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B)
- [Our prompting notes](../../../../../docs/research/prompting-for-feedback.md)

## Results

Completed seven stills, with no rejected jobs or regeneration. Each authored concept uses the same text and seed across models, with the native sampling recipes above. This keeps the concept comparable, but a shared seed does not mean the models receive equivalent noise or produce equivalent compositions.

**Assistant recommendation:** Krea's living cathedral. Its nested openings, miniature structures and organic curves offer several places for controlled growth and twisting. Klein's cathedral is the meaningful alternative: stronger recession and darker lighting, with more literal branches and coral. Olof has not reviewed this set yet; this is not an accepted model or style selection.

![All six authored openings; Krea on the left and Klein on the right](../exports/opening-art-v001/overview.jpg)

| Opening | First-pass visual review | ComfyUI execution |
| --- | --- | ---: |
| [Krea cathedral](../exports/opening-art-v001/krea-cathedral/image.png) | Most promising imaginative architecture; coherent seed focal point and fine nested buildings. Flatter than Klein's chamber, but visually richer than the earlier pale arch. | 10.45 s |
| [Klein cathedral](../exports/opening-art-v001/klein-cathedral/image.png) | Strong foreground-to-background separation, textured coral and embedded buildings. More conventional fantasy chamber. A generated signature-like mark appears at lower right; it is not provenance or an artist credit. | 2.69 s |
| [Krea oracle](../exports/opening-art-v001/krea-oracle/image.png) | Closest subject/composition to the supplied face reference: sculptural mask, concentric machinery and cyan recesses. Attractive detail, though very symmetrical and somewhat doll-like. | 10.54 s |
| [Klein oracle](../exports/opening-art-v001/klein-oracle/image.png) | Clear porcelain material and sharp eyes; the huge glossy face dominates. Less unusual than the surrounding crown might suggest. | 15.68 s, first Klein load |
| [Krea moth](../exports/opening-art-v001/krea-moth/image.png) | Strong orchid/moth fusion, glasslike wings and perforated filigree. Readable shape; more decorative sculpture than evolving world. | 10.38 s |
| [Klein moth](../exports/opening-art-v001/klein-moth/image.png) | Good jade/brass contrast and tiny stairs, but the literal human face on the body feels less integrated. | 2.69 s |

The [official Krea control](../exports/opening-art-v001/control/image.png) produced convincing glass, hand lighting and ink drawings without the previous style-reference adapter. Default enhancement generated a 116-word description, archived in [expanded-prompt.json](../exports/opening-art-v001/control/expanded-prompt.json) and the run history. Its 30.58 seconds include text generation and the first Krea model load. This is a visually successful execution of the selected official settings, not a pixel-identical comparison against a published reference output.

These are materially better candidates in the assistant's judgment. They support changing our opening recipe and art direction before blaming model capability. They do **not** isolate the cause of the earlier poor opening: prompt, quantization, adapter use, encoder path and resolution differ from the immediately preceding study. No claim about animation quality follows from this still-image test.

If Olof selects an opening, the next proposal is a short same-model twist feedback test with one restrained repaint recipe. Keep the image as the sampling starting point; additional reference conditioning is a separate control. Do not infer animation approval from merely presenting these images.

## Archive, verification and cleanup

- All seven images are in `exports/opening-art-v001/`. Every export has a `source.json` pointing to its immutable run, graphs, prompt, seed, model manifest hash, runtime and image hash. Full run histories preserve the actual executed prompts. The seven convenience MP4 files made by the shared collector contain a single still; they are not animation experiments.
- Original template and source receipt: `references/assets/opening-art-v001/`. Media is local and Git-ignored; no new separate-disk backup is configured.
- Both model families' six pinned weight files passed size and SHA-256 verification. Live ComfyUI reported 0.34.0. All seven jobs completed successfully, each result was opened for visual review, and the labeled overview was inspected.
- Queue empty before shutdown. All nine remote input/output files (seven generated images and two bundled files) matched local SHA-256 hashes. Private receipts and logs: `work/opening-art-session/`.
- Owned Pod and its attached storage deleted. Final Pod list and network-volume list were empty; account spend rate was zero. Observed balance fell from $43.9400 to $43.7744, approximately **$0.17**, including setup and idle time; billing may settle after the snapshot. No network volume was created.
- Setup correction: the initial create response lacked a public SSH key. Updating the environment restarted the Pod and changed its external SSH port. Re-read the mapping after updates. Central friction record: `AF-20260909-083504`.
