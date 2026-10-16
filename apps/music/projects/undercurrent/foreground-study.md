# Foreground sound study

2026-10-16. Olof asked for a new musical example and a local inspection harness after finding the sounds basic and the chord idea weak. This study tests two 15-second foreground ideas over the existing foundation. Human preference is pending.

## Listen

[Open the shared player](http://localhost:3046/), bundle `exports/player-v005`. **Theme · evolving pulse** is initially enabled. Turn on **Theme · hollow hook** or **Chords · previous** to replace it at the same playhead position. Only isolates one part. Earlier 30-second rhythm comparisons remain in `player-v003`; the first foreground candidates remain in `player-v004`.

- **Evolving pulse:** overlapping low harmonic pulses, changing decay and brightness, a restrained fifth, and a retreat after the middle swell. Final source is [pulse-v002.strudel](source/pulse-v002.strudel).
- **Hollow hook:** a short F/E-flat/C phrase with inharmonic attacks settling into a tonal body, related calls and lower answers. Source is [hollow-v001.strudel](source/hollow-v001.strudel).

Both use original procedural samples from [make_foreground.py](make_foreground.py), synthesized at four times the output rate and reduced to 48 kHz PCM24. [Sample provenance](references/foreground-v001.json) records hashes. No reference recording is incorporated.

The seven shared drum, bass and detail parts use the first 15 seconds of the prior bundle. Samples are unchanged through 14.98 seconds; every track has the same final 20 ms fade to avoid an abrupt cutoff. [Publisher](publish_foreground.py) and [evidence](foreground-evidence.json) record source/output hashes and foreground gains. This is a foreground comparison, not a redesigned full arrangement.

## What inspection changed

[Foreground report](exports/foreground-lab-v002/report.md) compares actual isolated stems. Its shared-scale spectrogram shows the previous chord bursts, the pulse's more continuous harmonics and middle brightness increase, and the hollow hook's separated attacks and pitch changes. Momentary loudness confirms the pulse's gradual swell and retreat. These establish differences, not musical superiority.

[Mix/reference report](exports/mix-lab-v002/report.md) includes the club phone reference, offset one second. Plots retain original levels; matched listening copies attenuate the louder phone recording. Phone processing, PA and room sound remain confounds, so its frequency balance is not a studio mastering target.

| Final mix | Integrated LUFS | True peak dBTP |
| --- | ---: | ---: |
| Evolving pulse | −17.47 | −3.73 |
| Hollow hook | −17.45 | −3.14 |
| Previous chords | −17.52 | −3.93 |

All are 15 seconds, 48 kHz stereo, with no full-scale overload. Their average loudness differs by at most 0.07 LUFS. Low overall stereo width is measurable; these results do not establish club impact or preferred timbre.

One shuffled, matched audio-model review used the initial pulse-v001, previous chords and hollow-v001. `google/gemini-4-argon` was verified in the current catalog and called with high reasoning; completed cost was $0.022872. Receipts and answer key are local under `../../work/foreground-20261016/`. The model identified broad sustained-versus-plucked differences and flagged the pulse's middle brightness. Some descriptions overstated static pitch/timbre, so they were treated as hypotheses. Pulse-v002 modestly reduces the middle gain and upper frequencies; final plots/levels were checked, but that revision received no second model review. No personal-hearing claim or taste approval is implied.

## Harness and player checks

[Sound Lab](../../docs/sound-lab.md) adds reusable section recipes, shared-scale spectrograms, RMS/sample-peak timelines, 400 ms LUFS, waveform close-ups, peak-safe matched mixes and saved provenance. [Foreground recipe](foreground-lab.json) and [mix recipe](mix-lab.json) reproduce these inspections into fresh output folders.

Live player testing exposed `OSError: [Errno 55] No buffer space available` while sending large audio files in one write. The server now sends 64 KiB chunks; an 8 MiB transfer test verifies complete bytes and length. Desktop/mobile checks passed after the change, covering loading, all ten rows, alternative switching, exclusive Only, playback/seek and acknowledged shared controls. The adapter now reads comparison IDs from the manifest. 39 Python tests, six player-engine tests and Ruff pass. The renderer is unchanged.

The Terminal Manager service is intentionally running at port 3046 with player-v005. Reconnecting the user's in-app tab was unavailable because no tab was exposed and the Mac was locked; headless product checks passed. Open/reload the player to establish a fresh shared browser session.

## Reproduce

From `apps/music`, with the preserved sample folder present:

```sh
uv run --locked python music.py render projects/undercurrent/source/pulse-v002.strudel --end 8 --sample-rate 48000 --samples projects/undercurrent/references/assets/foreground-v001 --trace-events --out NEW_PULSE_RENDER --timeout 90
uv run --locked python music.py render projects/undercurrent/source/hollow-v001.strudel --end 8 --sample-rate 48000 --samples projects/undercurrent/references/assets/foreground-v001 --trace-events --out NEW_HOLLOW_RENDER --timeout 90
uv run --locked python sound_lab.py projects/undercurrent/foreground-lab.json --out NEW_FOREGROUND_REPORT
uv run --locked python sound_lab.py projects/undercurrent/mix-lab.json --out NEW_MIX_REPORT
```

`make_foreground.py` creates its versioned sample folder only when absent. `publish_foreground.py` uses preserved renders and refuses an existing output bundle; select a new version constant for a new publication. Media/reports stay local and ignored; generators, sources, recipes and evidence are tracked.
