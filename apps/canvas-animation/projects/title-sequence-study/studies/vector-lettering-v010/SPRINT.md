# Two-hour typography improvement goal

Started 2026-10-10 at 09:30:46 UTC / 11:30:46 Stockholm. Hard deadline 11:30:46 UTC / 13:30:46 Stockholm.

Olof rejects editorial-v009 as low quality compared with the references. Its technical correctness and assistant shortlist did not establish adequate visual quality. This sprint aims to improve the visual result, not increase the number of effects or catalogue entries. Silence remains mandatory. Existing outputs stay preserved.

Approach: generate unusually strong letter geometry, preserve it as editable vector paths rather than manually approximating it with generic fonts, construct materials and local motion in code, compare against the intended design, then make a short controlled high-energy edit from successful identities. Vector tracing is part of the existing image-to-code experiment; the raster will remain a reference, not a playback asset. “WILD HOURS” stays placeholder copy from the previous studies.

Acceptance evidence: comparative stills and a screened silent cut with an honest account of what improved and what remains weaker. Human taste approval is not assumed. If the new path fails to preserve quality, present the evidence and best result at the deadline instead of claiming the ceiling is solved.

## Outcome

Selected `output-final-02/wild-hours.mp4`: ten seconds, 1600×900, 24 fps, 240 frames, silent. Twenty shots last 6–28 frames; holds alternate with short accents without a two-frame strobe passage. Four custom lettering designs support six graphic constructions. The sequence mixes identities from its opening and includes isolated words, off-centre placements, close details, registration and one final hero hold.

Assistant judgment: materially stronger silhouettes and graphic construction than v009. The before/after sheet is illustrative, not a controlled A/B test because the words and layouts differ. The script still has less nuanced local shaping than the generated target. The film references have far broader text/design variety, and our silent placeholder study does not establish parity with their editorial rhythm. Olof has not reviewed v010.

## Experiments and selection

- Generated a monochrome lettering board and a separate material target. Originals and project copies are preserved; exact prompts and hashes are tracked.
- Extracted 39 vector paths across four identities, plus 87 paths in two script-highlight layers. No raster is loaded by the art renderer.
- Corrected crop overlap between panels; changed the mechanical trace to cleaned polygons to remove rounded corners and raster stair steps.
- Replaced arbitrary screen-space mechanical facets with part-based planes. Replaced normalized rainbow bevels with fixed-width contours. Separated red and blue showcard lines with ivory and removed the uniform hatch treatment.
- Two read-only Claude Opus 5.5 / high-effort critiques informed revisions. Accepted the diagnosis that the edit was grouped like a logo catalogue; interleaved identities and removed literal repeated demonstrations. Rejected a sustained two-frame strobe because it conflicts with controlled medium-high intensity in silence.
- A four-sample shutter trial produced visible trails and was rejected. Mechanical assembly now uses crisp two-frame steps. The script uses a directional light pass, while liquid contours and print registration retain their own local motion.
- Replaced clipped patterned rings with whole solid dots and a readable script secondary line. Strengthened wire strokes after the encoded MP4 revealed that thin colored lines were too faint.
- All still checkpoints, composition probes, draft edits, rejected blur versions and selected outputs remain preserved in ignored output directories. No server or cloud GPU was started; no audio work was performed.

## Verification and visual inspection

- Final renderer report: `output-final-02/report.json`. Deterministic seeking and exact modulo-frame wrap pass; this is not a claim of a seamless visual loop. No runtime errors or network requests. H.264 decoding succeeds, with one video stream and no audio stream.
- Final screening report: `output-screen-final-03/report.json`. The standalone code preview initializes without raster assets; previous/next-shot controls, playback and a 390px mobile viewport pass. The MP4 plays to completion in Chromium. The review page loads its selected movie and its MP4 link opens the correct local file.
- Assistant inspected the base designs, before/after comparison, complete shot sheet, a consecutive assembly strip, 49 decoded-frame samples spanning every shot and construction events, and review/preview screenshots. These support frame-level judgment; browser playback completion is a technical check, not a human judgment of continuous rhythm.
- Local-file browser security prevented canvas export of video frames; screening now extracts encoded frames with FFmpeg. A local MP4 link did not trigger a download event, so the UI correctly says Open MP4 file and verifies navigation. Both failed screening attempts remain preserved.
- Selected media SHA-256 and exact render-source hashes are in `delivery.json`. Source and all previous studies remain intact.

## Lessons for the next piece

1. Begin with demanding custom letter geometry. More filters on familiar fonts did not solve the source-design weakness.
2. A generated target can supply designed highlight geometry, but the reconstruction method must preserve that detail rather than replace it with a generic bevel.
3. Each surface needs an appropriate construction. Flat planes, fixed-width bands and separated ink contours proved cleaner than pushing every style through the same shading model.
4. Whole-word masks should follow vector components, not rectangular crops that cut ornamental capitals.
5. Interleave identity, scale and layout early. Materials alone cannot turn four centred logos into a varied edit.
6. Inspect the encoded movie: thin chromatic strokes lose presence after H.264 chroma subsampling.
7. Technical passes, independent model critique, assistant taste and Olof approval are separate evidence. The output-quality incident is recorded centrally as AF-20261010-121017; it does not create a new global instruction.

Screening and source verification completed 2026-10-10 10:11:44 UTC, within the two-hour maximum. The improvement goal is complete at the assistant-screening level; human taste review remains the next checkpoint.
