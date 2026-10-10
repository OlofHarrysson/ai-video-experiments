# Saved-project workflow dogfood

2026-10-10. Exercise project rendering, named stems, effect-preserving previews and revision comparisons on a structured arrangement. This is tooling material, not a selected song or human-approved mix. GitHub importing was explicitly deferred; all sample audio comes from the retained practical-study assets.

## Arrangement and revisions

The [recipe](project.json) owns the versioned sources, sample folders, stem membership, export length and sections. Nine source layers are grouped into drums, music and samples. Each version renders a master and all three stems from the same source, without separate hand-edited stem files.

120 BPM, 48 kHz stereo, 34 cycles / 68 seconds. The first 32 cycles form the arrangement; two additional silent cycles allow effects to decay.

| Section | Cycles | Seconds | Intent |
| --- | --- | --- | --- |
| Intro | 0–4 | 0–8 | Chords, then hats establish the pulse |
| Main | 4–12 | 8–24 | Kick/bass enter; clap, lead and speech accumulate |
| Breakdown | 12–16 | 24–32 | Rhythm drops away; sliced/reversed music and chords remain |
| Return | 16–28 | 32–56 | Rhythm and lead return, with another speech phrase |
| Ending | 28–32 | 56–64 | Percussion leaves; bass/chords finish |
| Tail window | 32–34 | 64–68 | No new source events |

- `v001`: baseline with a direct drum/bass return at 32 seconds.
- `v002`: arrangement revision. Kick, clap and bass return at 36 seconds, with the lead entering then too. Hats continue through the first four seconds of the return.
- `v003`: mix revision of v002. Only the hats gain changes, from .085 to .045.

Drum samples, the generic Daniel TTS phrase and the two-second synth sample are retained by the [practical study](../practical-dogfood/README.md). No new sample acquisition or voice generation was needed.

## Commands

From `apps/music`, with the locked Python/Node dependencies installed, choose a new output directory for each run:

```sh
uv run --locked python music.py render-project projects/workflow-dogfood/project.json --revision v001 --out outputs/replay-v001
uv run --locked python music.py render-project projects/workflow-dogfood/project.json --revision v002 --out outputs/replay-v002
uv run --locked python music.py preview outputs/replay-v001 --section breakdown --lead 2 --tail 2 --out outputs/replay-breakdown
uv run --locked python music.py compare-revisions outputs/replay-v001 outputs/replay-v002 --section return --lead 2 --tail 2 --out outputs/replay-arrangement-ab
```

Existing completed runs are `renders/v001`, `renders/v002` and `renders/v003`. Each has `master/render.wav`, three stem folders with WAV/inspection results, original/evaluated source, and a `project-render.json` receipt. The recipe snapshot records the original configuration; it is not a standalone bundle of every sample dependency.

## Acceptance evidence

All **12 renders completed**, each with **3,264,000 frames / 48 kHz / stereo**. Sources and samples were preserved. Stem/source membership must be a complete, non-overlapping partition; unknown or ambiguous labels fail. JavaScript parsing selects labels using Strudel's native mute syntax, leaving comments, strings and multiline expressions intact.

| Master | Integrated loudness | Sample peak | True peak | Full-scale samples |
| --- | ---: | ---: | ---: | ---: |
| v001 | −16.27 LUFS | −3.84 dBFS | −3.74 dBTP | 0 |
| v002 | −16.28 LUFS | −3.88 dBFS | −3.76 dBTP | 0 |
| v003 | −16.29 LUFS | −3.86 dBFS | −3.75 dBTP | 0 |

The baseline waveform/spectrogram was visually inspected and shows the planned sparse intro, dense main section, breakdown, return and ending. Low-pass drum energy below 180 Hz during 32–36 seconds fell from −19.95 to −72.01 dBFS RMS between v001/v002, consistent with the delayed kick return. During that same hats-only interval, v002/v003 drum RMS fell **5.53 dB**, versus the intended **5.52 dB** gain change. These are objective checks of the edits, not listening preferences.

Both previews are exact decoded-sample copies from the saved master:

- `../../outputs/workflow-v001-breakdown/preview.wav`: source 22–34 seconds, 576,000 frames, with two seconds of context on each side.
- `../../outputs/workflow-ending-preview/preview.wav`: v003 source 56–66 seconds, 480,000 frames, including two seconds after the ending.

Because previews use an existing master, earlier reverb/delay state and any random choices are preserved. Following context also includes following notes; it is not an isolated effect-tail render. Insufficient context is rejected explicitly.

Two labelled, matched A/B pairs are ready:

- [Arrangement comparison](../../outputs/workflow-arrangement-ab/README.md): v001/v002 master, source 30–58 seconds. A measures −16.30 LUFS; B −16.29 LUFS after matching.
- [Hi-hat comparison](../../outputs/workflow-mix-ab/README.md): v002/v003 drums over the same window. Both measure −16.23 LUFS. Their original measured loudness already matched, so no attenuation was needed.

Original excerpts, matched copies, hashes, revision labels, edit notes and gain values are preserved in those folders. The full record is [evidence.json](evidence.json); media remains local/ignored.

## Checks and limits

**19 Python tests and 11 renderer tests pass**, none skipped on this machine; Ruff and fresh `npm ci` pass. Tests cover exact excerpts, effect state at a boundary, bounds and hash checks, loudness matching, tempo mismatch, silent comparison failure, batch failure receipts, parsed layer selection and dry stem reconstruction. The dry stem test allows two PCM16 steps at overlapping release tails; shared wet effects are not expected to reconstruct exactly.

There was no new audio-model request or human listening verdict. Reverb varies between independent renders, so not every waveform difference belongs to the deliberate revision. These checks establish a usable render/inspect/preview/compare workflow. Choosing a preferred arrangement or mix remains a listening decision.
