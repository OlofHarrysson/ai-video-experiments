# Music setup — handoff

Updated 2026-10-10. Current scope: tooling and foundations, before the first song. Work in `/Users/olof/git/ai-video-experiments/apps/music`; the brainstorm workspace is historical.

## Completed and checked

- Dedicated uv Python workspace, locked dependencies, local CLI and credential template. No server or cloud compute is running for music.
- Strudel operating guide and all 47 official documentation snapshots, DJ_Dave interview/demo research and original sketches copied from the brainstorm workspace. All 68 copied files matched SHA-256 before adding the old workspace's migration pointer. See `migration.json`.
- The existing Window Seat WAV inspected: 20 seconds, stereo 48 kHz, integrated -14.94 LUFS, sample peak -0.242 dBFS, estimated true peak -0.24 dBTP. No samples reach full scale. This is technical evidence, not a favorable listening verdict.
- `outputs/window-seat-analysis-v002/spectrogram.png` generated and visually inspected: labeled time/frequency axes, log frequency, waveform above, visible transient and harmonic patterns. The first failed analysis directory is retained; FFmpeg appended progress after its JSON, and the parser was corrected to decode the first object.
- Ten-second excerpt rendered to `outputs/window-seat-excerpt.wav`; offline OpenRouter preflight passed without network calls. Four anonymous calibration WAVs are ready in `work/calibration/`.
- Eight tests pass, including actual FFmpeg measurements, antiphase stereo and silent input, duration/preservation, aligned summing, overload visibility, loudness matching, calibration copies and the mocked API adapter/attempt limit. Ruff passes.
- Latest selected Pro model and audio modality verified against the live OpenRouter catalog; snapshot in `openrouter-model.json`. Gemini 3.1 Pro Preview, high reasoning. Direct Google billing rejected by Olof; use OpenRouter only.
- Practical theory and references saved in `music-foundations.md`. Review protocol and evidence boundaries saved in `listening.md`.

## Pending

- Olof's `OPENROUTER_API_KEY` in `apps/music/.env`. File created and opened; empty when last checked. No paid requests or uploads have occurred.
- Real API compatibility and blinded listening calibration. Mock success is not provider validation, and audio input support is not proof of useful musical critique. Initial plan: four calls maximum with $0.25 reserved per attempt against a $1 planning budget. See the adapter's ledger and protocol before running.
- First synchronized Strudel stem export/reconstruction check. The mixer works on aligned files; correct browser stem export remains to be exercised. Native stereo export already produced the retained original WAV earlier in this session.
- Direction for the first actual song. The earlier Window Seat/live sketches are learning artifacts, not the approved first-song brief.

## Continue in the next chat

Suggested opening message:

> Continue the music project in apps/music. Read AGENTS.md, README.md and docs/status.md. Finish the OpenRouter listening calibration if my key is present, report what the model actually detects, then help me choose a direction for the first original song. Use the Strudel and DJ_Dave research as background; keep original source and versioned renders. Do not resume paused video studies.

Once the key exists, run the four anonymous calibration clips with the same neutral prompt, inspect complete responses, compare with the answer key and record observed successes/failures plus actual costs. Ask one focused question about song direction after that. Do not produce a ten-minute set without a short reviewed musical checkpoint.
