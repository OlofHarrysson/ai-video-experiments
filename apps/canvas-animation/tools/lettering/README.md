# Generated lettering → editable vectors

A small manifest-driven pipeline for bespoke words and titles. It extracts artwork, preserves source provenance, validates semantic groups, and provides a visual comparison. It does not synthesize a font or infer stroke order.

Proven on [KEEP UP v011](../../projects/title-sequence-study/studies/keep-up-v011/README.md): three independently generated plates, 33 paths, eight manually declared groups. Earlier WILD HOURS experiments supplied the tracing approach; they remain unchanged.

## Canonical workflow

1. Generate one monochrome plate per identity, with open counters and generous margins. Save an independent project copy and the exact prompt. Review spelling before tracing.
2. Write a project-owned manifest. Each asset supplies `id`, `text`, `source` relative to the manifest, `mode` (`spline` or `polygon`), and `groups`. Threshold defaults to 130, light foreground. Optional `simplify` removes redundant polygon vertices; it is a pixel tolerance, not a quality level.
3. Trace to a **new** vector directory:

   ```sh
   uv run --script apps/canvas-animation/tools/lettering/trace.py path/to/lettering.json path/to/vectors-v001
   ```

4. Inspect to a **new** output directory:

   ```sh
   node apps/canvas-animation/tools/lettering/inspect.mjs path/to/lettering.json path/to/vectors-v001 path/to/output-inspection-v001
   ```

5. Open `inspect.html`. Check source/vector, overlay, group boundaries and pivots. Inspect narrow counters, long tips, separated decorations and word isolation. Update the manifest and create a fresh trace if needed. The source and manifest hashes prevent comparing old vectors against changed inputs.
6. Consume `assets.json` and `runtime.js` in the project renderer. `Lettering.prepare(asset)` returns combined and grouped `Path2D` objects, component bounds and pivots in original source coordinates. The caller controls materials, composition and animation. `Lettering.serializable()` exports the measured grouping without browser objects and can be prepared again.

The inspector deliberately embeds the original image for comparison. A film renderer can use only paths, with no source images. The pipeline uses existing repo-local Playwright/Chromium and PEP 723 Python dependencies; it needs no server or GPU subscription.

## Grouping

```json
{
  "id": "title",
  "text": "TWO WORDS",
  "source": "reference/title.png",
  "mode": "polygon",
  "simplify": 0.55,
  "groups": [
    {"id":"first", "label":"TWO", "role":"word", "region":[0,0,1,0.5], "pivot":[0.5,1]},
    {"id":"second", "label":"WORDS", "role":"word", "region":[0,0.5,1,1], "pivot":[0.5,0]}
  ]
}
```

Regions are normalized `[left,top,right,bottom]` bounds. A path must fit wholly inside the region; using its center could silently cut semantic groups. If word bounding boxes overlap, use `"parts":["p000","p003"]` instead of `region`. The inspector's `prepared.json` lists each path's measured bounds. Every path must belong to exactly one group. Include detached details with the correct word or glyph. A pivot is normalized within the group's bounds; `pivotPoint` is its measured source-coordinate position. Group assignment is manual design intent, not OCR.

## What checks mean

- Touching the source-image boundary stops extraction; insufficient configured margin produces a warning for inspection. Generated images do not reliably obey margin instructions.
- Duplicate, missing, unknown or empty groups stop inspection. Guard checks exercise missing/duplicate/unknown assignments.
- Pixel intersection-over-union compares the thresholded source silhouette with the rasterized SVG. This experiment requires >98% overlap as a basic regression guard, followed by visual screening. It does not establish letter quality, spelling, perceptual equivalence or production suitability. Tiny important features may contribute few pixels.
- Browser errors, deterministic output, layout and source hashes provide technical evidence. Artistic approval and motion quality remain separate.
- Path IDs are stable for a frozen source and recipe; retracing with changed settings can change them. Recheck grouping after every retrace.

## Current limits

The tracer is pinned to VTracer 0.6.15 to reproduce the existing experiment, not presented as the latest release. Its supported transform is translation. Source plates are opaque monochrome images; transparent or multicolor sources need deliberate preparation. Polygon cleanup preserves detail at the expense of more vertices; spline fitting can look smoother but altered fine tips in this test. High-resolution curves should be rechecked if enlarged far beyond the source scale. Separately authored highlight layers and stroke skeletons are not automatically extracted by this tool.
