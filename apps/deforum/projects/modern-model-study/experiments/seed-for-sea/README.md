# A Seed for the Sea

2026-09-16 UTC. A new surreal piece built over one hour with the established Krea feedback loop. [Starting vision](BRIEF.md) · [Creative decisions](DECISIONS.md) · [Frozen configurations](configs/).

A red boat and a luminous pearl connect an empty desert, a dormant flower and a sea that grows between its petals. The story follows a theme and recurring shapes while adapting to what the model actually paints. It does not establish a physically tracked journey of one boat: the boat remained in the opening shell, then returned in the later world.

The assistant previews the spatial movement on the actual artwork, generates a short passage, inspects selected paintings and branches when the result suggests a better route. A measured approach to the distant flower uses the motion-preview CLI and matches the incoming speed. A later regional curl and pullback accompanies the flower-to-coastline transformation. The final passage turns the pearl into a small tree in the boat, completing the gift/life motif.

![A Seed for the Sea — 24-second piece](../../exports/seed-for-sea-v001/s4-the-floating-garden/faster/rife-moving-tail/preview.mp4)

[Local reviewer: full piece and shorter ending](http://localhost:3028/seed-for-sea) · [Frame inspection](quality-review.md)

## Preserved versions

| Case | Purpose |
| --- | --- |
| `o1-the-last-pool` | Alternative opening; two pearl-like objects. |
| `o2-the-last-pool` | Selected opening; clearer single pearl, boat, river and destination. |
| `s1-leaving-the-shell` | Five-second departure view. The boat stays in the shell, so the route follows the water. |
| `s2-the-waiting-flower` | Ten-second approach. Later shading becomes flatter; the next passage rewinds to source frame 300. |
| `s3-a-sea-unfolds` | Sixteen-second version ending on the new sea. |
| `s4-the-floating-garden` | 24-second continuation with a tree growing from the boat's pearl. |

All source paintings, unused later takes and spatial-only previews are retained. The original motion-plan draft is [branch-4f67f4b46883](../../branches/branch-4f67f4b46883/).

## What worked and what did not

The useful adaptation was to follow the painted water when the boat would not leave the shell, then let the pearl and red vessel return in the new world. The flower-to-coastline conversion and the tree growing from the pearl provide two distinct changes with a shared theme. The second motion preview keeps the final boat toward the left third instead of allowing a nearly static ending.

Literal boat transport failed. One early pullback exposed a reflected duplicate at the top and was rejected before generation. A later flower take lost shading; branching from source 300 preserved the useful part. Small shore details still redraw and the final scenery is softer than the opening. These are observations from one art piece, not controlled evidence that one setting universally improves animation.

## Method

Same-model opening and recurrent repainting with Krea Turbo, CFG 1, three Euler intervals, independently recorded seeds, time-based Lanczos warps and staged prompts/noise. Source cadence 12 at 24 fps means two paintings per source second. Delivery runs 1.5× faster at 24 fps, retaining every painting: three paintings per displayed second. RIFE 4.25 scale 1 fills the intervals outside the feedback loop; the last seven frames continue actual spatial warps.

`run.py` is a thin project adapter over the established generation/verification/retiming tools. `review.py` makes bounded painting sheets and exact spatial-only previews from saved artwork. No shared renderer or model architecture was changed.

From `apps/deforum/`:

```bash
uv run --locked python projects/modern-model-study/experiments/seed-for-sea/run.py --help
uv run --locked python projects/modern-model-study/experiments/seed-for-sea/review.py --help
```

## Execution and preservation

[Execution receipt](execution-summary.json). All 77 new image jobs were verified against actual graphs, parent/input/output hashes and exact spatial-warp pixels. The 1,373-entry remote archive was downloaded and hash-verified before deleting the owned RTX PRO 6000 Pod. The existing 50 GB model volume remains. A separate task started a Night Orchard Pod afterward; it was left untouched.

The full delivery retains all 72 paintings in 576 frames; the shorter cut retains 48 paintings in 384 frames. Both are 24 fps with seven moving tail frames, and full decoding/hash checks pass. The reviewer remains running through Devrun. Three server tests, scoped lint and the served-media checks pass.

Estimated session compute/disk cost is about **$1.85**; the posted account debit at cleanup was **$1.6974**, which can lag billing. A $2.10 reserve brings the ongoing conservative series reserve to **$8.75/$10**. All unique originals and unused attempts remain preserved.
