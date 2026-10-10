# Sound player design

## User stories

1. When a sound disrupts the groove, I can turn that part off and back on while the music keeps playing, so I can judge its contribution in context.
2. When I cannot identify a sound, I can hear only that instrument. Choosing another instrument replaces the isolated selection; pressing the same Only button again returns to my previous mix.
3. When we revise a musical idea, I can switch between separate original and revised chord rows at the same playhead position, so I can compare the change directly.

4. When I ask the assistant to focus on a sound, it can read the actual player state and change the same controls I see, so we can discuss the same listening setup.

## Player intent

The working player is the reference; preserve its track overview and synchronized transport. This is a detail refinement, not a new editor architecture. The page contains the title, transport, timeline, named sound rows and Reset mix. Remove the palette selector, notes, instructional paragraphs and track subtitles. Original and revised chords are adjacent alternatives; switching one on turns the other off. Reset restores the revised mix. Feedback happens in the conversation.

Use neutral charcoal surfaces, warm white text and a restrained amber accent for playback, waveforms and active Only selection. Sound on/off is a switch, visually separate from the exclusive Only button. A muted row has a dim waveform; its controls remain readable. Only temporarily overrides the mix's on/off settings, preserving them when released. Toggling a sound while isolated returns to the mix and applies that toggle.

Keep track names and controls aligned. Desktop has a single row per sound; narrow viewports put the waveform below its controls. Preserve visible keyboard focus, sufficient text contrast and no horizontal overflow. Taste acceptance belongs to Olof; the current proposal is pending review.

## Design Harness

Installed workflow, capture, geometry and review modules live in `../../tools/design-harness`. Follow the [workflow](../../tools/design-harness/modules/workflow/README.md). Consumer-owned adapter: `validate.mjs`. Registry ID: `music-player` in [Design Harness](https://github.com/OlofHarrysson/design-harness); source maintenance guidance lives in its `docs/maintenance.md`.

With the Terminal Manager music-player service running, from `apps/music`:

```sh
npm run design:before
npm run design:validate
npm run design:review
```

`PLAYER_URL` overrides the local endpoint. The adapter uses the existing playwright-core dependency and installed Chrome, closes its own browser and does not control the shared service. Capture before editing. Review desktop/mobile original PNGs and the generated comparison; reports are evidence, not automatic visual approval. Evidence is ignored under `player/design/evidence/` and the generated fragment is `player/design/review.html`. The review has full page context and a chord-row detail crop at matched viewports. The snapshots do not follow later changes. Browser validation temporarily owns the shared control session; reload the human-facing player after validation.
