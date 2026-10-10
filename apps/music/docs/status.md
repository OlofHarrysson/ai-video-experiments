# Music tooling — handoff

Updated 2026-10-10. Work in `apps/music`; the brainstorm workspace is historical.

## Current goal

Improve and dogfood the music tooling. Simple compositions are authorized as test fixtures; producing an impressive first song is not the goal. Olof manages the OpenRouter balance: no assistant-imposed dollar budget, price ceiling or attempt cap. Keep actual usage records.

## Completed and checked

- Dedicated locked uv workspace, CLI, private credential file and preserved Strudel/DJ_Dave research. The original migration verified all 68 copied files by SHA-256; see `migration.json`.
- OpenRouter key works. Six audio reviews completed with Gemini 3.1 Pro Preview, high reasoning. Reported costs total **$0.161604**; one additional timed-out request has unknown cost. No automatic retries or model fallback.
- Initial four anonymous calibration clips were reviewed before reading the answer key. Broad critique recognized silence but missed the known 8–10 second dropout, misreported durations, and gave questionable high-frequency descriptions of a heavily filtered clip.
- A focused timeline prompt located the dropout at 8–10 seconds and reported no silence in the original. This is narrow positive evidence, not validation of musical taste, mix judgment or general timing accuracy.
- Browser exported two full mixes and four isolated stems, all 8 seconds / 48 kHz / stereo. Dry stems sum exactly. Overlapping synths, panning and independent delay sum with a −96.44 dBFS RMS residual (peak −84.29 dBFS, two 16-bit quantization steps). No automatic alignment or gain correction.
- `inspect` now measures near-silent intervals and finds the injected dropout exactly. `compare` saves sample-difference evidence and a residual WAV. `review --prompt-file` accepts focused questions. Incomplete replies raise an error and remain preserved; transport failures record an unknown provider outcome.
- Verification: 13 tests pass, Ruff passes from `apps/music`, and `git diff --check` passes. Tests include preserved historical ledger records, uncapped requests, incomplete responses and a timeout without automatic retry.
- Original sketches, fixtures, stems, reconstructed WAVs, analyses and provider receipts are preserved. Strudel was left stopped with the complete v002 fixture. No local server or cloud compute is running for music.

Read the [validation study](../projects/tooling-validation/README.md), [machine-readable evidence](../projects/tooling-validation/evidence.json) and [listening protocol](listening.md). Raw audio and provider receipts remain local/ignored.

## Next tooling work

1. Extend export checks to sample-based drums, shared reverb and nonzero cycle starts. Existing findings cover deterministic synths with independent delay only.
2. Exercise a real revision: change one layer, rerender, inspect that stem and compare matched full mixes. Preserve intent, source and playback together.
3. Improve listening only through specific questions with known controls and objective checks. Broad critique is exploratory; do not automatically edit music based on it.

A song brief and a polished composition remain deferred. Do not resume paused video studies.
