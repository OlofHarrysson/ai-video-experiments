# Review — Big Softie v3

Olof liked the previous film overall, but identified a green opening frame, an odd final frame, and a jump into the cuddle without intermediate action. The revision removes the colored fade overlay completely and replaces the separate closing artwork with seven paired cels on the existing park plate.

The return pass now decelerates before the dogs stand, crouch, sit, lie down, lean together and close their eyes. The adult stays on the left and puppy on the right through the finish. The cels share a fixed scale and manually registered paw baselines; the camera only begins its closing push after the cuddle. The original score now resolves over the longer ending. The full film lasts 19.5 seconds.

## Verified output

- `renders/big-softie-v3.mp4`: 1920×1080, 24 fps, 468 H.264 frames, 48 kHz stereo AAC, 19.500 seconds, 19,674,892 bytes.
- `renders/big-softie.mp4`: delivery copy of v3. Earlier v1/v2/draft outputs remain preserved.
- `renders/poster-v3.jpg`: exact final video frame (467), without a colored fade.
- Strict HyperFrames check passed. The eleven-time targeted check had no lint, runtime, layout or contrast findings. Full video decode completed without errors.
- Audio mean −27.0 dBFS, peak −10.4 dBFS; no clipping. The previous music master is preserved as `assets/score-v2-master.wav`.

## Visual review

`review/continuity-v3/v001` covers the actual decoded opening, stopping motion, every new pose and closing image. `review/adjacent-v3/v001` inspects every displayed frame across the run-to-standing transition and partial-to-full cuddle transition. Those reviews confirm stable park geometry, consistent left/right order, visible intermediate actions, clear character edges and no opaque checkerboards in the composite. The final pose is held in full color through the last frame.

This remains limited cel animation: exposure changes are visible, and the generated pose drawings have small contour differences. The revision addresses the missing action rather than claiming feature-animation smoothness. Review evidence is decoded-frame and timing inspection; Olof's playback assessment remains the final taste check. The prior version's positive overall playback feedback is recorded above, not treated as approval of this revision.

## Reproduction and provenance

Seven originals and their alpha-prepared copies remain under `assets/source/settle-*`; each image generation is recorded in [settling-prompts.md](settling-prompts.md). `prepare-settling.mjs` validates transparency and retains full canvas coordinates. `build-film.mjs` records exact exposure times, scale, ground alignment and camera position. No cloud compute or persistent preview server was started.

---

# Previous review — v2

## Scope and evidence

The delivered film is 16.5 seconds, 1920×1080, 24 fps, 396 H.264 video frames, with 48 kHz stereo AAC sound. The final MP4 completed a full FFmpeg decode without errors. HyperFrames 0.8.33 passed lint, runtime, layout and contrast checks without findings at eleven authored times, and the high-quality render used `--strict-all`.

Visual review inspected the rendered MP4 using the repository's `apps/deforum/video_review.py`, including evenly spaced overview frames, every displayed frame around the first play-bow and chase transition, and selected entrance/exit/return/closing timestamps. Evidence remains in `review/decoded/v001` and `review/final/v001`. This is decoded-frame and timing review; it does not claim human playback approval or an independent real-time listening assessment.

## Revisions made

1. Two puppy sheets returned opaque checkerboards. An explicit image-generation alpha correction also returned an opaque sheet. Originals and the failed correction are preserved. The compositor now validates alpha; the two neutral, connected backgrounds were extracted deterministically without removing enclosed eye highlights. Rottweiler sheets already had alpha. Central incident: AF-20260909-191521.
2. The first cut gave the ball an unsupported moving trajectory. Final play focuses on the dogs chasing; the ball remains a stationary prop before play and in the rest shot.
3. The first chase staging relocated the dogs across the frame at the cut. Final pursuit starts from their established left/right positions. The puppy turns left, the big dog follows, both exit, and the return pass follows the offscreen turn.
4. Pose exposures were made regular at six drawing changes per second. Spatial positions update at twelve steps per second. No frame interpolation was used.
5. Airborne poses were aligned using their differing drawn extents to reduce unrelated head bobbing. Top-row Rottweiler run crops were widened/repositioned to retain paws and tails.
6. Return-direction cels were mirrored as derived assets, avoiding ambiguous negative transforms in the renderer's spatial audit.
7. The final title changed to dark ink for contrast against the sky. The music master was normalized, written as a finalized PCM WAV, and encoded into the movie. Final audio mean level: −26.6 dBFS; peak: −10.4 dBFS; no clipping.

## Final visual assessment

The setting and dog identities stay stable. The size contrast, hesitant reaction, reciprocal play bows, pursuit and shared rest make the story readable without dialogue. The separate hand-painted plate and cels preserve crisp outlines and avoid progressive repaint degradation. The closing artwork provides the warm payoff.

This is intentionally limited cel/cutout animation: running uses four drawn phases per dog, held at a stop-motion cadence. It does not have the in-between drawing density of a feature-length anime production. Within that short-film treatment, the final cut is the production candidate selected after the revisions above. Olof's playback judgment remains authoritative.

## Files

- `renders/big-softie-v1.mp4`: first draft.
- `renders/big-softie-v2.mp4`: revised high-quality master.
- `renders/big-softie.mp4`: verified delivery copy of v2.
- `renders/poster.jpg`: frame extracted from the delivered film at 15.25 seconds.
- `review/check-v1.json` through `review/check-v4.json`: iteration checks.
- `review/render-v2.log`, `review/audio-levels.txt`: final render and audio evidence.

All assets and earlier outputs remain local and are ignored by Git; tooling, prompts and review notes are versioned.
