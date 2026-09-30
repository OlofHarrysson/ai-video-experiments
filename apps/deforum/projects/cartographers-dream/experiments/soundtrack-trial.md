# Soundtrack trial

2026-09-30. Question: can a reusable Fal audio workflow give the preserved 75-second Cartographer cut a coherent score and a few useful sound accents?

Compare two Eleven Music v2.5 scores with the same six passage lengths: 12, 12, 16, 20, 12 and 3 seconds. A uses felt piano, strings and celesta; B uses warm synths and a gentle pulse. Both request instrumental music, evolving toward the floating-world reveal and a quiet ending. This is text-directed scoring based on the film's brief and sampled frames; neither music call receives the video.

Generate three separate ElevenLabs Sound Effects v2 assets: water (14 s), bending paper (8 s), orbital shimmer (5 s). Use the same sparse effect placements in both mixes. Preserve the original music-only tracks and individual effects so the mix can be revised.

Authorized by Olof's request to try Fal after the two-score proposal. Planned generation cost is $1.554 at the queried rates: music $0.60/minute, effects $0.002/second. This is an estimate, not a billing receipt. No video inference or GPU pod is needed.

Inputs and provider receipts: `../runs/soundtrack-20260930-v001/`. Preview exports and frame review: `../exports/soundtrack-trial-v001/`. The selected silent cut remains v002 until human review chooses a soundtrack.

## Results

All five Fal jobs completed and their downloads matched the provider-reported byte sizes. Both music tracks are stereo 48 kHz MP3, 75.024 seconds including encoding padding; the effects are stereo 44.1 kHz MP3 and match their requested lengths. The two scores have different hashes. [Frozen generation inputs](configs/soundtrack-trial-v001.json) preserve the exact prompts and composition plans.

| Asset | Endpoint | Request ID |
| --- | --- | --- |
| Acoustic score | `elevenlabs/music/v2.5` | `01a0f40f-df26-7bd1-89bd-35ed9547bd05` |
| Electronic score | `elevenlabs/music/v2.5` | `01a0f410-0204-7ff2-9659-371f42f2d333` |
| Water | `fal-ai/elevenlabs/sound-effects/v2` | `01a0f410-077a-7b13-967d-d94028b34809` |
| Paper | `fal-ai/elevenlabs/sound-effects/v2` | `01a0f410-0c01-7491-8c66-6df3112f33ae` |
| Orbit | `fal-ai/elevenlabs/sound-effects/v2` | `01a0f410-10d7-7f31-920b-06b756d12f3e` |

The three shared cues occupy 9–23 s, 60–68 s and 70–75 s. Music is initially set to -20 LUFS and the effects to -31/-32/-31 LUFS, with fades. The complete mixes target -18 LUFS and -2 dBTP. These are preview choices, not a production loudness standard. `deforum_lab.media.soundtrack` owns local mixing; it copies the original video packets into each full-resolution MP4.

| Requested direction | Compact playback | Full-resolution output | Measured loudness | Measured true peak |
| --- | --- | --- | --- | --- |
| Felt piano, strings and celesta | [Acoustic](../exports/soundtrack-trial-v001/acoustic/review.mp4) | [1536×1024](../exports/soundtrack-trial-v001/acoustic/preview.mp4) | -18.03 LUFS | -2.83 dBTP |
| Warm synths and soft pulse | [Electronic](../exports/soundtrack-trial-v001/electronic/review.mp4) | [1536×1024](../exports/soundtrack-trial-v001/electronic/preview.mp4) | -18.72 LUFS | -2.26 dBTP |

Compact reviews use 960×640 H.264 CRF 22 and copy the same AAC audio. Each export preserves a floating-point premaster WAV, a 24-bit master WAV, plan and validation receipt. Raw music-only tracks remain in the run directory.

## Verification and review boundary

- Both full-resolution outputs decode completely, have a 75-second container duration, and retain byte-identical compressed video packets. Source SHA-256 remains `f5be9f633b691a9fc97b7db1783c97684bc9be401876de33d23dc4df259ac8c6`.
- Audio is stereo AAC at 48 kHz. Measured true peaks are below -2 dBTP. Silence detection at -50 dB for at least 0.5 s found only the final decay: approximately 74.27 s onward in acoustic and 73.78 s onward in electronic. No interior gap met that threshold.
- The assistant inspected twelve video samples spanning the film, and checked audio duration, loudness, silence and file integrity. Direct auditory review was unavailable; instrumentation, absence of vocals, musical joins and emotional fit have not been confirmed by listening. The labels describe the commissioned direction.
- The existing media reviewer is silent-only, so these outputs are delivered as standalone playable MP4s. No server was started or changed.
- Five successful generations at the queried rates total an estimated **$1.554**. There were no paid generation retries. Final account billing has not been checked.

Human taste review is pending. First question: which musical direction fits the film better? The current selected film remains the silent v002; neither soundtrack is an approved replacement.

## Reuse

The [add-video-soundtrack skill](../../../../../.agents/skills/add-video-soundtrack/SKILL.md) records generation, timing, preservation, mixing and review boundaries. It is also linked into Olof's local Codex skills directory. The module's actual trial on both full-length films verifies the local path; future artistic results and other providers remain untested.
