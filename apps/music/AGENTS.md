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
- Use `docs/listening.md` for calibrated listening scope. Broad reviews missed a known dropout; a focused timeline question detected it. Confirm objective defects with local measurements; musical judgment remains unvalidated.
- Current Codex tools do not deliver browser playback back as heard audio. Distinguish numerical measurement, spectrogram interpretation, audio-model observations and Olof's listening verdict.
- OpenRouter is the agreed billing route. `.env` owns `OPENROUTER_API_KEY`; never expose it. Olof manages the account balance; impose no dollar budget, price ceiling or attempt cap. Record actual usage and unresolved request outcomes. No automatic paid retries or model fallback.
- Preserve originals and source code; create versioned outputs. Export stems from the same cycle range and sample rate. Grouping existing stems is not source separation.
- Use saved project recipes for arrangements: `render-project` owns the master/stems and inspection, `preview` extracts from completed audio to preserve effect state, and `compare-revisions` makes labelled matched copies. See the README for recipe fields and boundaries.
- For each study or song, create `projects/<name>/README.md` for intent and decisions, `source/` for versioned Strudel code and `renders/` for ignored WAVs. Current audition is [Undertow](projects/undertow/README.md): a short, bass-and-drums-led techno/club groove. Olof rejected both Soft Focus and Chrome After Rain as game-like. Prioritize heavy bass, strong drums, sparse melody and an adult underground edge, without assuming anger or aggression. Get a human response to the core before expanding another full arrangement.
- Validate changes with `uv run --locked pytest -q` and `uv run --locked ruff check .`; renderer changes also require `npm test`. Keep measurements and human taste separate.
