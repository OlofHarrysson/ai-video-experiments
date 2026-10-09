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
