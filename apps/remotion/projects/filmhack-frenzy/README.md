# AI Filmhack: frenzy cut

A 25.6-second, high-energy Instagram Reel for [AI Filmhack](https://filmhack.ai/), built with [Remotion](https://www.remotion.dev/). It is the chaotic sibling of the [canvas promo](../../../canvas-animation/projects/filmhack-promo/README.md): same facts and brand, much faster cuts, pop-art collage, stickers, confetti and a synth-pop score synthesized in code. There is no AI generation, footage or third-party audio.

## Watch

- Film: `renders/filmhack-frenzy-v2.mp4` (1080×1920, 30 fps, H.264 + AAC, −14 LUFS), with the melodic v2 score
- Cover for the profile grid: `renders/filmhack-frenzy-v2-cover.jpg`
- First score: `renders/filmhack-frenzy-v1.mp4`, same picture
- Studio: the `filmhack-frenzy` service of this repository in Devrun, or `npm run dev`

Renders, the soundtrack and downloaded fonts are local and ignored by Git.

## The film

Everything sits on a 150 BPM grid, which puts every beat on a whole frame at 30 fps: 12 frames per beat, 3 per sixteenth.

| Beats | Time | Scene |
| --- | --- | --- |
| 0–4 | 0–1.6 s | WARNING: / 48 HOURS / OF PURE / FILM CHAOS! stacks up like a ransom note, one word per beat, each on a fanfare chord. |
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

`src/audio/` is a separate program written with [Tone.js](https://tonejs.github.io/), rendered offline in headless Chrome by `scripts/score.mjs` and mastered with ffmpeg to −14 LUFS and −1.5 dBTP. One seeded generator makes the render reproducible.

The v2 score is a synth-pop anthem in A major built around one tune. The hook has the rhythm of LIGHTS! CAM-er-a AC-TION!: a held note, a quick run up to the octave, then an answer that sighs back down.

- **Cold open:** the run plays as a fanfare over I–IV–V–I, one chord per slammed word.
- **Drop one** (I–V–vi–IV, rock backbeat): hook and answer, twice.
- **Chaos:** brass stabs climb a step on each new panel over an E pedal, and the tape stops when the clock hits zero.
- **SUNDAY.:** lands on a flat-six chord. The film leader counts 3-2-1 up the flat seven into drop two: the ♭VI–♭VII–I arrival cadence of film and game scores. Under it, the bass rises E–F–G and lands an octave down on A.
- **Drop two** (four-on-the-floor): reaches higher, climbs to its top note on GET ON THE LIST! and resolves to the tonic on the final hit, beat 62.

The lead is a detuned saw with a brassy filter attack and chorus, doubled by an FM bell in drop two. Behind it are saw brass stabs, a supersaw pad, off-beat plucks, an octave-bouncing saw bass with a sine sub, and noise-based drums with a gated room on the snare. The kick pumps the bed (bass, pad, plucks) but never the lead, bell or brass, so the tune stays on top. The effects are limited to:

- booms on the big hits
- pink-noise risers
- reverse-cymbal swells
- the tape stop
- a silent breath before each drop

Olof found the v1 score “quite annoying” without “a good melody”. It was an arpeggiated hook under a siren, air horns, zaps, coins, a boing, beeps, typing and a synthesized crowd, all removed.

The assistant cannot listen, so v2 was checked by measurement; Olof's playback is the verdict:

- **Tune:** the lead was pitch-tracked back to the written tune. Between 300 Hz and 4 kHz it sits about 5.5 dB above drums and bed.
- **Harshness:** against v1 at equal loudness, measured with [MOSQITO](https://github.com/Eomys/MoSQITo), sharpness (DIN 45692) drops from 1.59 to 1.33 acum. Roughness (Daniel & Weber) in drop one drops from 1.09 to 0.32 asper. Zwicker's psychoacoustic annoyance is 15–28% lower per section.

Two delays kept v1's sound late:

- **Mastering, 12 ms:** Chrome's compressor looks 6 ms ahead, and the master runs two. The score now renders 12 ms long and is trimmed.
- **Encoding, 43 ms:** Remotion's own AAC track kept the encoder's 2048-sample priming as audio. Together, the two delays put every hit 55 ms (1.6 frames) late. `scripts/render.mjs` now renders the picture muted, and ffmpeg muxes the master, signalling the priming in an edit list. The decoded v2 shows no measurable lag against the master.

## Rebuild

From this directory:

```sh
npm ci
npm run assets   # fonts → public/fonts (MangoGrotesque from filmhack.ai, Geist Mono and DSEG7 via jsDelivr)
npm run score    # Tone.js score → public/soundtrack.wav, about a minute
npm run dev      # Remotion Studio (the port comes from $PORT under Devrun, else 3000)
npm run render   # picture via Remotion, soundtrack muxed by ffmpeg → renders/filmhack-frenzy-v2.mp4, about 35 s
npm run lint     # ESLint with Remotion's rules, then tsc
```

Render single frames for a quick look with `npx remotion render FilmhackFrenzy renders/frames --frames=0,120,400 --image-format=png`. Render revisions to a new file name so earlier versions stay intact.

## Code map

- `src/timing.ts`: the beat grid and scene windows, shared by picture and score.
- `src/FilmhackFrenzy.tsx`: the `<TransitionSeries>` of scenes, glitch overlays on the cuts, and the `<Audio>` track.
- `src/Root.tsx`: the main composition plus every scene registered as a connected composition in the `Frenzy-Scenes` folder, so each has its own Studio timeline.
- `src/scenes/`: one file per row of the table above.
- `src/components/`: slams, punches and shake (`motion.tsx`); tapes, stickers, confetti, rays and halftone (`decor.tsx`); the countdown, clapperboard and icons.
- `src/audio/`: `kit.ts` (instruments, buses and effects), `score.ts` (tune, chords and arrangement), `seed.ts`, `wav.ts`, `entry.ts`.
- `scripts/`: `score.mjs` (score → mastered WAV), `render.mjs` (picture + mux), `fetch-assets.mjs` (fonts).

Fixed copy is written inline in `Interactive.Div` elements, so text, colours and sizes can be edited in the Studio. Beat-synced motion is computed and stays in code.

## Status

v2 has the new score. The assistant screened it by measurement: pitch tracking, band balance, loudness, psychoacoustic sharpness and roughness, and audio sync. Olof's playback verdict is pending. The picture is unchanged from v1.
