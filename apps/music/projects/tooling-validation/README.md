# Music tooling validation

2026-10-10. The goal is a usable, evidence-based compose → export → inspect → revise workflow. Musical quality is deliberately outside this study's acceptance criteria.

## What ran

- Four anonymous 20-second Window Seat variants received the same neutral broad review prompt, without source code, filenames or condition labels. Complete responses were read before the local answer key.
- A follow-up prompt asked only for a timeline and provided the measured duration, without giving the expected silence interval. The same prompt went to the dropout and original clips.
- Two eight-second Strudel fixtures were evaluated and exported through the actual browser UI. For each, a full mix and two stems used identical cycle/rate settings. Muting used `_$:`; each changed source was evaluated before export.
- Existing `mix` reconstructed each mix. New `compare` measured the residual without alignment, gain fitting or normalization. `inspect` measured the injected dropout and the v002 tail.

## Audio-review results

Model: `google/gemini-3.1-pro-preview`, high reasoning, actual PCM16 WAV input through OpenRouter. Catalog and full responses are preserved in each private review directory. This session's Codex did not personally hear the WAVs.

| Input / request directory under `work/` | Observation from model response | Assessment | Reported cost |
|---|---|---|---|
| Silence / `calibration-review-01` | Recognized complete silence; claimed the end was 17 seconds | Silence detected; duration incorrect (file is 20 seconds) | $0.010028 |
| 450 Hz low-pass / `calibration-review-02` | Described muffled melody but also piercing high-frequency percussion | Mixed and insufficient evidence of detecting the filter; do not trust its EQ recommendation | $0.027524 |
| Original / `calibration-review-03` | Described a repeating groove; gave 9/18/21-second section claims and asserted no swing or velocity variation | Timing unreliable; source contains swing and velocity changes, though their perceptual salience is not established | $0.030752 |
| Dropout at 8–10 s / `calibration-review-04` | Missed silence; invented an entry at 7 s and end at 15 s | Failed the conspicuous dropout check | $0.071588 |
| Dropout, focused / `timeline-review-dropout-01` | No response within the 180-second read timeout | Provider outcome/cost unknown; preserved, not counted as a completed review | Unknown |
| Dropout, focused retry / `timeline-review-dropout-02` | Sound stops at 8 s and resumes at 10 s | Correct for this clip; retry used a 600-second timeout | $0.010622 |
| Original, focused / `timeline-review-original-01` | Sound throughout; no complete silence | Correct control result | $0.011090 |

Six completed requests report **$0.161604** in total, plus the unresolved cost of the timed-out attempt. A successful retry does not explain the timeout. The first four receipts retain the previous reservation metadata as historical evidence; the current adapter has no budget or attempt gate.

The focused pair supports asking a narrow question. It does not isolate why the earlier answer failed: the prompt, known duration, stochastic response and possible provider behavior differ. One success per condition does not establish reliability. Broad musical critique, instrument identification and taste remain unvalidated.

Local checks: the original has no ≥0.1-second interval below −80 dBFS on all channels. The dropout is exactly **8.000–10.000 seconds**. Welch spectral power above 1 kHz was about 2.20% for the original and 0.0000000335% after filtering (4096-sample windows, channel powers summed). This supports the filter's effect, not a subjective listening judgment.

The focused prompt is saved at `../../docs/timeline-review-prompt.txt`; it explicitly states 20 seconds and must be edited for other durations. Private reviews and raw results are under `../../work/`.

## Stem reconstruction results

Both fixtures use 120 BPM, cycles 0–4, 48000 Hz, Multi Channel Orbits off. Each WAV has 384000 frames and two channels. Browser exports are PCM16; the local summing tool writes float WAVs. The prior browser source matched the preserved `references/strudel/beats/window-seat-live/12-tail.strudel` exactly before replacement.

| Fixture | What it exercises | Reconstruction |
|---|---|---|
| `v001` | Two dry, non-overlapping synth voices | Exact sample equality; zero residual |
| `v002` | Overlapping bass/chords, rightward panning, independent delay and a final bar without new notes | Residual RMS −96.44 dBFS; peak −84.29 dBFS; residual 57.61 dB below reference RMS |

The v002 peak residual is two PCM16 quantization steps, consistent with independently quantized exports and summing precision; this is an interpretation of the measured residual, not an engine-level diagnosis. Timing was not adjusted. v002 falls below −80 dBFS continuously from 6.8555 s to the 8 s endpoint, providing tail room for this fixture.

Source versions are in `source/`; original and reconstructed WAVs are in ignored `renders/`. `evidence.json` records hashes and settings. Analysis and residual WAVs are in `../../outputs/stem-comparison-v001/`, `stem-comparison-v002/`, and `fixture-v002-inspection/`. The dropout spectrogram was visually inspected and clearly shows the 8–10 s gap. Browser settings screenshot: `../../outputs/tooling-validation-strudel.png`.

Sample-based drums, random patterns, shared reverb, nonzero start cycles, long exports and full song arrangements were not tested by this stem check.

## Tooling changes and verification

- Removed the dollar budget, price ceiling and attempt cap; retained actual provider cost receipts and append-only history.
- Added `review --prompt-file` and explicit complete/incomplete/transport-error outcomes. Truncated or empty text is not a successful review. No automatic retries.
- Added measured silence intervals to `inspect` and sample-difference evidence to `compare`.
- Regression tests include a fifth uncapped API request, incomplete responses with preserved costs, one-channel versus both-channel silence and a one-sample timing mismatch. Browser exports and real API observations are separate integration evidence.
- Final checks from `apps/music`: `uv run --locked pytest -q` — 13 passed; `uv run --locked ruff check .` — passed; `git diff --check` — passed.

Continue by testing sample-based stems/shared reverb/nonzero start cycles, then one deliberate musical revision through matched playback. Keep the scope on tooling. Friction record: AF-20261010-085156 in the central agent-friction log; the later focused-prompt success is recorded here without rewriting the initial failed evidence.
