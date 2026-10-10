# Music workbench

Make original, editable music with Strudel and review rendered audio before choosing revisions. This is a standalone music study inside AI Video Experiments, not a new video generation pipeline.

## Start here

- [README.md](README.md): setup, commands, file ownership and render workflow.
- [docs/status.md](docs/status.md): validation evidence, remaining work and next-chat handoff.
- [docs/music-foundations.md](docs/music-foundations.md): practical composition and sound-design references.
- [references/strudel/README.md](references/strudel/README.md): Strudel operating guide, export procedure and DJ_Dave study; local official documentation corpus alongside it.
- [docs/listening.md](docs/listening.md): audio review protocol and confidence boundaries.

## Working rules

- Use `uv sync --locked`, then `uv run --locked`; FFmpeg must be available. No server required.
- Before relying on remote listening, finish the blinded calibration in `docs/listening.md`. A successful API response does not prove musical judgment.
- Current Codex tools do not deliver browser playback back as heard audio. Distinguish numerical measurement, spectrogram interpretation, audio-model observations and Olof's listening verdict.
- OpenRouter is the agreed billing route. `.env` owns `OPENROUTER_API_KEY`; never expose it. Model and bounded trial constants live at the top of `music.py`. No automatic paid retries or model fallback.
- Preserve originals and source code; create versioned outputs. Export stems from the same cycle range and sample rate. Grouping existing stems is not source separation.
- For each song, create `projects/<song>/README.md` for intent and decisions, `source/` for versioned Strudel code and `renders/` for ignored WAVs. Do not start the first song until Olof supplies direction in the next chat.
- Validate changes with `uv run --locked pytest -q` and `uv run --locked ruff check .`. Keep measurements and human taste separate.
