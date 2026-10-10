# Wild Hours — acid print (v007)

Second image-to-code study, 2026-10-10. Olof approved a deliberately different generated reference after the ornate enamel design in [v006](../image-to-code-v006/README.md). This study reconstructs fluorescent print lettering and animates its cut sections. WILD HOURS remains placeholder text; no film theme has been chosen.

[Watch and compare](review.html) · [Editable design](index.html)

## Selected result

- `output-phrase/wild-hours-acid-print.mp4`: eight seconds, 1536×1024, 30 fps, 240 frames, silent.
- `output-phrase/hero.png`: full-size code still. `clean.png` removes print texture.
- `reference/acid-print-01.png`: independently preserved generated reference; original location and SHA-256 in [reference-source.json](reference-source.json).
- `output-screen/`: decoded frame windows, repeat-boundary comparison and verified review-page screenshot.

The render uses no reference pixels, fonts, external images or network resources. Nine original polygon glyphs become 18 movable sections. Ink gradients, halftone, pinholes, edge flecks and background grain are procedurally generated with fixed seeds. The comparison page alone loads the generated reference.

## Movement

| Time | Action |
| --- | --- |
| 0–2 s | WILD's diagonal sections slide into alternating held configurations; HOURS anchors the composition. |
| 2–4 s | HOURS answers with diagonal cuts and a stagger between letters; WILD holds. |
| 4–6 s | Shorter accents shift the two ink plates, step the radial motif and move the checkers. |
| 6–8 s | Both words shear in opposite directions, reduce the displacement and resolve to the opening. |

This replaces the first draft's identical hit/decay on every beat. Travel lasts 3–8 frames, with deliberate holds and varied event durations on a 120-BPM grid. It is one graphic identity with an authored phrase, not yet the multi-style film edit. Texture stays attached to each section rather than randomly flickering.

## Construction and reuse

- [geometry.js](geometry.js): nine named, editable polygon outlines, including counters.
- [art.js](art.js): local colour patches, procedural print plates, section compositing and motif drawing.
- [motion.js](motion.js): explicit poses and timing, independently editable from appearance.
- [index.html](index.html), [viewer.js](viewer.js): play/scrub, texture toggle, movement strength, letter isolation, PNG and outline SVG export.
- [render.mjs](render.mjs): immutable output checkpoints, image-free renderer checks, source snapshots, browser controls and FFmpeg export.
- [screen.mjs](screen.mjs): decode temporal windows, inspect repeat frames and exercise the actual video/review page.

The renderer caches cropped glyph plates instead of compositing 18 full-size canvases. The final headless draw plus pixel-readback measurement averages 8.25 ms/frame across 30 samples. This is a local Chromium measurement, not a guarantee across devices. An earlier 0.02 ms figure omitted the readback and measured queued commands; it is not a rendering-performance result.

New words still need new glyph design. The plate, texture, timing and export mechanics are reusable. This flat style uses Canvas 2D; the enamel design's distance-field material shader is unnecessary here.

## Screening and limitations

Assistant inspected the full hero, untextured geometry, generated-reference comparison, twelve temporal samples, every decoded frame in 0.500–0.767 s and 6.000–6.267 s, and the last/first decoded frames. The reference retains more organic edge wear and finer variation in the diagonal fragments. Our reconstruction deliberately retains some cleaner polygon edges. Some extreme cut poses touch/crop the frame edges; the home pose preserves the full intended letter composition.

All 240 frames decode. Render checks pass exact frame-0/frame-240 equality, repeat seeking, texture changes, zero-strength restoration, changed motion output and zero image/network requests. Browser checks pass live playback advancement, controls, PNG download, a valid nine-path image-free SVG, and mobile overflow. Review-page video metadata/playback and editor navigation pass. Source snapshots and reports accompany the selected output.

[Claude's read-only critique](claude-review.md) helped identify the repetitive first cadence and muddy transparency treatment. It reviewed the earlier draft; the final selection and inspection are the assistant's judgment. Olof subsequently called this much better than the first reconstruction and approved another contrasting style. He did not give separate feedback on each motion phase. Silent delivery is intentional; this does not demonstrate music synchronization.

## Reproduce

From the repository root, with the existing Animate Playwright dependency and FFmpeg:

```sh
node apps/canvas-animation/projects/title-sequence-study/studies/print-to-code-v007/render.mjs output-new --motion
```

The output path must be new. Media, generated references and source snapshots stay local and ignored by Git; source and documentation are tracked. `screen.mjs` screens the selected `output-phrase` and refuses to overwrite its existing screening output. No server or cloud job is needed or left running.

## Lessons from the second style

An image-to-code workflow transfers across substantially different visual identities, but the construction method should fit the design. Flat print benefited from polygons and clipped ink plates; reusing a 3D-looking material shader would add work without serving the reference. Testing motion early exposed repetitive timing before final polish. A crisp still needs locally authored colour and negative-space decisions; a global effect on all letters weakened the match. A stable word gives the other word room to fragment without losing the composition.

This is evidence from two fixed-title studies, not proof of an automatic general converter. Taste remains an iterative human checkpoint.
