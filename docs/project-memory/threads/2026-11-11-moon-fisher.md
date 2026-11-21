---
thread_id: import:claudeAgent:0daedaa9-baab-4935-85c0-e6dad8222b72
title: Animated film planning and production
provider: claudeAgent
model: claude-opus-5-5
created: 2026-09-29T08:35:21.207Z
settled: 2026-11-11T03:06:12.657Z
link: "[Animated film planning and production](t3-thread://v2/071bdbdb-bba7-4e87-b692-3de2e92037b2/import:claudeAgent:0daedaa9-baab-4935-85c0-e6dad8222b72)"
---

## Outcome

Planned and roughed out "The Moon Fisher", a wordless 9:16 code-drawn pixel-art
Remotion film: an old fisherman hooks the moon's reflection, pulls the moon into
his boat, then lets it go; his cat gets a fish. It reached animatic v006 (about
58.5 s) over a sampled-instrument score, with two asset upgrade passes done. Work
ran 2026-09-29 to 10-01; the sound-effects pass was proposed but not started.

## Decisions

- Premise: The Moon Fisher over Snail Mail and other pitches. Calm folk-tale tone,
  no dialogue, the moon has no face.
- Pixel density A (180×320, chunky) over the recommended B. Olof then asked for
  connected limbs and more drawn detail, which became the style.
- Everything is functions recomputed per frame (a pixel engine in `src/pixel/`,
  assets in `src/world/`), with an 11-bone rig for the fisherman.
- Score written as data and played by sampled instruments through Tone.js. v001 was
  too sleepy; v002 is a third faster with piano, violin and clarinet and no
  glockenspiel; v003 removed a false ending and was locked. A held bar for the
  hooking pause made it v004.
- Story rule, from Olof's question: whatever happens to the reflection happens to
  the moon. The float hangs straight down and the moon drifts into the hook while
  he sleeps.
- Dither dissolves don't suit pixel art: palette fades through black only where
  time passes, hard cuts elsewhere. The film ends on the cat with its fish under a
  closing iris.

## Changes

`apps/remotion/projects/moon-fisher/`: b2545bc (brief and pitches) through
8bbbb4b (upgrade pass 2, animatic v006), including style frame f4b4064, rig
5e84996, score lock 7fe0b76, storyboards a9edc24/a0b9b14/1892890, asset register
0faed97 and animatics b62b334–ea5fb59.

## Open ends

- Sound effects: 13 storyboard cues. Choose between synthesizing in code (free,
  artificial-sounding) and free recorded effects with a no-attribution licence.
- Known limits in the asset register: the cat's pounce tips its sitting body
  instead of a true crouch, and its tail is stiff.

## Working preferences

- Olof wants to understand how things are built (engine, assets, music) as part of
  the work; explain the mechanics when he asks.
- He describes sounds in his own words; name the instruments for him.
