# Surreal worlds — one-hour session

Olof calls the preceding stronger spatial motion an improvement and identifies **surrealism** as the art direction: odd and impossible scenes are welcome. This session follows that direction while retaining recurrent Krea feedback. Human preference among these new films is pending.

**Assistant shortlist:** the sixteen-second fruit-to-garden journey and the eight-second piano-to-swans shot. Both combine visible turns and travel with changing subject matter. [Open the two-film reviewer](http://localhost:3028/surreal-hour).

## Films and comparisons

Every film is preserved, including branches that did not improve the result. These are creative auditions, not evidence that one prompt or motion recipe universally wins.

| Attempt | What changed and what we learned | Video |
| --- | --- | --- |
| S1 — Pomegranate world | Fruit seeds become rounded buildings, then palace-fish. Clear world changes, but the largest fish conversion is abrupt and RIFE ghosts around 6.5 displayed seconds. | [8 seconds](../../exports/surreal-hour-v001/s1-pomegranate-world/faster/rife/preview.mp4) |
| **S2 — Piano into swans** | Strong rotation carries spiral keys into feathers, swans and red sails. The broad black-and-white curve remains readable. Some soft feather transitions; the near wing grows large. **Shortlist.** | [8 seconds](../../exports/surreal-hour-v001/s2-ivory-whirlpool/faster/rife/preview.mp4) |
| S3 — Matchbox night | Enter a miniature station. The change of scale reads clearly, but individual matchheads do not convincingly become moons; new moons appear elsewhere. Quieter and less surprising than the other openings. | [8 seconds](../../exports/surreal-hour-v001/s3-matchbox-night/faster/rife/preview.mp4) |
| **S4 — Through the blue ring** | Continues all of S1 through a blue opening into orchids, floating stairs and a river. Red fins become petals, making a visual connection between worlds. Late shading becomes flatter; fish-to-flower interpolation still ghosts. **Shortlist.** | [16 seconds](../../exports/surreal-hour-v001/s4-through-the-blue-ring/faster/rife/preview.mp4) |
| S5 — Open the sky | Same piano opening, text, noise, seeds and twists; adds less late enlargement and a small upward shift. More small swans remain visible, but the ending is busier. No clear overall upgrade over S2. | [8 seconds](../../exports/surreal-hour-v001/s5-open-the-sky/faster/rife/preview.mp4) |
| S6 — Earlier palace-fish descriptions | Same fruit opening, motion, noise and seeds; four extra descriptions introduce scales, eyes and fins earlier. Fish arrive earlier, but a concentrated change remains around 4.7–5 displayed seconds. Useful timing control, not a solution to gradual morphing. | [8 seconds](../../exports/surreal-hour-v001/s6-staged-palace-fish/faster/rife/preview.mp4) |
| S7 — Richer garden repaint | Same S4 through 20 original seconds; seven final repaints keep starting noise at 0.64 instead of declining to 0.30. Changes the late layout but does not clearly restore the earlier shading. Retain S4 for the shortlist. | [16 seconds](../../exports/surreal-hour-v001/s7-rich-garden-ending/faster/rife/preview.mp4) |

Review pages: [three initial worlds](http://localhost:3028/surreal-first), [piano endings](http://localhost:3028/surreal-piano), [fish descriptions](http://localhost:3028/surreal-fish), [garden endings](http://localhost:3028/surreal-garden). The prior session remains at [motion-hour](http://localhost:3028/motion-hour).

## What to carry forward

A visual connection between subjects helps these examples: seeds into rounded buildings, keys into feathers, and red silk or fins into petals. This is an artistic observation across a small set, not an isolated causal result. Surrealism gives us room to retain strange intermediate forms rather than forcing every painting toward a realistic destination.

Spatial motion needs a visible destination and a way to settle. Large nearby forms make motion legible, but continued enlargement can crowd the frame. Reframing changes what the next repaint has available to develop; reducing zoom does not guarantee a cleaner composition.

Intermediate descriptions can move a transformation earlier without spreading it smoothly. Increasing late noise does not reliably recover shading. Keep the accepted diffusion defaults; the next creative work should build on compositions and transitions that already look interesting. RIFE ghosting, incidental detail changes, reflected borders and late flattening remain technical limitations.

## Method and timing

- Krea Turbo makes each opening and every subsequent painting. Full eight-interval opening; three Euler intervals per repaint, CFG1, fresh independent noise. Each repaint starts from the **encoded, warped previous painting**. No independent text-only frames replace the recurrence.
- Original timeline: **24 fps, one painting every 0.5 seconds**. Bounded time-based Lanczos transforms with reflected borders combine turns, translations, zoom and occasional elastic waves. Configs record the exact prompt stages and noise curves.
- Delivery: **24 fps, 1.5× original speed, three paintings per displayed second**. Every painting is preserved; RIFE 4.25 at scale 1 supplies seven intermediate frames per pair. RIFE never feeds back into generation. The last seven frames hold the final painting; spatial motion has settled by then. This session did not compare delivery speeds.
- S1–S3 have 24 paintings each. S4 adds 24 to S1. S5 and S6 each preserve their parent's first thirteen paintings and generate eleven more. S7 preserves S4's first 41 paintings and adds seven. S4/S7 use the original S1 opening, not the separately generated S6 ending; they cannot be exchanged without regenerating the continuation.
- Screened all three openings and spatial-only previews before continuing. Reviewed all original S1–S3 paintings, sampled the longer continuation, reviewed every new S5–S7 painting, and inspected dense RIFE windows around important redraws. [Independent S1 review](s1-independent-review.md) and [S3 review](s3-independent-review.md) provide additional evidence. [Matchbox proposal](creative-proposal.md) is background; executed configs are authoritative.

## Verification and resources

**125 unique image jobs** passed generation checks: executed workflows, output provenance, seeds/noise, parent lineage, retained prefixes and exact Lanczos initialization pixels. The complete cloud archive contains **2,143 verified entries**, including all 247 generated/uploaded media files. SHA-256: `eafba9c86bb30895e7317a0c8dee3e73fdc25a7b22b30c7d2663e317c323bf26`.

All seven 24 fps deliveries retain their painting anchors and have per-frame hashes, finishing manifests and full video-decode checks. Five are 192 frames; two are 384 frames. Pair checks reuse pixel-identical pairs already visually reviewed where a branch preserves its opening.

Temporary Pod `3vav6jlrqdq1i5`, its 247 remote media files and owned scratch are removed. A fresh Pod listing is empty; the authorized 50 GB model volume `vd3jnbwko1` remains. Posted account debit is **$0.581235**; conservative session allowance **$0.65**, bringing the three-session total to **$2.70 of the original $10 maximum**. Account-wide retained-resource spend after cleanup is $0.005/hour; this is not a zero-storage-cost setup.

The hour began 2026-09-15 at 06:38 UTC. All new image jobs finished by about 07:18 UTC; remaining time was used for local finishing, review, verification and documentation. Private billing data and operational receipts remain in ignored `work/surreal-hour-session/`; generated media remains in ignored exports. Configs, reusable experiment adapters and findings are tracked.

## Commands

Run from `apps/deforum` using the locked uv environment. Generation requires a deployment file; checks and finishing are local.

```sh
uv run --locked python projects/modern-model-study/experiments/surreal-hour/run.py check --batch s567 --cases s5-open-the-sky s6-staged-palace-fish s7-rich-garden-ending
uv run --locked python projects/modern-model-study/experiments/surreal-hour/retime.py s4-through-the-blue-ring check
```

`run.py` reuses the audited two-hour runner. `preview.py` creates motion-only previews; `review.py` and `retime.py` support review and finishing. Existing output is immutable: branch into a new case for a changed experiment.
