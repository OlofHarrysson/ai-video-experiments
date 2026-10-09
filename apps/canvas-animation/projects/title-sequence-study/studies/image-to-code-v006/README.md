# Wild Hours: generated design to editable lettering

2026-10-10. Olof proposed generating a stronger visual target, then rebuilding it in code for control. This study reconstructs the ornate Wild Hours target as 13 individually authored Bézier components, procedural materials and a six-second light loop.

**[Review the result](review.html)** · **[Edit the layers](index.html)** · [Selected still](output-final-01/enamel.png) · [Material loop](output-final-motion-01/wild-hours-material-loop.mp4)

Wild Hours is placeholder copy, not a selected film title or theme. This is one ornate identity within the broader typography library. The film's theme, soundtrack and final motion treatment remain undecided.

## Result and limits

The reconstruction has pink enamel faces, narrow stepped gold borders, crimson seams, purple depth, ivory chamfers, a gold plinth and faceted ornaments. Reflections and glints move while the lettering stays fixed. An ice/silver finish demonstrates material control. The viewer can isolate components, change depth, scrub the light, switch finishes, and export PNGs or SVG silhouettes.

Assistant judgment: the selected version is a strong, usable graphic identity and a substantial improvement over the earlier font/filter studies. It preserves the composition and recognisable lettering of the generated target. It is not a pixel-exact reproduction: the reference still has more varied local bevel widths, smoother bespoke curl transitions and subtler painted lighting. Human taste and playback review remain pending.

The SVG export contains editable outlines, not the WebGL enamel finish. This is bespoke lettering, not a font generator: changing the words requires new geometry. The light loop is a material demonstration, not the full energetic edit suggested by the film references.

## Source and controls

| File | Responsibility |
|---|---|
| `geometry.js` | Thirteen named letter, swash and ornament outlines in 1536×1024 coordinates. |
| `details.js`, `facets.js` | Authored reflection paths and translucent enamel planes. |
| `vector-fields.js` | Curve flattening, contour offsets, analytic signed distances and normals. Uses Clipper 6.4.2. |
| `renderer.js` | Gold/enamel/ivory profiles, cached extrusion geometry, lighting, palette, faceted jewels and glints. |
| `viewer.js`, `index.html` | Editing controls, image-free SVG outline export and full-quality PNG export. |
| `render.mjs` | Preserved still checkpoints, equal-size comparisons and source snapshots. |
| `motion.mjs` | Deterministic 144-frame / 24 fps MP4 export, source hashes and media metadata. |
| `verify.mjs`, `verify-viewer.mjs` | Geometry, seeking, loop, image independence, UI and export checks. |

`WildRenderer.draw(canvas, frame, options)` accepts `depth` (default 34), `palette` (0 pink/gold, 1 ice/silver), `glyph` (component ID or null), `flat`, `glints`, and `quality` (0.5–2 internal material scale). Frames wrap at 144. Full-quality output uses a 3072×2048 internal material buffer composited to 1536×1024. Playback uses a 768×512 material preview; pausing and exporting retain full detail.

The only rendering textures are generated from the editable paths. No pixels from the generated target enter the artwork renderer. The comparison page separately displays the target. The path parser supports the uppercase M/L/C/Q/Z commands used by this study; it is not a general-purpose SVG importer.

## Reproduce

From the repository root, install the title-study and Animate rendering dependencies if necessary:

```sh
npm ci --prefix apps/canvas-animation/projects/title-sequence-study
npm ci --prefix .agents/skills/animate
```

From this study directory:

```sh
node render.mjs output-next-still
node motion.mjs output-next-motion
node verify.mjs output-next-verification
node verify-viewer.mjs output-next-viewer-check
```

Chromium/Playwright and FFmpeg are required. The render and motion commands refuse to overwrite an existing output directory. The still comparison requires the preserved reference at `output/wild-hours-reference-01.png`; `motion.mjs` and `verify.mjs` work without it. Media remains local and is ignored by Git. No dev server is left running.

## Evidence and decisions

- [Sprint record](SPRINT.md) records the six-hour maximum, checkpoints and final screening. The selected result was completed in about 1 hour 45 minutes. Final evidence is preserved in `output-validation-final/`, `output-viewer-final/`, and `output-final-motion-01/`.
- Square-with-hole signed distances were checked at one and two samples per world pixel; maximum error was below 0.000016 pixels with no sign errors.
- Repeat seeking, an exact frame-0/frame-144 loop, and restoration after depth/palette/quality changes passed. A separate page rendered without any image assets or network requests.
- Viewer checks exercised palette/depth/component controls, SVG and PNG downloads, playback, and a 390px mobile viewport. The exported isolated W SVG has one vector path and no images.
- Full-quality software rendering initially took roughly 1.5 seconds per frame. Caching geometry reduced that to approximately 560 ms; the lighter playback preview measured roughly 42–57 ms. These are SwiftShader measurements, not a benchmark of a hardware-accelerated desktop browser.
- Four read-only Claude Opus 5.5 consultations informed visual critique: [first](claude-first.md), [second](claude-second.md), [third](claude-third.md), [fourth](claude-fourth.md). Earlier advice was corrected against the images. The final S uses the fourth consultation's proposed contour with further local positioning changes.
- Full-color VTracer probes are preserved in `output-vector-probe` and `output-vector-fine`. They produced 4,692 and 20,537 paths and visibly posterized color patches. They were rejected as the rendering approach; `trace-reference.py` preserves the probe settings.

The useful workflow is to establish a demanding visual target, author a small set of meaningful shapes, and design the material profiles around those shapes. An automatic color trace did not supply that structure. A generic bevel alone also left a visible quality gap; the lettering needed local ornaments, curve corrections and individually shaped reflections.

## Generated target provenance

Built-in image generation produced `output/wild-hours-reference-01.png` from [this exact prompt](prompt-01.md), without an input image. It follows the earlier preferred Night Fever direction. The original is independently preserved at `/Users/olof/.codex/generated_images/01a11531-7ce5-7fd1-bc3d-a4921247fd3d/exec-39d41025-c58e-4daf-82e8-5fb9d55f8ba8.png`.

Reference dimensions: 1536×1024. SHA-256: `212e4d1ef5c0f4dc523f6f2eb2fe81fc8a7300dc72e6b512e4e2ecc7a94026c9`. The reconstruction uses no additional image generation, cloud GPU or paid media job.
