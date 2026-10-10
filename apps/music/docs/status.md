# Music workbench — handoff

Updated 2026-10-10. Work in `apps/music`; the brainstorm workspace is historical.

## Current goal

Build an actual audio reference library and test the comparison workflow. Olof found Chrome After Rain still too much like a computer game, supplied DJ_Dave's YouTube channel and requested her popular work as audio references. The [DJ_Dave reference study](../projects/dj-dave-reference-study/README.md) owns this work. More specific taste direction will come later; no further full song is queued. Olof manages the OpenRouter balance: no assistant-imposed dollar budget, price ceiling or attempt cap. Keep actual usage records.

## Completed and checked

- **Five full DJ_Dave audio references downloaded and preserved.** A complete 79-upload channel inventory supports selection of Cycles, Castles, Airglow, Array and Easy as its most-viewed 2–6-minute song uploads. Original Opus streams, float WAV decodes, provenance and matched excerpts are available through the [reference library](../projects/dj-dave-reference-study/README.md). These are local reference recordings, not sample assets incorporated into our music.
- All five reference excerpts and our comparison excerpt match −18.07 LUFS within 0.01 LUFS, without clipping. An undisclosed identical-audio comparison passed: the reviewer correctly reported no audible differences. Actual reference/candidate comparisons are now possible; this does not establish expert taste judgment.
- Six reference-study audio reviews completed, reporting $0.141966. [Findings](../projects/dj-dave-reference-study/findings.md) distinguish model-described articulation/foreground differences from measured stereo similarity and unverified processing claims. No new composition, generation service or renderer change was added. Full downloads, decoded audio and excerpt hashes were verified.

- **Original composition exported: [Chrome After Rain](../projects/chrome-after-rain/README.md), v004.** Professional interview research and three collaborating agents informed a 136 BPM, 1:56 instrumental with nine original synthesized samples, a two-bar hook, suspended breakdown and half-time switch. Master and five named stems completed; the playback copy is `projects/chrome-after-rain/renders/v004/chrome-after-rain.wav` (−16.99 LUFS, −1.17 dBTP, no clipping). Source, recipe, palette generator and [evidence](../projects/chrome-after-rain/evidence.json) are tracked; media remains local/ignored.
- Four short hook/mix sketches, an initial full-length draft and two master/stem arrangement renders are preserved. Five composition-sprint audio-model reviews completed, reporting $0.130118. Reviews informed mix balance and phrase spacing but included incorrect rhythm/part descriptions; Olof subsequently found the piece too game-like. All 19 Python tests and Ruff passed; renderer code is unchanged. Panning was verified by hard-left/right controls. `duckorbit` failed in a scratch test with an uncreated target orbit, so this composition uses interlocking kick/bass timing.

- **Project workflow dogfood completed.** A saved recipe now renders and inspects the master plus named stems from one source. Master-derived section previews retain preceding effects exactly; labelled A/B copies use the existing loudness matcher. [Study and commands](../projects/workflow-dogfood/README.md), [evidence](../projects/workflow-dogfood/evidence.json).
- Three 68-second arrangements (baseline, delayed drum/bass return, quieter hats) produced 12 successful renders with aligned frames/rates. No master clipping. Two section previews match master samples exactly; two A/B pairs were verified within 0.01 LUFS. The isolated hats interval fell 5.53 dB, consistent with the intended gain change.
- Current verification: 19 Python tests and 11 renderer tests pass (none skipped here), plus Ruff. GitHub sample importing remains deferred at Olof's request. No new paid reviews or human listening verdict were used in this sprint.

- **Programmatic renderer implemented and verified.** `music.py render` evaluates trusted Strudel source in fresh headless Chrome, loads explicit local samples and saves stereo WAV/source/provenance. It closes its temporary server/browser after success, failure or timeout. No UI export clicks required.
- Pinned npm 1.3.0 needed a scheduling fix: whole-piece scheduling differed from the saved practical dry export by −30.55 dBFS RMS. A checksum-verified patch using the website's chunked scheduling reduced the residual to −132.40 dBFS RMS, with a one-PCM16-step peak. Dry synths match exactly; overlap/delay passes the one-step bound. A 128-second wet render completed without engine errors. [Renderer evidence](renderer-validation.md).
- Earlier renderer checkpoint: 13 Python tests, 9 renderer integration/parity tests (none skipped on this machine), Ruff and fresh `npm ci` pass; npm audit reports zero vulnerabilities. Three parity tests require the ignored reference corpus on new clones.

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

Latest: [DJ_Dave audio reference study](../projects/dj-dave-reference-study/README.md). [Chrome After Rain](../projects/chrome-after-rain/README.md) is the preserved original-composition comparison. The [saved-project workflow study](../projects/workflow-dogfood/README.md) records the previous tooling sprint. The [programmatic renderer validation](renderer-validation.md) records the engine scheduling fix and parity evidence. The earlier [practical beat study](../projects/practical-dogfood/README.md) covers browser sampling and listening. Local import, slicing and reversing work; vocal extraction from a finished song is not implemented.

## Next work

1. Use the downloaded reference corpus and matched comparisons to inform a short sound/groove experiment. Treat sustained versus plucked articulation, foreground performance and spatial texture as testable production choices. Do not infer that vocals are mandatory or that these five tracks are Olof's individually approved favorites.
2. Keep using saved project recipes, master-derived previews and explicit local sample folders. Add further tooling only for concrete friction encountered during composition.
3. GitHub importing, vocal extraction, automatic beat/key detection and sample discovery remain deferred. Keep model listening questions specific and confirm objective claims locally.

Do not resume paused video studies.
