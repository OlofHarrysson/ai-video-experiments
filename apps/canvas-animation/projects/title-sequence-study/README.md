# Title Sequence Study

Working project name; theme and final title are undecided.

## Intent

Develop an original short film or motion-graphics piece after studying the opening/credit sequence of *Enter the Void*. Olof supplied [this YouTube reference](https://www.youtube.com/watch?v=wNtxgxYY7sI) and highlighted approximately **1:50 onward** as the visually interesting section. The timestamp belongs to that upload and has not yet been verified against a local file.

First understand the reference visually, then discuss what our project should be about. Do not infer a theme from the reference film's subject matter. Duration, aspect ratio, text, soundtrack, narration and degree of resemblance remain open.

## Current state — 2026-10-09

- Project initialized inside the existing canvas-animation workspace.
- Reference source and intake recorded in [reference-source.json](reference-source.json).
- Olof supplied the local video after YouTube access was blocked. A hash-verified independent copy is preserved at `references/original/enter-the-void-intro.mp4`.
- [The first visual study](reference-study.md) is complete: overview, varied typographic samples and every-frame inspection of three short windows around 1:50 onward.
- [Twelve typography feasibility studies](studies/typography-v001/README.md) test font-based effects, integrated graphics and custom letter geometry. Frames, reference comparisons and a silent motion proof have been screened by the assistant; Olof's assessment is pending.
- Local reference media belongs in `references/original/`; derived clips, frames and contact sheets belong elsewhere under `references/`. The entire reference directory is ignored by Git.
- No theme, film storyboard or original soundtrack has been selected. The typography and motion studies are tests, not an approved film treatment.

## Olof's direction — 2026-10-09

Olof likes the text-based visual chaos and the gradual escalation from a calm beginning: more motion, colors, layers and increasingly difficult reading, with sound building alongside it. Easy readability throughout is not the intended look. The audience should recognize the theme and relate to the story.

AI progress, investment and hype accelerating toward loss of control is a candidate, not the selected theme. Possible material includes model names, money and headlines, but Olof questions whether historical model names such as BERT would resonate with a broad audience. His personal experience in AI informs the idea; this does not establish an insider-history format or verify on-screen claims.

The immediate priority is visually compelling graphic identities. Olof explicitly requested these feasibility tests ahead of theme and story selection. Next: review the twelve studies and identify strong and weak families, then resume theme discussion.

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
