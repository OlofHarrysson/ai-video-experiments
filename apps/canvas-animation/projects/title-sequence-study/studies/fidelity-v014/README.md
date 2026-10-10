# Fidelity laboratory — BILLIONS / KEEP UP

The selected result preserves the generated surface and animates light through softened vector masks. It removes the destructive color-to-SVG transfer from these two ornate designs. This is **hybrid artwork with code-controlled animation**, not recovered editable lettering.

[Play the eight-second silent check](output-motion-v004/clean-lettering.mp4), [inspect the close comparison](output-quality-v004/review-comparison.png), or [open the interactive player](index.html). Comparison columns are previous SVG, selected hybrid, original. NEXT remains unchanged.

Olof found v013's first and third designs textured, insufficiently sharp and below the generated targets. He authorized a two-hour tooling goal, including alternative tracing, SVG cleanup and different reconstruction techniques. The work window began 2026-10-10 12:08:07 UTC, with a deadline of 14:08:07 UTC (16:08 Stockholm). Original artwork and earlier attempts remain preserved. The selected study tests fidelity and restrained material lighting; it is not a new high-energy edit or an approved full intro.

## What the experiments established

Quantization was not the main failure. Native-grid tracing and speckle removal lost fine anti-aliased contours; flat paint regions also stepped continuous shading. Hard material classifications could add another layer of visible seams during lighting.

| Representation | BILLIONS native RGB MAE | KEEP UP native RGB MAE | Decision |
| --- | ---: | ---: | --- |
| Previous v013 SVG | 11.011 | 5.540 | Preserved baseline; visible roughness |
| Four-times-resolution spline trace | 4.870 | 2.563 | Better edges, still banded; extremely large |
| Packed adaptive color mesh | 0.723 | 0.468 | Visually close; retained research alternative |
| Original surface with vector controls | 0.000 | 0.000 | Selected for these designs |

Errors compare unlit native 1672×941 RGB pixels, on a 0–255 scale. They are not artistic scores and do not describe MP4 compression or arbitrary scaling. Exact hybrid identity is expected because it preserves the pixels; it does not demonstrate reconstruction of editable lettering. Source hashes and selected asset provenance are in [assets/provenance.json](assets/provenance.json).

Additional bounded experiments:

- A crop matrix isolated quantization, polygon versus spline fitting, zero versus one-pixel speckle removal, stacked versus cutout regions, and upsampling before versus after quantization.
- Four-times-resolution full traces created 350,780 BILLIONS paths and 190,405 KEEP UP paths. The spline geometry compressed to about 90 MB / 68 MB, respectively. More geometry did not recover semantic controls.
- Linear-contour cleanup reduced KEEP UP's 13.5 million contour points to 5.8 million with a 0.2-source-pixel tolerance. It helps size, not the underlying flat-color representation.
- BILLIONS ink separation produced cleaner engraving in places, but changed tones and flattened the target. It remains a graphic variation, not a faithful transfer.
- Adaptive Delaunay color fitting reached 600,000 / 400,000 vertices. Packed payloads are 6.25 MB / 4.20 MB, versus 2.53 MB / 1.86 MB for the originals. It reproduces the native image remarkably closely but functions as a lossy image representation. It is not an editable vector drawing, a font, or a source of unlimited detail.

## Selected implementation

1. Keep the two approved source surfaces byte-for-byte in `assets/`. Build directly from those preserved inputs.
2. Extract broad visible-surface control regions. KEEP UP has an enamel channel; BILLIONS has face, red and blue channels. These are approximate control regions, not true surface normals or isolated glyphs.
3. Rasterize those vectors separately with the shared [mask tool](../../../../tools/artwork/mask-texture.js). Feather controls by three source pixels. Never blur the artwork to hide transfer damage.
4. Apply continuous bounded exposure in the project shader. Neutral rendering bypasses the lighting transform exactly; highlights retain detail rather than receiving opaque paint patches.
5. Render motion at 3200×1800, downsample to 1600×900, then encode H.264 at CRF 14. Keep the original native-resolution proofs separately.

The reusable [artwork tools](../../../../tools/artwork/README.md) document when to keep surfaces and when to use the existing monochrome lettering-to-vector workflow. The mesh fitter, packer and browser decoder remain available as a measured alternative. The project owns material selection and lighting direction.

## Screening and limits

The assistant inspected native close crops and whole frames, decoded movie overviews, consecutive motion samples, final delivery crops, and magnified crops where mask feathering changed the image most. The selected controls produce less abrupt local lighting boundaries. The base artwork is visibly much closer than v013, including thin gold edges and enamel gradients. Human judgment of the motion remains open.

The selected render passes deterministic seek, 192 distinct frames, no browser errors or external requests, full FFmpeg decode and silent browser playback to the end. Play/pause, scene selection, seeking and a 390-pixel mobile layout pass. Pixel comparison confirms exact unlit native surfaces in the actual selected player. Packed mesh results were measured from the actual packed player, not inferred from the offline fit. An isolated build using only the selected assets and source recreates both players byte-for-byte. The final mesh neutral shader bypasses an unnecessary gamma round trip; its change versus the frozen mesh proof is bounded to one RGB level, while the selected hybrid stays exactly identical. Consolidated evidence is in [results.json](results.json). Submission-time microbenchmarks in render reports are not presented as real playback FPS.

The MP4 is lossy: sampled encoded-frame MAE is 2.27 for BILLIONS and 1.55 for KEEP UP relative to the pre-encode frame. Thin colored lines still incur chroma-subsampling loss. Supersampling improved edge presentation; it does not create new source detail. The interactive surface and native proofs are the fidelity reference.

This does **not** recover independent letters, hidden ornament, physically correct reflections, or arbitrary-resolution paths. Animated exposure is controllable; changing the wording or moving overlapping glyphs independently still requires new component artwork or deliberate redrawing. For future identities needing that motion, author separate parts before assembly rather than reverse-engineering a finished flattened plate. Flat NEXT-style artwork remains a good candidate for true vectors.

## Reproduce

From the repository root, with the Animate browser dependencies installed as documented in the [app guide](../../../../README.md):

```sh
node apps/canvas-animation/projects/title-sequence-study/studies/fidelity-v014/build.mjs
node apps/canvas-animation/projects/title-sequence-study/studies/fidelity-v014/render.mjs apps/canvas-animation/projects/title-sequence-study/studies/fidelity-v014/output-motion-new
node apps/canvas-animation/projects/title-sequence-study/studies/fidelity-v014/screen.mjs output-motion-new
```

The player is self-contained and needs no server. Render output must be a new directory. It includes native proofs, every rendered frame, encoded movie, contact/event sheets, validation and frozen page/source. The selected assets are versioned; reproduction does not depend on ignored exploratory output.

To recreate the controls, use `uv run --script prepare-masks.py assets/keep.png NEW-DIRECTORY --kind keep` from this study, or `--kind billions` with the other image. Mask recipes are project-specific. For the mesh, follow the shared tool guide: KEEP UP uses 400000 vertices / batch 25000 / initial step 8; BILLIONS uses 600000 / 35000 / 6, both with `--fit-colors`. `build-mesh.mjs` creates a separately labelled `mesh.html` research player. It does not replace the selected player.

`inspect-quality.py`, `check-masks.mjs` and `inspect-masks.py` provide matched evidence. The baseline comparison additionally needs the preserved v013 proof output. Trace diagnostics are in `trace-matrix.py`, `trace-hires.py`, `clean-linear.py`, `ink-separation.py`, `render-matrix.mjs`, `score-matrix.py` and `inspect-transfer.mjs`. Their local output directories preserve rejected attempts; they are not production dependencies.

## Independent critique

Two completed Claude CLI consultations resolved to `claude-opus-5-5` at high effort. The first helped isolate geometric damage and suggested upsampled tracing, separated inks and a hybrid control. The second judged the mesh visually close but challenged its production value: it was larger than the PNG, did not recover letter semantics, and needed checks at actual packed/scaled playback. That critique changed the recommendation from mesh-first to preserved surfaces with clean controls. Its mask-edge concern led to feathering and lit-crop checks. Raw consultation JSON remains local; this record distinguishes its advice from the tested result.
