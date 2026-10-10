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

Completed 2026-10-10; see the [validation study](../projects/tooling-validation/README.md). Broad critique detected silence but missed the injected dropout. A focused timeline question subsequently located 8–10 seconds correctly and reported no silence in the original. Use local measurements for objective defects; the model's broader musical critique remains unvalidated.

A subsequent [28-second practical beat](../projects/practical-dogfood/README.md) showed the limit of that result: a focused question detected voice and percussion dropout/return, but placed the actual 8–12-second drum break at about 11–14 seconds. Treat model timestamps as approximate hypotheses even after a simple control passes.

During [Chrome After Rain](../projects/chrome-after-rain/README.md), a broad comparison incorrectly called a syncopated pattern four-on-the-floor and described effects as absent. Solo measurements instead revealed that the kick overwhelmed the hook. A neutral comparison after rebalancing identified rhythmic space and lead masking more usefully. Use specific listening questions and independent stem evidence; do not optimize toward every confident model statement or treat its praise as proof of quality.

`work/calibration/` contains four anonymous clips made from our own retained Window Seat render: original, complete silence, a two-second dropout and severe low-pass filtering. `answer-key.json` records the mapping but is not sent to the reviewer. These are conspicuous controls, not a music-understanding benchmark. The original and altered clips have equal duration; their loudness is deliberately not matched because silence/filtering are part of these first test conditions.

1. Check that the key is installed without printing it. Use the four review calls below, substituting each anonymous filename and a unique output directory. Each receives the same neutral prompt from `music.py`.
2. Read responses before comparing them with the answer key. Check whether silence is recognized without invented music, the dropout is located near 8–10 seconds, and the filtered clip is described as having reduced high-frequency content. Compare descriptions against the original to detect generic statements repeated without evidence.
3. Store a brief comparison with each response: observed detection, missed change, hallucination, reported cost and finish reason. A truncated response does not count as a complete review.
4. If a failure occurs, inspect it before another request. Olof manages the OpenRouter balance; there is no dollar budget or attempt cap. Record actual costs when returned and unknown outcomes after transport failures. Do not automatically retry or switch models.
5. Only after this baseline, consider subtle blind A/Bs using matched loudness and Olof's verdict. Do not claim that four obvious controls validate taste, arrangement judgment or accurate pitch/tempo estimation.

```sh
uv run --locked python music.py review work/calibration/CLIP.wav --out work/calibration-review-01 --send
```

## Sources

- [OpenRouter audio inputs](https://openrouter.ai/docs/guides/overview/multimodal/audio): base64 `input_audio` on chat completions. Verified 2026-10-10.
- [OpenRouter Gemini 3.1 Pro Preview](https://openrouter.ai/google/gemini-3.1-pro-preview) and [catalog endpoint](https://openrouter.ai/api/v1/models): selected flagship input modalities and prices. Snapshot in `openrouter-model.json`; prices rechecked before calls.
- [Gemini audio understanding](https://ai.google.dev/gemini-api/docs/audio): documented audio reasoning tasks; product claims do not establish our calibration results.
- [FFmpeg filters](https://ffmpeg.org/ffmpeg-filters.html#loudnorm): use input measurements from `loudnorm`, not its normalized output values.

## Working review procedure

1. Run `inspect` first. Its near-silence intervals require every channel to remain at or below −80 dBFS for at least 0.1 seconds. A detected interval may be an intentional rest; measurements do not establish artistic intent.
2. Ask one focused listening question via `review --prompt-file`. Keep ground truth and condition labels out of the prompt for calibration. The saved `timeline-review-prompt.txt` states a measured 20-second duration; adjust this fact for other clips.
3. Read the full response and compare objective claims with local evidence. The default broad prompt remains available for exploration, but its suggestions are hypotheses, not instructions to change a mix.
4. Require `status: complete` and `finish_reason: stop` before treating a new adapter result as a completed response. An incomplete reply is saved separately. Completion means the provider finished, not that the response is correct. Initial pre-change receipts used `response_received`; their stored finish reasons show completion.
5. Use matched playback and Olof's judgment to evaluate taste. Stem grouping, spectral analysis and model text do not substitute for a human listening verdict.

Six completed requests reported $0.161604; one timed-out request has unknown cost. The retry passed with a longer timeout, without proving the cause of the timeout. Full provenance is in the validation study. No audio-model verdict is part of the DJ_Dave research; that research used text sources and captions.
