# Assistant screening

Human feedback on the long cut is pending. Olof likes the preceding short. The observations below are assistant judgments from actual paintings, evenly sampled decoded video frames and selected dense windows; they are not an exhaustive real-time playback review.

## Selected passages

| Passage | What works | Limitations |
| --- | --- | --- |
| Descent under the floating garden | Reflected roots and ivory arches establish a new space. The pearl remains readable through the transition. | Tree/boat identity is symbolic; the city becomes decorative late in the passage. |
| Pearl, glass bell, jellyfish | Several readable intermediate forms connect the pearl to the bell and its tendrils. | The surrounding arch stays too long; minor architecture and the red accent redraw. |
| Architecture becomes current | Rigid stone becomes flowing ribbons and clears into open water. Jellyfish become warm lantern shades. | Filaments and highlights rearrange; the red boat motif briefly becomes a petal/ribbon. |
| Lanterns above the sea | Glass shades become paper lanterns, red boat baskets return, and the waterline clears into sunset air. | Paper folds redraw; tiny person-like marks sometimes appear in the boat without controlled character identity. |
| Rain returns | Lanterns pour water onto dunes; streams, boats and a turquoise river link the return to the shell. | Two scene changes remain brisk. The cloud becoming a shell is surreal rather than physically literal. |
| Final garden reveal | Roots, flowers and a golden tree connect the returned pearl to an abundant world; the pullback keeps the shell readable. | Shell geometry becomes ornamental. Tiny unplanned figures change in number and appearance. |

## Evidence

The ignored media root is `projects/modern-model-study/exports/seed-for-sea-long-v001/review/`. Painting selections and directing decisions are recorded in [DECISIONS.md](DECISIONS.md).

- `descent-film/v001`: nine overview samples; dense displayed windows 5.125–5.375s and 15.95–16.25s. All three contact sheets inspected.
- `opening-join/v001`: every displayed frame 23.45–24.05s in the first 40-second assembly. Both contact sheets inspected; the shared painting has no duplicate hold.
- `bell-film/v001`: eight overview samples and every displayed frame 7.08333–7.375s. Both sheets inspected.
- `current-film/v001`: eight overview samples and every displayed frame 4.0–4.3s. Both sheets inspected.
- `sky-film/v001`: eight overview samples and every displayed frame 5.1667–5.5s. Both sheets inspected.
- `rain-film/v001`: eight overview samples and dense windows 4.25–4.75s and 7.0–7.33333s. All three sheets inspected. RIFE provides in-between shapes at the two brisk semantic changes, but the lantern/boat and cloud/shell events are still faster than the earlier bell/jellyfish morph. No blank frame in these samples.

- `garden-film/v001`: eight overview samples and every displayed frame 15.9167–16.25s through the last painting and moving tail. Both sheets inspected. The final composition remains readable, with no held tail or blank frame in the sampled window.

Generation checks validate parent hashes, exact warped input pixels, submitted graphs and completed image jobs. Delivery checks validate painting retention, timestamps, frame hashes, shared boundaries and full decode success. These mechanical checks do not establish artistic quality or flawless temporal coherence.

## Complete edit

The final cut passes 2880-frame, 360-painting, 24 fps and 120-second verification, with seven moving tail frames and hash-verified shared boundary paintings. Full decode succeeds. Inspected all 24 overview samples in `full-film/v001` and all three sheets in `all-joins/v001`, covering dense windows around 39.6667, 55.6667, 71.6667, 87.6667 and 103.6667 seconds. The first join at 23.6667 seconds was already inspected in the 40-second working assembly, whose retained source frames are identical in the final edit. No duplicate hold or discontinuity at the inspected joins.

The strongest longer-form sequence, in the assistant’s judgment, is pearl → glass bell → jellyfish → lanterns. The rain passage is more abrupt; the final garden is calmer and more ornamental. Together the passages establish new environments and a changed return, rather than stretching or looping the original short.
