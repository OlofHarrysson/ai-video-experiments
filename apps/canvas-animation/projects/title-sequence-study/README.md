# Title Sequence Study

Working project name; theme and final title are undecided.

## Intent

Develop an original short film or motion-graphics piece after studying the opening/credit sequence of *Enter the Void*. Olof supplied [this YouTube reference](https://www.youtube.com/watch?v=wNtxgxYY7sI) and highlighted approximately **1:50 onward** as the visually interesting section. The local source has since been preserved and inspected; exact sample timestamps are recorded in the reference study.

First understand the reference visually, then discuss what our project should be about. Do not infer a theme from the reference film's subject matter. Duration, aspect ratio, text, soundtrack, narration and degree of resemblance remain open.

## Current state — 2026-10-10

- Project initialized inside the existing canvas-animation workspace.
- Reference source and intake recorded in [reference-source.json](reference-source.json).
- Olof supplied the local video after YouTube access was blocked. A hash-verified independent copy is preserved at `references/original/enter-the-void-intro.mp4`.
- [The first visual study](reference-study.md) is complete: overview, varied typographic samples and every-frame inspection of three short windows around 1:50 onward.
- [Twelve typography feasibility studies](studies/typography-v001/README.md) test font-based effects, integrated graphics and custom letter geometry. Olof finds them decent but less impressive than the reference, with insufficient motion in several examples.
- [Eight motion studies and an escalating edit](studies/motion-v002/README.md) use project-local GSAP timelines, OpenType outline extraction and reusable drawing primitives. Catalogue and montage await Olof's motion review.
- Olof finds v002 better, but identifies simple/plain graphic design as the primary risk. [Three focused graphic identities](studies/design-v003/README.md) test compound script, custom chrome lettering and dense poster typography, with a short stepped-motion study. These await his visual judgment. Claude consultation was attempted but blocked by an expired login.
- Olof prefers Night Fever among the v003 stills and rejects its whole-image crop/scale movement. He calls [v004's fixed-composition material cycle](studies/motion-v004/README.md) much cooler. Its three cadences remain alternatives; no speed has been selected.
- Olof supplied *All Of The Lights* around 1:21–2:00 as a second reference. A hash-verified independent copy and [timestamped inspection](reference-all-lights-study.md) are preserved.
- [v005's construction library](studies/style-library-v005/README.md) now contains 17 families / 68 states plus seven composition studies / 28 treatments: original lettering, neon, pressure-based script, lamps, print, wire, modular shapes, depth and surface materials. A 25-second silent showcase and two slower catalogues are ready for visual review. [Open the review page](studies/style-library-v005/review.html) or [interactive library](studies/style-library-v005/index.html). This is preparation for a film, not a selected treatment.
- Olof finds the first v005 opening too slow and its fastest ending a little too fast. [A 24-second rhythm experiment](studies/style-library-v005/RHYTHM.md) uses medium to medium-high activity, recurring motifs and quarter-/half-second holds; the original ramp is preserved. He finds this substantially better, while the graphic design remains too plain.
- [Generated design to editable lettering](studies/image-to-code-v006/README.md) tests Olof's proposed image-generation-to-code workflow. Wild Hours is now reconstructed as 13 editable vector components with enamel/gold/ivory materials, a six-second light loop, palette/depth controls and SVG/PNG exports. [Review the result](studies/image-to-code-v006/review.html). Assistant screening and deterministic rendering checks are complete; human taste review remains pending.
- [Acid print v007](studies/print-to-code-v007/README.md) reconstructs a second generated reference with nine polygon letters, procedural fluorescent ink and an eight-second call-and-response motion phrase. Olof authorized this contrasting image-to-code test after the enamel study. [Watch and compare](studies/print-to-code-v007/review.html). Renderer, export and playback checks pass; assistant screening is complete and human motion feedback is pending.
- Olof calls v007 much better than the first reconstruction and approves a third direction. [Woven ribbons v008](studies/ribbon-to-code-v008/README.md) constructs the blue/ivory reference from 17 editable curve components, with returning bands, depth-resolved crossings and an eight-second travelling-pattern loop. [Watch and compare](studies/ribbon-to-code-v008/review.html). Assistant screening and technical checks are complete; human feedback on this reconstruction is pending.
- [Motion plan](MOTION-PLAN.md) records the authorized scope and deferred GPU effects, font collection, custom lettering, sound and theme work.
- Local reference media belongs in `references/original/`; derived clips, frames and contact sheets belong elsewhere under `references/`. The entire reference directory is ignored by Git.
- No theme, film storyboard or original soundtrack has been selected. The typography and motion studies are tests, not an approved film treatment.

## Olof's direction — 2026-10-09

Olof likes the text-based visual chaos and the gradual escalation from a calm beginning: more motion, colors, layers and increasingly difficult reading, with sound building alongside it. Easy readability throughout is not the intended look. The audience should recognize the theme and relate to the story.

AI progress, investment and hype accelerating toward loss of control is a candidate, not the selected theme. Possible material includes model names, money and headlines, but Olof questions whether historical model names such as BERT would resonate with a broad audience. His personal experience in AI informs the idea; this does not establish an insider-history format or verify on-screen claims.

The immediate priority is a large variety of graphic identities and motion behaviors. Olof explicitly requested these feasibility tests ahead of theme and story selection. He likes the neon look but wants meaningful motion, finds the detached script flourish out of place, and likes the tangled outlines' activity. Simple treatments can coexist with complex ones. He authorized motion tooling and the next study, recommending GSAP from prior experience. Next: review the v006 image-to-code reconstruction alongside the v005 medium-high rhythm experiment, choose a handful of contrasting identities, and apply them to actual words when a theme is selected. More font filters alone are unlikely to close the remaining finish gap.

## First milestone: inspect and discuss

1. Acquire the exact reference locally; retain the original file, record its SHA-256, duration, dimensions and frame rate in the source manifest.
2. Inspect a small overview around 1:50 and the later visual progression. Select representative frames with absolute source timestamps.
3. Inspect consecutive frames in two or three short intervals to distinguish cuts, internal movement, type changes, flashes and holds. Sparse stills alone cannot establish playback rhythm.
4. Use the Animate reference analyzer on a bounded clip if useful. Its cut/flicker estimates need visual checking, especially for rapid flashes; numeric output is not proof of perceived rhythm or music synchronization.
5. Present a small contact sheet and a concise account of composition, typography, color, transformations and timing. Clearly separate observations, measurements and interpretations.
6. Discuss theme with Olof using that visual evidence. Only then propose the original piece's story and look.

Acceptance evidence is actual inspected reference imagery and a timestamped account of how the sequence works. This evidence is recorded in [the study](reference-study.md); theme selection remains open. A downloaded file or automated analysis alone is insufficient.

## Workflow

Use the repo-local [Animate skill](../../../../.agents/skills/animate/SKILL.md), the [canvas-animation guide](../../README.md), and the repository [review agreement](../../../../docs/review-and-feedback.md). The feasibility study uses Canvas 2D and Animate's Playwright dependency. Final film structure, delivery format and font packaging remain undecided.

Preserve original reference media and keep all source-derived pixels local. Reference material informs the original work; it is not automatically an output asset. Record artistic decisions here as they are made; add a separate experiment note when there is an actual experiment to reproduce.
