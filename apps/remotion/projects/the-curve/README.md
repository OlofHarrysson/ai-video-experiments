# The Curve

A silent, 45-second film about the AI race: so many labs, so many new models, so many data centres, all on a curve that keeps getting steeper. It is built in TypeScript with [Remotion](https://www.remotion.dev/) and Three.js (through `@remotion/three`), drawn entirely in code, and timed to a 120 BPM grid so music can be laid under it later.

**The idea in one sentence:** we ride an exponential that keeps turning into a wall, and every time the chart refits, the wall we just climbed drops into the flat floor of a bigger one.

## Watch

- Film: `renders/the-curve-v004.mp4` (1920×1080, 30 fps, H.264, no audio). v001–v003 are earlier passes, kept for comparison.
- Look check: `renders/look-v1/look-check.png`
- Studio: `npm run dev`

Renders are local and ignored by Git.

## The film

Olof chose the story, the captions-plus-closing-line text plan and 16:9 on 2026-10-16. He then made the race the theme ("so many data centres being built, so many new models… this big race") rather than what AI can do. The "IT CAN …" captions became NEW MODEL tags and headline fragments. He approved the look from the four style frames and asked for the motion to be built.

| Time | Beat | What happens |
| --- | --- | --- |
| 0–6 s | Stillness | A lone figure in a long coat, seen from behind, stands on an endless dot-grid chart at night. A spark leaves their feet and draws a line toward the dawn on the horizon. Years tick past: 2016, 2018, 2020. |
| 6–12 s | The race starts | The camera arcs over the figure and rides with the spark. Rival lines sweep in from the dark, one colour per lab. Each launch pops a ring and a NEW MODEL tag, and leaves a bead on its line. Ticks run 2021–2025. |
| 12–18 s | The build-out | Data centres rise beside and ahead of the pack: a glowing wireframe, then the shell, then rows of server lights and a red roof beacon. The curve bends up, the ticks turn into months, and more labs join. |
| 18–24 s | The wall | The pack goes vertical and climbs together as a twisting ribbon. Headline cards (NEW MODEL, BILLIONS, NEW DATA CENTER, GIGAWATTS, IS THIS AGI? …) burst around the climb, one a beat, then four. Ticks run through days, hours and minutes to NOW. The camera rolls and shakes, and the city glows below. |
| 24–25 s | Freeze | Everything stops mid-motion for one beat while the lens closes in a touch. This is where the music goes silent. |
| 25–33 s | The reveal | The loudest hit lands on 25.0. The camera rockets back to a side view, and the climb is a hockey-stick chart over a city of data centres. The chart refits to the head again and again, sooner each time (2 s, 1.5 s, 1 s … 0.1 s). Each refit drops yesterday's wall into the floor, until the curve is an L. |
| 33–45 s | The ending | A hard cut to the opening framing, changed: the same figure, now facing the whole race as a twisted column of light rising out of sight. The camera rises and pulls back to show thousands of people, heads tipped back, facing it. At 38 s: **THIS IS THE SLOWEST / IT WILL EVER BE.** Fade to black. |

### Sync points for music

The picture runs on 120 BPM at 30 fps, 15 frames to a beat, with bars at even seconds.

- 0.0 s: fade up from black, quiet
- 6.0 s: the race starts (the camera move begins at 5.0 s)
- 12.0 s: the build-out
- 18.0 s: the wall; launch density and cards keep accelerating to 24.0 s
- **24.0 s: freeze, silence**
- **25.0 s: the reveal, loudest hit**
- 27.0, 28.5, 29.5, 30.1, 30.5 s …: refits, closing up toward 31.0 s
- **33.0 s: hard cut to the ending**
- 38.0 s: closing line
- 43.8–45.0 s: fade to black

### On-screen text

All of it is deliberately generic: years, months, weekdays and clock times; NEW MODEL tags; and headline fragments with no company names, model names or figures. The closing line is an opinion, not a factual claim. There is nothing to cite.

## How it works

- **Chart space.** `src/race.ts` defines the curve `h(s) = 0.05 (e^(s/12) − 1)`, with `s` running along the ground away from the figure. A `Mapping` scales chart space into the world: time, height, ribbon width and a sideways offset. The ride uses the identity mapping. The reveal fits the mapping to the head, and the ending squeezes the whole race into a floor line and a column.
- **The race.** The leader's progress is integrated from a speed table, so it never jumps. The leader slows along the ground in the wall while its climb keeps accelerating, then takes off after the freeze. Each lab enters on the beat grid with its own gap and wobble. Gaps are measured along the line, so the pack stays together when the curve stands up. The ribbon twists as it climbs.
- **Launches.** `LAUNCHES` is a fixed, seeded schedule on sixteenth notes that speeds up from roughly one launch every few seconds per lab to several a second. Each launch leaves a bead, a ring and a NEW MODEL tag.
- **The camera.** `ride()` sits in the curve's own frame: behind, out along the normal and to one side. As the curve stands up, the chase becomes a climb without a cut. `src/reveal.ts` owns the pull-back and the refits, and `src/ending.ts` owns the final crane.
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
- `src/camera.ts`, `src/reveal.ts`, `src/ending.ts`: the three camera regimes.
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

## Status

The assistant screened v004 by frame samples across every beat and the transitions, and found no black frames or broken joins. It did not judge playback rhythm or pacing, and Olof has not yet watched it.
