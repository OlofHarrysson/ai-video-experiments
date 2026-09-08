# Reviewing experiments together

Living working agreement, 2026-09-07. Learning filmmaking, model behavior and how to collaborate on visual work are all part of this project. Treat this process as a hypothesis: adjust it from actual feedback, preserve what was learned, and keep the resulting videos central.

## Responsibilities

Preserve the agreed animation feedback loop when changing model or conditioning recipes. Before a comparison, describe three inputs separately: the warped previous image used to initialize sampling, the text prompt, and any additional reference-image conditioning. State which input changes and which stay fixed. If terminology such as “text-to-image” suggests removing an established mechanism, clarify the intended data flow before implementing that interpretation. A narration of an assumption is not confirmation of alignment.

### Misunderstanding record — 2026-09-08

**Confirmed assistant misunderstanding:** Olof requested a text-conditioned Deforum feedback loop with an optional additional native image reference. The assistant interpreted “text-to-image” as independent fresh-noise generations and removed previous-image initialization in the text-only arms. The reference arms used the previous frame as conditioning while also sampling from fresh noise; they did not add reference conditioning to the conventional partially noised previous-image path. These experiments therefore did not test the intended combination.

**Intended experiment:** retain previous artwork → spatial deformation → partial-noise diffusion initialization → repaint → next artwork, with the text prompt throughout. Compare that loop with the same loop plus a model-supported reference-image input. The reference might be a previous frame, the opening, or another deliberately chosen image. Its selection and whether it is warped should be stated explicitly. Simultaneous initialization and reference conditioning must be verified for each model; the proposed benefit remains a hypothesis.

**Prevention:** distinguish sampling initialization from conditioning whenever describing “image input.” Map a proposed change onto the existing loop, then confirm any interpretation that would remove feedback or replace its mechanism. Compare the agreed baseline with an additive change, unless Olof explicitly requests a different architecture. Preserve the mistaken runs and label their scope accurately; they are not evidence against the intended combined mechanism.

Establish a convincing opening before extending a new visual recipe into animation. A narrow mechanism test may use a diagnostic image, but successful execution or improved continuity is not evidence of artistic quality. Screen composition, visual richness and fit to the supplied art references separately from temporal behavior.

The assistant does the first pass: verifies the experiment, inspects images over time, investigates suspected defects, compares matched examples and recommends a small shortlist. Olof supplies taste, creative direction and playback judgments. Neither technical measurements nor the assistant's recommendation override a stated preference. An explanation being presented does not establish that Olof understood or retained it.

Default human review: **one recommendation and one meaningfully different alternative**, often just one video when there is no useful choice. Keep all outputs and link the full experiment index, but do not require Olof to rank six nearly identical clips. Show the whole set when requested. Keep playable videos inline in chat.

Use descriptive names with stable experiment IDs in parentheses, rather than unexplained node names. Each shortlisted video gets:

1. **What changed:** one plain-language sentence relative to a named baseline.
2. **Why:** the visual problem the change was intended to address.
3. **What to watch:** a specific feature or short time range, such as the portal's outline at 5 seconds.
4. **What happened:** the assistant's evidence and any unresolved tradeoff.
5. **One taste question when a decision is needed:** for example, whether a smoother transition keeps enough visible repainting. “No noticeable difference” is a valid answer; it need not trigger more similar variants.

Do not bury the video under a settings table. If Olof likes it, explain the few settings/mechanisms that made that version, then link the complete recipe. Preserve the chosen baseline so the next comparison stays recognizable.

For spatial motion, first show an animated simple drawing and grid with diffusion disabled. Olof found this much easier to understand than a repainted video. Use these previews to build a small vocabulary of effects and align on movement, then show the final diffusion result for artistic judgment. Keep direct mathematical controls, visual mesh/stroke manipulation and guide footage as distinct possible authoring routes; do not assume every effect needs a guide. See the [animated lesson](research/spatial-controls-lesson.md).

## Assistant review: broad view, then close inspection

Use the [local review harness](video-review.md). Its image limits are practical defaults, not a claim about a fixed model context limit.

- Start with 6–12 evenly spaced frames per clip. Describe what persists, changes, disappears and returns across the beginning, middle and end.
- Choose 1–3 short intervals from that overview, Olof's comments, and optional pixel-change candidates. Inspect a representative good transition as well as a suspected defect; the largest numerical change is not necessarily the most useful artistic event.
- Use `--window START END` to inspect **every displayed frame** in each chosen interval. Around a 24 FPS transition, 0.25 seconds is usually a useful first window. Expand only when the evidence requires it.
- Use `--compare` for the same elapsed times in a baseline and candidate. Keep labels and actual timestamps visible. Comparing matching source frames isolates a finishing operation; comparing the same moment in two independently evolving generations shows different outcomes, not guaranteed object correspondences.
- Load small contact-sheet pages selectively. Open full-size extracted images when fine contours need inspection. A long video is reviewed by overview and selected windows, not by loading its entire frame sequence into model context. The current default is 12 images per page and at most 64 displayed images per call, counting both sides of a comparison. A larger explicit budget still produces separate pages.
- RIFE manifests label original images, synthesized in-betweens and final holds. Repeated delivery frames are not additional diffusion steps. Do not judge interpolation only at timestamps that show original anchors.
- Write a short first-pass note: observed progression, specific defects with timestamps, what was actually inspected, proposed shortlist, and the one unresolved taste decision. Images can reveal doubled lines and sudden replacements; a few stills cannot establish the rhythm of normal-speed playback.

After human feedback, record the preference with its scope and uncertainty in [the learning journal](olof-learning-journal.md). Update the selected baseline and experiment note. Preserve disagreeing assistant observations as limited evidence rather than repeating them as the verdict.

## How the continuity experiments were organized

These were small controlled comparisons using the same SDXL image model and art LoRA. They were not seven separate model architectures. A parent recipe, input image, prompt schedule and camera were held constant while selected settings changed. One sub-agent handled local RIFE setup/execution while the main agent ran the three cloud generation comparisons and the local flow-stabilizer test.

| Question | Comparison | Meaning |
| --- | --- | --- |
| What if each repaint uses the same random starting noise? | P3 → C01 | Fixed diffusion seed; separate added pixel noise stays on. |
| What if we stop adding extra noise directly to the image? | P3 → C02 | Pixel noise removed; diffusion seed still changes each frame. |
| What if we do both? | C01 → C03, or C02 → C03 | Completes a small two-factor comparison; each of those pairs changes one factor. |
| Can we bridge the jumps between already painted frames? | Raw P1/P3/C02 → their RIFE exports | Same original images, learned in-between images added afterward. RIFE was applied to these three, not all seven outputs. |
| Can we reduce small detail changes between frames? | Raw P3 → P3 with Flow Stabilize | Aligns the preceding image to the current one, then blends detail where they agree. Creates no extra frames; the large redraws remain. |

One artistic sequence and seed family were tested, so these comparisons establish behavior for this example rather than universal best settings. Sub-agents divide the work; the experimental questions determine the variants.

## Current preferred recipe: P3 with RIFE

Olof tentatively prefers **P3 + RIFE** from the seven continuity outputs; he found C01/C03 boring and the others pretty good, while noting that similar variants were difficult to distinguish. This preference supersedes the assistant's earlier recommendation of C02 + RIFE.

The key ingredients of P3 + RIFE are:

- **Image model/style:** SDXL base with an art LoRA, producing the teal, orange, cream and black graphic treatment.
- **Feedback:** each new image starts from the previous painted image. A strong repaint setting allows noticeable transformation; this is not a single still moved around by a video editor.
- **Evolution:** the prompt shifts from mechanical toward organic forms; a changing diffusion seed supplies a fresh noise pattern each step. Guidance is lower than P1 (CFG 4.5 versus 7). Those are recipe facts, not proof of which ingredient caused Olof's preference.
- **Finishing:** the model painted 48 images at 8 images per second. RIFE created two intermediate images between each neighboring pair. Two final holds preserve a six-second video at 24 FPS. RIFE tries to estimate how pixels move between two images; it does not understand the intended story or generate new diffusion keyframes.
- **Camera:** only a gentle 2D zoom in this comparison. The liked morphing does not establish a successful 3D camera workflow.

Exact settings, immutable frame sources and results: [parameter study](../apps/deforum/projects/brain-entity-study/experiments/parameters.md), [continuity study](../apps/deforum/projects/brain-entity-study/experiments/continuity.md), and [RIFE finishing](../apps/deforum/projects/brain-entity-study/experiments/rife-results.md).

The next creative experiment should start from this preferred recipe and ask one question. The research suggests making the random noise change gradually during generation; that remains an unimplemented hypothesis. Establish the improved review loop before commissioning another broad sweep.
