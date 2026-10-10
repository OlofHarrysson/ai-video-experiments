# Wild Hours — custom vector lettering (v010)

A silent, ten-second typography study built from four custom lettering designs. This tests a stronger source-art workflow after Olof rejected v009 as low quality compared with the film references. “WILD HOURS” remains placeholder copy; no film theme or hackathon message has been selected.

[Watch the selected cut](review.html) · [Scrub the editable renderer](index.html)

## What is different

The letter shapes were designed with image generation, extracted as editable vector paths, then finished and animated in code. They are not downloaded fonts. The script also uses two vectorized highlight layers from the generated material reference. The animation loads **no raster artwork, video, audio, web fonts, or network resources**.

| Identity | Graphic construction | Motion and editorial role |
| --- | --- | --- |
| Enamel script | Sweeping connected strokes, gold/oxblood edges, red faces and shaped highlights | One directional light pass; held hero and swash detail |
| Mechanical | Cleaned straight polygons, silver/lime planes, hard cobalt offset | Sixteen parts assemble diagonally on two-frame steps |
| Engraved showcard | Tuscan letterforms, ivory faces, separated red/ivory/blue contours and a hard offset | Ink registration, intact isolated words, and a diamond-counter crop |
| Psychedelic | Organic letterforms with fixed-width pink, orange and cream bands | Bands move inward; tight crops contrast with the full reading |
| Dotted/script hybrid | Mechanical WILD paired with ivory script HOURS | Selected whole dots alternate in brightness |
| Wire planes | Six colored copies of the mechanical contours | Planes open during a brief accent |

There are four underlying lettering designs in this small sample, not six font systems. The last two compositions recombine existing geometry. Lettering is bespoke to these words: changing the text requires new outlines. Materials, positions, layer ordering, timing, crops, and construction events remain editable.

## Workflow and ownership

- `trace.py` segments the preserved monochrome reference and extracts vectors with VTracer 0.6.15. The mechanical design uses polygon tracing plus removal of raster stair-step vertices; the other designs use splines.
- `geometry.js` and the four `.svg` files preserve the editable shapes. The renderer normalizes their placement without stretching their proportions.
- `trace-highlights.py` extracts two specular masks from the material reference into `highlights.js`. This transfers designed reflection shapes rather than claiming a generic bevel recreates them.
- `art.js` draws the surfaces and compositions. It reuses the analytic distance-field implementation in `../image-to-code-v006/vector-fields.js` and the project's existing Clipper dependency.
- `edit.js` owns the fixed shot list and distinct construction events. The piece does not use camera drift or an ever-accelerating intensity ramp.
- `build.mjs` produces a self-contained `index.html`. The preview needs WebGL 2 and floating-point render targets; initialization errors are surfaced in the page.
- `render.mjs` makes full-size stills and a material board. `motion.mjs` exports the silent MP4 and freezes its source. `screen.mjs` checks preview controls and browser playback, and extracts frames from the encoded MP4 for inspection. `probe.mjs` records composition checks.

The materials are graphic approximations, not physically based 3D surfaces. In particular, the script's generic reflections still have less intentional local shaping than the generated target. The fixed-width psychedelic treatment uses clean graphic bands. The final edit favors flat ink registration over the more ornate material treatment.

## Evidence and decisions

The first reconstruction exposed a crop overlap, rounded mechanical corners, arbitrary screen-space facets, and pinched bands from local-width estimation. The next passes corrected the extraction regions, used polygons and part-based planes, and replaced normalized bands with fixed-width inlines. A rectangular word crop also clipped the Tuscan capitals; word views now select the actual vector components.

[Claude's first read-only critique](claude-first.md) helped prioritize those changes. [The second critique](claude-second.md) led to an interleaved edit, simpler dot construction and removal of repeated shots. The suggested two-frame strobe passage was rejected because Olof requests controlled medium-high intensity. Final evidence is recorded in [the sprint record](SPRINT.md). Technical correctness is separate from artistic quality, and no assistant or model judgment constitutes Olof's approval.

References and generated source images remain local under ignored `reference/`. Original model outputs are independently preserved in the Codex generated-image directory. Exact prompts and source hashes are recorded in [reference-prompt.md](reference-prompt.md), [material-prompt.md](material-prompt.md), `reference-source.json`, and `material-source.json`. No film-reference pixels are used in the artwork.

## Selected result

`output-final-02/wild-hours.mp4`: 1600×900, 24 fps, 240 frames, ten seconds, no audio stream. Twenty shots last 6–28 frames. The selected movie and source hashes are recorded in `delivery.json`; all earlier proofs and cuts remain preserved.

Assistant assessment: the custom shapes are materially stronger than the previous stock-font treatments. The finish and editorial breadth still fall short of the references. This establishes a better design workflow, not reference-level parity or a finished film concept. Olof subsequently calls v010 much better and amazing. He identifies strong generated letterforms converted to vectors as the breakthrough and authorizes making that process repeatable.

## Reproduce

From the repository root, with existing Animate/Playwright and title-study dependencies installed:

```sh
uv run --script apps/canvas-animation/projects/title-sequence-study/studies/vector-lettering-v010/trace.py
uv run --script apps/canvas-animation/projects/title-sequence-study/studies/vector-lettering-v010/trace-highlights.py
node apps/canvas-animation/projects/title-sequence-study/studies/vector-lettering-v010/build.mjs
node apps/canvas-animation/projects/title-sequence-study/studies/vector-lettering-v010/render.mjs output-new-stills
node apps/canvas-animation/projects/title-sequence-study/studies/vector-lettering-v010/motion.mjs output-new-motion
node apps/canvas-animation/projects/title-sequence-study/studies/vector-lettering-v010/screen.mjs output-new-motion output-new-screen
```

Only retracing needs the local generated PNGs. The committed vectors are sufficient to build and render. Output directories refuse overwriting; earlier proofs and cuts are preserved. Media is ignored by Git. No server or cloud GPU is required.
