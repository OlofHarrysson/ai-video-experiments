# Chord rhythm revision

Olof clarified that the original chord instrument was acceptable; its rhythm and echoes disturbed the song's flow. Haze made it worse. This comparison restores the original instrument and changes only the chord part's rhythm, velocities and echo settings.

**Chords · steady rhythm** plays on beats two and four throughout the active bars. Main echoes fall one beat later at lower level and feedback. Busy phrase-end chord replies are removed. The original harmonic sections, held breakdown chord and final resolving chord remain. The seven other audio parts are copied without changes, with the original global playback gain.

**Chords · original rhythm** is the old player stem. Both are rows in the [player](http://localhost:3046/), with steady rhythm on initially. Turning one on turns the other off. Only isolates one row without changing the saved mix. The difference is a hypothesis for Olof to judge, not an assistant listening verdict.

## Evidence and reproduction

[Evidence](flow-evidence.json) verifies unchanged source lines for non-chord parts, original sample hashes, exactly 28 rhythmic chord onsets at quarter/three-quarter cycles (beats two/four), no reply onsets, and identical hashes for the seven reused audio tracks. Revised mix: **−17.64 LUFS, −3.57 dBTP**, 30 seconds, 48 kHz stereo, no clipping. No global loudness correction was applied; the original player mix is −17.61 LUFS.

From `apps/music`:

```sh
uv run --locked python music.py render projects/undercurrent/source/flow-v002.strudel --end 16 --sample-rate 48000 --samples projects/undercurrent/references/assets/samples --solo theme --solo colour --solo held --solo resolve --solo reply --trace-events --out projects/undercurrent/renders/flow-v002-chords --timeout 60
uv run --locked python projects/undercurrent/publish_flow.py
```

Outputs refuse overwriting. `exports/player-v002` is the new flat-track player bundle; `player-v001` and all original palettes remain preserved. Full listening mix: `renders/flow-v002-chords/flow.wav`. The first `flow-v001` attempt retained the old middle-section rhythm; source inspection caught this before publication. Its source/render remain preserved, and v002's exported event audit verifies the correction.
