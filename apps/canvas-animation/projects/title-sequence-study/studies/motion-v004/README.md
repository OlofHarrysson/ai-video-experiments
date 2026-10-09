# Night Fever render cycle v004

2026-10-09. Olof prefers the Night Fever still and rejects v003 movement. The artwork is drawn by hand-written Canvas code, using a local Snell Roundhand face, layered strokes, gradients, offset passes and custom Bezier flourishes. No image-generation model is used.

## Experiment

[Nine-second cadence comparison](output/cadence-comparison.mp4): three labeled sections of equal duration. The same six treatments cycle at 4, 6 and 12 replacements per second (6, 4 and 2 frames at 24 fps). Geometry stays fixed, with no camera motion or cropping. [Material sheet](output/materials.png): lacquer, cream and separated colored echoes, contour echoes, hollow bevel, silhouette and dots. Stars change positions every two frames. Odd frames draw the plate at 88% opacity over near-black; this is intentionally milder than the reference alternation described by Claude. There is no full-frame white flash or audio.

This is a narrow timing/material test. It does not replace the intended large vocabulary of different graphic identities with one look, and it does not establish a final film theme. No claim that its real-time experience matches the reference is made.

## Claude consultation and judgment

The restored existing Pro login completed a read-only consultation on Claude Opus 5.5 (`claude-opus-5-5`), high effort. [Prompt](../design-v003/consultation-motion-prompt.txt), [full advice and limitations](../design-v003/claude-motion-review.md). The original JSON receipt is ignored under `references/consultations/design-v003-motion-review.json`.

Claude distinguished abrupt material changes within a stable composition from v003's slow changes to the crop of a fixed image. Its review of the PAZ frames identified filled/outlined/echo states, paired brightness changes and changing stars. Codex checked the existing dense reference sheet and agrees this is a useful local observation. Claude's broader frame-change/luma statistics over 110–131.5 seconds were not independently reproduced; they are not acceptance thresholds here. Neither assistant claims real-time playback or audio assessment.

Adopted: fixed geometry, six treatments derived from existing layers, comparison at three rates and changing star positions. Deferred: stacked earlier treatments and scale creep, to keep this test interpretable. Modified: milder bright/dim alternation and star changes on paired frames. No new libraries or paid API fallback.

## Implementation and evidence

The v003 drawing code exposes `nightLayer` without changing its previous rendering. The renderer verifies the preserved v003 Night Fever PNG hash before export. All three cadences pass same-time hash checks after out-of-order rendering. Font identity is inherited from the checked v003 rendering on this Mac; portability remains unverified.

Assistant inspected all six materials and an encoded every-frame window from 6.0–6.458334 seconds, covering a full six-treatment fast cycle. See `output/review/v001/contact-sheet.jpg`, its timestamp manifest and `output/report.json`. Export: 1280×588 including the review label, 24 fps, 216 frames, 9 seconds, no audio. Preview cadence and play/pause controls were exercised. Olof's judgment of the actual motion is pending.

Run from the project directory:

```sh
node studies/motion-v004/render.mjs
```

The v003 baseline PNG must exist. The renderer refuses to overwrite existing `output/`; rename that directory to preserve a completed run before rerendering. Source-derived media stays outside the artwork and Git.
