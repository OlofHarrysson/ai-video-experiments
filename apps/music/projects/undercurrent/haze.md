# Haze: chord-only comparison

Olof identified **Chord stabs & echoes** as the part he dislikes. Haze replaces its sample sound with a softer pitched-noise chord texture. This is a sound-design hypothesis; his taste verdict is pending.

Select **Current** and **Haze · new chords** in the [player](http://localhost:3046/) to compare. Solo **Chord stabs & echoes** to isolate the change. Haze is left selected, paused at the start, with all sounds enabled.

The original score, chord pitches, onset timing, arrangement and effect settings are unchanged. The other seven stem files and their playback levels are identical to Current. Only the new chord stem receives a constant energy-matching gain. There is no whole-mix renormalization. The new full mix measures −17.55 LUFS / −3.84 dBTP with no clipping, compared with Current at −17.61 LUFS. Both are 30 seconds, stereo, 48 kHz.

[Generator](make_haze.py), [sample provenance](references/haze.json), [publisher](publish_haze.py) and [comparison evidence](haze-evidence.json) preserve the experiment. The publisher checks the evaluated score hash, frame alignment and unchanged stem hashes before adding Haze to the existing player manifest. It preserves the old manifest as `manifest-before-haze.json`; existing feedback stays in place.

## Reproduce

From `apps/music`, with the original `exports/player-v001` bundle prepared:

```sh
uv run --locked python projects/undercurrent/make_haze.py
uv run --locked python music.py render projects/undercurrent/assemblies/v002/source.strudel --end 16 --sample-rate 48000 --samples projects/undercurrent/references/assets/haze --solo theme --solo colour --solo held --solo resolve --solo reply --trace-events --out projects/undercurrent/renders/haze-chords --timeout 60
uv run --locked python projects/undercurrent/publish_haze.py
```

These scripts refuse to overwrite existing outputs; the commands describe initial creation. Restart Terminal Manager service `music-player` after publication so its asset allowlist includes the new audio. The full listening mix is `renders/haze-chords/haze.wav`.

Validation: 37 Python tests and Ruff pass. Live in-app browser checks loaded Haze, played its solo chord track, then restored all sounds and stopped at the start. No browser warnings or errors were reported. These checks verify preparation and playback controls, not personal listening or musical quality.
