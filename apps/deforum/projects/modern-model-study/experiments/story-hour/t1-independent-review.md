# T1 new passage: independent visual review

Reviewed 2026-09-15. Scope: `exports/story-hour-v001/t1-through-the-opening` original anchors 0384–0564 only, and its `excerpt-0384` delivery. No earlier passage or other movement branch reviewed.

**Verdict:** the staircase-to-railway idea is readable through the small curved stair/bridge: its white treads become sleepers and acquire rails while preserving the curve toward the opening. The large right-hand staircase remains a staircase. This is a successful visual connection, but the station-to-carriage and glass-to-rock changes still contain conspicuous intermediate ghosts. The ending establishes the railway world more convincingly than the first reveal establishes a continuous transformation.

## Timing and evidence

The completed delivery check reports 16 paintings, 128 frames, 24 fps. RIFE manifest reports complete, RIFE 4.25 scale 1, with anchors at displayed frames 0, 8, …, 120. Independently checked all 128 output PNG hashes against the manifest and all sixteen original paintings against their displayed anchors: exact matches. Original frame `384 + 12k` maps to excerpt displayed frame `8k`; the delivered excerpt already incorporates the requested 1.5× timing. All ranges below are **zero-based excerpt displayed frames**, inclusive, with excerpt-local times.

Reviewed all sixteen paintings in an overview, RIFE every four frames across 0000–0124, and every frame in 0024–0040, 0072–0088, and 0104–0120. Opened full-resolution 1536×1024 RIFE frames 0036, 0076, 0108 and originals 0432, 0444, 0504 to distinguish source redesign from intermediate artifacts. This is sequential still-frame inspection, **not video playback**; perceptual flicker and overall playback smoothness remain untested.

## Exact windows

| Displayed frames / time | Finding |
| --- | --- |
| **0024–0032 / 1.000–1.333 s** (originals 0420→0432) | Strongest semantic bridge. The small central curved white stair gains two rails while its repeated treads remain legible as sleepers. This continuity gives the transformation an understandable direction. The large right staircase and orchid provide stable reference forms. Peripheral flowers and glass details nevertheless change during this interval. |
| **0032–0040 / 1.333–1.667 s**, most evident **0035–0037** (originals 0432→0444) | Weakest first reveal. A pitched-roof gold station-like structure becomes a rounded carriage with glowing windows; the thin S-shaped route inside the opening becomes a broad railway crossing the landscape. At full-resolution 0036, the old/new track alignments coexist, signals have softened or duplicate attachments, the foreground red petal has a transparent extra tip/edge, and the small upper flower is ghosted. The source paintings themselves make a substantial semantic/topological change; RIFE spreads it into a short superposition rather than establishing a single continuous object. The new carriage also floats above its track in original 0444, so that disconnection is not caused solely by interpolation. |
| **0072–0080 / 3.000–3.333 s**, most evident **0075–0077** (originals 0492→0504) | Second major replacement. The circular glass rim becomes an irregular rocky opening, a left suspended platform appears, and the railway acquires branching supports. Frame 0076 shows the old turquoise rim over the new rock and semi-transparent emerging platform/support structure. Foreground petals have doubled translucent edges. The train remains identifiable, but its undercarriage/track connection briefly looks tangled. |
| **0080–0088 / 3.333–3.667 s** (originals 0504→0516) | More coherent continuation after the large replacement. The same train, curved rails, orchid and opening can be followed through every inspected frame. The vista expands and suspended structures develop without another comparably large wholesale switch. Thin bridge/cable detail still softens; this is relative improvement, not artifact-free morphing. |
| **0104–0120 / 4.333–5.000 s** (originals 0540→0564) | Strongest late temporal continuity among dense windows. Train silhouette, track direction, balloons and landscape remain readable. Full-resolution 0108 keeps clear carriage geometry and coherent rails. The orchid changes petal anatomy and gold center decoration, but the railway remains the scene's stable identity. Fine supporting cables/details continue to shift. |
| **0120–0127 / 5.000–5.292 s** | Manifest records seven final-hold frames after the last anchor; hashes confirm the same painting through the end. This excerpt stops moving for its final eight displayed frames (one-third second including frame 0120). Treat that as a delivery hold, not a demonstrated generation defect. |

## Recommendation

Keep T1 as a readable surreal passage candidate, particularly the stair-tread/sleeper connection and the established railway ending. Prioritize 0032–0040 when comparing further attempts; 0072–0080 is the next most useful diagnostic window. Do not describe this attempt as a seamless conversion of the dominant staircase: that staircase persists, and the smaller curved route carries the transformation. No model or diffusion-default change is justified by this bounded review alone.

Contact sheets: `work/story-hour-session/independent/t1-anchors.jpg`, `t1-rife-overview.jpg`, and `t1-dense-0024-0040.jpg`, `t1-dense-0072-0088.jpg`, `t1-dense-0104-0120.jpg` (paths relative to `apps/deforum`; latter filenames share the same work directory). Only these ignored sheets and this review note were created.
