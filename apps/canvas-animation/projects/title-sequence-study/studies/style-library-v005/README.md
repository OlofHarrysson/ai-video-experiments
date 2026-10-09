# v005 · Typography construction library

**In progress, one-hour sprint, 2026-10-09.** See [sprint plan](../../VISUAL-LIBRARY-SPRINT.md) for the deadline and scope. Seventeen constructions and 68 states now exist. The resumed pass adds original connected Wild lettering, a surface-material experiment and six composition studies. First-pass pixels and source are preserved in ignored `output-first-pass/`; they are not the final selection.

The user supplied *All Of The Lights*, approximately 81–120 seconds, as a second reference. [Reference observations](../../reference-all-lights-study.md) distinguish source evidence from interpretation. [Claude's direction review](claude-direction.md) is advisory. The user liked Night Fever's fixed-composition material cycle in v004; no particular cadence, theme or final treatment is selected.

## Interface

`TypeLibrary.render(id, word, state, frame, canvas, {label:false})` renders a pure frame at 1280×720. `families` holds stable IDs, display names, default words and material names. Four states per family. A labelled review frame uses a 1280×768 canvas.

`index.html` is a local preview with family, sample text, material and cadence controls; playback is paused by default. Only its preview clock uses real time. Artwork and exported frames use explicit frame numbers and seeded functions. The preview is a small inspection surface, not a film authoring application.

Run from repository root:

```sh
node apps/canvas-animation/projects/title-sequence-study/studies/style-library-v005/render.mjs
OUTPUT=output-reviewed node apps/canvas-animation/projects/title-sequence-study/studies/style-library-v005/render.mjs --video
```

The renderer refuses to replace an existing output directory. It uses the Animate skill's local Playwright, bundled font files and system FFmpeg. No cloud image generation, source pixels or borrowed music. Earlier studies are unchanged.

## First-pass screening

- All 12 families produced four states without browser errors.
- Each family produced byte-identical PNGs after out-of-order seeks at the same frame.
- Short and long sample words rendered; these smoke checks do not prove good typography for arbitrary wording.
- All 48 states and both catalogue sheets were inspected visually.
- A mirror-position defect in Mercury sport was found: its reflection was below the canvas. Fixed in source after preserving the first pass.
- Wingline needs a more deliberate feather silhouette; the first version reads as leaves or an insect.
- Electric palace is richer than plain text but still too evenly sparse around the lettering. Its next pass should deepen the sign construction.
- Some states are just colour changes; construction diversity is stronger across families than within every four-state row. Keep useful variants, but report them honestly.

## Current continuation

Resumed by Olof for another hour at 19:38:43 UTC, deadline 20:38:43 UTC. Both Claude consultations completed successfully; read `claude-first-pass.md`. No Claude processes are running. `output-refined/` holds the second still pass: fixed mirror placement, attached feather roots, selective light spill, better serif spacing, thicker wire strokes, clipped nested outlines and a rebuilt orbital arrangement. The refined video is not yet exported. Preserve the prior outputs and continue from the current library source.

## Resumed-hour checkpoint — 20:02 UTC

- `output-script-first/`: original hand-drawn Wild script in neon and shaded resin; generic uppercase input remains available.
- `output-marquee-refined/`: larger enamel letters with bulbs sampled along interior distance ridges. The result is more readable than the original dense grid; bulb spacing remains an optical refinement opportunity.
- `output-layouts-first/`: six fixed composition variants (cropped depth, tiny chrome, giant glyph, three exposures, interlocked two-line sign, a wall of signs). These are layouts, not six new alphabets.
- `output-cut-first/`: 400-frame, 16.67-second same-word cut. It predates the script and new layouts and is not the final montage.
- Current complete source is checkpointed on the existing branch; all earlier output directories remain preserved.
- The new reflective material still has visible small bands/ticks. The resin state is cleaner. Do not claim the reflective version is polished or physically based rendering.
- `check-surface.mjs` compares Euclidean distances to an independent brute-force oracle on small masks.

Deadline for the resumed hour remains **20:38:43 UTC**. Next: improve composition joins, inspect dense motion windows and full state pages, export the current catalogue and updated montage, finish documentation and commit. No Claude processes remain running; the latest advice is `claude-expanded.md`.
