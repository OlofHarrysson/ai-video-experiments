# Music workbench

A small production workspace for original Strudel music: preserve source, export WAVs, inspect mixes and stems, ask an audio model for observations, and revise deliberately. Olof directs taste; the assistant owns composition tooling and initial technical review.

Current work: [three 30-second club studies](projects/club-detail-sprint/README.md), developed through modular composition, original sound design and comparative screening. Olof approved [Undertow](projects/undertow/README.md) v003 as an improvement and requested a substantial increase in identity and detail. [Soft Focus](projects/soft-focus/README.md) and [Chrome After Rain](projects/chrome-after-rain/README.md) remain rejected comparisons. The [DJ_Dave reference library](projects/dj-dave-reference-study/README.md) is preserved.

The current goal is to make better music while exercising the tooling on real compositions. Local inspection, stereo export, stem reconstruction and local voice/music sampling have been exercised end to end. Real OpenRouter audio input works, but timing accuracy and musical judgments remain limited. See [current status](docs/status.md), the [initial validation](projects/tooling-validation/README.md) and [practical dogfood](projects/practical-dogfood/README.md).

## Setup

From `/Users/olof/git/ai-video-experiments/apps/music`:

```sh
uv sync --locked
npm ci
# Requires Node.js 20+, Google Chrome, patch, ffmpeg and ffprobe; installed on this Mac.
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

For integer PCM exports, `inspect` also counts samples touching either representable rail and the longest consecutive run. This catches positive PCM16 saturation that a `>= 1.0` check misses. A rail contact is evidence to investigate, not proof of audible distortion; inspect the original render before attenuating it.

`inspect` also reports intervals of at least 0.1 seconds where every channel stays at or below −80 dBFS. These are measurements of near-silence, not automatic defect judgments: intentional rests and tails count too. `compare` subtracts a reference from a candidate and saves a residual WAV, hashes, exact sample equality and residual levels. It requires matching rates, channels and frame counts and never aligns or changes gain. A JSON `null` level means zero energy (or an undefined ratio), not 0 dB.

## Rendering and revision

Render saved source directly through the CLI. It uses a fresh headless Chrome process and a temporary loopback server, then closes both. There is no persistent service to start and no editor/menu automation.

```sh
# Synth-only fixture; tempo comes from setcpm/setcps in the source.
uv run --locked python music.py render projects/tooling-validation/source/v001-full.strudel --end 4 --out outputs/my-synth-v001

# Practical beat with explicit local drum and speech/music libraries.
uv run --locked python music.py render projects/practical-dogfood/source/v002-full.strudel \
  --begin 2 --end 16 --sample-rate 48000 \
  --samples projects/practical-dogfood/references/assets/drums \
  --samples projects/practical-dogfood/references/assets/samples \
  --out outputs/my-practical-v001
```

Use `render --trace-events` when a rhythm's global phase or layer interaction is unclear. It saves `events.json` with cycle/file-relative onset times, scheduled durations and primitive control values. Combine it with repeated `--solo` labels to inspect particular voices. The trace observes the offline exporter's actual pattern queries without issuing additional queries or changing the returned events. It is a schedule trace, not measured audio: gain-zero events, effect tails, sample envelopes and masking still require separate interpretation. Complex controls are listed as omitted and stateful events are flagged. The receipt hashes the trace.

Each new output directory contains `render.wav`, an exact `source.strudel` copy and `render.json`: tempo, range, frame count, engine/browser versions, source/sample/output hashes, requested sample paths and logs. Failed engine runs retain a failed receipt and any partial audio as `incomplete.wav`; they never publish that audio as `render.wav`. Existing output directories are rejected. `--timeout` defaults to 120 seconds for browser startup and separately for evaluation/rendering; longer arrangements can use a larger value. It is not a spending limit.

The renderer pins `@strudel/web` 1.3.0 with a checksum-verified scheduling patch. The unpatched npm exporter measurably changed the practical sample layers; matching the website's chunked scheduling fixed the discrepancy. `npm ci` applies the patch; runtime refuses an unverified bundle. See [renderer validation and limits](docs/renderer-validation.md).

1. Preserve versioned source and sample originals. Use `setcpm` or `setcps` explicitly. Only trusted local JavaScript source belongs in this tool.
2. Render a stereo mix, then stems by muting other layers with `_$:` and using the identical range/rate. Multi Channel Orbits stays off. Include rests for effect tails; events before the start are not warmed up and tails beyond the end are cut off.
3. Inspect the mix and relevant stems, then make a short excerpt for focused listening. Use `match` for before/after comparisons.
4. Change one musical issue, render to a new directory and record the decision. Preserve wet masters: shared reverb and randomized patterns can vary across renders, so exact wet reconstruction is not an invariant.

The [Strudel guide](references/strudel/README.md) remains useful for interactive editing and browser export. The automated path passed reference comparisons for dry synths, overlap/delay and the practical dry sampled beat, plus a 128-second wet arrangement. This is evidence for those recipes, not all Strudel features.

## Projects, section previews and revision comparisons

A project recipe records source versions, local sample folders, named stem groups, section boundaries and the export endpoint. Paths in the recipe are relative to its own directory; output paths are relative to the command's working directory. See the tested [workflow project](projects/workflow-dogfood/project.json) and [study](projects/workflow-dogfood/README.md).

```sh
uv run --locked python music.py render-project projects/workflow-dogfood/project.json --revision v001 --out outputs/study-v001
uv run --locked python music.py render-project projects/workflow-dogfood/project.json --revision v002 --out outputs/study-v002
uv run --locked python music.py preview outputs/study-v001 --section breakdown --lead 2 --tail 2 --out outputs/breakdown-preview
uv run --locked python music.py compare-revisions outputs/study-v001 outputs/study-v002 --section return --lead 2 --tail 2 --out outputs/return-comparison
```

`render-project` renders the master and every stem, then inspects each. It saves source/recipe snapshots, per-render receipts, measurements, spectrograms and a summary in a new output directory. A failure preserves completed work and marks the overall receipt failed. The CLI result includes master LUFS, true peak and PCM rail count. Rail contacts or true peaks over 0 dBTP produce visible warnings for every affected master/stem; they never trigger automatic normalization or erase the original render. Completion reports successful export, not a clean or musically successful mix. All project exports begin at cycle zero. `end_cycle` must include the desired effect-tail window, with the source silent during that window. The recipe's `sections` are cycle pairs; the preview command's `--lead` and `--tail` are seconds.

Use unique top-level source labels such as `kick:`, `bass:` and `voice:`. Each label must belong to exactly one stem in the recipe. Labels must start with a lowercase letter and must not end with `_`; anonymous `$:` layers are supported by the low-level renderer but not by named project stems. The renderer uses JavaScript parsing and Strudel's native mute syntax to select layers; it retains both the original and evaluated source. For an individual render, repeat `render --solo NAME` to select a group. No manually maintained stem-source copies are needed.

`preview` extracts `preview.wav` from an already completed master. Earlier notes' reverb/delay state is preserved exactly; there is no fresh evaluation or random rerender. Lead/tail context includes any adjacent notes present in that master. Insufficient context fails explicitly rather than padding or truncating silently. Use `--stem drums` (or another declared stem) to inspect a specific group. The CLI checks the saved audio hash before extracting it.

`compare-revisions` selects the same section from two completed runs and creates `matched/01-A.wav` and `matched/02-B.wav`, with revision labels, edit notes, original hashes and attenuation values. It reuses the existing loudness-matching tool. Tempo, sample rate and section cycle boundaries must match; silent comparisons fail explicitly. No compression, stretching or automatic alignment is applied. A comparison folder's README links the two matched clips. Shared reverb can vary independently of the revision, and no preference is inferred automatically.

## Modular composition and focused listening

`assemble` combines independently editable Strudel modules into the existing project renderer. One setup module declares tempo/constants; each sound module names its stem. The assembler checks duplicate layers and top-level bindings, requires one tempo declaration and saves exact module snapshots, source hashes, concatenated source and a ready-to-render recipe. It does not create a separate synthesis engine.

```sh
uv run --locked python music.py assemble projects/pressure-study/assembly-v003.json --out outputs/assembly-v003
uv run --locked python music.py render-project outputs/assembly-v003/project.json --revision v003 --out outputs/render-v003
uv run --locked python music.py analyze-project outputs/render-v003 --out outputs/bands-v003
uv run --locked python music.py audition first.wav second.wav --duration 28 --gap 2 --out outputs/pair-v001
```

The assembly manifest has `version`, `title`, `revision`, `end_cycle`, `sample_rate`, `samples`, `sections` and `modules`. Each module has `file` and, when it contains sound layers, `stem`. Paths are relative to the manifest. [Pressure Study](projects/pressure-study/assembly-v003.json) is a working example.

`analyze-project` verifies completed audio hashes and measures continuous band-filtered RMS per cycle for master and stems. It writes CSV, JSON and a plot for low (30–180 Hz), body (180–1200 Hz), presence (1200–6000 Hz) and air (6000–20000 Hz), bounded by sample rate. `--window-cycles` changes the window size. These measurements help find buried parts and verify edits; they do not establish audibility, masking or musical quality. Levels below −120 dBFS become `null`; the plot floor is −90 dBFS.

`audition` takes equal-duration windows (`--start-first`, `--start-second`), attenuates to matched loudness, randomizes their A/B order and saves one review WAV, a neutral prompt and a private `answer-key.json`. The total including `--gap` must be at most 60 seconds. It rejects out-of-bounds windows or mismatched formats instead of padding/resampling. Read the comparison before decoding the key. An identical-input control checks invented differences, but does not validate musical taste or timestamps.

## Local voice and music samples

For a complete arrangement, use the saved-project workflow below so sample paths and stem membership live in one recipe.

Put retained audio in `projects/<study>/references/assets/samples/<sound-name>/<file>.wav`, then pass the parent `samples` folder with `--samples`. Immediate child folders become sound names; files use case-sensitive filename order, recorded by index in the receipt. Multiple `--samples` folders are allowed, but duplicate sound names fail. WAV is tested; MP3/OGG/FLAC/M4A depend on Chrome decoding and have not been separately validated here.

Use `s("sound-name")` to trigger a clip, `slice` to reorder segments and negative `speed` to reverse playback. Speech chopping and reversed music slices work in a fresh profile. No microphone recorder or extraction of vocals from a mixed song is implemented. The website can also import these folders through **sounds → import-sounds → import sounds folder**; browser storage is not a backup.

Drum libraries must be explicit too: `.bank("RolandTR909")` expects folders such as `RolandTR909_bd`. This study retains the four index-zero drum samples it actually uses, with source URLs/hashes in [drum-sources.json](projects/practical-dogfood/drum-sources.json). Other banks and sample indices require their own files. Runtime HTTP requests outside its local server fail explicitly; download and preserve dependencies before rendering. It does not automatically load the website's entire sound library.

## OpenRouter audio review

```sh
# Offline preflight: no upload, no charge, no output directory created.
uv run --locked python music.py review outputs/window-seat-excerpt.wav --out work/review-v001
# Actual upload and inference, once the key is present:
uv run --locked python music.py review outputs/window-seat-excerpt.wav --out work/review-v001 --send
# Supply a focused question when testing a specific audible issue:
uv run --locked python music.py review work/calibration/d87652a5.wav --out work/timeline-review-new --prompt-file docs/timeline-review-prompt.txt --send
```

Only `--send` makes a paid request. Each request sends actual PCM WAV audio plus a neutral prompt, without Strudel source or the filename. The adapter rechecks model audio support/prices and stores the model metadata, input hash, prompt, response, finish reason and reported usage/cost. It defaults to Gemini 3.1 Pro Preview with high reasoning, verified in OpenRouter's catalog on 2026-10-10. Review windows are limited to 60 seconds / 24 MB. `--model MODEL_ID` explicitly selects another current audio model for a planned evaluation; it never changes the default or creates a fallback. `--provider NAME` pins one OpenRouter provider for a deliberate route test. The receipt records requested/returned provider and the exact encoded PCM16 audio hash. Catalog audio support alone does not prove the chosen route processes audio correctly. High reasoning is sent when the catalog advertises support, otherwise omitted and recorded as `null`. Verify each model against controls before using its observations. Model selection should be rechecked in later sessions.

Olof manages spending through the OpenRouter balance. The adapter imposes no dollar budget, price ceiling or attempt cap. `work/review-ledger.jsonl` is an append-only request history; earlier reservation records remain historical. Each output folder preserves provider usage/cost when reported. There are no automatic retries or model fallbacks. A timeout has an unknown provider outcome and cost, not a free request. Catalog preflight has a 30-second timeout; the paid response timeout is 600 seconds. Receipts record preflight, dispatch and completion states with timestamps. Concurrent requests share only a brief ledger-append lock, so one slow request does not block independent reviews. Empty or truncated replies are saved as incomplete and raise an error; they are never presented as completed reviews. Read [listening and calibration](docs/listening.md) first. The example timeline prompt states a 20-second duration; update it when using a different clip.

## Files and preservation

- `music.py`, `tests/`, `pyproject.toml`, `uv.lock`: local CLI and reproducible Python environment.
- `renderer/`, `patches/`, `package.json`, `package-lock.json`: pinned browser render engine, scheduling patch and integration tests.
- `workflow.py`: saved project runs, master-derived previews and revision comparisons.
- `analysis.py`, `audition.py`: time-resolved stem inspection and anonymous matched listening pairs.
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
npm test
```

Tests cover spectral/stereo cancellation behavior, real FFmpeg measurements, silent input and intervals, exact excerpts, preservation, alignment rejection, overload visibility, loudness matching, reconstruction differences, calibration conditions, offline preflight, uncapped requests and incomplete provider responses. Real provider and browser results are recorded separately in the validation study.

Renderer tests cover successful synthesis, fresh-profile samples, missing sounds, invalid source, remote-dependency failure, timeout cleanup and output preservation. Three reference-parity tests use ignored local media and explicitly skip when that corpus has not been restored. The current suite has 16 tests, including module assembly and an event-trace check for sustained notes, global four-cycle phase, cropped offsets and unchanged dry audio; all 16 passed on this restored workspace.

Project workflow tests cover exact master excerpts with existing tails, context bounds, changed-file detection, matched revision copies, tempo mismatch, silent comparison failures, stem partition checks and failed batch receipts.
