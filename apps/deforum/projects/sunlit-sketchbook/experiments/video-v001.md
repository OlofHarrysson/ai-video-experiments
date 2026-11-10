# Silent opening — first animation test

2026-11-10. Complete ten-second cut, awaiting Olof’s playback judgment.

![Silent opening](../exports/video-v001/sunlit-sketchbook-opening.mp4)

## Scope and feedback

Olof accepted the stills as close enough. He preferred the original’s space/galaxy imagery to frame four, but accepted the forest if it matched the original piece. The forest appears in the original opening; the galaxy arrives later. This test keeps the forest, with the cosmic setting recorded as a preference rather than automatically expanding scope. Music remains a later step.

## Generation and edit

Three independent jobs used Fal’s `alibaba/wan-3.0-prime/image-to-video`, selected by its live capability-aware recommendation. All requested 1080p, 16:9, silent output, reasoning enabled and prompt expansion enabled. The expanded prompt was not returned (`actual_prompt: null`); exact submitted prompts are preserved, but the provider’s internal rewrite is unknown.

| Cut time | Source | Conditioning and action |
| --- | --- | --- |
| 0–3s | [Artist](../runs/video-artist-v001/video.mp4) | A2 as first frame; small pencil movements, blink and pause. |
| 3–7s | [Transformation](../runs/video-transformation-v001/video.mp4) | B as first frame and C as last frame; graphite becomes dimensional while book and hands remain in place. |
| 7–10s | [Outdoors](../runs/video-outdoors-v001/video.mp4) | D as first frame; subtle horse/head movement, tail and foliage motion. |

Joined all three complete source clips with hard cuts, without re-encoding, interpolation, speed changes, added holds or audio. Native delivery is 30 fps. The originals remain intact.

## Assistant screening

- **Artist:** face, room and clothing remain recognizable across eight overview samples. Pencil/hand motion remains small; the blink and subsequent lifted gaze are visible. The gaze drifts slightly away from the page near the end despite the requested downward gaze. The room stays in the flatter illustrated treatment Olof approved.
- **Transformation:** the graphite image develops shading and volume, with some independent mane movement. The page, desk and illustrated hands remain visually steady in sampled frames. An every-frame window from 1.8–2.067s supports a gradual local material change rather than a hard replacement. No sudden cut or major geometry break is apparent in that inspected window.
- **Forest:** body and horn remain recognizable, with clear tail/foliage movement across samples. The style change to naturalistic rendering remains pronounced; this was already present in the approved stills. The forest’s lower fantastical appeal remains Olof’s stated reservation.
- **Assembly:** inspected an overview plus every displayed frame around both joins, at 3s and 7s. Both are intentional hard cuts; no black or extra transition frames appeared in those windows.

Inspection used decoded frame sheets, not continuous audiovisual playback. Sparse overview frames cannot establish perceived rhythm or absence of flicker throughout the whole film; Olof’s playback judgment is still needed. A separate every-frame artist window (1.5–1.767s) covers the blink and hand pose.

## Validation and preservation

All three source clips and the final cut decode fully without FFmpeg errors. Sources contain only H.264 video, 1920×1080, 30 fps, with 90/120/90 frames. Final cut is exactly 10.0 seconds and 300 frames with no audio stream. Original bytes, hashes, receipts and review frames are preserved locally.

- [Actual submitted recipes and request IDs](video-v001-receipt.json)
- [Completed results, seeds and output URLs](video-v001-results.json)
- [Source decoder facts and SHA-256](video-v001-files.json)
- [Assembly command, source hashes and final probe](video-v001-assembly.json)
- [Cut definition](../cuts/v001.md)

The initial combined submission was rejected before any job started: the tool advertised a nullable end-frame field but rejected null for the two single-frame shots. A fresh single-frame recommendation made the field optional; omitting it succeeded. The transformation request was submitted once, unchanged. Three paid video jobs completed; no duplicate generation was submitted. The returned base rate was $0.05/second without resolved resolution-specific billing; actual charges were not returned, so no exact total is claimed.
