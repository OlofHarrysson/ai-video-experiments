# Music workbench

Make original, editable music with Strudel and review rendered audio before choosing revisions. This is a standalone music study inside AI Video Experiments, not a new video generation pipeline.

## Start here

- [README.md](README.md): setup, commands, file ownership and render workflow.
- [docs/status.md](docs/status.md): validation evidence, remaining work and next-chat handoff.
- [docs/music-foundations.md](docs/music-foundations.md): practical composition and sound-design references.
- [references/strudel/README.md](references/strudel/README.md): Strudel operating guide, export procedure and DJ_Dave study; local official documentation corpus alongside it.
- [docs/listening.md](docs/listening.md): audio review protocol and confidence boundaries.

## Working rules

- Use `uv sync --locked`, then `uv run --locked`; Install the renderer with `npm ci`; Node.js, Chrome, `patch` and FFmpeg must be available. Rendering owns a temporary server/browser and closes both; no persistent service required.
- Use `docs/listening.md` for calibrated listening scope. Early focused questions detected a known dropout, but later short duplicate comparisons invented differences. Confirm objective defects locally; neither focused questions nor a passed control validate subtle mix judgment.
- Current Codex tools do not deliver browser playback back as heard audio. Distinguish numerical measurement, spectrogram interpretation, audio-model observations and Olof's listening verdict.
- OpenRouter is the agreed billing route. `.env` owns `OPENROUTER_API_KEY`; never expose it. Olof manages the account balance; impose no dollar budget, price ceiling or attempt cap. Record actual usage and unresolved request outcomes. No automatic paid retries or model fallback.
- Preserve originals and source code; create versioned outputs. Export stems from the same cycle range and sample rate. Grouping existing stems is not source separation.
- Use saved project recipes for arrangements: `render-project` owns the master/stems and inspection, `preview` extracts from completed audio to preserve effect state, and `compare-revisions` makes labelled matched copies. See the README for recipe fields and boundaries.
- For each study or song, create `projects/<name>/README.md` for intent and decisions, `source/` for versioned Strudel code and `renders/` for ignored WAVs. Current work is the [30-second club sprint](projects/club-detail-sprint/README.md). Olof approved [Undertow](projects/undertow/README.md) v002’s sound and v003’s improved arrangement, then requested a substantial quality increase through modular collaboration. Preserve heavy bass, strong drums, sparse melody and underground edge; Pressure Lock v011 and Negative Space v011 are the selected 30-second excerpts awaiting his taste judgment; Latch v006 remains a preserved alternative. Soft Focus and Chrome After Rain remain rejected as game-like.
- Validate changes with `uv run --locked pytest -q` and `uv run --locked ruff check .`; renderer changes also require `npm test`. Keep measurements and human taste separate.
