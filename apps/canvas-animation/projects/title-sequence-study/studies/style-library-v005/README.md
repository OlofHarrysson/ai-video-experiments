# Typography construction library · v005

A reusable visual vocabulary developed from Olof's *Enter the Void* and *All Of The Lights* references. **17 construction families, 68 material/composition states, and seven additional fixed layouts with four treatments each.** These counts describe alternatives, not 96 equally finished designs. Theme, final film structure and soundtrack remain open.

The current [medium-to-medium-high timing experiment](RHYTHM.md) responds to Olof’s feedback that the opening was too slow and the peak too fast. It uses a repeated visual pulse with 0.25–0.5-second holds. The original escalation cut remains available for comparison.

Start with [the local review page](review.html): a new 24-second rhythm cut, a 25-second escalating showcase, a 34-second construction catalogue, a 14-second composition catalogue, and a 16-second internal-motion comparison. Then [open the interactive library](index.html) to change words, compare treatments, animate a single treatment, or save a PNG. The videos are silent. Playback starts only when requested.

## What is worth taking forward

- **Wild neon** and **Wild / Hours**: original connected lettering, glass/hot-core/cold-tube construction, travelling gas and a contrasting serif partner.
- **Wild compound brush sign**: the same original path with thick downstrokes, thin return strokes, layered edging, engraving and a moving stripe finish. This is an alternative to monoline tubing; it is not another font.
- **Depth / broken frame**, **giant glyph / razor caption**, and **tiny chrome**: useful scale extremes. The depth layers move while the front contour remains registered.
- **Dynamo marquee**, **overprint**, **pinboard**, and **slats**: lamp architecture, print, discrete lights and sliced geometry provide contrast to script.
- **Rose resin**: the cleanest surface study. Silver/gold remain experiments; their self-crossings and sharp reflections still need optical work before a long hero hold.

Orbital's sparse dial, some wing ornaments, the busiest modular weave and the competing-sign wall are secondary studies. Keep them available for brief accents; they have not earned equal prominence. The original Night Fever artwork and v004 material-cycle comparisons are preserved unchanged.

## What was built

| Owner | Responsibility |
| --- | --- |
| `library.js` | Seventeen deterministic constructions and their four states; masks, sampling, original uppercase alphabets |
| `lettering.js` | Original Wild cubic paths, neon, ribbon and pressure-based compound sign |
| `surface.js` | Cached analytic/bitmap fields, approximate resin/metal shading and bulb placement |
| `compositions.js` | Seven fixed art-directed layouts; words and placement are deliberately designed together |
| `cut.js` | Explicit 610-frame, 24 fps escalation study; no whole-image camera animation |
| `catalogue.json` | Per-family construction, source observation, motion and reuse notes |
| `index.html` | Inspection controls; cycle treatments or animate the selected one independently |
| `review.html` | Small visual shortlist and three exported review videos |

Canvas 2D, local fonts, hand-authored vector paths, headless Chromium and FFmpeg produce the work. No image model, cloud media generation, source-video pixels or borrowed music are used. Earlier GSAP timeline tooling remains in v002; this library uses explicit frames and discrete state changes because that fits these studies.

## Reuse

```js
TypeLibrary.render('tube', 'Wild', 2, 36, canvas, { label: false });
TypeLibrary.render('wire', 'FUTURE', 1, 12, canvas);
TypeCompositions.render('interlock', 0, 24, canvas);
TypeCut.render(240, canvas);
```

Artwork is 1280×720 at 24 fps. A labelled catalogue uses a 1280×768 target. `TypeLibrary.canvas()` creates an artwork target; pass `transparent: true` to omit its background when layering a construction.

The editable [Wild centreline SVG](assets/wild-centreline.svg) is included alongside its source paths. `Wild` is a bespoke logotype, not a complete script font. Exactly that spelling activates the drawn path in `tube`, `ribbon` and `softmetal`. The alternate input path in those families, plus `wire` and `modular`, accepts uppercase A–Z and spaces. Other families use the bundled fonts. Unsupported alphabet input produces an explicit error. The seven layouts use fixed wording; the interface hides the editable-word control for them.

The smoke checks cover short and long sample strings; they do not prove attractive spacing for every word. Use the ranges and limitations in `catalogue.json`, then optically adjust the actual film wording. A full alphabet, layout system or 3D renderer is not implied by a successful sample.

## Reproduce and inspect

Use the repository's installed Animate Playwright/Chromium and FFmpeg dependencies. Run from this directory, choosing a new output name each time:

```sh
OUTPUT=output-release-library node render.mjs --video
OUTPUT=output-review-layouts node render-compositions.mjs --video
OUTPUT=output-delivery-showcase node render-cut.mjs
OUTPUT=output-release-inspection node inspect-library.mjs
OUTPUT=output-native-review node render-native.mjs
node check-surface.mjs
node inspect-review.mjs
node verify-exports.mjs
```

Renderers refuse to overwrite an existing directory. On this checkout these outputs already exist; select another name to rerender. New clones must render them before opening the review page, or adjust its local paths to their chosen output directories. Source, dependencies and licensed fonts are tracked; references, renders and inspection pixels are local ignored files. Each render contains a source snapshot and hashes. Font licensing and provenance live in `../../fonts/`.

[Screening notes](REVIEW.md) distinguish code checks, decoded-frame inspection and human playback judgment. [Surface notes](SURFACE-NOTES.md) explain the approximation and unresolved seams. [Reference observations](../../reference-all-lights-study.md) retain source timestamps. [Sprint record](../../VISUAL-LIBRARY-SPRINT.md) records the interrupted and resumed windows.

Claude Opus 5.5 provided read-only visual reviews: [direction](claude-direction.md), [first pass](claude-first-pass.md), [expanded library](claude-expanded.md), and [lettering/layouts](claude-lettering-layouts.md). [Final shortlist review](claude-final-shortlist.md) favours the script/serif pair, compound brush sign, palace, marquee and print/depth. Reflective seams remain unresolved; the showcase uses resin and gives the ornate serif sign more time instead. The principal adopted changes were custom lettering, stronger scale contrast, an opened W–i join and less crowded sign placement. These are advisory judgments, not Olof's approval.

[Authoring guide](AUTHORING.md) gives the path from a selected phrase to a deterministic shot, with concrete next experiments.

## Next creative checkpoint

Review the short cut and choose a handful of contrasting identities. Once the wording/theme is selected, letter the actual hero phrases, tune their individual motion, and design the timing with sound. More font filters alone will not close the remaining gap to the references; optical lettering, composition, purposeful transitions and musical timing are the next work.
