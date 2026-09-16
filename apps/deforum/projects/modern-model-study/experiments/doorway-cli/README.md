# A continuous passage through the doorway

2026-09-16. Dogfood the assistant's motion-preview CLI on the doorway shot. Olof supplies artistic vision and taste feedback; the assistant operates the production tools, inspects results and revises the route.

![Continuous passage — selected 20-second take](../../branches/doorway-textured-arrival/faster/rife-moving-tail/preview.mp4)

[Compare new and previous films](http://localhost:3028/) · [Generation and delivery receipt](execution-summary.json) · [Original doorway revisions](../doorway-revision/README.md)

The new take preserves the opening through **11.67 seconds**, approaches the doorway in one continuous move, reveals an open meadow, and releases the forward zoom into a gentle sideways drift. The red train connects the two worlds. This is an artistic revision with coupled framing, prompt and noise choices, not an isolated proof of one motion setting. Human playback feedback is pending.

## What the tooling changed in practice

1. Inspected saved paintings through the CLI. A first motion-only preview from source frame 468 led directly into the giant harp. Rejected that route before inference.
2. Rewound to source frame 420, before the harp appeared. Previewed the actual clear opening, matching the incoming pan/zoom velocity. A narrower doorway required a larger push than the old CLI limit allowed; the CLI now admits enlargement up to 32× and warns above 8×. The selected move reaches 26× over six displayed seconds, then ends zoom velocity while retaining lateral drift.
3. Saved the original CLI draft unchanged in [branch-379a1d60345e](../../branches/branch-379a1d60345e/). Prepared a separate production branch with staged descriptions and noise. Motion preview and production use the same curve; the production plan adds the arrival interval.
4. Generated only nine new paintings through source frame 528 and inspected [the checkpoint](../../exports/doorway-cli-review-v001/checkpoint.jpg). The doorway stayed legible and the route remained open, so the generation continued.
5. The first ending became flatter as noise fell to 0.36. Preserved it, branched at frame 588, and tried 0.58–0.56 instead. [The ending comparison](../../exports/doorway-cli-review-v001/endings.jpg) favors the steadier-strength take for texture. Movement and descriptions are identical between these two endings.

The saved [motion plan](motion-plan.json), [preview summary](preview-summary.json), [production plan](production-plan.json) and [frozen configs](configs/) own the exact decisions. The browser remains a playback reviewer. No authoring controls were added.

## Story timing

| Display time | Purpose and observed result |
| --- | --- |
| 0–11.67s | Preserved whale railway and doorway approach; all 281 archived PNG frames through the branch match the prior delivery. |
| 11.67–14.67s | Continuous approach; daylight, trees and a small train appear beyond the readable doorway. |
| 14.67–16.67s | Door margins move out of view; the meadow takes over without the previous giant foreground harp. |
| 16.67–17.67s | Forward enlargement eases to zero. |
| 17.67–20s | Gentle sideways drift and continued small repaint changes; no second forward push. |

## Inspection and limits

The assistant reviewed six checkpoint paintings, six arrival paintings, matched endings at frames 612/660/708, and [the finished-film sheets](../../exports/doorway-cli-review-v001/film/v001/contact-sheet.jpg). Dense displayed-frame windows cover the preserved/new join and the zoom release. This supports continuity of the inspected shapes; it is not an exhaustive playback judgment. Olof's review remains decisive for perceived rhythm.

The destination is open and readable, and the new curve avoids the old branch-speed discontinuities. Some harp-string lines remain near the edges; the scene still simplifies relative to the opening and the train is a recurring motif rather than an exactly tracked physical locomotive. Low-strength finishing was not a clean solution to preserving texture. The steadier ending is preferred by the assistant, not yet selected by Olof.

Krea Turbo, CFG 1, three Euler intervals and recurrent warped-image initialization remain unchanged. Source time is 24 fps with cadence 12. Delivery is 1.5× faster at 24 fps, retaining all 60 paintings; RIFE 4.25 scale 1 fills the intervals and never feeds the recurrent loop. The final seven frames use actual spatial warps.

## Execution and preservation

34 new image jobs: 24 for the first passage and ten for the alternate ending. All parent/input/output hashes, executed graphs and spatial warps were verified. The 678-entry remote archive was downloaded and verified before deleting the temporary Pod. The original cached-model volume remains in EU-RO-1. Generation used a temporary RTX PRO 6000 in EUR-IS-2 because allocation failed in the cached region and for 4090 requests elsewhere; Olof authorized another region. Posted account debit was about $0.64; the conservative session reserve is $0.80, bringing the recorded series reserve to $6.65/$10.

Capacity and asynchronous sequencing friction were recorded centrally as `AF-20260916-180515` and `AF-20260916-180515-2`. Transfer and generation prerequisites must finish before extraction or review. The local reviewer remains managed by Devrun.

Validation passed: 84 Python tests, two timeline tests, scoped lint and document-link checks. The browser loaded both full-resolution films side by side, played through the ending and stepped back to the final painting with Shift+Left. Devrun confirmed the reviewer ready on port 3028 with successful media range requests.

## Reuse

From `apps/deforum/`, `uv run --locked python projects/modern-model-study/experiments/doorway-cli/run.py --help` exposes the existing renderer, verification and finishing operations for a frozen branch. `prepare.py` reproduces the first production configuration from the preserved CLI draft. The alternate ending's frozen configuration records its sole intervention: the later noise schedule.

Next production use: keep the preview → short generation → inspect → branch loop. Preview cannot predict repainting, and the current CLI requires a finished parent delivery. Supporting a saved painting directly may be useful later; this experiment did not need another authoring interface.
