# Noise schedule and clean-reference study

2026-10-12. Olof approved execution of the [staged research plan](../../../../../../docs/research/reference-conditioned-repainting.md). Original World Seed film remains selected. Masks, pixel copyback, refinement and resolution changes are excluded.

## Controls and acceptance

Two preserved 1536×1024 paintings: `tidal-specific-b` (shell, planet, mineral terraces) and `city-full-material-a` (ornate avenue, architecture, circular opening). Keep full material descriptions, CFG1 and plain Euler. Initial probes are stationary and share seed/input across schedule arms. Subsequent recurrent branches feed back their own output; moving branches reuse the existing uninterrupted camera phrases. All cases freeze input hashes, exact sigmas, prompts, seeds and initialization/reference policy before generation.

First compare N60, N72-scaled and N72-fixed-tail with two seeds per world: twelve one-repaint probes. Check stationary recurrence before movement. Then establish the community Krea Identity Edit v1.2 recipe using its supported eight-step full-noise target. That is a feasibility control. The hybrid retains partially noised previous-image initialization and adds the same already-warped image through both clean VAE reference tokens and image-grounded language conditioning. Reference boost starts at 1, LoRA strength 1, grounding resolution 768. No second reference is supplied.

Look for persistent major silhouettes/counts and clear fine relief, without locking the camera or introducing doubling. A still improvement does not establish video quality. Screen all raw paintings in overview and selected dense interpolated windows before asking for human taste review. If native editing works but three-step hybrid fails, check a frozen eight-step partial schedule before rejecting the recipe.

## Execution

`run.py` reuses the shared graph, recurrence, transport and immutable record helpers. `noise-probes.json` freezes the first twelve cases. Outputs live under `projects/world-seed/exports/v002/nr-*`; original and executed graphs, source copies, PNG metadata, history and checksums are preserved in the shared v002 run archive. The script validates parent hashes, recomputed camera transforms, exact graph/history equality, embedded PNG graph and dimensions.

Infrastructure receipts are private under `work/noise-reference-session/`. The study uses the retained model volume, pinned ComfyUI 0.34.0 runtime, a separate locked runner environment and one RTX PRO 4500 Blackwell at $0.72/hour. The edit node and adapter are isolated additions; no ComfyUI core patch or base-weight replacement is used. See `assets.json` for revisions and the verified adapter SHA256.

## Results

The clean-reference recipe is a useful structural-preservation result, but it does not meet the requested sustained high-detail look. Keep the original film selected. [Compare the two worlds](http://localhost:3028/world-seed-reference): the default pair is the tidal scene; the two city clips are available in the same selector. Each is two seconds, eighteen paintings and 48 delivery frames. These are matched new controls, not excerpts from the original film.

| Stage | Cases | New paintings | Purpose |
| --- | ---: | ---: | --- |
| Noise probes | 12 | 12 | Two worlds, two seeds, three schedules |
| Stationary noise recurrence | 6 | 36 | Six repaints per world/schedule |
| Native edit controls | 4 | 4 | Supported full-noise eight-step editing |
| Three-step hybrid holds | 2 | 12 | Six repaints per world |
| Eight-step hybrid holds | 2 | 12 | Separate sampling comparison |
| Explicit color/detail wording | 2 | 12 | Separate preservation-prompt comparison |
| Moving baseline/reference | 4 | 68 | Seventeen repaints per world/recipe |
| Moving second-seed check | 4 | 32 | Eight repaints per world/recipe |
| Water-color transformation | 2 | 8 | Four repaints per recipe |
| Total | 38 | 196 | Original input copies are not generation jobs |

Twelve no-motion probes across two seeds and two scenes and six six-repaint holding chains show no consistent detail/preservation win from the tested noise schedules. N72 fixed-tail still simplifies the terrain and reconfigures city architecture. N72-scaled remains an established comparison, not a claimed optimum.

All four native eight-step reference controls run successfully. Their major shapes and original compositions remain much closer to the inputs than the plain three-step repaints; the first tidal seed changes the lower-right mineral shelves. These full-noise controls only establish editing capability.

The three-step hybrid keeps the shell, planet, hollow spires and city layout much closer through six recurrent paintings. It still gradually warms the palette and softens city ornament. Eight updates, formed by splitting the three original intervals into 3/3/2 pieces, show nearly the same limitation on both scenes. No eight-step advantage is selected. A separate prefix comparison adds explicit color, lighting and tiny-detail preservation while retaining the full material description. Six-painting tests on both worlds look nearly unchanged; this extra wording is not selected.

The longer moving tests expose the remaining failure clearly. Both references follow the planned zoom, lateral drift and bank. The tidal shell and open spires remain recognizable; the city keeps its avenue, circular opening and floating central object. The ordinary repaints redesign these structures more. However, by painting 17 the reference city's tiny relief has become broad, smooth ornament, its blue object has become a pale faceted lattice, and the lighting is substantially more amber. Tidal grain becomes pitted and faceted, with changing shell chambers and a warmer palette. Major composition is more stable; original surface detail is not. No abrupt doubled major silhouette was apparent in the inspected dense windows, but texture changes remain.

These judgments come from all raw paintings in the main moving comparisons, selected native-resolution paintings, first interpolation intervals, and every displayed frame in 0.50–0.75s and 1.50–1.75s windows. They are assistant frame-screening observations, not a human playback preference or a perceptual metric. Encoded MP4s are for playback; native PNGs are the detail evidence. The two-second duration limits any claim about sustained thirty-second scenes.

All four eight-repaint second-seed chains show the same broad result: clean references retain the original scene structure more closely; the baseline changes spires, chamber shapes, towers and iris geometry more. The city reference still warms and simplifies. This reproduces the qualitative result on another noise trajectory, not a statistical estimate of success rates.

The four-repaint water-edit control gradually turns the reference branch's water greener while largely retaining shell and terrace structure. The baseline changes color more strongly and quickly, accompanied by greater restructuring of the shell, terraces and spires. Thus reference conditioning does not completely freeze prompt-directed change, but it attenuates this edit. This small color test does not establish that a major world transformation will work. All five paintings per branch were screened in sequence.

## Interpretation and next decision

A rolling clean reference gives the model a stronger view of the previous painting, but that previous painting already includes earlier simplification and color drift. The observed sequence is consistent with that limitation; it does not isolate VAE loss, resampling, adapter bias or denoiser behavior as its sole cause. Extra sampling or preservation adjectives did not solve it in the tested arms.

Olof rejects the strength-1 reference result as too static and warm after inspecting the tidal scene. He does not consider this a successful film treatment and asks to keep the next check to that one artwork. His mode-collapse explanation remains a hypothesis. He rules out the proposed original-keyframe reference for now because it could conflict with a world evolving far from its opening.

The approved follow-up tests [lower reference influence](reference-weights.md) at 0.5 and 0.2, followed by [0.05 and 0.01](reference-low-weights.md), using the already-moved previous painting throughout. The very low values permit more local redesign, especially larger shell holes at 0.01, but do not resolve warming or fine-detail simplification. Olof subsequently finds 0.01 promising and requests further parameter exploration; that branch remains under active development. Reference attention boosts are influence controls, not literal percentages or pixel blends. [Pinned author implementation and usage](https://github.com/lbouaraba/comfyui-krea2edit/tree/86f886dac23013d88996e3a2e99093ba44d322fb).

The approved [sampler and reference-control comparison](sampler-reference-controls.md) completes 85 new paintings: 0.60 Euler versus gentle ancestral sampling without a reference, then separate edit-adapter-strength and grounding-resolution variants around 0.01 with a fresh same-GPU control. No clear ancestral advantage is found. Half-strength editing reduces some amber treatment while redesigning shapes more; grounding 384 does not improve color or grain. No new production recipe is selected.

Masks, pixel copyback and refinement remain outside this study. No new production recipe is selected from these results.

## Reproduce and inspect

All 196 generation jobs pass exact graph/history, PNG metadata, parent-image hash and recomputed-warp checks. All 2,858 remote files (1,718,357,198 bytes) match their local copies. The four main deliveries pass finishing and provenance checks; the reviewer validates decoding, timestamps and dimensions. Its page returns HTTP 200 and all four original-media range requests return 206. Three server tests and focused Ruff checks pass. [Execution receipt](execution-summary.json).

The queue was empty before cleanup. All 392 owned ComfyUI input/output duplicates were hash-checked against preserved originals before removal; the two temporary adapter/node symlinks were removed. The owned Pod is deleted and absent from the Pod list, while the 50GB model volume remains. Estimated compute is about $0.72, excluding retained storage. Private transfer manifests, archives, runtime source/logs and cleanup receipts remain in `work/noise-reference-session/`. The local `media-review` service remains available through Terminal Manager for human review.

From `apps/deforum`, run `uv run --locked python projects/world-seed/experiments/noise-reference/run.py check projects/world-seed/experiments/noise-reference/suite.json`. Generation uses `render` instead of `check`, an explicit `--deployment` receipt and optional `--ids`; completed records cannot be overwritten. `suite.json` is the union of the frozen stage matrices.

`assets.json` pins the author node revision and full-rank adapter hash. The ordinary Krea model, Qwen3VL encoder and VAE remain the existing pinned assets. In the native controls the shared runner records the uploaded reference under its generic `initialization_sha256` field, but the executed sampler graph uses `EmptySD3LatentImage`; all hybrid cases use `VAEEncode(previous warped painting)` for initialization. In every reference case, the same uploaded image also supplies the clean appearance and image-grounded language paths.

This compares complete editing recipes, including the adapter and preservation instruction. It does not measure a reference-only causal effect with the rest of the model unchanged. No direct percentage interpretation should be attached to reference attention boosts.

## Adapter and sampler follow-up

Olof prefers the half-strength editing adapter for its reduced color drift. The [follow-up](adapter-sampler-followup.md) tests editing strengths 0.25 and 0.75 around that control, plus Heun and DPM++ 2M against Euler at noise 0.60 with the reference paths off. [Frozen matrix](adapter-sampler-followup.json).

The follow-up is complete: 0.25 stays cooler but invents moons and honeycomb-like geometry; 0.75 keeps a quieter sky but warms more. Neither additional sampler demonstrates a fine-detail gain over Euler. Keep the human-preferred 0.5 reference baseline; new-clip preference remains pending. Both repeated controls reproduce prior paintings and videos exactly. All 102 jobs and 1,446 remote files are verified locally, the GPU is deleted, and the model volume remains. Estimated compute $0.56 excluding storage. [Execution receipt](adapter-sampler-followup-execution.json).
