# AI intro — richer graphic direction

Olof rejects v011: “I don't love this storyboard though. It's a bit too simple graphics.” The six-frame board is preserved as a rejected visual direction. This feedback does not establish approval or rejection of its particular story beats; the story remains open.

The assistant had reduced three custom lettering plates to simple contour treatments and used plain font compositions for the remaining cards. That was a regression from the richer v010 work Olof liked. Repeatable extraction was useful, but technical reliability did not establish an adequate design standard. The new occurrence is recorded as AF-20261010-132235, related to AF-20261010-121017.

## Current experiment

Develop three finished graphic targets for the AI theme before deciding what information to extract. Keep image-generated composition, ornament, surfaces and local detail in view during reconstruction. Test one target's transfer to editable vectors against the actual artwork before extending a board or animating it.

- **BILLIONS:** financial showcard lettering and integrated security-print ornament; ivory, gold, red and blue on black.
- **NEXT:** an asymmetric collision of custom architectural letterforms, nested linework, scale and overlap.
- **KEEP UP:** elaborate red enamel calligraphy, interwoven swashes, gold edges and designed highlight shapes.

These are design candidates, not a new approved sequence. Text is thematic language rather than attributed headlines or numeric factual claims. Silence and controlled medium-high intensity remain the intended eventual motion direction. No animation is authorized by a still-frame preference alone; prior animation review boundaries remain in place.

Generated originals and independent project copies are preserved. [Exact prompts](prompts.json) record the built-in image-generation calls. The finished targets are raster artwork until a separate reconstruction is shown; they must not be represented as rendered code.

## Result

[Inspect all directions](index.html) · [NEXT rendered from vectors](next.html) · [NEXT side-by-side comparison](output-next-proof-v002/comparison.png)

Three targets were generated and inspected. Independent source copies and originals have matching SHA-256 hashes in [sources.json](sources.json). The candidate words are correctly present; ornate P readability in KEEP UP deserves human inspection. These are visual candidates, not approved designs.

The **NEXT vector proof** uses 241 paths and six declared inks: black, ivory, chartreuse, cobalt, red and cyan. It preserves the full composition, cropped background letters, interior rails and diagonal overlap, rather than extracting only the word silhouette. `vector-next-v003/art.svg` is 33,009 bytes. It draws deterministically without runtime errors, using no raster inside the self-contained [vector renderer](next.html). The assistant inspected the full-size vector drawing and target comparison. The transfer removes subtle source shading; this is an intentional flat-ink approximation, not pixel identity.

The first adaptive eight-color NEXT trace created 2,963 paths from incidental color variation. Explicit ink assignment reduced this to 241. Spline fitting rounded mechanical edges; polygon tracing with the shared 0.55-pixel cleanup restored sharper geometry and reduced SVG size from 342,243 to 33,009 bytes. This is a useful bounded transfer, not proof that every source can be reduced in the same way. Ordered paint paths are not complete movable word layers: occluded geometry still needs art direction and reconstruction before independent word motion.

**BILLIONS full-color transfer was rejected.** Its 16-color trace produced 15,757 paths and a roughly 7 MB SVG, yet the inspected proof muddies fine engraving and loses blue/red presence. Source and attempted conversion remain preserved under `reference/`, `output-vector-billions-v001/` and `output-billions-proof-v001/`. This target needs lettering/ornament/material separation or another deliberate reconstruction; it is not presented as successful code art. KEEP UP remains a generated material target; it has not been reconstructed in this experiment.

No production animation, soundtrack or server was started. The next human checkpoint is whether these targets meet the intended graphic ambition. The v011 story has not been reaffirmed by this visual experiment.

## Reproduce the selected transfer

```sh
uv run --script apps/canvas-animation/projects/title-sequence-study/studies/art-direction-v012/trace-color.py apps/canvas-animation/projects/title-sequence-study/studies/art-direction-v012/reference/next.png apps/canvas-animation/projects/title-sequence-study/studies/art-direction-v012/vector-next-new --palette 000000,f6f0dc,d7ff00,0735ed,ff1527,00cae7 --mode polygon
node apps/canvas-animation/projects/title-sequence-study/studies/art-direction-v012/inspect-transfer.mjs vector-next-new reference/next.png output-next-proof-new
```

The source PNG is needed only for extraction/comparison. Committed vector geometry is sufficient to regenerate the Canvas drawing. The inspector writes a self-contained `vector.html`, its PNG rendering, a comparison and a technical report. Selected reports are `output-next-proof-v002/report.json` and `vector-next-v003/report.json`. Paint-path segmentation remains experimental and project-owned; it has not replaced the simpler shared silhouette/grouping tool.
