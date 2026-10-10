# Practical beat and sampling dogfood

2026-10-10. Test a realistic composition workflow, local sampling, shared reverb, nonzero export starts and one controlled revision. The music is tooling test material, not a finished song or a human-approved mix.

## Material and reproduction

- 120 BPM, eight layers: TR-909 kick/clap/closed and open hats, synth bass, synth chords, speech slices and slices of an existing music render.
- Imported `references/assets/samples/` through Strudel **sounds → import-sounds → import sounds folder**. The UI registered `testvoice (1)` and `testloop (1)`; console confirmed writing them to the browser database. No sample-hosting server was needed.
- Voice: local macOS Daniel text-to-speech, 135 words/minute, text “Move with the rhythm. Bring it back.” Original AIFF retained. FFmpeg converted it to stereo 48 kHz WAV. This is a generic generated voice fixture, not a singer, cloned voice or commercial song sample.
- Music: first two seconds of our preserved `../tooling-validation/renders/tooling-v002-full.wav`, extracted with the music CLI. Both inputs, hashes and original voice are preserved under ignored `references/assets/`.
- Strudel `slice(8, ...)` reorders selected eighths; rests omit slices; `speed(-1)` reverses selected music-sample playback. The isolated sample stem is non-silent in the planned sections. `renders/voice-chops-preview.wav` extracts four seconds of voice-only chops from the stem.
- `source/v001-full.strudel` owns the baseline. Drum, music and sample variants mute other groups with `_$:`. `v002-full` halves hi-hat gain from .11 to .055. `v003-dry-full` disables room sends to investigate repeatability.
- Every full/stem export used cycles **2–16**, 48 kHz, stereo (Multi Channel Orbits off): **28 seconds, 1,344,000 frames**. Each source was read back before evaluation. A second export of an unchanged source received a distinct filename.

If reconstructing the workflow in a new browser profile, import the retained sample folder before evaluating the saved source. Browser storage is a convenience, not the canonical copy. Export settings reset when leaving and reopening the export panel in the tested app; recheck them.

## Findings

**Practical exporting and sampling worked.** All eight complete exports and the voice excerpt are retained; every full export has the expected length/rate/channels. v001 peaks at −2.08 dBFS / −2.08 dBTP, v002 at −2.17 dBFS / −2.16 dBTP; neither reaches full scale. v002 integrated loudness is −15.22 LUFS. No mastering target was imposed.

**Shared reverb prevents exact reconstruction in this test.** Separately rendered drum/music/sample groups sum with a −51.51 dBFS RMS residual, 32.62 dB below the full mix RMS. Repeating the unchanged full source gives a similar −51.32 dBFS RMS residual. Disabling reverb reduces repeated-render residual to −133.17 dBFS RMS, with a one-PCM16-step peak. This strongly implicates the reverb path in render variation for this fixture; the exact engine mechanism was not diagnosed. Do not interpret the wet residual as a missing stem or automatically fix it by alignment/normalization. Preserve the wet master; use dry controls when a precise difference test matters.

**The revision workflow was exercised.** v002 changes only hi-hat gain. Both complete mixes were inspected, and `match` saved comparison copies at −15.22 LUFS under `../../outputs/practical-matched-v001/` (v001 attenuation −0.01 dB, v002 unchanged). Independent reverb renders also vary, so their waveform difference cannot be attributed solely to the hats. No human preference between the versions has been recorded.

**Focused AI listening remains approximate.** Gemini via OpenRouter recognized speech-like sounds and a percussion dropout/return, but reported the main gap at approximately 11–14 seconds. Source and drum-stem measurements place the event gap at 8–12 seconds, with reverb decaying below −80 dBFS from 8.73125 seconds. Vocal source events occur at 4–8 and 12–20 seconds, with tails; the model claimed broader/later ranges. Its proposed intelligible words overlap the original TTS text, but actual chopped-word intelligibility has not been independently judged. Near-silence on all channels begins at 24.7745 seconds in v002; the model's claim of synths continuing to 28 seconds is unsupported. Full response and usage are in `../../work/practical-review-v002/`; reported cost $0.015716, completed normally. The spectrogram was visually inspected and confirms the major energy changes.

## What sampling supports

Existing WAV/MP3/OGG clips can be imported and then triggered, trimmed, sliced, reordered, reversed and played at different speeds. This test exercised local WAV import, slicing and reverse playback with speech and music. It did not test full commercial songs, automatic beat/key detection, vocal extraction, independent pitch/time stretching, sample search or recording a microphone. Speed changes can change pitch as well as duration. Vocal extraction from a mixed song would need a separate source-separation tool; it is not necessary when we start with a voice recording, generated phrase or isolated vocal clip.

## Programmatic Strudel route

The initial study used the official UI. The follow-up [programmatic renderer](../../docs/renderer-validation.md) is now implemented and validated. The published `@strudel/web` and `@strudel/webaudio` **1.3.0** packages were inspected from the npm registry on this date. `@strudel/web` documents `initStrudel`, `evaluate`, sample loading and playback. `@strudel/webaudio` exports:

```js
renderPatternAudio(pattern, cps, begin, end, sampleRate, maxPolyphony, multiChannelOrbits, downloadName)
```

It creates an `OfflineAudioContext`, schedules pattern events and generates a WAV browser download. It uses DOM/browser APIs and does not return WAV bytes directly. Thus it offers a route around editor/menu automation, not an established HTTP service or proven pure-Node renderer. Its event scheduling catches and logs individual sound errors, so a future wrapper must capture those errors and reject partial renders. The npm build and live website may differ; do not assume parity.

The follow-up implements that browser-backed renderer with explicit local samples and saved WAV/provenance. It required a patch to match the website's chunked scheduling; unpatched npm output does not match this practical dry reference. See the linked validation for measured parity and limitations. The packages declare AGPL-3.0-or-later; preserve their license requirements in any integration.

Sources: [Strudel samples](https://strudel.cc/learn/samples/), [integration guide](https://strudel.cc/technical-manual/project-start/), [package overview](https://strudel.cc/technical-manual/packages/), [published webaudio source](https://unpkg.com/@strudel/webaudio@1.3.0/webaudio.mjs), [web package README](https://unpkg.com/@strudel/web@1.3.0/README.md).

## Evidence and limits

`evidence.json` records source/media hashes, export parameters, measured results, reconstruction and repeat comparisons. All original renders and samples remain local/ignored. Code was unchanged in this study; validation was actual browser export, numerical measurements, visual spectrogram inspection and one real audio-model request. Codex did not personally hear playback. This initial study did not test longer arrangements or fresh-browser restoration. The linked renderer follow-up covers both. Automatic stem separation remains unimplemented.
