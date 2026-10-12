# A World Inside Every Seed

A continuous thirty-second surreal journey: alien jungle, an ancient black-and-gold city, opalescent geometry and a small living world inside a crystalline seed.

[Watch the film](exports/v002/p12-the-seed-holds-a-world/faster/rife-moving-tail/preview.mp4) · [Local reviewer](http://localhost:3028/world-seed) · [Direction and screening](experiments/choreography.md)

## The journey

| Delivery | World and event | Motion and visual treatment |
| --- | --- | --- |
| 0–10s | A flowering jungle gateway becomes an ancient city | Preserved opening; jewel-green/coral painting becomes black lacquer and gold |
| 10–13s | Follow the suspended golden road | Broad bank and lateral reframing around the actual towers |
| 13–17s | The road curls into intricate mineral lattice | Local unfurling; engraved brass becomes nested ivory ribs |
| 17–21s | Look through an oval window into the crystalline garden | Sideways glide and plane turn; rose/cyan glass and tiny worlds appear |
| 21–26s | Approach a fern garden inside an emerald cell | Diagonal approach with a small membrane flex; the selected cell stays recognizable |
| 26–30s | Reveal the chamber around the living garden | One outward move with a continuing turn; a seed-like shell among hanging glass pods |

## Production

The film has no cuts, dissolves or independently initialized replacement shots. Ninety paintings from the earlier opening are preserved; 180 new paintings continue their feedback chain. Every new painting initializes from the warped preceding painting. The three original stills establish visual targets; the city and crystal stills are not inserted into the film.

Krea Turbo, CFG 1, three Euler repaint intervals, recorded noise and seed schedules, native 1536×1024. Source cadence is twelve frames at 24 fps; delivery is 4.5× faster, retaining all 270 paintings. Local RIFE fills intervals outside recurrence. The silent working film is 24 fps and thirty seconds.

The [motion study](../../../../docs/research/motion-design-foundations.md) informed attention, overlapping movements and varied paths. Each new passage was composed from its actual starting painting, previewed without diffusion, then generated and inspected in short sections. The literal mechanical iris in the initial storyboard became an unfurling road; the ending follows the fern-filled chamber that emerged. [Recorded decisions and limitations](experiments/choreography.md) · [Execution and preservation](experiments/execution-summary-v004.json).

Fine details and small structures continue to repaint. The plane turn is a flat-image transform, not true depth parallax. Olof finds this film much better, with beautiful middle/end imagery and interesting movement. The jungle and dark doorway need crisper, richer detail; retain the liked second-world style and bridge/cloud setting. [Opening diagnosis and next comparison](experiments/choreography.md#human-review-and-opening-diagnosis--2026-10-10).

## Preserved versions

[Opening detail comparison](experiments/opening-detail.md): two-second baseline, full prompt with three steps, and full prompt with six steps. Olof finds them very similar and tentatively prefers the original, which remains the working choice. The follow-up audit checks exact prompts and official Krea Turbo guidance for style and quality language. The complete film remains v004.

[Digital rendering comparison](experiments/digital-detail.md): Olof finds this similar or worse than the original. The [cross-scene prompt study](experiments/prompt-study/README.md) follows with 51 stills across four worlds and seventeen recurrent cases. Concrete material descriptions yield strong new stills, but no wording-only cure for accumulated simplification. On 2026-10-12, Olof rejects 0.25, finds 0.6 acceptable and 0.72 better in some respects, and finds 0.85 too changeable. Small flicker is acceptable; major objects disappearing are not. The [continuity review](experiments/continuity-options.md) checks earlier step/CFG tests and proposes bounded follow-ups. Original jungle and full film remain selected. The [reviewer](http://localhost:3028/world-seed-detail), all attempts and receipts are preserved.

[Noise and clean-reference study](experiments/noise-reference/README.md): on 2026-10-12, matched two-world experiments find better preservation of major forms through the editing-reference route, while fine detail and palette still drift. Neither eight partial updates nor explicit color/detail preservation wording establishes a fix. [Compare the two-second videos](http://localhost:3028/world-seed-reference). Olof rejects the strength-1 treatment as too static and warm. The [lower-weight follow-up](experiments/noise-reference/reference-weights.md) tests only the tidal artwork, retaining the moving previous-image reference. Weight 0.5 remains similar to 1.0; 0.2 allows more local redraws, but neither resolves the warming and detail loss. The [0.05 / 0.01 follow-up](experiments/noise-reference/reference-low-weights.md) allows more shell redesign while retaining the main planet, yet still fails to recover fine material detail. Olof finds 0.01 promising and asks to continue its development while addressing color drift. The [sampler and reference-control comparison](experiments/noise-reference/sampler-reference-controls.md) tests gentle ancestral noise independently of the editing controls. No clear ancestral benefit is found; half-strength editing is a cooler but more redesigned alternative, and smaller grounding does not fix color/detail drift. All 85 jobs are preserved and verified, and the owned GPU is deleted. [Sampler reviewer](http://localhost:3028/world-seed-samplers) · [Reference controls](http://localhost:3028/world-seed-reference-controls). The selected film stays unchanged; original-keyframe references, masks and refinement are excluded.

[Opening with sustained rhythm](cuts/v003.md) · [First continuous opening](cuts/v002.md) · [Original opening with dissolve](cuts/v001.md) · [All cuts](cuts/README.md) · [Three visual targets](exports/world-stills.jpg)

Human direction: highly detailed unreal worlds, distinct styles and palettes, purposeful travelling motion and surprising transformations. Olof prefers the cut-free opening and its revised rhythm, but found it too dominated by zoom. Strong motion is welcome; repeated acceleration and braking are not. Earlier reference recommendations were not considered a higher quality bar than our own films. All prior stills, configurations and takes remain preserved.

[Adapter-strength and sampler follow-up](experiments/noise-reference/adapter-sampler-followup.md): Olof prefers half-strength editing for its reduced color drift. Tests of 0.25/0.75 bracket that choice; 0.25 is cooler but adds moons, while 0.75 is warmer with a quieter sky. Neither Heun nor DPM++ 2M at noise 0.60 improves fine material detail over Euler in this trajectory. Both repeated controls reproduce their prior paintings and videos exactly. All 102 new jobs and six two-second deliveries are verified, and the GPU is deleted. [Adapter comparison](http://localhost:3028/world-seed-reference-controls) · [Sampler comparison](http://localhost:3028/world-seed-samplers).
