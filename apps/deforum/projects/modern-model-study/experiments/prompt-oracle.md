# Simplified Oracle prompt

## Plan before rendering

One case, `simple`, tests one simplified natural-language Oracle description. The planned reference was `oracle-steps-v001/high3/cadence-24`; execution uses the fresh unchanged `three-directions-control-v001/high3/cadence-24` control from the same runtime, as explained below. Hypothesis: fewer competing background-detail demands may make the face easier to develop while retaining the architectural composition. This is a content-simplification experiment, not a claim that shorter prompts improve Krea or protect identity.

The [local prompting notes](../../../../../docs/research/prompting-for-feedback.md) distinguish resulting-scene descriptions from edit instructions. The [official Krea guide](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md), checked 2026-09-10, recommends natural language, favors detailed prompts and also demonstrates concise descriptions. This experiment freezes one authored description without prompt expansion or imperative editing language.

### Exact simplified Oracle prompt (2–11 seconds)

> A surreal visionary painting of a porcelain mechanical oracle, seen in a close frontal portrait. The large, clearly readable face occupies the middle half of a wide composition, with luminous turquoise eyes, ivory ceramic skin and a calm, enigmatic expression. Curved architectural ribs frame the head and recede into deep black space, forming a living cathedral around the face. Translucent cyan glass and small amber lights accent the ivory architecture. Strong sculptural side lighting gives the face and surrounding ribs tactile three-dimensional form.

### Exact unchanged cathedral prompt (1 second)

> A richly painted surreal living cathedral viewed from inside a vast organic chamber. A huge curling ivory arch rises close to the viewer on the left and twists overhead; its surfaces transform between carved bone, coral polyps, copper machinery and intricate miniature buildings. At the center a glowing amber seed floats above a dark pool, framed by several progressively smaller arches that spiral into a deep turquoise abyss. Broad sculptural foreground forms frame countless delicate tendrils and tiny illuminated windows farther away. Vermilion coral folds and oxidized copper filigree run through the architecture like veins. Pools of near-black shadow separate the layers. Warm light from the seed grazes the ribs while cold teal light seeps from distant openings. Painterly visionary science-fiction art, intricate but readable, dramatic depth, tactile mineral textures, a feeling of ancient intelligence continuously growing into new structures. Wide composition with the luminous seed slightly right of center and the sweeping arch dominating the foreground.

### Matched recipe

Reuse the same archived opening; generate no opening image. Eleven repaints: cathedral at 1s, Oracle at 2–11s. Every repaint uses Krea Turbo FP8 with warped-previous-image initialization, matched incrementing seeds, CFG 1, Euler, and the exact high3 manual sigma string `0.600000000000, 0.512844085693, 0.310901075602, 0.000000000000`. Native 24 fps, 12 seconds, cadence 24, 1536×1024, identical time-based Lanczos twist/expansion. The inherited motion settles at local 7s. Graph construction delegates directly to `oracle_steps.graph('high3', seed)` before replacing Oracle text and the SaveImage prefix.

RIFE 4.25 scale 1.0 remains the finishing recipe, with twelve source paintings at 1 fps and multiplier 24. Interpolation never feeds back. Oracle first appears as a painting at 2s; interpolation toward it begins after the shared 1s cathedral painting. The final 11–12s uses native warp-only frames. No reference conditioning, masks, new motion, seed changes or sampling changes.

The main agent owns infrastructure, the GPU queue, execution, archive collection and final integration. The prompt subagent prepared the recipe and reviewed local paintings; it performed no cloud changes or inference. The runner requires an explicit deployment path to avoid accidentally using an inherited study's deployment.

## Execution

From `apps/deforum/`:

```bash
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/prompt_oracle.py simple --check
```

This bounded local check compares all eleven graphs with both the high3 builder and its archived requested graphs, checks the unchanged opening bytes, and freezes both prompts plus all candidate graphs in `work/prompt-oracle-session/preflight.json`. It makes no inference calls.

Generation command used by the main agent after supplying its deployment JSON and GPU lease (generation is now complete):

```bash
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/prompt_oracle.py simple --deployment /absolute/path/to/main-supplied/deployment.json
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/three_directions_review.py prompt build-raw
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/three_directions_review.py prompt prepare
```

The main agent retains normal shared-run archives produced by the existing runner. Candidate exports are `projects/modern-model-study/exports/prompt-oracle-v001/simple/cadence-24/`. The execution-specific `three_directions_review.py` adapter sets `study.BASELINE` to the fresh control without changing the prompt source. Its `prepare` validates every requested/executed graph and recurrent warp/lineage, then additionally requires pixel-identical opening and 1s cathedral painting against that fresh control. Main's prepare step passed, including pixel-identical opening and first repaint against the fresh control.

Use the existing RIFE environment and pinned baseline code/weights. Render the first pair:

```bash
work/rife-session/.venv/bin/python interpolate.py projects/modern-model-study/exports/prompt-oracle-v001/simple/cadence-24/rife-sources projects/modern-model-study/exports/prompt-oracle-v001/simple/cadence-24/rife-pair --source-frames 12 --source-fps 1 --multiplier 24 --motion-scale 1.0 --pair-only
```

Inspect the pair before supplying its manifest for full interpolation:

```bash
work/rife-session/.venv/bin/python interpolate.py projects/modern-model-study/exports/prompt-oracle-v001/simple/cadence-24/rife-sources projects/modern-model-study/exports/prompt-oracle-v001/simple/cadence-24/rife-raw --source-frames 12 --source-fps 1 --multiplier 24 --motion-scale 1.0 --validated-pair projects/modern-model-study/exports/prompt-oracle-v001/simple/cadence-24/rife-pair/manifest.json
```

Finally:

```bash
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/three_directions_review.py prompt finish
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/three_directions_review.py prompt compare
```

The adapted comparison reads the fresh control's finished frames without altering them, and writes `exports/prompt-oracle-v001/baseline-vs-simple/`. After finishing, inspect an interpolation window around face emergence as well as playback; reduced pixel change alone is not success.

## Preparation findings

Local preflight passes for all eleven graphs against both the high3 builder and archived requested graphs. The 1s cathedral graph differs only in SaveImage prefix; all ten Oracle graphs differ only in text/prefix. The reused opening matches high3 byte-for-byte. Both exact prompts and all eleven candidate graphs are frozen in `work/prompt-oracle-session/preflight.json`. The wrapper compares RIFE settings and provenance directly against high3's manifest.

Bounded local smoke checks also pass: note/code prompt equality, all eleven scheduled seeds through the mocked renderer, 24fps/12s/cadence-24 renderer arguments, comparison source paths and transition captions, high3 RIFE-reference routing, syntax, and refusal to invoke generation without an explicit deployment file. The mocked renderer submits no inference.

## Runtime control and execution status

The first unchanged cathedral repaint on the temporary RTX4090 did not byte-match the historical RTX PRO4500 run. The main agent therefore rendered an unchanged fresh control on the treatment runtime: `exports/three-directions-control-v001/high3/cadence-24`. This is the reference for every visual finding below. The historical result remains preserved; the cross-runtime difference does not isolate hardware from environment differences as its cause. See [the coordinated study](three-directions.md#runtime-control).

The main agent reports all 33 Krea jobs across control, movement and prompt branches and all 558 archive files downloaded and verified locally, with the Pod deleted. Those are combined session totals, not this prompt branch's job count. This branch contains eleven repaints plus the reused opening. Main subsequently verified decoded-pixel equality of the first repaint, completed raw reconstruction and RIFE finishing, and reviewed the finished comparison. This review did not run inference, RIFE or shared-source changes.

## First-pass painting review

Reviewed all twelve paintings per branch in four timestamp-matched contact-sheet pages, then opened the 4s and 11s images from both branches at their original 1536×1024 resolution. Times below are local shot times; the anchor filename is `72 + 24 × seconds`.

| Time | Fresh original-prompt control | Simplified prompt |
| --- | --- | --- |
| 0s | Curling ivory cathedral, deep teal rings and amber seed. | Same visible opening composition. |
| 1s | Warped cathedral repaint with finer ivory ribs around the seed. | Visually matches the fresh control; pixel equality subsequently verified. |
| 2s | A turquoise eye appears left of the central opening amid dense scrollwork. | A small nose/mouth form appears in that upper-left ivory region; a separate turquoise eye sits higher in the arch. |
| 3s | The left eye becomes more explicit; narrow lattices and shell-like details accumulate. | The nose and lips become readable as a tilted face fragment; the surrounding ivory surface remains broader. |
| 4s | Strong isolated left eye, with carved grids and shell ornament around it. | Clear nose, lips and chin occupy more of the upper-left arch; several eye-like forms remain spatially separate. |
| 5s | Architecture dominates; the amber seed remains intact at the center. | The face fragment enlarges, with smoother cheek shading and a turquoise eye over the inner ring. The seed persists. |
| 6s | Dense ivory ribs frame the left eye; another eye begins to read inside the tunnel. | Larger nose/mouth/chin surfaces and additional eyes make the architecture more overtly face-like, without a coherent portrait. |
| 7s | Two separate eyes are readable at different depths; the tunnel remains strongly architectural. | A prominent turquoise eye at upper right and another at lower left surround the separate nose/mouth form. |
| 8s | Fine framework, shells and nested ribs remain the main visual texture. | Broad ivory facial surfaces contrast with open dark cavities and fewer small competing ornaments. |
| 9s | The seed reads as a polished, increasingly pale metallic object within the detailed tunnel. | The seed remains warmer amber and more translucent; the disconnected facial features continue enlarging. |
| 10s | Isolated eyes and tightly packed ivory structure persist; no complete face forms. | Nose, lips and large right eye are strong focal features, but the facial arrangement remains fragmented. |
| 11s | Dense mechanical lattice, two isolated turquoise eyes, and a glossy pale amber seed. | Large ivory nose/mouth/chin, a clear turquoise right eye, another lower-left eye, and a saturated translucent amber seed. No unified frontal portrait. |

Full-resolution inspection confirms a real difference in forms, not just thumbnail contrast: at 4s the candidate has a modelled nose, lips and chin where the control principally has an eye and engraved structure. At 11s its broader ivory surfaces and larger facial features read more immediately; the control retains more miniature grids, shells and thin layered ribs. Both retain depth through nested teal/black openings and sculptural shading. The simplified version still has intricate edge latticework; it has not become a plain or empty scene. Its warmer seed and turquoise accents retain the requested palette, although the face remains split across incompatible positions in the architecture.

**Assistant recommendation:** shortlist `simple` for playback when prioritizing recognizable facial morphing. Keep the fresh original-prompt control as the meaningful alternative for dense mechanical architecture. The simplified branch develops more of a face earlier, but neither branch replaces the seed or achieves the requested coherent frontal Oracle portrait by 11s. This is a painting-level preference, not Olof's selection or evidence of smoother motion, less flicker or better interpolation.

**Prompt attribution:** this one matched seed sequence is consistent with the hypothesis that reducing background demands leaves more room for broad facial forms. It does not isolate that mechanism: the rewrite changes length, descriptive emphasis and material/detail requests together. Larger facial features, reduced ornament and warmer amber are observed outcomes; attributing each to a particular removed phrase would be speculation. Confirming the common first repaint strengthens the comparison, but one trajectory still cannot establish a general rule about prompt length or identity preservation.

## Result index

Painting links below exist and were inspected. Videos are finished; main inspected overview frames and a consecutive-frame window around 5.5s. Human playback feedback remains pending.

| Result | Candidate | Fresh control |
| --- | --- | --- |
| Painting at 4s | [Simplified](../exports/prompt-oracle-v001/simple/cadence-24/anchors/0168.png) | [Original prompt](../exports/three-directions-control-v001/high3/cadence-24/anchors/0168.png) |
| Painting at 11s | [Simplified](../exports/prompt-oracle-v001/simple/cadence-24/anchors/0336.png) | [Original prompt](../exports/three-directions-control-v001/high3/cadence-24/anchors/0336.png) |
| Raw diagnostic | [Simplified](../exports/prompt-oracle-v001/simple/cadence-24/preview.mp4) | [Original prompt](../exports/three-directions-control-v001/high3/cadence-24/preview.mp4) |
| RIFE 24fps | [Simplified](../exports/prompt-oracle-v001/simple/cadence-24/interpolated/preview.mp4) | [Original prompt](../exports/three-directions-control-v001/high3/cadence-24/interpolated/preview.mp4) |

Finished side-by-side result: [fresh control versus simplified Oracle](../exports/prompt-oracle-v001/baseline-vs-simple/preview.mp4). Inspect especially 3–6s for emergence of the nose/mouth form and 7–11s for the fragmented eye arrangement, seed persistence and loss or retention of architectural interest.
