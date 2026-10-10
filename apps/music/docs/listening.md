# Listening and calibration

## What each check can tell us

| Evidence | Useful for | Does not prove |
|---|---|---|
| Source and theory | Intended notes, timing, harmonic relationships and structure | The actual mix sounds as intended |
| Waveform and metrics | Silence, peaks, dynamics, level changes and stereo cancellation | Groove, interest or emotional impact |
| Spectrogram | Frequency distribution over time, transients, sustained harmonics, broad filtering | Instrument identity or musical quality by itself |
| Audio-capable model | Hypotheses about audible roles, changes and mix problems | Expert or human-equivalent hearing; precise measurements |
| Olof's playback | Taste, desired energy, boredom, emotional impact | A universal preference |

Codex in this session can inspect the images and numbers, but playback in the browser does not feed audio back to it. OpenRouter is a separate audio-input model: actual waveform input, textual observations returned. Do not describe those observations as Codex personally hearing the result. Do not replace audio input with a transcript for instrumental music.

## Initial calibration

`work/calibration/` contains four anonymous clips made from our own retained Window Seat render: original, complete silence, a two-second dropout and severe low-pass filtering. `answer-key.json` records the mapping but is not sent to the reviewer. These are conspicuous controls, not a music-understanding benchmark. The original and altered clips have equal duration; their loudness is deliberately not matched because silence/filtering are part of these first test conditions.

1. Check that the key is installed without printing it. Use the four review calls below, substituting each anonymous filename and a unique output directory. Each receives the same neutral prompt from `music.py`.
2. Read responses before comparing them with the answer key. Check whether silence is recognized without invented music, the dropout is located near 8–10 seconds, and the filtered clip is described as having reduced high-frequency content. Compare descriptions against the original to detect generic statements repeated without evidence.
3. Store a brief comparison with each response: observed detection, missed change, hallucination, reported cost and finish reason. A truncated response does not count as a complete review.
4. If a failure occurs, inspect it before spending another reservation. Stop after the four-call trial; discuss usefulness and further budget before extending it.
5. Only after this baseline, consider subtle blind A/Bs using matched loudness and Olof's verdict. Do not claim that four obvious controls validate taste, arrangement judgment or accurate pitch/tempo estimation.

```sh
uv run --locked python music.py review work/calibration/CLIP.wav --out work/calibration-review-01 --send
```

## Sources

- [OpenRouter audio inputs](https://openrouter.ai/docs/guides/overview/multimodal/audio): base64 `input_audio` on chat completions. Verified 2026-10-10.
- [OpenRouter Gemini 3.1 Pro Preview](https://openrouter.ai/google/gemini-3.1-pro-preview) and [catalog endpoint](https://openrouter.ai/api/v1/models): selected flagship input modalities and prices. Snapshot in `openrouter-model.json`; prices rechecked before calls.
- [Gemini audio understanding](https://ai.google.dev/gemini-api/docs/audio): documented audio reasoning tasks; product claims do not establish our calibration results.
- [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html#loudnorm): use input measurements from `loudnorm`, not its normalized output values.

No API review has been run as of initial setup. No audio-model verdict is part of the artist research; that research used text sources and captions.
