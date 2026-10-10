# Prompting for rich surfaces and depth

Started 2026-10-10 at 17:51 UTC. Olof authorized roughly 60–90 minutes of iteration, testing several worlds and motion, and asked for the strongest screened result. He finds the previous `d03-crisp-digital` treatment similar or worse than the original; its cleaner linework did not supply the expected high fidelity. The original film remains selected.

## Result and shortlist

The strongest new moving material treatment is the [tidal world at 0.85](../../exports/v002/ps-tidal-specific-n085/faster/rife-moving-tail/preview.mp4): clear water, granular mineral shores, textured copper and a sharply lit ivory shell. It also has a visible planet-size jump at 0.33–0.46 seconds. The [gentler 0.25 alternative](../../exports/v002/ps-tidal-specific-n025/faster/rife-moving-tail/preview.mp4) preserves structure better but gradually smooths the surfaces. [Compare them in the reviewer](http://localhost:3028/world-seed-detail). This is an assistant artistic shortlist, not a new universal sampling default or a replacement for the original film.

For a still-image fidelity target, keep the [2016×1344 engraved city](../../exports/v002/prompt-study/city-full-material-2k/anchors/0000.png) and [native tidal opening](../../exports/v002/prompt-study/tidal-specific-b/anchors/0000.png). The city combines densely specified architecture with copperplate/lacquer material language and restrained lighting. Its larger-resolution composition has not been animated. Exact prompts are in the three matrices below; the recurrent prompts are in the [case configs](../configs/).

**Main lesson:** concrete material/structure descriptions are a better working direction than a fixed quality suffix, but no wording-only cure for recurrent detail loss was demonstrated. Cleaner outlines do not equal richer surfaces. Lower repaint noise retains more original structure while stronger noise can regenerate more relief; both have visible costs. The original jungle remains selected.

51 native still generations cover four worlds, with neutral/material/quality retests on a second seed. Seventeen recurrent cases add 289 repaints. All 340 unique generation jobs and 4,730 remote files are verified locally. Owned compute and 629 verified ComfyUI duplicates were removed; the shared model volume remains. Estimated GPU compute: $0.83 excluding storage. [Execution receipt](execution-summary.json) · [Noise-pair config audit](controls.json).

## Questions and controls

Does rendering language produce visibly richer material detail and depth across different surreal worlds? Does that appearance survive the existing recurrent animation loop?

First establish fresh opening stills independently of the inherited oil-painted jungle. This is a still-image audition, not a replacement for animation feedback. Round one compares five treatments on three identical scene bodies with matched seeds: neutral description, the previous illustration phrase, material/light language, digital matte painting and generic quality keywords. The three original prompts are separate references, because their scene descriptions also differ. All use the same Krea 2 Turbo checkpoint, Qwen3VL encoder, Qwen Image VAE, native eight-step Euler/simple CFG1 at 1536×1024. No automatic prompt enhancement, added reference conditioning, sharpening or upscaling.

Promising approaches will be retested with different seeds and another scene. Animation will retain warped previous RGB → VAEEncode → partial-noise sampling → next RGB, with the existing three Euler intervals. RIFE remains outside recurrence. Compare initialization, prompt language and temporal detail retention separately; do not treat a sharper still as proof of better moving imagery.

Screen full compositions and native-resolution regions for distinct small structures, credible material texture, dimensional shading, clear atmosphere and artistic interest. Distinguish useful fine detail from outline density or noisy surface patterns. Examine every painting in short recurrent tests and dense displayed-frame windows before recommending a delivery. These are assistant judgments until Olof reviews them.

## Reproduction and provenance

`matrix-01.json` records exact bodies, styles, seeds and full prompts. `stills.py` submits native graphs through the shared Pod client, retains complete run receipts and checks executed/history/embedded graphs, job identities and image hashes. Outputs are preserved under `../../exports/v002/prompt-study/`; later rounds use new immutable IDs. The owned RunPod is billed at $0.89/hour; preserve all outputs before deleting it. Retain the existing model volume.

The [official Turbo guide](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md) recommends natural language and includes both short and paragraph-length examples. The [official expansion template](https://github.com/krea-ai/krea-2/blob/main/docs/expansion.txt) emphasizes grounded attributes and spatial relationships while respecting existing detail. Neither establishes a universal quality suffix or a recurrent-animation recipe. Rechecked 10 October 2026.

## Round 1: first-seed screening

The original jungle re-render has identical decoded pixels to the preserved opening. Native graphs differ only in the output filename prefix. This checks the baseline reproduction independently of file metadata.

All 18 stills were verified and screened in full-frame comparison sheets. Jungle original/neutral/materials/matte/quality and city quality were additionally inspected at native resolution. These are early observations, not a winner selection:

- **Jungle:** the illustration treatment makes the foliage and bridge flatter and more uniformly outlined. Material language improves sculpted shading and highlights but some plants look polished. Matte and quality treatments are credible alternatives, without an obvious richness improvement over the original. The original has especially strong foreground framing and distant scale.
- **City:** the original prompt's richly engraved structures remain a strong reference. Several shorter-body variants reduce the tiny ornament despite explicit quality language. Illustration creates bright, legible, cleaner geometry but changes the atmosphere markedly. The quality suffix produces a credible dimensional scene; it cannot be dismissed as ineffective on this evidence.
- **Crystal:** illustration yields crisp decorative complexity with shallower-looking shading. Materials and matte treatments give rounder volumes and larger smooth facets; they do not obviously improve intricate detail. The quality variant retains more small structures. The original has stronger near/far scale variation than several simplified descriptions.

The common-body variants show that rendering language changes both surface treatment and composition. The original comparisons also change scene phrasing and descriptive density, so they cannot isolate medium alone. Round 2 repeats neutral/material/quality on a second seed, tries two stronger rendering prefixes, and separately retains the original dense description while modifying its medium/light language.

## Round 2: repeatability and descriptive density

All 18 additional stills pass graph/history/image verification and were screened in full-frame sheets. The jungle VFX, micro-detail and full-material variants, city full-material, crystal full-material and crystal quality second seed were inspected at native resolution.

The rendering treatments still do not rank consistently across scenes and seeds. The second city seed has substantial ornament even without a quality suffix. The crystal quality second seed has attractive iridescent ribbons and visible fine branching; the material version has larger, less intricate facets. The micro-detail prefix tends toward clean sculptural or ornamental forms rather than obviously more physical surface texture.

Retaining the full original scene description while revising medium/material wording gives the strongest new city reference and a credible richer jungle alternative. For the crystal, replacing frosted/internal-glow language yields clearer chambers and stairs but also changes their arrangement; it is not an isolated sharpness proof. These prompts preserve more concrete near/middle/far structure than the shorter common bodies. This motivates carrying detailed, surface-specific descriptions forward, rather than adopting a universal adjective suffix.

The recurrent jungle comparison uses the original RGB opening, original camera, original seed/noise schedule and original three-interval sampler. Only the two travelling rendering phrases change for materials, VFX, quality and micro-detail. A separate full-material case holds the longer description and should be compared with the prior `d01-full-prompt`, not described as a rendering-only change from the short baseline.


## Round 3: a different world and resolution

The transfer scene is an alien tidal basin: vermilion mineral terraces, narrow turquoise pools, copper spires and an enormous nested ivory shell reflected in a cobalt sea. It has neither the earlier bridge/doorway composition nor vegetation. Six treatments were compared at two matched seeds. A scene-specific material paragraph describes porcelain edges, pitted shell layers, nacre, sedimentary laminae, quartz grains, copper veins, restrained highlights and sharp reflections.

Both scene-specific stills are strong candidates. `tidal-specific-b` is the preferred new opening: the whole shell remains visible, the foreground channel gives the camera a route, and fine eroded edges contrast with quiet water and sky. The neutral description also performs well. The result does not establish that every added material sentence improves the image. Generic material/quality variants sometimes produce smoother surfaces or crop the shell; there is no consistent cross-scene winning suffix.

Three separate 2016×1344 generations retain the full-material prompts and seeds for jungle, city and crystal. They produce rich larger images, especially the engraved city, but changing the latent grid also changes composition. These are native resolution auditions, not aligned before/after sharpness tests, and were not tested in recurrence. All 51 still generations pass graph/history/PNG/hash checks. Full-frame sheets were screened, with selected images inspected individually.

## What transfers into prompting practice

Use a natural paragraph that establishes the impossible world, then places its large structures in space. Give the foreground, middle distance and background distinct jobs. Describe what the small details actually are and what material carries them. Specify light direction, highlight restraint, shadow behavior and atmosphere when they matter to the desired appearance. Keep a quiet area so detail has contrast.

For example, the useful part of the tidal treatment is:

> The shell has thin porcelain-like edges, finely pitted exterior layers and nacre within its deep chambers. Terraces expose thousands of razor-thin sedimentary laminae, tiny angular quartz grains and branching copper veins. Sharp reflected edges lie on the still water. Restrained highlights and clean contact shadows reveal physical relief; clear air, deep focus and finely resolved distant silhouettes.

This is our tested prompt text, not an official quotation. Adapt the material nouns and lighting to each world instead of copying every noun into unrelated scenes. Preserve a successful prompt's concrete content when revising its medium. “Digital illustration” changed rendering toward outlines and flatter graphic forms here; “3D environment” and VFX language sometimes made surfaces look polished or clay-like. None of those labels is a reliable fidelity control.

Prompt length was not independently controlled. The richer full descriptions often beat the simplified descriptions, but that could reflect their scene content rather than length. There is no evidence for a fixed ideal word count. Quality keywords are not proven useless: several quality variants were attractive, but the ranking changed across seeds and scenes. Writing “8k” did not change the configured output dimensions.

These recommendations come from four subjects and small matched-seed comparisons, judged visually by the assistant. They are a practical starting point, not a universal Krea quality ranking. Initial-image prompting and recurrent detail retention must be evaluated separately.

## Recurrent tests: findings before finishing

Seventeen two-second cases each use eighteen paintings, including a shared opening and seventeen new repaints. The previous-image feedback loop, three Euler intervals, seed schedule and motion are unchanged within each stated pair. The lower-noise cases separately change starting noise while holding the corresponding full material prompt fixed.

- Five jungle prompt treatments at the original noise schedule all lose bark/moss texture and tend toward broader, smoother or outlined forms. The full material description preserves more of the original world identity, but is not a clear fidelity improvement. The four short rendering replacements do not beat the preserved original convincingly.
- City original/full-material and crystal original/full-material both simplify fine structures during recurrence. The city pair becomes cleaner, rounded architectural ornament; the crystal pair thickens delicate lattice and turns it into more regular patterns. Rewording alone does not prevent the effect.
- The tidal specific-material treatment affects the shell surface, including growing dark pits, but at standard noise its fine terrain texture also smooths away. The wording has an effect without necessarily achieving the intended scale of detail.
- The city lower-noise case visibly retains more engraved structure and material shading than its matched standard-noise case. This is a separate sampling result, not evidence that the prompt alone solved detail loss. Jungle and tidal lower-noise screening and the finished shortlist are recorded below.


### Noise controls and their limits

At 0.25, the jungle retains more of the opening's leaf/root layout and the city retains many more engraved structures than their stronger repaint counterparts. Both still lose contrast, material sparkle and tiny irregular texture, becoming muted or patterned. The jungle 0.40 case is closer to the simplified stronger-repaint treatment. These settings do not make every frame as rich as the native opening.

The tidal 0.25 case keeps the copper spires, granular terraces and shell geometry more stable. The 0.60 material prompt grows conspicuous dark pits in the shell and simplifies the terrain. That illustrates a temporal prompt hazard: a small surface feature named in a still prompt can become a large repeated motif after feedback. The effect is visible, but this is not a controlled test of removing that one word.

A separately recorded 0.85 case tests stronger regeneration with the same tidal prompt. Early paintings have rougher, more dimensional terrain and shell edges, but the planet grows abruptly and the shell shifts substantially. A final 0.72 case samples between that regeneration and the standard 0.60 setting. Neither changes the feedback architecture or adds reference conditioning.

### Review evidence

First pairs are checked before full RIFE finishing. Finished clips preserve all eighteen paintings, have 48 displayed frames at 24 fps, native 1536×1024, and use the same 4.5× retime with a short moving tail. There is no sharpening, upscale or frame blending added to these deliveries. RIFE in-betweens never initialize generation.

The city 0.25/0.60 pair was inspected at six overview times and every displayed frame in 0.875–1.125s and 1.750–1.959s, including the final moving tail. The lower-noise city keeps more complex ornament but develops subdued shading; the standard-noise city has cleaner, simplified architecture. Neither shows an obvious broken frame edge or major doubled object in those windows. This is frame-based screening, not a claim of subjective normal-speed playback assessment.


The tidal 0.25/0.60 pair and jungle lower-noise/original pair received the same six-point overview and dense middle/end inspection as the city. The tidal lower-noise clip holds its shapes more consistently but develops regular dots and smooth relief. The jungle lower-noise clip becomes muted and soft; the original has stronger contrast and clearer dark doorway, so it remains preferable for the existing film. That jungle comparison changes both text and noise; the separate matched-noise tests above isolate those questions.

The 0.85 tidal clip received a six-point overview, every frame from 0.250–0.625s around the planet expansion, and every frame from 1.750–1.959s. The planet grows over only a few frames, with briefly smeared intermediate contours. This is a real continuity defect, not planned camera acceleration. Later frames have convincing fine granular shores and stronger material relief; the native final painting was inspected individually. The constant camera curve itself contains no repeated acceleration/braking.

The 0.72 follow-up does not resolve the tradeoff: a second moon briefly appears around 0.54s and disappears by 0.67s, and shell pits continue to grow. Its complete painting sequence was screened; it is retained as a selectable diagnostic, not the recommendation. Eight cases have full verified 48-frame MP4 deliveries; the remaining cases retain their original painting chains and all generation evidence. No longer film was generated from a recipe still showing these defects.

## Reproduce and continue

Run from `apps/deforum` using the locked environment:

```sh
uv run --locked python projects/world-seed/experiments/prompt-study/stills.py check projects/world-seed/experiments/prompt-study/matrix-01.json
uv run --locked python projects/world-seed/experiments/film.py check ps-tidal-specific-n085
uv run --locked python projects/world-seed/experiments/finish.py ps-tidal-specific-n085 check --version v002
```

Repeat the still check for matrices 02 and 03. Rendering requires an explicitly owned Pod deployment and preserved source lineage; the session Pod is deleted. Existing output IDs are immutable. The next useful test is preserving this stronger material treatment while controlling its larger structural changes, on more than one subject. Do not spend another round merely adding “high quality” synonyms to the jungle. No architecture change or new model was evaluated in this study.
