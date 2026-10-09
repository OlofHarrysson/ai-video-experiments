# Rough 3D to styled video

30 September 2026. Both paid runs completed and the local comparison rendered.

## Result

Both styles substantially improve the character's appearance. Twelve evenly spaced samples per output show stable hair, glasses, face shape, clothing and lighting, with broad correspondence to the source's mouth poses. Film is the stronger result: a more expressive sculpted face, detailed swept hair and warmer lighting. Clay is a distinct handmade treatment, although some segmented shoulders remain.

An additional 8 FPS sample sequence between 7 and 8 seconds shows the source blink and a slightly later film blink, about one 125 ms sampling interval apart. Clay's eyes stay open in all eight samples. Mouth opening also differs across these matched times. This establishes approximate performance transfer with deviations, not exact motion or lip-sync. These are sampled-frame findings, not a claim of uninterrupted playback quality.

Both edits change the requested composition. Film crops out the hands, changes proportions, and replaces the ivory background with brown. Clay reframes more strongly into a close-up, removing most of the body. Both output video streams are 12.041667 seconds versus 12.2 seconds in the source: 0.158333 seconds of video tail lost. The source's final 0.2 seconds contain audible signal, so end trimming affects real content rather than guaranteed silence.

Both decoded mono audio tracks at 8 kHz have a normalized waveform correlation of 0.9883 with the source after a 16.625 ms sample offset. The source audio track starts at 17 ms and each output starts at 0 ms, so matched speech is effectively aligned in the container timeline. This confirms close speech preservation over the overlap; it does not validate mouth synchronization or the missing tail.

Browser automation stopped responding while opening the MP4, including one recovery attempt. Media metadata and extracted frames were inspected directly. Uninterrupted audiovisual playback and the final review UI remain unverified in this session.

**Conclusion:** visual restyling of a crude character works convincingly in this small trial. Exact performance, framing and full speech duration are not preserved. Use an existing rig and a stronger motion clip for the next experiment; include a short silent end pad and evaluate speech timing before attempting a longer production.

The homepage now contains one comparison player and a disclosure for full-size videos and notes. The old authoring tools remain at `/studio.html`. Existing tests and both frontend builds pass. No generated videos were bundled into the static build.

## Question

Can a crude talking character render become a visually appealing, controllable character through AI video restyling, without investing in a custom production rig first?

Olof directs the character in conversation. Script and voice may be placeholders. The current source reuses the previous 3D prototype; future animation work should use an existing rig.

## Method

- Source: `.private/restyle/source.mp4`, 12.239 seconds including container padding, 1742 × 1066, normalized to 30 FPS, H.264/AAC. The source's video stream is 12.2 seconds.
- Character: fictional procedural geometry, brown crop hair, glasses, terracotta top. Modest head tilts, blinks and arm motion. Mouth follows audio energy, not phonemes.
- Voice: Qwen3-TTS stock Aiden; no likeness or voice sample from Olof.
- Model: `fal-ai/kling-video/o3/pro/video-to-video/edit`. Current schema accepts MP4/MOV, 3–15 seconds, 720–3840 pixels on each side and 24–60 FPS. This supersedes the shorter O1 input limit.
- Two prompts on the exact same full source: stylized animated film and handmade clay. Both explicitly request unchanged framing, movement and mouth timing. `keep_audio: true`.
- No reference still or image-to-video generation: the entire source performance is supplied to the editor.
- Original outputs stay under `.private/restyle/film.mp4` and `clay.mp4`. The comparison center-crops each frame after scaling to the same height, places them side by side with the source, and uses the source audio once. It ends at the shortest video duration and does not repair timing or movement.

## Acceptance checks

| Check | Evidence to inspect |
| --- | --- |
| Appearance | Improved face, materials and lighting; visibly different requested styles. |
| Consistency | Stable hair, glasses, face shape, clothing and background throughout. |
| Performance | Same direction and timing of head tilt and blink events. |
| Mouth | Open/closed motion agrees with the source across speech and pauses. Audio retention alone is not evidence of lip-sync. |
| Audio | Duration, track offsets and signal agreement with the original. |

The clip has little body movement. Even a successful result does not establish reliability for large gestures, turns, occlusion, new shots, longer scripts, or a consistent recurring identity. The output is a video, not a new rigged 3D asset.

## Budget

Two video runs at the returned rate of $0.14 per second × 12.239 seconds: approximately $3.42692. Prior stock speech: $0.01557. Estimated project total: **$3.44249 of $50**. Duration rounding and the final invoice are not reconciled. No subscription.

Request IDs, full submitted prompts, source URL and output metadata live in [restyle.json](restyle.json). The Fal connector uses the existing authenticated account; no new API key was needed.

## Reproduce the comparison

With all three videos saved under `.private/restyle/`, run:

```sh
node scripts/build-comparison.mjs
```

This is local FFmpeg postproduction and makes no paid calls. It also saves media metadata and one-second contact sheets. Repeating a provider generation is a separate paid action; do not resubmit merely to retrieve a result.

## Provider references

- [Kling O3 Pro edit schema](https://fal.ai/models/fal-ai/kling-video/o3/pro/video-to-video/edit/api)
- [Wan 2.7 video editing](https://fal.ai/models/fal-ai/wan/v2.7/edit-video/api): alternative direct video restyling endpoint; inspected but not run.
- [Wan-Animate preprocessing](https://github.com/Wan-Video/Wan2.2/blob/main/wan/modules/animate/preprocess/UserGuider.md): pose/face extraction and proportion mismatch introduce separate failure modes. Motion transfer onto a still character image would test a different pipeline.
