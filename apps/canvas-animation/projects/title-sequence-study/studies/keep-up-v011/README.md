# KEEP UP — AI intro storyboard and lettering workflow

[Open the six-frame storyboard](index.html) · [Source/vector inspector](output-inspection-v003/inspect.html) · [Story proposal and sources](BRIEF.md) · [Problem map](TOOLING.md)

Olof selects the AI progress/investment/news-overload theme and authorizes making the successful generated-lettering workflow repeatable. This checkpoint contains working tools and six code-rendered still frames for a proposed eighteen-second silent intro. The title, personal turn and exact sequence remain proposals; no production animation has been made.

The proposed story moves from the promise of AI through repeated breakthroughs and a real dated funding announcement to a personal question: **AM I ALREADY BEHIND?** The working title **KEEP UP** can read as both an invitation and pressure. This avoids requiring recognition of niche model names or declaring that AI is a bubble.

## Actual work

- Generated three separate monochrome lettering plates using built-in image generation: KEEP UP, $40B, BREAK THROUGH. Exact prompts are in [prompts.json](prompts.json); independent source copies are preserved in ignored `reference/`; original locations are in [lettering.json](lettering.json). The trace records SHA-256 hashes, dimensions and settings.
- Built shared [extraction and inspection tools](../../../../tools/lettering/README.md). All three plates pass through the same code with project-owned settings and grouping.
- Declared eight semantic groups across 33 paths: two title words, four money glyphs, and two announcement words. The diamond ornament belongs to the zero; both separated pieces of the 4 belong to the 4. KEEP and UP use explicit path IDs because their bounding boxes overlap. BREAK/THROUGH use declared regions.
- Selected `vectors-v003`: polygon tracing with simplification of 0.55 source pixels for the curved designs and 1.05 for mechanical lettering. The first spline recipe and a second spline-setting experiment remain preserved as `vectors-v001` and `vectors-v002`. Spline fitting softened tips and changed thin gaps in this test; it remains available for other artwork.
- Built vector-only finished frames with local code colors/contours, existing licensed font outlines for supporting copy, and an interactive storyboard selector. No renderer source-image, web-font, network, audio or video dependency.

## Evidence

Selected inspection: `output-inspection-v003/report.json`. KEEP UP source/vector mask overlap is 98.41%, $40B is 98.05%, BREAK THROUGH is 99.17%. Missing, duplicate and unknown group checks pass; all groups are populated and every path is assigned exactly once. The KEEP UP source has only 3.8% minimum margin and is flagged; inspected tips remain intact. Rendering places it with deliberate additional breathing room.

Selected board: `output-board-v002/storyboard.png`; six individual 1600×900 frames and the desktop/mobile preview screenshots are beside it. `output-board-v002/report.json` records deterministic frame redraws, working previous/next controls, no network/runtime errors, no source raster in the renderer and no overflow at 390px. A failed initial build used a deprecated OpenType loader; it was replaced by parsing the existing local font bytes before successful screening. No server was started.

Assistant inspected the full board, title and funding frames at full size, source/vector comparisons and group views. The three bespoke lettering cards are the visual anchors; simpler copy provides context and a human turn. The hard blue shadow and graphic contours are intentionally flat. No claim is made of physically accurate material rendering, reference-film parity or approved rhythm. Human feedback on v011 is pending.

## Continue

Review the six frames and [timed sequence](BRIEF.md). After story/board approval, build local construction events for the grouped artwork and render the silent eighteen-second edit. Keep date/company/announcement context legible for the money card; use the human-question beat as a brief compositional change, not a slow opening or a strobe finale. Preserve this board when iterating.

Rebuild the current static board:

```sh
node apps/canvas-animation/projects/title-sequence-study/studies/keep-up-v011/build.mjs
node apps/canvas-animation/projects/title-sequence-study/studies/keep-up-v011/screen.mjs output-board-new
```

The committed vectors suffice for building the board. Retracing and source comparison also require the ignored original PNG copies. See the shared tooling guide for those commands. Outputs refuse overwrites.
