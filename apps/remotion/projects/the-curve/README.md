# The Curve

A silent, 45-second film about the AI race: so many labs, so many new models, so many data centres, all on a curve that keeps getting steeper. It is built in TypeScript with [Remotion](https://www.remotion.dev/) and Three.js (through `@remotion/three`), drawn entirely in code, and timed to a 120 BPM grid so music can be laid under it later.

**Feeling:** small, overwhelmed and unable to look away: awe and dread at once. **Message:** nobody can keep up anymore, and this is the slowest it will ever be. One person stays on screen the whole time; the race happens to them.

## Watch

- Film: `renders/the-curve-v005.mp4` (1920×1080, 30 fps, H.264, no audio): the locked current cut. v001–v004 are earlier passes, kept for comparison.
- Look check: `renders/look-v1/look-check.png`
- Studio: `npm run dev`

Renders are local and ignored by Git.

## The film

Olof chose the story, the captions-plus-closing-line text plan and 16:9 on 2026-10-16. He then made the race the theme ("so many data centres being built, so many new models… this big race") rather than what AI can do, and the "IT CAN …" captions became NEW MODEL tags and headline fragments. After watching v004 he asked how it makes people feel and what the message is. The assistant judged v004 as mostly spectacle, because the person vanished for 27 of 45 seconds. Olof chose "can't keep up" as the feeling to leave people with. v005 retells the same race through the person.

| Time | Beat | What happens |
| --- | --- | --- |
| 0–6 s | Stillness | A lone figure in a long coat, seen from behind, stands on an endless dot-grid chart at night. A spark leaves their feet and draws a line toward the dawn. The first NEW MODEL tag pops at 5 s. |
| 6–12 s | It passes them | Rival labs streak in from behind and past them on both sides, converging on the horizon. Their head turns to follow each one: right, left, right. The camera comes in over their shoulder and starts to circle them. |
| 12–18 s | It surrounds them | Data centres taller than buildings rise all around. The person turns to look behind, then steps back. Notification cards pop into the air around them (NEW MODEL, IS THIS AGI?, BILLIONS …), one a second at first. |
| 18–24 s | Overwhelm | The race goes vertical into a tower of light far ahead, the labs' colours bleach toward white-hot, and the cards come about ten a second. The person looks up and steps back again. The camera's orbit becomes a dizzying spin that keeps them at its centre. |
| 24–25 s | Freeze | Everything stops: a low angle from behind as they look up at the tower, the storm frozen around them. This is where the music goes silent. |
| 25–33 s | Left behind | The loudest hit and a white flash land on 25.0, then the camera rockets back to a side view of the race as a chart. **YOU** marks the person at its start, **NOW** marks where we froze. Each refit drops yesterday's wall into the floor and slides NOW back toward YOU, while a bigger wall rises out of reach, sooner each time, until the curve is an L. |
| 33–45 s | Ending | A hard cut to the opening framing, changed: the same person, head tipped back, facing the whole race as a column of light. **NOBODY CAN KEEP UP.** The camera rises to show thousands of others, all in the same place. **THIS IS THE SLOWEST / IT WILL EVER BE.** Fade to black. |

### Sync points for music

The picture runs on 120 BPM at 30 fps, 15 frames to a beat, with bars at even seconds.

- 0.0 s: fade up from black, quiet
- 5.0 s: first NEW MODEL tag
- 6.0–12.0 s: rivals pass the person, one per beat-pair at first
- 12.0 s: data centres rise, the storm of cards begins
- 18.0 s: overwhelm; launch density, cards and the spin keep accelerating to 24.0 s
- **24.0 s: freeze, silence**
- **25.0 s: the reveal, loudest hit**
- 27.0, 28.5, 29.5, 30.1, 30.5 s …: refits, closing up toward 31.0 s
- **33.0 s: hard cut to the ending**
- 36.5 s: NOBODY CAN KEEP UP.
- 39.5 s: THIS IS THE SLOWEST IT WILL EVER BE.
- 43.8–45.0 s: fade to black

### On-screen text

All of it is deliberately generic: years, months, weekdays and clock times; NEW MODEL tags; and headline fragments with no company names, model names or figures. The closing line is an opinion, not a factual claim. There is nothing to cite.

## How it works

- **Chart space.** `src/race.ts` defines the curve `h(s) = 0.05 (e^(s/12) − 1)`, with `s` running along the ground away from the figure. A `Mapping` scales chart space into the world: time, height, ribbon width and a sideways offset. The ride uses the identity mapping. The reveal fits the mapping to the head, and the ending squeezes the whole race into a floor line and a column.
- **The race.** The leader's progress is integrated from a speed table, so it never jumps. The leader slows along the ground in the wall while its climb keeps accelerating, then takes off after the freeze. Each lab enters on the beat grid with its own gap and wobble. Gaps are measured along the line, so the pack stays together when the curve stands up. The ribbon twists as it climbs.
- **Launches.** `LAUNCHES` is a fixed, seeded schedule on sixteenth notes that speeds up from roughly one launch every few seconds per lab to several a second. Each launch leaves a bead, a ring and a NEW MODEL tag.
- **The person and the camera.** `src/person.ts` scripts the person's pose: head turns that follow each passing rival, a turn to look behind, two steps back, and a look up. The camera orbits the person on monotone splines, so its speed carries through each keyframe instead of stopping. Its aim never strays more than about a third of its distance from them, so they stay anchored while the world moves. `src/reveal.ts` owns the pull-back and the refits, and `src/ending.ts` owns the final crane.
- **Drawing.** Lines are camera-facing strips with a white core, a coloured halo and near-plane clipping (`world/glowLine.ts`). Points of light, rings and text are instanced billboards. The data centres are one instanced box shader, the floor is a dot-grid shader whose fog meets the sky colour exactly, and the figures are merged primitives with a rim-light shader. Bloom, AgX tone mapping, chromatic aberration and the vignette come from `postprocessing`. The composer is built synchronously, so the first captured frame is already bloomed.
- **Text.** Fonts load through `@remotion/google-fonts`: JetBrains Mono for ticks and tags, Anton for headlines and Inter for the closing line. The canvas mounts only after every string has been drawn into one atlas texture, so no frame renders without its text.
- **Determinism.** Everything is a function of the frame: seeded hashes, no `Math.random`, no wall clock. Per-frame updates run in layout effects, before Remotion's ThreeCanvas advances the frame.

## Rebuild

From this directory:

```sh
npm ci
npm run dev                          # Remotion Studio (port from $PORT, else 3000)
node scripts/stills.mjs 4.5 15.5 42  # stills at those seconds → renders/stills/, plus sheet.png
node scripts/render.mjs v002         # the film → renders/the-curve-v002.mp4
npm run lint                         # ESLint with Remotion's rules, then tsc
```

`scripts/label-sheet.py` makes a labelled contact sheet: `uv run --script scripts/label-sheet.py OUT.png "Title" img.png:"1 Label" …`.

## Code map

- `src/timing.ts`: frame rate, beat grid, story beats and the world clock that holds through the freeze.
- `src/race.ts`: the curve, the mapping, the leader, the labs, the lanes, the ticks.
- `src/content.ts`: launches, tags, ticks and headline cards placed in the world.
- `src/person.ts`: the person's performance and the camera that circles them (0–25 s).
- `src/camera.ts`: the shot type. `src/reveal.ts` and `src/ending.ts` own the other two camera regimes.
- `src/World.tsx`: assembles the race world (0–33 s) and the ending world (33–45 s).
- `src/world/`: line, glow, label, ground, sky, data centre, figure, crowd and post-processing components.
- `src/text/`: fonts and the text atlas. `src/headlines.ts`: the headline fragments.
- `src/overlay/EndLine.tsx`: the closing line.
- `scripts/`: stills, render, labelled sheet.

## Versions

- **v001:** first full motion render. Screening found black frames before the cut: the reveal's take-off overflowed 32-bit floats in the floor shader, and the NaN spread through bloom.
- **v002:** NaN fixed. The past stays colourful and the future draws white. A NOW drop line follows "now" into the floor. The ribbon stays face-on in the climb and twists only into the column.
- **v003:** the ending column is tightened into a rope, and a single white flash lands on the 25.0 s hit.
- **v004:** the data centres became visible. They now rise 7–25 units from the race, 2.5–5.5 s ahead of the pack, with brighter facades, a pop when each comes online and campus light pollution. The climb camera aims below the pack, so the race rises out of a lit city.
- **v005:** retold through one person, for "can't keep up". The person is on screen throughout, with a posable head and body that turns, steps back and looks up. Rivals now come from behind and pass them, data centres are building-sized and rise around them, a storm of notification cards gathers, and the colours drain to white. The camera orbits them on splines and ends in a spin. YOU joins NOW in the reveal, and the closing words become "Nobody can keep up." / "This is the slowest it will ever be."

## Status

**v005 is the locked current cut.** Olof watched it on 2026-10-17 and said "it lands". The assistant's screening covered frame samples across every beat and transition; playback rhythm is Olof's verdict. The film is silent; music is still to be laid on the sync points above.
