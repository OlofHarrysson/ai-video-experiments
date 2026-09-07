# Review harness practice

2026-09-07. Improve the assistant's first-pass review and the clarity of human feedback before generating another batch. No new diffusion or interpolation renders, paid API requests or cloud resources were used. Existing movies and prior reviews remain unchanged.

## Human evidence and selected baseline

Olof found C01/C03 boring, the other continuity results pretty good, and **tentatively prefers P3 + RIFE**. He found the similar variants difficult to distinguish and their labels insufficiently explained. P3 + RIFE is now the baseline; the assistant's prior C02 preference does not supersede this feedback. See the [living collaboration agreement](../../../../../docs/review-and-feedback.md).

## What changed in the tool

The shared [video_review.py](../../../video_review.py) now offers every-frame windows, timestamp-matched A/B comparisons, paginated sheets, an explicit image budget, separated pixel-change candidates and verified labels for original/interpolated/final-hold frames. The existing `--overview`, timestamp/event extraction, exact PTS and immutable versioning remain available. Full-size extracted frames remain separate from the sheets.

Default attention budget is 12 images per page and 64 displayed images per call. Comparisons count both sides. It is a workflow limit that can be raised explicitly, not a claim about model capacity. The harness never silently skips requested window frames to meet it.

## Applied reviews

Review artifacts live under `exports/review-harness-practice/`. Initial `v001` sheets exposed crowded captions; `v002` separates frame provenance from selection reasons and fits text to each tile's width. Earlier versions are preserved. The candidate scan only needed one version.

| Review | Selection | Displayed images / pages | Purpose |
| --- | --- | --- | --- |
| [P3 overview](../exports/review-harness-practice/p03-overview/v002/contact-sheet.jpg) | 12 points across the whole six seconds | 12 / 1 | Understand progression before choosing close-up intervals. |
| [P3 finishing comparison](../exports/review-harness-practice/p03-intermediates/v002/review.json) | Every frame at 5.000–5.250 and 5.500–5.625 s, beside original P3 at matching times | 22 / 3 | Distinguish learned in-betweens from repeated delivery frames and inspect contour defects. |
| [P3 versus C02](../exports/review-harness-practice/preferred-vs-candidate/v002/review.json) | Six overview moments plus every frame at 2.875–3.125 s; both use RIFE | 26 / 3 | Compare the two generation outcomes without changing finishing settings. |
| [Change candidates](../exports/review-harness-practice/change-candidates/v001/contact-sheet.jpg) | Threshold 0.08, three candidates at least one second apart, ±0.083333 s context | 9 / 1 | Locate additional intervals to inspect, not score the art. |

The agent inspected the selected image groups, paired pages and a full-size decoded frame at 5.583333 s. A caption crop was also inspected to check readability. The harness verifies source-video hashes before/after extraction, records exact PTS and verifies interpolation-manifest alignment. Normal-speed playback was not reviewed by the assistant during this harness task; Olof's previously stated playback preference is the human evidence.

## First-pass observations

- **Overall P3 progression:** mechanical portal, head-like form, small domed structure, then a graphic opening that becomes more organic. Around the midpoint, detail simplifies into broad teal/orange/cream shapes. Toward the ending, curling outlines and branching shapes return. These are descriptions of visible samples, not explanations of why Olof likes it.
- **Finishing at 5.000–5.250 s:** at the same timestamps, original P3 repeats its existing image while RIFE provides different intermediate images. RIFE's first intermediate remains close to the left endpoint and the second often resembles the right. More intermediate pictures do not ensure evenly spaced semantic changes.
- **Defect at 5.583333 s (delivery frame 134):** a cream branch appears doubled, with a broad faint horizontal band across the lower part of the image. The corresponding original P3 frame is still holding its preceding image. The full-size extraction makes the defect clearer than an overview alone. This is a specific target for improvement; it does not invalidate the user's preference for the finished clip.
- **P3 versus C02:** at 1.167 s, P3 shows a head-like form while C02 still resembles a mechanical portal. Around 3 s both have become flatter but their geometry differs. P3 keeps a prominent oval opening; C02 develops an offset circle and branching lines. At the ending P3 remains an opening surrounded by flowing contours, while C02 has a tree/root form beneath an orange disk. This gives concrete differences to discuss instead of asking for a vague ranking.
- **Automatic candidates:** the three selected decoded frames are 1, 89 and 126 (0.041667, 3.708333 and 5.250000 s). They cover the opening, renewed organic detail and a later shape transition. They do not include the 5.583333 s defect selected from prior visual evidence. Pixel-change scoring therefore supplements manual interval choice; it cannot replace it.

## Human presentation and next experiment

Keep **P3 + RIFE** as the chosen baseline and explain its ingredients in [the recipe summary](../../../../../docs/review-and-feedback.md#current-preferred-recipe-p3-with-rife). No new taste decision is needed to accept this harness change. The next round should show that familiar baseline and one challenger, with one question about gradual transformation versus lost detail. Keep C01/C03 in the archive rather than asking Olof to rank them again.

A plausible next challenger changes the random noise gradually during generation, retaining the P3 model/style, prompt/camera intent and RIFE finishing. This remains a research hypothesis and was not implemented here. Avoid combining a new model, camera path and finishing method in the same comparison.

## Validation

Thirty local tests pass, including seven new review tests covering every-frame variable-rate windows, budget rejection before file creation, page coverage, comparison alignment/held frames, provenance validation, separated candidate selection and CLI integration. Existing source preservation, exact extraction, editing, transport and interpolation tests also pass. The harness was then exercised on the actual archived P3/C02 videos as described above. Small sheets, source-label captions and full-size diagnostic frames were inspected visually. No movie was regenerated or overwritten.
