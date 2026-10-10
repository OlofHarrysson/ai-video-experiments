# BILLIONS → NEXT → KEEP UP

[Watch the six-second silent cut](output-v004/three-identities.mp4) · [Interactive player](index.html)

Olof approves this rhythm study after praising v015's increased motion. It combines three already approved graphic identities into one short sequence, retaining the ornate artwork's finish and giving each design a different movement vocabulary. This is preparation for the AI progress/news-overload intro; the full film story remains open.

## The edit

| Time | Treatment |
| --- | --- |
| 0–1.67 s | BILLIONS: compressed version of the approved eight-letter arrival, unfolding ornament and assembled hold. The first frame is already in motion. |
| 1.67–2.33 s | Ornament clears, letters scatter vertically, and NEXT's blue geometry enters. Lime and ivory ink arrive from opposite sides, followed by the red lower word. |
| 2.33–3.54 s | NEXT: two abrupt framing steps and a separate red-ink move punctuate the planted word. |
| 3.5–4.17 s | KEEP interrupts NEXT's outward motion with a broad curved reveal. Original red enamel and gold edges stay intact. |
| 4.17–5.17 s | UP arrives from the opposite direction through a second curved reveal. |
| 5.17–6 s | Full KEEP UP composition holds. |

BILLIONS uses the existing eighteen-part cutout rig. NEXT's 241 ordered vector paths render at double size, including their black counters, before separation into four ink layers. KEEP UP uses two broad complementary control regions over its original surface. These are visibility controls, not independently recovered glyphs, a font, or a new 3D reconstruction. No lighting shimmer or added texture is used.

## Screening and fidelity

The assistant inspected the decoded overview, every frame of both transition windows, the KEEP UP reveal and full-size native holds. The first transition visibly exchanges vertical letter movement for horizontal geometric movement. The second establishes KEEP before the lower word sweeps in. Cropping NEXT briefly at its scale punches is intentional.

The actual BILLIONS and KEEP UP timeline holds match their 1672×941 source RGB pixels exactly: mean and maximum difference are both zero. Delivery is 1600×900 H.264 and remains lossy; native proofs are the surface-quality reference. Native identity does not prove the quality of moving overlaps.

The export contains 144 frames at 24 fps, exactly six seconds, with no audio. Deterministic seeking, no external requests or page errors, full decode, browser playback, timeline navigation and the narrow player layout are checked. The HTML is self-contained and needs no server. Technical checks and sampled image inspection do not establish normal-speed taste; Olof's rhythm judgment is pending.

The main remaining artistic tradeoff is KEEP UP: its broad reveals preserve the material convincingly, but provide less independent shape movement than BILLIONS. The quiet final beat is intentional. Human feedback should establish whether the cut feels connected and whether that landing lasts the right amount of time.

## Iterations

- **output-v001:** all three designs connected; narrow curved stroke masks finish KEEP UP too early, leaving an extended static ending. Some NEXT lines linger into the next identity.
- **output-v002:** outgoing NEXT travels farther and the lower reveal happens later. This exposes awkward chopped-off regions in KEEP UP for too long and leaves a sparse interval in the transition.
- **output-v003:** two broad complementary curved reveals replace the narrow stroke masks. KEEP starts earlier, overlaps the departing NEXT, and gives the lower word its own beat. The final assembled hold lasts about 0.83 seconds.
- **output-v004 (selected):** NEXT enters behind the departing BILLIONS letters, avoiding a blue tint over engraving. Only the KEEP UP visibility mask receives a light feather; the original artwork is applied afterward with no blur.

A completed read-only Claude Opus 5.5 consultation examined the v002 still evidence. Its critique independently identified the mask cutoffs and sparse join already being corrected in v003, and additionally caught blue NEXT ink tinting BILLIONS during overlap. The final pass follows its layer-order suggestion and light mask feathering. Claude did not assess normal-speed playback or review the final v004.

Prior outputs and their frozen implementations remain local. [The approved scope](brief.md) and [validation/provenance](results.json) record this sprint. No new images or paid generation were used.

## Reproduce

From the repository root:

```sh
node apps/canvas-animation/projects/title-sequence-study/studies/rhythm-cut-v016/build.mjs
node apps/canvas-animation/projects/title-sequence-study/studies/rhythm-cut-v016/render.mjs apps/canvas-animation/projects/title-sequence-study/studies/rhythm-cut-v016/output-new
node apps/canvas-animation/projects/title-sequence-study/studies/rhythm-cut-v016/screen.mjs apps/canvas-animation/projects/title-sequence-study/studies/rhythm-cut-v016/output-new
uv run --script apps/canvas-animation/projects/title-sequence-study/studies/rhythm-cut-v016/verify-quality.py apps/canvas-animation/projects/title-sequence-study/studies/rhythm-cut-v016/output-new
```

Render output must be a new directory. It preserves all frames, the decoded movie, timestamped inspection sheets, native holds, source hashes and a frozen self-contained HTML implementation. Source assets remain owned by v014/v013; the BILLIONS motion and rig remain owned by v015. Rebuilding consumes those versioned sources, while each frozen output is independent of subsequent edits.
