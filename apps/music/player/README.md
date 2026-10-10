# Sound player

Local player for synchronized audio parts. **Undercurrent** has seven unchanged foundation/detail tracks and two alternative chord rows: **steady rhythm** (enabled initially) and **original rhythm** (disabled initially). Haze, Smoke and Wire remain preserved in the prior study bundle.

**On/off** includes or removes a sound without restarting playback. **Only** temporarily isolates exactly one row; pressing it again returns to the prior mix, including previous off switches. Choosing another Only replaces the selection. Turning a sound on/off exits Only. Chord alternatives share a group: turning either on turns the other off. **Reset mix** restores the initial arrangement. Transport supports play/pause, restart, seeking, loop and volume.

Feedback belongs in the conversation. The notes UI and endpoint are removed; historical feedback remains preserved in `exports/player-v001/feedback.jsonl`.

## Running

Terminal Manager service `music-player`, repository `/Users/olof/git/ai-video-experiments`, runs:

```sh
uv run --locked python player/server.py --bundle projects/undercurrent/exports/player-v002
```

It binds only to loopback at Terminal Manager's assigned `PORT`. Current verified URL: http://localhost:3046/. It is intentionally left running for Olof; stop through Terminal Manager when no longer needed. No paid service is involved. The service expects a version-2 manifest with flat `tracks` entries containing id, name, enabled, URL, hash and waveform. Optional `alternativeGroup` prevents doubling alternative takes. Prior palette bundles remain archives; [publish_flow.py](../projects/undercurrent/publish_flow.py) creates this version from the preserved original and new chord render.

## Shared control

The open browser owns audio and sends actual state about three times per second. The assistant can inspect it with `GET /api/state`, and send JSON to `POST /api/control`:

| Action | Fields | Effect |
| --- | --- | --- |
| `only` | `track: "chords-flow"` (or null) | Isolate exactly one part, or return to the mix |
| `enabled` | `track`, boolean `value` | Set a part on/off; exit isolation |
| `play`, `pause`, `reset` | none | Transport or initial mix |
| `seek` | seconds in `value` | Move the shared playhead |
| `volume` | 0–1 in `value` | Master volume |
| `loop` | boolean `value` | Loop setting |

Other IDs: `chords-original`, `kick`, `bass`, `clap`, `hat`, `openhat`, `brush`, `air`. Read the manifest/state for current IDs instead of assuming them for another song.

A control response returns `queued`, not a claim of success. Wait for `last_applied_command` to reach that sequence and inspect `state.error` plus the actual tracks/playback state. `connected: false` means the state is stale; do not present it as current. A browser must be open, and its first playback may require a human or UI click to satisfy browser audio policy. No secret or model API is involved.

`POST /api/connect` and `/api/sync` are the browser's session protocol. The latest loaded tab owns shared control; an old tab is told to reload. This avoids commands being applied by multiple tabs. Acknowledged commands leave the queue. Reload resets the listening setup; persistent mix sessions are not implemented.

## Design and verification

[User stories, design direction and Harness commands](design/README.md) own UI intent and before/after evidence. Harness modules are installed from pinned source with hashes; project-specific adapters remain outside managed files. All audio sources start on one AudioContext clock; mute, Only and alternative switching change gains without rescheduling.

37 Python tests, six player-engine tests and Ruff pass. Desktop/mobile browser checks verify nine rows, no palette/notes controls, exclusive Only, return to saved mix, chord alternatives, playback, and the real shared-control acknowledgement/state loop. Geometry/captures show no horizontal overflow at 1100 and 390 px. Musical taste is pending Olof's review.

```sh
uv run --locked pytest -q
uv run --locked ruff check .
npm run test:player
npm run design:validate
npm run design:review
```
