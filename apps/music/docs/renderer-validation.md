# Programmatic renderer validation

2026-10-10. The accepted sprint was to replace repetitive Strudel editor/export clicks with one local command accepting saved source, explicit samples and a cycle range. It saves WAV/source/provenance and closes its temporary browser/server. Music remains test material.

## Implemented path

`uv run --locked python music.py render SOURCE --out NEW_DIRECTORY --end CYCLE` invokes the Node renderer using pinned Strudel and Playwright packages. It uses installed Google Chrome, a fresh profile and a temporary loopback server serving only the engine and supplied sample files. No external HTTP dependencies are allowed during rendering. Repeat `--samples FOLDER` for local libraries. The [README](../README.md#rendering-and-revision) has the practical beat command.

`render.json` records exact source/sample/output hashes, source copy, sample index ordering, requested assets, npm lock/bundle/renderer hashes, browser and Node versions, tempo, cycle range, rate, frames and logs. Tempo is read from the evaluated source. WAV output is PCM16 stereo. Source code is trusted JavaScript, not a sandboxed upload format.

All inputs are read without modification. Output directories must be new. Engine errors—including Strudel sound errors reported through ordinary logs—fail the run. If a WAV was downloaded before an error was detected, it remains `incomplete.wav`. Invalid code and timeouts leave failed receipts. Startup/configuration failures before output creation may leave no receipt. Browser/server cleanup runs in `finally`; no persistent music service remains.

## The practical parity test found an upstream difference

The unpatched npm 1.3.0 exporter schedules the whole piece before calling `startRendering`. The live website's exporter interleaves one-cycle scheduling and offline rendering. Synth-only tests did not expose this difference.

For the 28-second practical dry beat, the unpatched renderer differed from the saved website export by **−30.55 dBFS RMS**, with a **−6.92 dBFS peak residual**, concentrated in sampled sections. Querying the whole range or each cycle separately produced exactly the same multiset of **272 events**. A diagnostic change to the scheduling/render interleaving reduced the residual to approximately −133 dBFS RMS. This establishes the scheduling fix for this recipe; the deeper audio-graph state mechanism was not isolated.

The production integration carries that change as a [checksum-verified patch](../patches/README.md). A fresh `npm ci` successfully installed and applied it. Runtime refuses any other bundle checksum. The final practical dry render has **−132.40 dBFS RMS residual**, with a maximum difference of **one PCM16 step**. No gain adjustment or alignment was applied. All original exports, failed probes and comparisons remain preserved locally.

## Acceptance evidence

| Check | Result |
| --- | --- |
| Dry synth versus website | Byte-identical initial render; exact sample parity regression passes |
| Overlap, panning and delay | One PCM16 step maximum difference; initial comparison −149.16 dBFS RMS |
| Practical dry beat, cycles 2–16 | 28 s / 48 kHz / stereo; one-step maximum, −132.40 dBFS RMS residual |
| Practical wet beat, cycles 2–16 | 28 s / 48 kHz / stereo; −50.97 dBFS RMS residual versus website, comparable to prior unchanged wet rerender variation |
| Longer wet arrangement, cycles 0–64 | 128 s / 6,144,000 frames / 48 kHz / stereo; six local sample assets loaded, no engine errors |
| Long-render inspection | −2.14 dBFS sample peak, −2.13 dBTP, −15.23 LUFS, no full-scale samples; waveform/spectrogram shows the planned repeating sections and rests |
| Fresh-profile local sample test | Audible sliced/reversed generated WAV, byte-identical repeated exports |
| Missing sound / invalid code / remote dependency | Failed explicitly; no successful WAV published |
| Nonterminating source | Timed out; browser/server closed and failed receipt preserved |
| Existing output | Rejected without changing saved WAV |
| Verification | 13 Python tests and 9 renderer tests passed, none skipped here; Ruff and fresh npm install passed; npm audit zero vulnerabilities |

Machine-readable evidence: [renderer-evidence.json](../projects/tooling-validation/renderer-evidence.json). Final playable short output: `outputs/renderer-v002-practical-wet/render.wav`; long output: `outputs/renderer-v002-long/render.wav`. Raw receipts, audio and plots are ignored/local. The restored drum source URLs/hashes are in [drum-sources.json](../projects/practical-dogfood/drum-sources.json).

## Scope and remaining limits

- Three golden-reference tests require the preserved local WAV/sample corpus. They explicitly skip on a fresh clone without it; six synthetic integration tests require no retained media. A green run with skips does not establish website parity.
- Browser versions are recorded, not frozen. Chrome/engine updates can change samples; rerun the references before accepting a new baseline.
- No personal listening verdict or new audio-model review was used in this sprint. Measurements establish technical behavior for these fixtures, not musical taste.
- Shared reverb and random patterns may vary across renders. Preserve wet masters; use controlled dry tests for precise comparisons.
- Samples are explicit local files. The website's complete drum/instrument libraries are not automatically installed; only four TR-909 index-zero drum files used by this recipe were restored. No source separation, microphone recording or automatic key/beat analysis is included.
- Cycles before `--begin` are not rendered as preroll, and effect tails after `--end` are truncated. Put appropriate rests inside the export window. Named UI controls, external integrations and visual-only Strudel extensions are outside this renderer's validated scope.
- Supported decoding beyond WAV, much longer/heavier sessions and all possible Strudel patterns remain untested. The 128-second result is one repeated arrangement, not an exhaustive stress test.
