# Wild Hours — woven ribbons (v008)

Third image-to-code study, 2026-10-10. Olof preferred [the acid print study](../print-to-code-v007/README.md) to the earlier enamel treatment and selected a cobalt/ivory woven-lettering reference for the next experiment. WILD HOURS remains placeholder copy, not a chosen film theme.

[Watch and compare](review.html) · [Edit the design](index.html)

## Selected result

- `output-delivery/wild-hours-ribbons.mp4`: eight seconds, 1536×1024, 30 fps, 240 frames, silent.
- `output-delivery/hero.png`: full-resolution code still; `clean.png` shows the underlying surfaces without coloured bands.
- `reference/ribbon-reference-01.png`: generated reference, independently preserved. [Source and checksum](reference-source.json) · [Exact prompt](reference-prompt.md).
- `output-screen-delivery/`: decoded transition windows, last/first-frame comparison and review-page screenshot.

The renderer reads no reference pixels, images or fonts. Seventeen authored curve components construct nine letters and their crossing ribbons. A small WebGL2 renderer projects the surfaces and resolves overlaps with depth testing. Ivory bands, cobalt fields and fine hatching are computed in the fragment shader.

The motion is continuous colour travel and local rolling of ribbon surfaces. Four twist cycles and six colour-travel cycles fit the eight-second loop. The composition stays in place. This deliberately adds a flowing behavior to the library alongside the print design's cuts; it is not a full multi-style sequence or a demonstration of music synchronization. Crossing surfaces have depth, but the study does not re-knot the letters or alternate every over/under relationship.

## Construction

- [geometry.js](geometry.js): editable cubic centre lines, widths, roll parameters, depth and crossing components.
- [art.js](art.js): path sampling, returning contours, smoothed curvature, ribbon meshes, terminal caps, authored band profiles and deterministic rendering.
- [index.html](index.html) and [viewer.js](viewer.js): playback, scrubbing, movement strength, glyph isolation, coloured/surface view, PNG export and SVG path-guide export.
- [render.mjs](render.mjs): independent image-free rendering, immutable checkpoints, source snapshots, controls/export checks and MP4 encoding.
- [screen.mjs](screen.mjs): decoded-frame sheets and review-page video/playback checks. Accepts selected-output and screening-output directory names; refuses overwrites.

The I, H stems and R stem use returning paths: bands turn around and travel down the other side. Other open strokes use concentric terminal geometry. Curvature smoothly redistributes the band profile near bends. Broader crossing bundles taper into their parent letters. Roll is limited to avoid narrow bow-ties. Movement strength controls amplitude, preserving the loop period at intermediate slider settings.

SVG exports contain the 17 source guides and widths, not a baked vector copy of the shaded WebGL image. New words require new lettering. The ribbon construction and rendering mechanics can be reused.

## Iterations and lessons

The first prototype resembled uniformly striped tubes. Its shadow pass also wrote depth, incorrectly hiding parts of the same surfaces; the shadow pass now leaves depth to the artwork. Simple round masks clipped the stripes at terminals. Returning paths and concentric caps solved that structural problem.

[Claude's still/source critique](claude-review.md) helped identify band hierarchy, terminal construction and overly pinched crossings. The adopted revision uses explicit band widths, cobalt outer fields, smoother curvature and wider crossing ribbons. A final comparison prompted broader ivory areas and more asymmetry; the earlier contour-like treatment remains preserved.

The surface is ruled across its width, so it did not need twelve subdivisions across every segment. Reducing that tessellation lowered local headless render time from approximately 43 ms/frame to approximately 5–6 ms/frame with GPU completion included. This is a local measurement, not a guarantee for every device.

## Verification and visual limits

The selected run's reports accompany the output. Checks cover exact frame-0/frame-240 equality, repeated seeks, zero-strength restoration, a non-default strength loop, changed material/motion output, no image/network dependencies, and WebGL errors during frame rendering. Browser checks cover live playback, controls, PNG download, valid 17-path image-free SVG and mobile overflow. The complete 240-frame MP4 decodes; the review page's video metadata, playback and editor link are exercised separately.

Assistant screening includes full-size stills, the uncoloured surfaces, generated-reference comparison, temporal contact sheets, every decoded frame in 0.500–0.767 s and 6.000–6.267 s, and the repeat boundary. Human judgment of normal-speed motion remains pending.

The reference still has richer local asymmetry, tighter layering and more organic ribbon joins. The W's tight turns and the R's joins are the weakest fidelity areas. This is a controllable interpretation with real ribbon geometry; it does not reproduce every generated detail. Technical checks do not establish equal artistic quality.

## Reproduce

With the existing Animate Playwright dependency and FFmpeg, from the repository root:

```sh
node apps/canvas-animation/projects/title-sequence-study/studies/ribbon-to-code-v008/render.mjs output-new --motion
node apps/canvas-animation/projects/title-sequence-study/studies/ribbon-to-code-v008/screen.mjs output-new output-screen-new
```

Media and checkpoints stay local and ignored by Git. Source and documentation are tracked. No dev server, cloud resource or new image generation is needed for reconstruction or rendering.
