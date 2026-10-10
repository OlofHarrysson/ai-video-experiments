# Music workbench

A small production workspace for original Strudel music: preserve source, export WAVs, inspect mixes and stems, ask an audio model for observations, and revise deliberately. Olof directs taste; the assistant owns composition tooling and initial technical review.

The current goal is to improve the tooling using simple music as test material. Local inspection, stereo export and synchronized stem reconstruction have been exercised end to end. Real OpenRouter audio input works; broad critique was unreliable, while a focused timeline prompt detected a known dropout. See [current status](docs/status.md) and the [validation study](projects/tooling-validation/README.md).

## Setup

From `/Users/olof/git/ai-video-experiments/apps/music`:

```sh
uv sync --locked
# Requires ffmpeg and ffprobe on PATH; installed on this Mac.
uv run --locked python music.py --help
```

Put the key in `/Users/olof/git/ai-video-experiments/apps/music/.env`:

```dotenv
OPENROUTER_API_KEY=your-key-here
```

The private file already exists and is ignored by Git. `.env.example` is safe to track. Shell-provided credentials take precedence over the file. All billing goes through OpenRouter; the selected Gemini provider still processes the uploaded audio. No direct Google account or billing setup is used.

## Local tools

These commands incur no API charges. Output paths must be new to preserve prior versions.

```sh
uv run --locked python music.py inspect references/strudel/beats/window-seat-96bpm.wav --out outputs/inspection-v002 --bpm 96
uv run --locked python music.py excerpt references/strudel/beats/window-seat-96bpm.wav --start 5 --duration 10 --out outputs/excerpt-v002.wav
uv run --locked python music.py mix projects/example/renders/drums.wav projects/example/renders/bass.wav --gain-db -6 --out outputs/rhythm-v001.wav
uv run --locked python music.py match projects/example/renders/v001.wav projects/example/renders/v002.wav --out outputs/comparison-v001
uv run --locked python music.py compare projects/example/renders/full.wav projects/example/renders/reconstructed.wav --out outputs/reconstruction-v001
```

`inspect` saves `spectrogram.png` (waveform above, logarithmic frequency against time below) and `metrics.json` (LUFS, true/sample peak, RMS, stereo correlation and mono RMS). Fixed color limits allow comparisons across renders. Channel powers are averaged for the spectrum so out-of-phase stereo does not disappear. These are per-bin spectral levels, not a calibrated sound-pressure measurement. Supplied BPM adds four-beat bar boundaries; it is not tempo detection.

`mix` sums aligned stems and applies the specified overall gain. Rates, channels and frame counts must match; it never guesses offsets or resamples. Float WAV preserves any overload for inspection instead of clipping it silently. `match` attenuates copies to the quietest file's measured integrated loudness; it does not master or compress them. Compare similar musical sections. Originals remain untouched.

`inspect` also reports intervals of at least 0.1 seconds where every channel stays at or below −80 dBFS. These are measurements of near-silence, not automatic defect judgments: intentional rests and tails count too. `compare` subtracts a reference from a candidate and saves a residual WAV, hashes, exact sample equality and residual levels. It requires matching rates, channels and frame counts and never aligns or changes gain. A JSON `null` level means zero energy (or an undefined ratio), not 0 dB.

## Rendering and revision

1. Read the [Strudel guide](references/strudel/README.md), including the verified browser WAV export procedure. Preserve each evaluated source and its BPM, cycle range, sample rate and sample-bank dependencies.
2. Export a stereo mix with **Multi Channel Orbits off**. Export stems by muting other layers, using the identical cycle range and sample rate each time. Start with deterministic patterns. Random pattern choices and shared reverb/delay can prevent independently rendered stems from summing exactly to the original mix; verify any reconstruction.
3. Inspect the full mix, then the individual stem or explicit stem group relevant to a suspected problem. Include effect tails in the arrangement/export window; exports can cut them off.
4. Make a short representative excerpt. Review audio with the workflow below and compare before/after copies at matched loudness.
5. Change one musical issue, render under a new version, and record what changed and why. Show Olof a small number of actual playable candidates.

The browser exporter was verified on Window Seat and two eight-second fixtures. Dry non-overlapping stems reconstructed exactly; overlapping voices with panning and independent delay reconstructed with a −96.44 dBFS RMS residual. Shared reverb, sample loading, random patterns and nonzero export starts remain outside that stem-validation scope. There is no headless Strudel render engine or automated source-separation system here.

## OpenRouter audio review

```sh
# Offline preflight: no upload, no charge, no output directory created.
uv run --locked python music.py review outputs/window-seat-excerpt.wav --out work/review-v001
# Actual upload and inference, once the key is present:
uv run --locked python music.py review outputs/window-seat-excerpt.wav --out work/review-v001 --send
# Supply a focused question when testing a specific audible issue:
uv run --locked python music.py review work/calibration/d87652a5.wav --out work/timeline-review-new --prompt-file docs/timeline-review-prompt.txt --send
```

Only `--send` makes a paid request. Each request sends actual PCM WAV audio plus a neutral prompt, without Strudel source or the filename. The adapter rechecks model audio support/prices and stores the model metadata, input hash, prompt, response, finish reason and reported usage/cost. It defaults to Gemini 3.1 Pro Preview with high reasoning, verified in OpenRouter's catalog on 2026-10-10. Review windows are limited to 60 seconds / 24 MB. Model selection should be rechecked in later sessions.

Olof manages spending through the OpenRouter balance. The adapter imposes no dollar budget, price ceiling or attempt cap. `work/review-ledger.jsonl` is an append-only request history; earlier reservation records remain historical. Each output folder preserves provider usage/cost when reported. There are no automatic retries or model fallbacks. A timeout has an unknown provider outcome and cost, not a free request. The response timeout is 600 seconds after one observed 180-second timeout. Empty or truncated replies are saved as incomplete and raise an error; they are never presented as completed reviews. Read [listening and calibration](docs/listening.md) first. The example timeline prompt states a 20-second duration; update it when using a different clip.

## Files and preservation

- `music.py`, `tests/`, `pyproject.toml`, `uv.lock`: local CLI and reproducible environment.
- `references/strudel/`: retained operating guide, DJ_Dave research, original sketches, and local documentation snapshots.
- `docs/`: foundations, listening protocol, selected catalog snapshot and current handoff.
- `outputs/`: ignored analysis images and review copies.
- `work/`: ignored calibration clips, provider responses and request history.
- `projects/<song>/`: future composition source, decisions and ignored original renders.

The 68 source files were copied from the brainstorm workspace and SHA-256 verified on 2026-10-10. That earlier folder is retained as an archive; this folder owns future work. Audio, screenshots, raw third-party documentation snapshots and provider receipts stay local and ignored here. Git is not a backup of those files. New clones need media/snapshots restored separately or new renders produced.

## Verification

```sh
uv run --locked pytest -q
uv run --locked ruff check .
```

Tests cover spectral/stereo cancellation behavior, real FFmpeg measurements, silent input and intervals, exact excerpts, preservation, alignment rejection, overload visibility, loudness matching, reconstruction differences, calibration conditions, offline preflight, uncapped requests and incomplete provider responses. Real provider and browser results are recorded separately in the validation study.
