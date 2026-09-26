# AI Filmhack: frenzy cut

A 25.6-second, high-energy Instagram Reel for [AI Filmhack](https://filmhack.ai/), built with [Remotion](https://www.remotion.dev/). It is the chaotic sibling of the [canvas promo](../../../canvas-animation/projects/filmhack-promo/README.md): same facts and brand, much faster cuts, pop-art collage, stickers, confetti and a synthesized hyper score. There is no AI generation, footage or third-party audio.

## Watch

- Film: `renders/filmhack-frenzy-v1.mp4` (1080×1920, 30 fps, H.264 + AAC, −14 LUFS)
- Cover for the profile grid: `renders/filmhack-frenzy-v1-cover.jpg`
- Studio: the `filmhack-frenzy` service of this repository in Devrun, or `npm run dev`

Renders, the soundtrack and downloaded fonts are local and ignored by Git.

## The film

Everything sits on a 150 BPM grid, which puts every beat on a whole frame at 30 fps: 12 frames per beat, 3 per sixteenth.

| Beats | Time | Scene |
| --- | --- | --- |
| 0–4 | 0–1.6 s | WARNING: / 48 HOURS / OF PURE / FILM CHAOS! stacks up like a ransom note, one word per beat, over a siren. |
| 4–8 | 1.6–3.2 s | STOP stutters three times, SCROLLING., then a yellow flip to START CREATING. under crossing caution tapes. |
| 8–12 | 3.2–4.8 s | Drop: LIGHTS! (spotlights), CAMERA! (viewfinder), ACTION! with the slate clapping on beat 10. |
| 12–16 | 4.8–6.4 s | The 48-hour clock starts; absurd prompts type, generate and get stamped RENDERED on every beat. |
| 16–20 | 6.4–8 s | WRITE! PROMPT! SHOOT! ANIMATE! VOICE! SCORE! CUT! RENDER!, one per eighth note. |
| 20–24 | 8–9.6 s | A hundred creators pop into a grid: 100 CREATORS, 30+ TEAMS. |
| 24–28 | 9.6–11.2 s | The frame splits into 4, then 9 panels (the SCORE! panel is an equalizer driven by the soundtrack), spins into the countdown, hits zero and switches off like a CRT. |
| 28–32 | 11.2–12.8 s | "…and then" types out, SUNDAY. lands, and a film leader counts 3-2-1. |
| 32–40 | 12.8–16 s | Drop two: YOUR FILM. ON THE BIG SCREEN!, the disco-ball moon from the prompts plays in a cinema, confetti cannons, a cheering crowd. |
| 40–52 | 16–20.8 s | Logo slam, then one card every two beats: NOV 12–15, FILMUNIVERSITÄT BABELSBERG, FREE. €0, ONLY 100 SPOTS! |
| 52–64 | 20.8–25.6 s | GET ON THE LIST!, the FILMHACK.AI button pulsing with the kick, LINK IN BIO, a final hit and a glitch back into the loop. |

Full-screen colour changes happen at most once per beat (2.5 per second), under the three-flashes-per-second guideline for photosensitive viewers. Key text stays inside the Reel-safe band.

## The score

`src/audio/` is a separate program written with [Tone.js](https://tonejs.github.io/), rendered offline in headless Chrome by `scripts/score.mjs` and mastered with ffmpeg to −14 LUFS and −1.5 dBTP. It is an E major I–V–vi–IV track: breakbeat under the montage, four-on-the-floor with a bouncing "donk" bass for the premiere, a chiptune hook, and a siren, air horns, laser zaps, a coin chime, a spring boing, camera shutters, typing, pops and granular crowd applause, all synthesized. The kit queues every trigger and plays the queue in time order, because Tone.js sources reject out-of-order starts. One seeded generator makes the render reproducible.

The mix was balanced by measurement for phone speakers: octave-band balance, sub content, stereo width and loudness over time. The assistant cannot listen to audio, so it still needs a human playback check.

## Rebuild

From this directory:

```sh
npm ci
npm run assets   # fonts → public/fonts (MangoGrotesque from filmhack.ai, Geist Mono and DSEG7 via jsDelivr)
npm run score    # Tone.js score → public/soundtrack.wav, about a minute
npm run dev      # Remotion Studio (the port comes from $PORT under Devrun, else 3000)
npm run render   # renders/filmhack-frenzy-v1.mp4, about 40 s
npm run lint     # ESLint with Remotion's rules, then tsc
```

Render single frames for a quick look with `npx remotion render FilmhackFrenzy renders/frames --frames=0,120,400 --image-format=png`. Render revisions to a new file name so earlier versions stay intact.

## Code map

- `src/timing.ts`: the beat grid and scene windows, shared by picture and score.
- `src/FilmhackFrenzy.tsx`: the `<TransitionSeries>` of scenes, glitch overlays on the cuts, and the `<Audio>` track.
- `src/Root.tsx`: the main composition plus every scene registered as a connected composition in the `Frenzy-Scenes` folder, so each has its own Studio timeline.
- `src/scenes/`: one file per row of the table above.
- `src/components/`: slams, punches and shake (`motion.tsx`); tapes, stickers, confetti, rays and halftone (`decor.tsx`); the countdown, clapperboard and icons.
- `src/audio/`: `kit.ts` (instruments and effects), `score.ts` (arrangement), `seed.ts`, `wav.ts`, `entry.ts`.

Fixed copy is written inline in `Interactive.Div` elements, so text, colours and sizes can be edited in the Studio. Beat-synced motion is computed and stays in code.

## Status

v1 is rendered and screened by the assistant: frames across every scene, the decoded MP4 at 2 fps, loudness and spectral balance. It is awaiting Olof's playback feedback.
