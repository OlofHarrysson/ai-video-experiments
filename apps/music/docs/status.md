# Music tooling — handoff

Updated 2026-10-10. Work in `apps/music`; the brainstorm workspace is historical.

## Current goal

Improve and dogfood the music tooling. Simple compositions are authorized as test fixtures; producing an impressive first song is not the goal. Olof manages the OpenRouter balance: no assistant-imposed dollar budget, price ceiling or attempt cap. Keep actual usage records.

## Completed and checked

- Dedicated locked uv workspace, CLI, private credential file and preserved Strudel/DJ_Dave research. The original migration verified all 68 copied files by SHA-256; see `migration.json`.
- OpenRouter key works. Seven audio reviews completed with Gemini 3.1 Pro Preview, high reasoning. Reported costs total **$0.177320**; one additional timed-out request has unknown cost. No automatic retries or model fallback.
- Initial four anonymous calibration clips were reviewed before reading the answer key. Broad critique recognized silence but missed the known 8–10 second dropout, misreported durations, and gave questionable high-frequency descriptions of a heavily filtered clip.
- A focused timeline prompt located the dropout at 8–10 seconds and reported no silence in the original. This is narrow positive evidence, not validation of musical taste, mix judgment or general timing accuracy.
- Browser exported two full mixes and four isolated stems, all 8 seconds / 48 kHz / stereo. Dry stems sum exactly. Overlapping synths, panning and independent delay sum with a −96.44 dBFS RMS residual (peak −84.29 dBFS, two 16-bit quantization steps). No automatic alignment or gain correction.
- `inspect` now measures near-silent intervals and finds the injected dropout exactly. `compare` saves sample-difference evidence and a residual WAV. `review --prompt-file` accepts focused questions. Incomplete replies raise an error and remain preserved; transport failures record an unknown provider outcome.
- Verification: 13 tests pass, Ruff passes from `apps/music`, and `git diff --check` passes. Tests include preserved historical ledger records, uncapped requests, incomplete responses and a timeout without automatic retry.
- Practical dogfood added a 28-second beat with sampled drums, synths, shared reverb, local speech/music slicing, a breakdown and a quieter-hi-hat revision. Eight browser renders verified cycles 2–16 / 48 kHz / stereo. Local sample-folder import worked without a hosting server.
- Shared reverb renders vary: wet stem reconstruction and unchanged full rerenders have about −51 dBFS RMS residual. Dry repeated renders differ by only −133.17 dBFS RMS. Exact wet reconstruction is not an appropriate invariant for this recipe. Preserve the wet master and use dry controls for precise difference checks.
- The practical audio review recognized voice and drum dropout/return but misplaced transitions by several seconds. The simple calibration success does not establish accurate timing on fuller music.
- Original sketches, fixtures, stems, reconstructed WAVs, analyses and provider receipts are preserved. Strudel was left stopped with practical beat v002. No local server or cloud compute is running for music.

Read the [validation study](../projects/tooling-validation/README.md), [machine-readable evidence](../projects/tooling-validation/evidence.json) and [listening protocol](listening.md). Raw audio and provider receipts remain local/ignored.

Latest: [practical beat, sampling and API investigation](../projects/practical-dogfood/README.md), with [evidence](../projects/practical-dogfood/evidence.json). Local import, slicing and reversing work; vocal extraction from a finished song is not implemented.

## Next tooling work

1. Align on a small browser-backed programmatic renderer before implementation. Published `@strudel/web` / `@strudel/webaudio` 1.3.0 expose evaluation and `renderPatternAudio`, which uses OfflineAudioContext and downloads WAV through the DOM. This is a promising direct integration, not a working CLI/API in this repository. Verify parity with saved reference renders and capture partial-render errors.
2. Further practical checks: longer arrangements, local-sample restoration in a fresh profile and controlled A/B listening. The first full revision and matched comparison files exist; no human listening preference is recorded.
3. Improve listening only through specific questions with known controls and objective checks. Broad critique is exploratory; do not automatically edit music based on it.

A song brief and a polished composition remain deferred. Do not resume paused video studies.
