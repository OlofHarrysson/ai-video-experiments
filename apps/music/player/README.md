# Sound player

Local listening UI for aligned audio parts. Current study: **Undercurrent — Current, Smoke, Wire and Haze**, with eight independently mutable sounds per palette.

Use **Mute** to remove a part, **Solo** to isolate one or several, and **All sounds** to reset. Playback, pause, restart, seek, looping, volume and palette changes share one playhead. A palette change pauses while its files load, then resumes at the same position with the same mute/solo selection. Feedback saves the note, palette, position and selected parts to the study's ignored bundle directory; the assistant can read these notes in later turns.

## Running

Use Terminal Manager's `music-player` service for repository `/Users/olof/git/ai-video-experiments`. It runs:

```sh
uv run --locked python player/server.py --bundle projects/undercurrent/exports/player-v001
```

The server uses Terminal Manager's assigned `PORT`, binds only to loopback, serves an explicit asset list, and appends local feedback at `projects/undercurrent/exports/player-v001/feedback.jsonl`. Check Terminal Manager for the current URL; at handoff it is `http://localhost:3046/`. The service is intentionally left running for Olof's review. Stop it through Terminal Manager when no longer needed. No remote service or API billing is involved.

To prepare a fresh bundle from the preserved source/sample palettes:

```sh
uv run --locked python projects/undercurrent/prepare_player.py projects/undercurrent --out NEW_BUNDLE
```

The preparation belongs to this composition: it declares the eight musical roles and preserves the score. Completed bundles refuse overwriting. Interrupted preparation can resume only already-completed renders with matching source, sample manifests and solo labels; a failed render remains an explicit error. Original masters and samples stay untouched. The player itself consumes the resulting `manifest.json` and aligned WAVs.

Haze is a chord-only alternative to Current, added by the project-specific [Haze workflow](../projects/undercurrent/haze.md). It reuses the other seven files and the same global playback gain. Preparing the original three-palette bundle does not automatically add Haze.

## Synchronization and evidence

Each part is a separate full-length render including its effect tails. All buffers start at the same AudioContext time and offset; mute/solo changes gain without rescheduling. A seek creates a fresh synchronized set of sources. Short gain ramps reduce clicks; existing mix levels are retained when soloing, with a common loudness adjustment per palette. [Web Audio scheduling reference](https://developer.mozilla.org/en-US/docs/Web/API/AudioBufferSourceNode/start).

All parts are stereo, 48 kHz, 1,440,000 frames. Kick and bass files are shared across palettes. Recombination measures −17.61/−17.59/−17.61 LUFS before matching. Wet rerender differences from the original masters measure roughly −52 to −54 dBFS RMS; these are closely matching stem mixes, not byte-identical original masters. [Audio evidence](../projects/undercurrent/player-evidence.json).

Validation: 37 Python tests, Ruff and 5 player-engine tests pass. Tests cover shared scheduling, mute/solo without restarting, pause/seek, cancellation of pending play, loop position and seeking to the end. The HTTP test verifies saved feedback context, invalid input rejection and the asset allowlist. Live in-app browser checks covered playback, mute, solo, palette switching, loop wrap, end seeking, reset and note persistence; the synthetic verification note was removed from the user feedback file. No browser warnings/errors were reported at final inspection. This verifies controls and signal preparation, not personal hearing or musical taste.

```sh
uv run --locked pytest -q
uv run --locked ruff check .
npm run test:player
```
