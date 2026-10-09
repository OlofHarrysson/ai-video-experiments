# Eight-second motion transfer test

Completed 5 October 2026 using the source prepared 1 October. **The large motions transfer successfully, with small timing differences.** Kling improves the face, hair and lighting but retains much of the crude torso, segmented arms and simplified hands. This supports controllable performance → AI styling, but does not establish that AI can hide an arbitrarily poor rig.

Watch the silent eight-second comparison at **http://localhost:3044/motion.html**. Source is on the left, Kling on the right. Both full frames are fitted into equal panels without cropping, time scaling or motion correction.

## Result

| Check | Observed result |
| --- | --- |
| Correct arm and two waves | Preserved. Alternating wave poses match at 1.7, 2.0667, 2.4333 and 2.8 seconds. |
| Lowering the arm | Slight lag. At 3.7 seconds the source has settled while Kling is still slightly outward; it settles around 3.8–3.9 seconds. |
| Head turn directions and extent | Viewer-right at 5.0 seconds, viewer-left at 6.2667, front at 7.2 and 7.8. Broadly comparable turn magnitude; exact output angles are unmeasured. |
| Head transition timing | Around 5.6 seconds the source is front-facing while Kling still faces slightly viewer-right. Dense samples suggest roughly 0.1 seconds of local lag, not a constant offset across the clip. |
| Framing and identity | Both hands stay visible in inspected frames; no evident major zoom or crop. Character identity remains recognizable through both turns. The background changes from ivory to warm brown. |
| Style and anatomy | More detailed hair, face, sweater and lighting. Cylindrical torso, arm segmentation and tiny simplified hands remain. |
| Duration and audio | Source 8.000 seconds, output 8.041667 seconds; neither has an audio stream. No tail loss this time. |

Assessment used 2 FPS contact sheets, 12 paired checkpoints, denser transition samples and a second independent visual review. The browser player also completed all eight seconds without a media error. This confirms playback, while motion judgments above come from sampled frames rather than a formal pose-error measurement. This silent test says nothing about lip-sync.

## Source and method

The test isolates gross motion from lip-sync. It reuses the existing rough character, fixed camera and Creative appearance, with no speech, mouth movement or incidental blinking. It does not introduce a new rig.

| Time | Source action |
| --- | --- |
| 0–0.5 s | Neutral pose |
| 0.5–1.5 s | Raise the character's right arm, on the viewer's left |
| 1.5–3.0 s | Two waving cycles with distinct reversals |
| 3.0–3.7 s | Lower the arm |
| 4.1–4.7 s | Head turns 60° toward the viewer's right |
| 4.7–5.2 s | Hold |
| 5.2–6.0 s | Head turns to 60° toward the viewer's left |
| 6.0–6.5 s | Hold |
| 6.5–7.2 s | Return to front |
| 7.2–8.0 s | Hold neutral |

Source: `.private/motion/source.mp4`, H.264, 1280 × 960, 30 FPS, exactly 240 frames / 8 seconds, no audio. The browser rendered and saved the underlying WebM successfully. A 16-frame contact sheet at `.private/motion/source-contact.jpg` confirms the arm and hand remain inside the frame and both head turn directions are visible.

Model: `fal-ai/kling-video/o3/pro/video-to-video/edit`, same animated-film style family as the earlier comparison. The prompt requests exact source motion, a fixed camera and no cropping of the hands. Full prompt, source URL and result are in [motion.json](motion.json). Request: `01a10d8e-fbb0-7331-a6f8-c884814f3e24`. One job was submitted after the account passed its readiness check and the source upload returned HTTP 200.

Output: `.private/motion/styled.mp4`, 1660 × 1244, 24 FPS, 193 frames, 6,040,952 bytes. [Original provider output](https://v3b.fal.media/files/b/0aad32de/fgdTrmzJkL1K2JDBCoSn4_output.mp4). The 1920 × 720 comparison displays both clips at 30 FPS, duplicating output frames as needed and ending at the shorter eight-second source. Full provider output is preserved separately.

Cost: rate rechecked 5 October, $0.14 per second, estimated **$1.12** from the eight-second input. Prior project estimate $3.44249; **cumulative estimate $4.56249**, within the $50 ceiling. The provider account balance is separate from this project budget. No invoice reconciliation.

Rebuild local comparison and evidence with `node scripts/build-motion-comparison.mjs`. This only reads the saved videos; it does not call paid APIs. Evidence is in `.private/motion/media-metadata.json`, `checkpoint-contact.jpg`, `checkpoints/`, and `reviewer/`. `npm run verify` passed both speech-validation tests and the four-page Vite build; its existing Three.js chunk-size warning remains.

Production source: `/motion-source.html`, `src/motion-source.js`, and the pure timeline in `src/motion-sequence.js`. The existing avatar renderer accepts an optional pose override; ordinary studio playback remains unchanged.
