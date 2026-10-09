# Reconstruction sprint

Authorized 2026-10-09. Goal began at 21:53:48 UTC (23:53:48 Stockholm); hard stop is 2026-10-10 03:53:48 UTC (05:53:48 Stockholm), six hours later. Finish earlier if the intended quality and controls are achieved. Do not extend beyond this deadline without Olof's instruction.

## Outcome

A faithful, exceptionally polished code reconstruction of the generated Wild Hours design, with editable silhouettes and independently controllable material layers. Preserve source artwork and every meaningful visual checkpoint. Render equal-size comparisons and inspect the actual result. Demonstrate material motion after the still is strong.

## Sequence

1. Recover and refine the letter silhouettes. Compare flat geometry against the reference before materials.
2. Build the nested gold edges, enamel faces, purple sidewalls, shaped highlights and local ornament. Inspect full composition and enlarged glyph crops.
3. Iterate on the weakest visible differences. Seek Claude's read-only visual critique if useful; retain responsibility for judgment.
4. Add deterministic material animation with the composition fixed, plus controls that expose meaningful editability.
5. Screen rendered stills and decoded video, verify deterministic seeking, preserve provenance, document limitations and commit the result.

Code recreation may use reference-derived vector outlines as geometry, but must not depend on the generated bitmap for the artwork at runtime. The comparison viewer may show it beside the reconstruction. This is a fixed title design, not a font generator or final film.

## Acceptance evidence

- High-resolution reference/reconstruction comparison and untextured silhouette view.
- Clean joined curves, purposeful overlaps, differentiated face/rim/sidewall materials.
- Editable geometry and working material controls, with no bitmap artwork in the renderer.
- Stable, deterministic frames; a short inspected motion preview and honest account of any remaining fidelity gap.

## Checkpoint: 2026-10-09 22:34 UTC

Goal is active; hard stop remains 03:53:48 UTC. No motion export or final quality claim yet.

- Thirteen separately authored Bézier components and a browser comparison viewer are implemented. `geometry.js` owns silhouettes; `details.js` owns optional reflection paths; `renderer.js` builds geometry-derived signed distance fields and WebGL materials. No reference pixels enter the renderer.
- Iterations `output-first` through `output-ninth`, plus `output-profile-01` onward, preserve visual checkpoints and source snapshots. The general shader is still visibly less intricate than the generated target. `output-eighth` is a useful earlier baseline.
- Two read-only Opus 5.5 consultations are recorded in `claude-first.md` and `claude-second.md`. The second corrected the first: ivory has a flat face and narrow perimeter chamfer, and crimson is a front-plane band. Some earlier advice was wrong; compare actual images before following it.
- The reference depth mostly projects down-right. An outward-flaring trial was rejected after inspecting the W curl and H foot. Current geometry-derived depth uses a down-right displacement. HOURS now uses a union mask for the continuous lower body.
- A full-color VTracer probe is preserved in `output-vector-probe` and `output-vector-fine`. It recovers the reference composition but creates posterized patches (4,692 and 20,537 paths respectively). It is not the selected renderer or an adequate substitute for clean authored geometry. `trace-reference.py` records the reproducible probe.
- Current work refines the explicit edge-band profile and corrects the primary reflection direction: highlights belong on the upper-left-facing shoulders. A prior positive reflection-band offset lit the wrong side.
- The generated reference SHA-256 is `212e4d1ef5c0f4dc523f6f2eb2fe81fc8a7300dc72e6b512e4e2ecc7a94026c9`. It remains local, preserved independently of all generated outputs.
- No dev server, cloud GPU or paid generation is running. Two Claude calls completed successfully.

Next: inspect the newest profile render, continue refining visible gaps, add meaningful editing controls and SVG export, then deterministic motion evidence. Do not claim the requested quality is achieved merely because the technical checks pass.

## Checkpoint: 2026-10-09 23:22 UTC

The active goal remains within its six-hour window. Current still: `output-cache-02/enamel.png`. Motion proof `output-motion-01` is an earlier geometry checkpoint, not the final delivery. Do not use it as evidence of the later S correction.

- Replaced raster-derived normals with analytic distances to flattened Bézier segments. `vector-fields.js` uses GPU closest-segment distances and exact scanline signs; Clipper 6.4.2 resolves contours and mitered offsets. This removes the earlier striped reflections.
- Darkened purple sidewalls, added a dark seam/crimson lip, made the lower plinth predominantly gold, added concave faceted stars and H/R spurs, and refined the H crossbar and S. Authored translucent enamel planes live in `facets.js`.
- Renderer uses cached depth geometry and local stroke widths. These are derived from paths, not the reference bitmap. Browser playback uses a 768×512 material preview; paused/PNG/video renders use a 3072×2048 internal material buffer, composited to 1536×1024.
- Software WebGL measurements improved from approximately 1.5 s/frame to 42–57 ms/frame in preview. Full-quality rendering is about 560 ms/frame. This is a SwiftShader test, not a measurement of the user's hardware-accelerated browser.
- `verify.mjs` passes square-with-hole distances at densities 1 and 2 (maximum error below 0.000016 world pixels), repeat seeking, exact frame-0/frame-144 loop, restoring state after palette/depth/quality changes, and image-free rendering with zero network requests.
- `verify-viewer.mjs` passes UI interactions, isolated W SVG export with no image elements, PNG export, playback advancement and mobile overflow checks. Paused/full PNG output remains full quality.
- Third read-only Opus 5.5 critique is recorded in `claude-third.md`. Fourth is running and must be awaited on its existing process. It focuses on the S curl and whether the new enamel planes are genuinely improving the design.
- Still unresolved: S curl fidelity, a few overly uniform/material edges, final source snapshot and final video/decoded-frame review. Preserve all checkpoints; no new generated image or cloud resource is required.

## Selected result: 2026-10-09 23:39 UTC

Selected stills and equal-size comparisons: `output-final-01/`. Selected motion: `output-final-motion-01/wild-hours-material-loop.mp4`. The review page and editor link these results. The goal was completed in approximately 1 hour 45 minutes, within the six-hour maximum.

- Fourth Claude consultation completed successfully on Opus 5.5. Its S contour corrected a spine offset and allowed space for the outward rim. The selected version additionally shifts the lower curl left, refines the W's central leg, tapers an abrupt reflection at its join, warms the gold, and adds sparse violet/copper reflections on the sidewalls. All earlier attempts remain preserved.
- The selected still, first motion frame, and independent image-free verification render have the same SHA-256: `bcee6387bd98c597afe910a826f615acc3e27543520d7b8fc8194c7342386e76`. Both copies of the generated reference still match its original hash.
- `output-validation-final/verification.json` passes numeric distance checks, repeated seeking, exact frame-0/frame-144 equality, restoration after depth/palette/quality changes, changed output for each meaningful control, and zero image/network dependencies.
- `output-viewer-final/report.json` passes controls, valid isolated SVG with one path and no images, PNG export, playback advancement and mobile overflow. Final software-rendered preview measured approximately 40–57 ms/frame; full-quality rendering approximately 590–631 ms/frame. Hardware-accelerated browser performance was not measured.
- All 144 video frames decode successfully: 1536×1024, 24 fps, six seconds, no audio. Source frames cross the loop boundary within ordinary adjacent-frame change. Initial interframe compression introduced a small boundary step; the preserved final export uses H.264 CRF 14, all-intra encoding. The decoded boundary difference is 0.881/255 grayscale units, below the maximum ordinary adjacent-frame difference of 0.948/255. This is a continuity check, not a perceptual quality score.
- Selected movie SHA-256: `48b45620f90312422c6bf34889bbfd0a8ee2042e5eed5fa4d498ccded4f8ae90`. Full media metadata, source hashes and decode checks are saved beside it. The earlier interframe MP4 remains preserved.
- Assistant inspected the selected full still, enlarged comparisons, palette variant, editor screenshots and decoded motion sheet. The result is selected as a strong reusable graphic identity. The target still has more varied local bevel widths and more organic curl transitions. Human taste/playback judgment remains pending; this is not a chosen film theme or final title sequence.
- No server, cloud GPU, image-generation job or Claude consultation remains running. No additional image generation was used during reconstruction. Source work is checkpointed on the existing main branch; the unrelated AGENTS.md change is preserved.
