# Three-robot layout benchmark

## Accepted question

Olof likes the Krea robot/tree results but questions whether regional prompting helps more than one complete prompt on that simple scene. The next accepted comparison tests three robots with distinct colors/props, deliberately different sizes and two prescribed arrangements. Do regions make composition changes more predictable?

Eight images: two layouts × two seeds (21001/21101) × two methods (complete prompt / masked regional conditioning). Use Krea's established native eight-step Euler/simple/CFG-1 generation at 1024 × 1024, with the same pinned model assets and ComfyUI runtime as the [first Krea study](krea.md). First generation pass only; no refinement, enlargement, LoRA or prompt expansion. Do not select seeds or adjust the recipe after viewing the eight results.

## Target arrangements

The identities and props remain red/flower, blue/open umbrella, yellow/flag. Layout B rotates those identities through the same three spatial slots.

| Slot | Rectangle x,y,width,height | Target robot body height | Layout A | Layout B |
|---|---|---:|---|---|
| Lower-left foreground | 32,448,384,512 | ~40% of image | Red + flower | Yellow + flag |
| Right middle distance | 624,384,352,384 | ~25% of image | Blue + umbrella | Red + flower |
| Upper-centre far distance | 448,288,160,224 | ~12% of image | Yellow + flag | Blue + umbrella |

The rectangles provide room for each robot and its held prop. They are not ground-truth robot bounding boxes, and the sampler masks do not guarantee final boundaries. All three rectangles are disjoint; 32-pixel inward feathering and background/region strengths 0.25/1.0 remain unchanged. The small upper slot is deliberately demanding, including enough room for its prop.

Both methods receive identical subject, placement and body-size sentences. The complete prompt concatenates all three plus shared separation/environment descriptions. Regional conditioning receives one subject paragraph per rectangle plus the same separation/environment text; its weak full-canvas background receives only the environment description, as in the previous Krea recipe. This compares practical conditioning recipes, with unequal numbers of model predictions per sampling interval.

## Review before a recommendation

Inspect all eight images for exactly three robots; correct robot color and held prop; intended left/right/upper-centre placement; large > medium > small body-size order; and clean, coherent artwork. Inspect each method's response when changing layout at the same seed. Keep body size separate from umbrella/flag extent. Record ambiguous judgments rather than inventing pixel-perfect measurements or a single quality score.

Save target diagrams, original images/latents, contact sheets, exact API/editable graphs, prompt metadata, history, model verification and remote/local hashes. Preserve every output. API execution and visual review are distinct from reopening the editable export in ComfyUI's frontend.

Preflight confirmed disjoint in-canvas rectangles, identical subject clauses in both conditioning paths, and matched first-pass sampling controls. The deployed Krea/Qwen tokenizer produces 286 tokens for each complete prompt including its system template; the local prompts use 169–173 tokens. Source inspection confirms that this tokenizer does not impose a short prompt-length limit. The long description is not being truncated to an SDXL-style context window.

## Execution

Use one owned Texas L40S Pod at the listed $1.09/hour and 50 GB temporary Pod volume. No existing Pod was active at preflight. Preserve the separately authorized model volume. Delete the owned Pod after every output is verified locally and its queue is empty.

## Results and assistant review

All eight prescribed images completed on 2026-09-10. No seed selection, prompt adjustment or refinement was applied after viewing them.

**The complete prompt is the stronger overall recipe in this benchmark.** All four complete-prompt images contain three distinct robots with the requested dominant body colors, all three correctly assigned held props, and the intended large > medium > small order. Both methods respond to the A→B identity/size rotation. Regional conditioning places the distant robot closer to the specified upper-centre box, but damages subject completeness and prop rendering.

| Layout / seed | Complete prompt | Masked regional prompts |
|---|---|---|
| A / 21001 | Three robots; red holds flower, blue holds open umbrella, yellow holds flag. Correct size order. Distant yellow robot is left and above its prescribed box. | Three correctly colored robots with clearer upper-centre placement. Red's hand is empty, blue has no umbrella canopy, yellow holds a pole-like object without flag fabric. |
| A / 21101 | Three robots with all three props and correct size order. Red faces away, which was not prohibited. Distant yellow robot is left and above its target box. | Three robots, but no correctly held flower, open umbrella or flag. Yellow has a bare pole; red has brown petal/hair-like growth on its head instead of holding a flower. |
| B / 21001 | Correct rotation: large yellow with flag left, medium red with flower right, small blue with open umbrella in the distance. Blue remains left of the target box. | Correct dominant colors and broad positions, but both large yellow and medium red lack heads; their size difference is weak. Small blue holds a bare shaft instead of an open umbrella. All three complete held props fail. |
| B / 21101 | All three props, correct color assignment and size order. Distant blue remains left of the target box. | Three robots in the intended broad positions. Yellow and blue appear connected through a long pole; blue also holds an umbrella-handle fragment. Red's hand is empty and its head is flattened. No complete requested held prop. |

These are manual visual judgments, not automated detections. A pole without flag fabric and a handle/shaft without an open canopy count as incomplete props. By that definition the complete-prompt images deliver 12/12 requested prop assignments, while the regional images deliver 0/12 complete prop assignments. All eight images contain three recognizable robot bodies with the correct dominant color assignment. This does not mean every body or head is intact.

### What this establishes

- The complete prompt remains competitive on three same-category subjects with different colors, props and relative sizes. Its A→B changes are consistent across both seeds.
- Regional conditioning has a visible positional effect: the distant robot is more central and closer to the assigned box. It also leaves more sky and open meadow. Those are useful controls, but they do not compensate for missing props and damaged robots in this recipe.
- Neither method accurately follows the requested 40%/25%/12% body heights. The complete-prompt foreground and middle-distance robots are visibly larger than requested. Regional sampling does not establish precise sizing either; layout B's headless pair is particularly unsuitable for interpreting body-height control.
- The result applies to this full-canvas masked-prediction recipe, these mask extents and strengths, and this model/schedule. It does not rank every regional method or prove that Krea cannot support better regional control.

A plausible explanation for the missing heads and props is that the complete object predicted under a local prompt extends beyond the region where that prediction contributes strongly. The mask is not a rigid bounding-box instruction to the model. That explanation is not isolated here: coverage, weighting, full-scene context and conditioning method remain possible factors. A targeted mask-coverage/context diagnostic would be more informative than making the scene still harder. Keep the complete-prompt results as the working baseline while evaluating such a change.

### Artifacts

- [Layout A comparison](../exports/krea-layouts-v001/comparison-A.png) and [target diagram](../exports/krea-layouts-v001/target-A.png).
- [Layout B comparison](../exports/krea-layouts-v001/comparison-B.png) and [target diagram](../exports/krea-layouts-v001/target-B.png).
- [Exact output inventory](krea-layouts-inventory.json): all eight images and eight latents, with hashes and source runs.
- Layout A [editable graph](../workflows/krea-layout-A.json) / [API graph](../workflows/krea-layout-A.api.json).
- Layout B [editable graph](../workflows/krea-layout-B.json) / [API graph](../workflows/krea-layout-B.api.json).

Both workflow pairs are exact exports from the executed seed-21101 runs. They include the complete-prompt and regional branches and their diagnostic saves. PNGs also embed the editable workflow. The API graphs ran successfully and the exported sockets/widgets were checked against node schemas; this round did not reopen them in the frontend.

### Verification, timing and cleanup

Four successful jobs saved eight PNGs and eight latents. Every image was decoded locally and visually reviewed at full resolution. All 16 files in the owned remote output directory were downloaded and matched against remote SHA256 hashes. The review script checks the shared seed, initial latent, sampler parameters and exact subject clauses between methods, plus archived runner/helper hashes. Each run retains node schemas, model revisions/hashes, workflow JSON, history, runtime statistics and submission/download receipts.

| Pair | ComfyUI job time |
|---|---:|
| A / 21001 | 41.138 s, including initial model loading |
| A / 21101 | 29.028 s |
| B / 21001 | 30.222 s |
| B / 21101 | 29.339 s |

All times cover both methods and their saves. The regional branch makes more model predictions per interval; the shared eight-step setting is not equal compute. These job timings exclude setup, HTTP collection, local review and idle time.

The same pinned three Krea assets passed hash verification. Runtime preparation took 27.658 seconds; downloads plus verification took 597.451 seconds, with both preparations overlapping. Runtime: ComfyUI 0.34.0 at commit `12d5279438bfefc058a269eae805ceab6047777f`, frontend 1.49.6, Python 3.12.3, Torch 2.10.0+cu128, L40S. Setup/download time dominated inference time on this uncached host.

Owned Texas Pod `9k0ek1rdbdebwk` and its temporary storage were deleted after full archive verification and an empty queue. A subsequent lookup returned 404. Its approximately 21.6-minute lifetime corresponds to about $0.39 of listed GPU compute, plus temporary storage; this is an estimate, not an invoice. The separately authorized network volume was preserved. Private infrastructure/account receipts remain under `apps/comfyui/work/krea-layouts/`.

### Reproduce

After preparing the pinned Krea runtime and assets on an approved-region Pod, use its explicit deployment receipt:

```sh
uv run --script apps/comfyui/projects/regional-composition/experiments/run_layouts.py run \
  --deployment PATH_TO_ACTIVE_DEPLOYMENT_JSON --layout A --seed 21001
```

Repeat with A/21101, B/21001 and B/21101. Each job generates both methods. Use the `targets` action for diagrams, or `collect --deployment ... --folder EXISTING_RUN` after an interrupted collection. The closed deployment cannot submit new work.
