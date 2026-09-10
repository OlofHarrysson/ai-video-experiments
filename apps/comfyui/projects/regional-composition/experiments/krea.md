# Krea 2 Turbo regional composition

## Question and fixed recipe

Olof approves a two-seed comparison of one complete prompt, masked regional prompts, and global refinement of the regional result. Keep the red robot / blue glass tree scene. This is a still-image experiment, independent of the Deforum animation runner.

Generate all outputs at 1024 × 1024. Holding resolution constant separates refinement from latent enlargement; an enlarged second stage can follow if this establishes useful regional control. Seeds are 21001 and 21101, with refinement seeds 21004 and 21104.

- Krea 2 Turbo FP8, Qwen3VL 4B FP8 text encoder, Qwen Image VAE. Reuse the three pinned assets and hashes from `apps/deforum/serverless/modern-models.json`.
- ComfyUI commit `12d5279438bfefc058a269eae805ceab6047777f`, the existing verified Krea runtime. Use core nodes only, no LoRA or automatic prompt expansion.
- Full generations: eight steps, Euler, simple schedule, CFG 1. Positive descriptions; zeroed negative conditioning.
- Regional generation: background strength 0.25; robot and tree strength 1.0. Original disjoint rectangles (64,384,384,512) and (576,384,384,512), feathered inward 32 pixels, full-canvas conditioning (`set_cond_area=default`). The weighted predictions are combined; the masks do not clip final objects.
- Refinement: the exact regional output latent feeds a second sampler, with freshly added noise and one complete scene description. Use the final three intervals of the native eight-step schedule via BasicScheduler → SplitSigmas(step=5) → SamplerCustom. No encode/decode round trip in its initialization, no enlargement, no third stage.

Both full generations use the same seed, dimensions and sampling settings. Their text is constructed from the same object and environment sentences, with explicit left/right placement in the complete prompt. Consequently this is a practical recipe comparison, not a pure mask-only ablation. Regional prompts require multiple model predictions per interval, so eight steps do not imply equal inference cost.

## Review criteria

Compare subject count, placement, blue glass material, shared lighting and ground contact, edge artifacts, and changes introduced by refinement. Preserve every generation, editable workflow and API graph. Do not select seeds after viewing the outputs. Inspect both seeds before recommending a recipe.

## Infrastructure

Use a short-lived owned Pod in an approved region, with temporary storage. An initial US A40 request returned no capacity and created no Pod. The subsequent L40S request in US-TX-4 succeeded at $1.09/hour, with 50 GB temporary Pod volume and the existing official CUDA 12.8 image. The separately owned Deforum Pod and retained Romania network volume are outside this experiment.

## Sources

- [Krea prompting guidance](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md): natural-language descriptions, detailed prompts.
- [Official ComfyUI workflow](https://docs.comfy.org/tutorials/image/krea/krea-2): native model files and eight-step Turbo generation.
- [Existing native-tail implementation](../../../../deforum/projects/modern-model-study/experiments/turbo_schedule.py), extended to three intervals in `turbo_transitions.py`.

## Focused prompting follow-up

The first regional recipe omits the robot on seed 21001 and merges the tree into the robot's arm on 21101. A bounded follow-up adds only `The robot stands on the left.` and `The tree stands on the right.` to their respective regional prompts. Preserve the first results; use both original seeds, masks, strengths and schedules again. The complete-prompt control stays unchanged. This tests explicit language alignment with full-canvas masked predictions, not another regional algorithm.

## Results and assistant review

Completed 2026-09-10. Both original seeds and both positioned follow-ups executed successfully. All images are 1024 × 1024.

| Recipe | Seed 21001 | Seed 21101 |
|---|---|---|
| One complete prompt | Clear separate robot and tall glass tree; strong material and lighting | Clear separate robot and tall glass tree; similarly coherent |
| Original regional prompts | Robot absent; small glass tree | Robot holds the tree canopy like a branch; no separate rooted tree |
| Original regional + global refinement | Robot appears with duplicated/stacked body parts | Separates robot and tree, but substantially changes the tree and robot |
| Positioned regional prompts | Separate subjects; robot has a box body without a distinct conventional head | Separate complete robot and glass tree, with clear ground contact |
| Positioned regional + global refinement | Adds a readable face to the box robot and changes hands, legs and canopy | Coherent separate subjects; changes arms, body panels, antennae, branches and roots |

**Recommended regional starting point:** explicit position descriptions plus feathered masks. Seed 21101 with global refinement is the assistant's preferred regional example. Seed 21001 retains its unusual box-shaped robot. The one-complete-prompt version is also a strong baseline and produces a much larger tree; these two straightforward left/right scenes do not establish that masks provide better placement than text alone.

The prompting adjustment fixes the missing/merged-subject problem in these two seeds. This is small-sample evidence, not a guarantee for other compositions. Full-canvas masked conditioning weights model predictions spatially; it is not object segmentation or a hard constraint on final object bounds. One plausible explanation is that position descriptions align the full-canvas prediction with the area in which it is retained. We did not inspect internal attention or isolate that causal explanation.

The three-interval global pass is a substantial redraw: it can repair object binding and make features more readable, but it changes designs. This is not a seam-only finishing pass. The positioned regional images already have integrated ground and lighting; the run does not establish that a second pass is always necessary.

**Olof's feedback:** the results look good, but this simple composition does not make regional prompting's advantage clear. He approves the [three-robot layout benchmark](krea-layouts.md) to test a harder case. This is not a selection of the assistant's preferred seed or an endorsement of regional prompting over the complete prompt.

### Comparisons and editable workflow

- [Original three-way comparison, both seeds](../exports/krea-comparison-v001/comparison.png)
- [Positioned three-way comparison, both seeds](../exports/krea-positioned-v001/comparison.png)
- [Editable ComfyUI comparison](../workflows/krea-regional-comparison.json) and [API graph](../workflows/krea-regional-comparison.api.json), exact exports from the positioned seed-21101 run. PNG metadata also embeds the workflow. The API graphs executed successfully; this round did not reopen the exported graph in the frontend.
- [Original inventory](krea-comparison-v001-inventory.json) and [positioned inventory](krea-positioned-v001-inventory.json) identify every image/latent and its hash.

### Execution and verification

Four successful ComfyUI jobs saved 12 PNGs and 12 latents. The positioned follow-ups save the unchanged complete-prompt controls again; their pixels and latent tensor payloads are identical to the respective original controls. There are ten distinct generated images across the four jobs.

All 24 files under the owned remote output directory were downloaded, full-decoded where applicable, and matched against remote SHA256 hashes. Each run preserves the exact runner source, API graph, editable graph, schemas, model metadata, system statistics, history and submission/download receipts. Graph checks verify that both initial samplers use the same seed and initial latent and that the saved regional latent directly initializes refinement.

| Run | ComfyUI job time |
|---|---:|
| Original seed 21001 | 39.149 s, including model initialization |
| Original seed 21101 | 24.651 s |
| Positioned seed 21001 | 19.311 s, complete-prompt branch cached |
| Positioned seed 21101 | 19.137 s, complete-prompt branch cached |

Model download/hash verification took 191.515 seconds; runtime preparation took 27.967 seconds and overlapped the downloads. Runtime: ComfyUI 0.34.0 at the pinned commit above, frontend 1.49.6, Torch 2.10.0+cu128, NVIDIA L40S. The three pinned model sizes and hashes were verified before inference.

The owned Texas Pod `jih2fwxtspntdx` and its temporary Pod storage were deleted after archive verification and an empty queue; a subsequent lookup returned 404. Its approximately 13m41s lifetime corresponds to roughly $0.25 of listed GPU compute, plus temporary storage. The account balance changed from $38.3842 to $37.9765 during the wider session, which also included another task's compute; that balance delta is not this experiment's bill. Other-task resources and the separately authorized retained model volume were preserved.

### Reproduce

Prepare a fresh owned Pod with the existing `setup_modern_pod.py` and `prepare_pod_models.py --krea-only`, then provide its explicit deployment receipt:

```sh
uv run --script apps/comfyui/projects/regional-composition/experiments/run_krea.py run \
  --deployment PATH_TO_ACTIVE_DEPLOYMENT_JSON --seed 21101 --positioned
```

Omit `--positioned` for the original local descriptions. Use `--seed 21001` for the other preselected seed. Use `collect --deployment ... --folder EXISTING_RUN` to recover an interrupted download without repeating generation. The deleted deployment receipt cannot submit new work.
