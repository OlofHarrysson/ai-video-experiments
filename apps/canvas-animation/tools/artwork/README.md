# Finished artwork: fidelity before conversion

Use [lettering tools](../lettering/README.md) for monochrome silhouettes and flat artwork that genuinely benefits from editable paths. For ornate engraving or rendered enamel, converting every color patch into SVG can destroy the approved design.

The [v014 fidelity study](../../projects/title-sequence-study/studies/fidelity-v014/README.md) compares tracing, contour cleanup, ink separation, adaptive color geometry and a hybrid surface. Its selected route preserves the original pixels, draws broad vector control masks, and animates light in code. This preserves appearance but does not recover editable glyphs, hidden geometry or a font.

## Repeatable decision

1. Preserve the original, its prompt and SHA-256. Inspect spelling and edges before extraction.
2. Render a neutral reconstruction at the original dimensions. Compare matched close crops of thin lines, counters, gradients and highlights, plus the whole image.
3. Separate surface fidelity from animation controls. A mask may be simplified and feathered without filtering the artwork. Do not classify thousands of individual bright pixels as independent shiny surfaces.
4. Test the actual packed asset, output dimensions and encoded movie. Native-grid similarity does not establish quality after scaling or compression.
5. Keep the simpler representation when two approaches provide the same controls. Do not call image samples stored in geometry an editable vector drawing.

## Adaptive color-mesh experiment

`fit-mesh.py` places Delaunay vertices where reconstruction error is high, then optionally fits RGB vertex colors with sparse least squares. `pack-mesh.py` spatially orders those vertices and packs half-pixel coordinates, RGB8 and triangle indices. `mesh-codec.js` decodes this format in a browser.

```sh
uv run --script apps/canvas-animation/tools/artwork/fit-mesh.py original.png output-mesh-v001 --vertices 400000 --batch 25000 --initial-step 8 --fit-colors
uv run --script apps/canvas-animation/tools/artwork/pack-mesh.py output-mesh-v001/mesh.json output-pack-v001
```

All outputs must be new directories. Python dependencies are isolated by `uv`; no system package installation is required.

This is **mesh-encoded image data**, not semantic vector lettering. At native size it substantially outperforms the tested color traces. It is larger than the original PNG, has no inherent glyph-editing advantage, and cannot invent detail beyond the source resolution. It is retained as a research tool, not the default production route. Budget limits are caps, not quality guarantees; inspect residuals and actual GPU renders. Current fitting assumes opaque RGB input and current packing supports half-pixel coordinates within uint16 range. Sorted triangle indices require face culling disabled.

## Evidence and ownership

The study owns its artwork, color-selection recipes, lighting direction, export and visual judgment. Shared tools own representation and browser mechanics. Original art remains the reproduction input; storing a generated HTML page is not a substitute for source provenance.

## Vector masks for preserved surfaces

`mask-texture.js` exposes `ArtworkMasks.render(data, options)`. Input uses source dimensions, `coordinateScale`, and named layers of SVG path data with translation transforms. The caller maps each layer to an RGB control channel. `feather` is measured in source-image pixels; it filters only the mask texture. Unknown channels and unsupported transforms are explicit errors.

```js
const controls = ArtworkMasks.render(maskData, {
  colors: {enamel: '#ff0000'},
  feather: 3,
});
```

Upload the returned canvas separately from the original artwork. In a fragment shader, sample the control channel to blend effects continuously. The v014 example applies bounded exposure in linear light; it preserves neutral pixels exactly and does not manufacture surface normals. Overlapping masks are painted in declared layer order, so author independent channels deliberately.
