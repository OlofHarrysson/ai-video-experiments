# Typography feasibility study

2026-10-09. Twelve original graphic identities drawn with Canvas 2D, testing visual feasibility before selecting the film's theme. View [all identities](output/all-identities.png) or open [the local study](study.html) in a browser. Cards are still by default. The [silent motion proof](output/motion-proof.mp4) shows 01, 05, 08 and 11 for three seconds each; it is not the proposed edit or escalation.

## Construction and assessment

| # | Identity | Construction | Assistant assessment |
| --- | --- | --- | --- |
| 01 | Architectural neon | Custom line-path SIGNAL glyphs, nested strokes, sign enclosure | Strong original sign; finer and more geometric than the source. |
| 02 | Perforated marquee | Text mask sampled into hollow circles, script overlay | Convincing family; final words need individual composition. |
| 03 | Varsity × signature | Rockwell outlines, Snell Roundhand, rules and star | Useful compound identity; less aggressive scale and density than the source. |
| 04 | Illuminated blackletter | UnifrakturCook, layered edges, gradient, drawn flourishes | Credible blackletter and dimensional color; different glyph construction. |
| 05 | Chromatic signature | Snell Roundhand, offset passes, gradient, strokes and stars | Functional but simpler than the source's elaborate swashes and spacing. |
| 06 | Emblem lettering | Rockwell plus a rotating drawn sunburst forming the O | Demonstrates integration of lettering and graphics; original interpretation. |
| 07 | Cut-metal stencil | Original polygon letters and diagonal cutouts | Strong custom-lettering proof; does not match the source's curved beveled glyphs. |
| 08 | Contour turbulence | Repeated rounded outlines, transforms and strip displacement | Controllable distortion; less dense and varied than the reference. |
| 09 | Rainbow wordmark | Rounded lettering, nested edges and integrated rainbow | Recognizable family; thinner and cleaner than the source. |
| 10 | Editorial collision | Impact with smaller Didot and script layers | Demonstrates type and scale contrast; needs denser layouts for the chaotic phase. |
| 11 | RGB print screen | Three offset colored dot lattices sampled through a text mask | Working colorful raster effect; source dot distribution and composition differ. |
| 12 | Bubble insignia | Rounded type, thick edging, script, star and orbit | Convincing compound treatment; Latin glyphs replace Japanese lettering. |

These are assistant assessments, not Olof's approval. MORE, SIGNAL and Becoming are sample words, not a selected theme or script.

## Reference mapping

[reference-map.json](reference-map.json) pairs every identity with an inspected source frame and describes the relationship. Comparisons: [01–04](../../references/inspection/typography-v001-comparisons/comparison-1.png), [05–08](../../references/inspection/typography-v001-comparisons/comparison-2.png), [09–12](../../references/inspection/typography-v001-comparisons/comparison-3.png). These contain reference pixels and remain ignored by Git. The original study artwork contains no reference pixels or generated images.

## Validation and limitations

- Twelve frames rendered at 1280×544 and visually inspected, together with all three reference-comparison pages.
- Same-timestamp rendering after a different timestamp gives the same PNG hash for all twelve. Font metrics differ from monospace fallback for all eight required families. See `output/render-report.json`.
- Motion proof: 288 frames, 24 fps, 1280×544, 12 seconds, no audio. This establishes controlled movement, not the final film's escalation, rapid readability or sound design.
- The custom polygon and line-path alphabets cover SIGNAL only. New words need new glyphs. Font-based effects can be adapted, with composition changes.
- Exact bespoke swashes, ligatures, multilingual lettering and dense custom logos still require individual drawing. These are editable scripts, not a general font-generation system.
- Seven faces are local Mac fonts: Impact, Rockwell, Snell Roundhand, Didot, Arial Rounded MT Bold, Avenir Next Condensed and Helvetica Neue. Their files are not copied. Other systems may render differently or require separately licensed equivalents.
- UnifrakturCook is bundled only in this study under the [SIL OFL](fonts/OFL.txt); [source and SHA-256](fonts/source.json). No system font installation was made. This test uses a local font resource rather than Animate's single-file delivery convention; the eventual film needs an explicit font-packaging choice.
- The first pass's Luminari looked too soft for the blackletter reference; `output-first-pass/` preserves it. `output-second-pass/` preserves the next version before dot-pattern refinements.
- The HTML rendered through Playwright, including a full-page screenshot. In-app browser navigation to its `file:` URL was blocked by browser policy; button interactions were not independently verified there. PNGs and MP4 are the primary review artifacts.

## Reproduce

From the repository root, using Animate's installed Playwright:

```sh
node apps/canvas-animation/projects/title-sequence-study/studies/typography-v001/render.mjs --motion
node apps/canvas-animation/projects/title-sequence-study/studies/typography-v001/compare.mjs
```

The comparison script needs the preserved local reference frames. Rendered media are ignored by Git. Before changing artwork, move the current `output/` to a new ignored `output-<revision>/` directory: rerunning overwrites current output filenames.

Next: Olof identifies which treatments are strong enough and what is missing. Then refine a small shortlist or choose a theme and design the escalation. No theme or visual approval is inferred from silence.
