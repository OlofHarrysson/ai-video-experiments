# Opening, transformation and arrival

Completed 2026-09-17. [Selected film](../cuts/v001.md): sixteen silent seconds. Olof delegated direction; taste feedback is pending.

## What was made

The opening places one amber pear against a blue glass greenhouse, connected to the foreground by a silver branch. An approach enlarges the pear while its veins become a silver tree. The tree develops fruit and floating islands; the surroundings become a night orchard. Forward movement relaxes into lateral travel. A short final glide lets the new landscape register.

This is a world transformation. Tiny orchard trees appear outside the pear before the scene changes fully, so the pictures do not establish literal entry into an enclosed fruit. That distinction comes from inspecting the paintings and the independent review, rather than rewriting the intent as an achieved action.

## Preserved takes

| Case | New paintings | Purpose and judgment |
| --- | ---: | --- |
| `o1-silver-branch` | 1 | Selected opening: broad branch, readable amber focal form and silver leaves. |
| `o2-silver-branch` | 1 | Wider alternate; the independent reviewer preferred its spatial context. |
| `p1-into-the-amber` | 16 | Eight source seconds of approach. Veins become a surface tree; an interior is not yet established. |
| `p2-a-world-within` | 12 | Amber framing, fruit-bearing trees and floating islands develop. Source prefix through 192 retained. |
| `p3-the-suspended-orchard` | 16 | Release the push, travel sideways and reveal the island landscape. Prefix through 336 retained. |
| `p4-lights-in-the-dark` | 15 | Rejected 0.8× widening: reflected tree/root forms become visible along the edge. |
| `p5-the-final-glide` | 15 | Same prefix, prompts, noise and seeds as p4; smaller glide and 1.06× scale. Select through 564, before later flattening. |

Both ending attempts preserve the same 45-painting prefix through 528. The full final branch contains 60 paintings; the selected film uses 48. All 76 unique generation jobs and 1216 remote files were verified locally before cloud cleanup. Generated media remains ignored by Git and is not an external backup.

## What worked and what still falls short

The amber/silver motif survives the changes of scale and setting. Floating roots and differently sized islands provide a destination distinct from the greenhouse. A second reviewer independently found the world change readable and the destination worth reaching, while identifying ambiguous containment as the chief narrative weakness.

The opening retains more dimensional material detail than the late orchard. Trees and leaves become more regular, and some foreground foliage remains large. Continuing for the planned 20 seconds adds little story development while flattening the image further. The 16-second selection uses editing to protect the stronger part of the result.

A motion-only preview correctly exposed possible reflection patterns, but cannot determine whether repainting will remove them. In p4 it did not remove the conspicuous root/tree extension. A shorter glide improved that issue; it did not solve recurrent texture loss. These are scoped visual judgments, not a universal noise or motion prescription.

## Verification and review

The shared Krea recipe uses CFG 1 and three descending Euler intervals for partial repainting; each generated painting uses a recorded fresh seed and the warped previous painting as initialization. Every executed graph, source/output hash, upload, PNG graph metadata and prefix was checked. Motion is a flat-image transformation, not a depth-rendered camera.

Delivery maps source frames 0,12,24…564 to frames 0,8,16…376 at 24 fps. RIFE 4.25 scale 1 produces the intervals outside recurrence. Seven final warps complete 384 frames, exactly 16 seconds. Anchor bytes, frame roles/timestamps/hashes, tail pixels, video dimensions and full decode pass.

Inspected evidence includes both full opening PNGs; actual checkpoint paintings; camera-only previews; every first-pair frame; transition sheets; the final 12-image overview; and dense delivered windows around 5.3,6.3,9.3,14.7 seconds and the final tail. Local 1× playback reached frame 383 and the full composition/controls were visible at 1280×720. This is sampled visual review plus playback verification, not a claim to have continuously judged every motion beat. Olof remains the taste reviewer.

See [execution summary](execution-summary.json) for hashes and cost. The owned RTX 4090 Pod was deleted, with zero Pods returned by the subsequent live listing; the existing 50 GB model volume remains. Compute cost is estimated from elapsed time at $0.74/hour because the billing endpoint had no posted entry at cleanup. Olof removed session caps before inference.

## Reproduction

Configurations and project runners are tracked in this directory. Original paintings, native graphs and ComfyUI histories live under `exports/v001/` in this project; delivery records are adjacent to the selected video. Private infrastructure/preservation receipts live in `../../../work/night-orchard-session/`. Preserve completed outputs and use a new case for creative changes.

A delegated finishing-code handoff overlapped the first pair run. The initial verification receipt was preserved, then revalidated after the adapter stopped changing. No paintings were lost. The working-process incident is recorded as AF-20260917-004801 in the central agent-friction log.
