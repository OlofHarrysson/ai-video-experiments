# Offbeat chord comparison

Olof approved the dark player on 2026-10-12 and asked to improve the chord rhythm using it to compare with the current version. **Chords · offbeat pocket** is the new take; **Chords · steady rhythm** is the previous version. The older original remains available too.

## Musical change

The steady take plays on beats two and four every active bar, reinforcing the clap. The new two-bar phrase places an anchor on **the “and” after beat one** each bar, with an answer on **the “and” after beat three** in alternate bars. Rhythmic echoes are removed. This reduces rhythmic chord attacks from 28 to 22 across the excerpt, with a recurring rest in the second bar. The hypothesis is a less insistent chord part that supports the groove while giving the backbeat space.

The original samples, note velocities, filtering, harmonic sections, held breakdown and final resolution remain. The held and resolving chord effects remain; only the rhythmic layers lose their delay. Rendered reverb can vary, so unchanged held/resolve source is not a claim of sample-identical wet audio. The seven other audio parts and both earlier chord stems are copied byte-for-byte, verified against their hashes. No overall gain adjustment is applied.

## Compare in the player

[Open the player](http://localhost:3046/) and play the full mix. Switch **Off** beside **Chords · steady rhythm** to hear the prior version; turn **Chords · offbeat pocket** back on to return. Each selection disables the other chord alternatives, retaining the playback position. Only can isolate a chord take, but judge its effect on flow in the full mix.

Start with the first 7.5 seconds: the new pattern repeats twice there. Compare whether the chords feel like part of the drum/bass groove or still interrupt it. The one-bar break at 20.625 seconds and return at 22.5 seconds retain their positions.

## Verification and preservation

The [source](source/pocket-v001.strudel), [publisher](publish_pocket.py) and [evidence](pocket-evidence.json) preserve the experiment. The actual renderer trace verifies all 22 expected offbeat onsets and zero rhythmic delay. The 30-second stereo mix is 48 kHz, −17.65 LUFS / −3.93 dBTP, versus −17.64 LUFS for steady rhythm; there is no sample overload. The final 20 ms peaks at −78.27 dBFS. Source assertions verify unchanged non-rhythmic lines and sample-bank hashes.

These are technical checks, not an assistant listening verdict. Browser playback is not available as heard audio to Codex. No audio-model preference was used, given its recorded unreliable subtle comparisons. Olof's preference remains pending.

Reproduce from `apps/music` into fresh output directories (the saved paths already exist):

```sh
uv run --locked python music.py render projects/undercurrent/source/pocket-v001.strudel --end 16 --sample-rate 48000 --samples projects/undercurrent/references/assets/samples --solo theme --solo colour --solo held --solo resolve --solo reply --trace-events --out projects/undercurrent/renders/pocket-v001-chords --timeout 60
uv run --locked python projects/undercurrent/publish_pocket.py
```

`exports/player-v003` contains the ten player tracks. Earlier bundles remain intact. `renders/pocket-v001-chords/pocket.wav` is the full listening mix. Media and captures are local/ignored; Git preserves source and evidence, not the audio files. The browser check now reads the manifest's row count and exercises every chord alternative, so another take does not require hardcoding a new count.

Validation: 37 Python tests, six player-engine tests and Ruff pass. Desktop/mobile browser checks pass with all ten rows and three mutually exclusive chord takes. The human-facing shared API acknowledged isolation of the new take and switching between new/steady at the same 7.5-second playhead. It was left paused at the start with offbeat pocket selected.
