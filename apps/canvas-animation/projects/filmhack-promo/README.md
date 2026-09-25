# AI Filmhack promo

A 30-second vertical Reel that promotes [AI Filmhack](https://filmhack.ai/) (Nov 12–15, 2026, Filmuniversität Babelsberg) on Instagram. Everything is drawn and synthesized in JavaScript: no AI generation, footage, photos or third-party music.

## Watch

- Film: `renders/filmhack-reel-v1.mp4` (1080×1920, 30 fps, H.264 + AAC, −14 LUFS)
- Cover for the profile grid: `renders/filmhack-reel-v1-cover.jpg`
- Mastered soundtrack: `renders/filmhack-reel-v1.wav`

Renders are local and ignored by Git; rebuild them with the commands below.

## The film

The concept is "You've watched enough": the Reel interrupts the scroll, hands the viewer the slate, starts the 48-hour clock and builds one short film from script to cinema screen before landing the facts and the call to action. The visual language comes from filmhack.ai: black, red `#C80528` and cyan `#00D2E6`, MangoGrotesque italic headlines, Geist Mono labels, the DSEG7 countdown, the slate panel and the RGB-split glitch.

| Beats | Time | What happens |
| --- | --- | --- |
| 0–8 | 0–3.75 s | Two generic Reels flick past and slam to a stop on black. YOU'VE / WATCHED / ENOUGH. hits one word per beat. |
| 8–12 | 3.75–5.6 s | The site's slate rises and claps on the drop: DIRECTOR: YOU. NOW MAKE ONE. |
| 12–16 | 5.6–7.5 s | The countdown appears at 48:00:00 and ticks once per beat: 48 HOURS. ONE FILM. |
| 16–36 | 7.5–16.9 s | The clock races through the weekend while one film is made: WRITE IT (script), SEE IT (diffusion-style denoise), MOVE IT (camera push, rain), HEAR IT (live waveform and meters), CUT IT (timeline). |
| 36–44 | 16.9–20.6 s | SCREEN IT: a projector lights the film in a cinema and the crowd cheers. |
| 44–56 | 20.6–26.3 s | Logo slam, "Europe's first hybrid AI × film challenge", then the date, venue, free entry and 100-spot chips. |
| 56–64 | 26.3–30 s | GET ON THE LIST, filmhack.ai, link in bio; the last frames glitch back into the loop. |

Text stays inside the Reel-safe band (y 250–1450) and works with the sound off. The cover frame also survives the 3:4 profile-grid crop. Reels loop, so the final glitch hands straight back to the opening flick.

## The score

An original 128 BPM track in D minor, so the 30 seconds are exactly 16 bars and every cut lands on the grid. It uses an i–VI–III–VII progression, a four-on-the-floor kick with side-chained bass and pads, a ping-pong-delayed arpeggio, and supersaw stabs on each stage change. A drone-and-riser build leads into the drop, and the premiere lifts to an open pad. Sound effects are synthesized too: the slate clap, clock beeps and ticks, typewriter keys, denoise blips, timeline snaps, projector flutter at 24 fps, granular applause, glitches, impacts and a trailer braam on the logo and final hit.

The mix was balanced by measurement for phone speakers: octave-band balance, stereo correlation and loudness over time. It is mastered to −14 LUFS integrated with −1.5 dBTP of headroom for Instagram's re-encode. The assistant cannot listen to audio, so the sound needs a human playback check.

## Rebuild

From this directory:

```sh
npm ci
npm run assets    # downloads the MangoGrotesque display face from filmhack.ai into assets/
npm run dev       # preview at http://localhost:5190: play, scrub, chapter jumps, safe-zone overlay
npm run stills    # key moments and a contact sheet → renders/stills/
npm run render    # film, mastered WAV and cover → renders/filmhack-reel-v1.*
node scripts/render.mjs --audio   # soundtrack only, for mix iteration
```

A full render takes about four minutes on the production Mac. Pass `--out renders/filmhack-reel-v2.mp4` for a revision so earlier versions stay intact.

## Code map

- `src/config.ts`: canvas size, beat grid, brand colours and the scene windows.
- `src/film.ts`: sequencing, and the shared hits (shake, RGB split, slice glitch, flash) that land with the score's accents.
- `src/scenes/`: one file per section of the table above.
- `src/draw/`: the slate, countdown panel, rooftop film, generic Reel cards, text effects and post-processing (grain, glitch, vignette).
- `src/audio/`: `studio.ts` holds the synthesizers and effects, `score.ts` the arrangement, `wav.ts` the export.
- `scripts/render.mjs`: serves the page with Vite, drives headless Chrome frame by frame, pipes raw frames to ffmpeg and loudness-normalizes the soundtrack.

## Provenance

MangoGrotesque is the event site's self-hosted display font; it is downloaded locally and not redistributed. Geist, Geist Mono and DSEG7 come from the `geist` and `dseg` npm packages (SIL Open Font License). Event facts come from filmhack.ai as of 2026-09-25, when applications were not yet open, which is why the call to action is "Get on the list". Change the CTA copy once applications open.

## Status

v1 is rendered and screened by the assistant: stills across every section, the decoded MP4 at one frame per second, loudness and spectral balance. It is awaiting Olof's playback feedback.
