# Regional composition

Status: all three SDXL methods executed and reviewed on 2026-09-10, with two seeds per final recipe. All outputs are local and verified; owned compute is deleted.

Build images by assigning a full-canvas background prompt and separate foreground prompts to spatial regions. Start with rectangles; retain a path to painted masks and incremental object insertion. Use ComfyUI on RunPod independently of the Deforum animation experiments.

- [Research and recommendation](../../../../docs/research/regional-composition.md)
- [Results and comparisons](experiments/results.md)
- [Two-stage regional/global refinement](experiments/refinement.md) — clean 2048 detail at denoise 0.60 on two seeds, with object redesign; human preference pending.
- [Experiment design and follow-up decisions](experiments/baseline.md)
- [Tested editable workflows](workflows/README.md)
- [Upstream workflow evidence](references/README.md)

The first model is ordinary SDXL base 1.0, already used in this repository. Regional prompting with feathered masks gave the most consistent integration in this small comparison. Noisy composition gave a good first image but a framed tree on the repeat. Incremental inpainting preserved pixels outside the insertion regions exactly, but left conspicuous patches that the gentle finish did not fix. None convincingly delivered the requested glass material. These are initial recipes, not rankings of the methods' ultimate capabilities.

A modern-model follow-up should retain the same scene brief and spatial controls while adopting that model's native conditioning and sampling recipe.

Olof's review: regional prompting looks best. Noisy composition may suit intentionally distinct areas or styles, but its weak blending limits general use. He rejects these layered-inpainting results and wants the apparent foreground overlap explained before further experiments.
