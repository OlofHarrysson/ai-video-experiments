# The Moon Fisher

A calm short film in pixel art, with no dialogue, drawn in code with [Remotion](https://www.remotion.dev/). Working title. The film is in planning. This README records each agreed deliverable: the brief, style frame, sound decision, storyboard, asset register and animatic. Renders stay local and are ignored by Git.

*An old fisherman who can't catch anything hooks the moon's reflection and pulls the moon into his boat.*

## Brief

Approved by Olof on 2026-09-29, including the 60-second length and the faceless moon. The premise was chosen from [four pitches](pitches.md).

- **Length:** about 60 seconds. The music sets the exact length.
- **Format:** vertical 9:16, delivered at 1080×1920. The style frame fixes the pixel resolution and scale.
- **Platforms:** Instagram Reels, YouTube Shorts and Bluesky, and this notebook.
- **Audience:** general, all ages. There is no dialogue, so the film works in any language and with the sound off. The music makes it land with the sound on.
- **Tone:** calm, tender, a folk tale, gently funny through the cat. Stillness and a few strong poses rather than busy motion.
- **Ending:** gentle wonder, then a smile. The viewer should feel the rightness of giving back something that was never yours to keep, and enjoy the small gift that comes back.

### Story

1. **Setup, about 15 s.** Night on a still sea. A small boat, an old fisherman and his cat. The moon's reflection wobbles right beside his float, already visible in the first shot. Nothing bites. The cat stares into an empty bucket; the fisherman dozes off.
2. **Turn, about 25 s.** The line jerks. He hauls up the reflection, and it comes out of the water as the moon itself, dripping and flopping in the boat like a fish. The sky goes black and the sea goes flat. The only light left is the moon in his bucket, lighting his face from below. Then its glow starts to fade, like a fish out of water.
3. **Payoff, about 20 s.** He tips the bucket over the side. The light sinks and goes out, followed by a held beat of darkness. Then the sea brightens from below and the moon rises back into the sky. Silver light spreads across the water and fish leap through it. One lands in the boat, and the cat gets it. The last shot mirrors the first: the moon high, its reflection back beside the line, the fisherman smiling.

### Characters

- **The fisherman:** old, patient and kind. He acts through posture, head and hands, in a few clear poses.
- **The cat:** his companion and the audience's appetite. It wants a fish, eyes the moon as if it were one, and gets one at the end.
- **The moon:** alive but faceless. Its glow, its wobble and a fish-like flop show that it is alive.

### Visual principle

The moon is the only light. Whether it is in the sky, in the water or in the bucket decides how the sky, the sea and the faces are lit. The style frame tests this.

### Craft goals

- Story and rhythm matter more than the density of effects.
- Few assets, each brought to finished quality. Build with simple placeholders, cut the animatic, then upgrade the weakest assets one at a time.
- Draw mostly in code; SVG and raster images can be mixed in. No video clips.
- The music is melodic and restrained.

### Precedents

Hooking the moon out of the water is an old folk motif; in one version, Nasreddin Hodja tries to pull the moon out of a well. Pixar's *La Luna* also puts a small boat under the moon on a night sea. Its story is different, and the look should stay away from it.

## Style frame

The key image shows the moon in the bucket lighting the fisherman and the cat from below while the sky stands empty. v002 compared two pixel densities. Olof chose the coarser one on 2026-09-29 because it “looks less like simple shapes”. He found the limbs too detached from each other, asked for more detail, and liked the sea and the reflection. v003 answers that; his verdict on it is pending. `renders/style-frame/v003/` holds the still, a before/after sheet against v002 and a four-second loop of the ambient motion.

- **Pixel grid:** scenes are authored on a 270×480 design frame and drawn at 180×320, enlarged six times to 1080×1920. The finer 270×480 grid (four times) was the alternative; its smooth curves exposed the geometric shapes underneath.
- **Palette:** 24 colors in `src/pixel/palette.ts`. There are seven night blues for sky, sea and shadow, five moonlight colors from silver to the moon's cream, and twelve warm colors for the oilskins, wood, skin and the cat. Nothing is drawn outside it: glows brighten a pixel by climbing its own color family.
- **Light:** the moon is the only light. Every part of an object has a surface, so the scene can be relit from wherever the moon is. The light picks a step on each material's ramp of four to seven colors.
- **Forms:** a body, a limb chain or a head is grown as one piece with rounded joins, so it shades as a single surface instead of separate tubes and balls. A part in front shades what is behind it only on the side away from the moon.
- **Outlines and shading:** there are no black lines. A silhouette's edge is one step darker where it faces away from the light, and edges facing the light keep their color. Characters and props are shaded in clean bands, with stray single pixels removed.
- **Detail:** fur markings such as tabby stripes and the white chest take the same light as the form beneath them. Folds, seams, strands, rivets and grain shift the finished shade by a step, so they follow the light too.
- **Dithering:** only in the air and sky, with an ordered 4×4 pattern: the seams between sky colors, the Milky Way, the moon's halo and the light shaft.
- **Water:** still water mirrors whatever floats on it, one or two steps darker, broken into ripples about two world units tall.
- **Frame rate and cadence:** 24 fps. Poses and ambient motion hold for three frames, eight drawings a second; quick actions such as the haul hold for two. Everything moves in whole pixels, like the boat's one-pixel bob on a two-second swell.

Weak spots for the upgrade passes: the near-black hull, the broad back of the coat and the dark tin of the bucket.

## Skeleton and poses

The fisherman has a skeleton: spine, chest, head, both arms and legs. His style-frame drawing is the rest pose, and every part rides on one bone, so a pose is just a set of bone directions. In-betweens are computed per bone, so a movement can lead with the head and let the arms follow.

`renders/poses/v001/` holds three key poses and a motion test:

- **Doze:** slumped asleep, hat over his eyes, his float bobbing in the moon's reflection below the boat.
- **Haul:** thrown back against a bent rod, the line taut to the reflection glowing on the hook.
- **Tip:** leaning out to tip the bucket while the moon spills from it and the cat watches.
- **Motion test (3 s):** a tug, his head snaps up, the body and arms follow into the haul, and he settles into a pulling rhythm while the catch brightens. Action poses hold for two frames; the water and stars keep their three.

Each shot is a scene spec: the camera, where the moon is, the fisherman's pose, props and the cat. Specs can change with the frame, which is how the motion test works; the storyboard will be built the same way. Olof's verdict on the poses is pending.

## Sound

On 2026-09-29 Olof asked for the film's music and sound to be made for it, rather than found or licensed. He found score v001, a slow lullaby, “not bad” but “a bit slow/boring… a little bit sleepy”, and disliked the glockenspiel. He liked what he heard as piano (most likely the harp), the violin, and a “soft trumpet or saxophone” (the clarinet). He called v002, livelier and with a real piano, “good”, but found the end of the finale and the start of the coda “a bit weird”: the tune stopped for a stray piano run and a plucked cadence that sounded like the end, then restarted. v003 makes that ending one continuous close; Olof approved it on 2026-09-30 (“ending works now”), and it is the film's score. `renders/score/v003/` holds the score as WAV and MP3 and a review video that lights up each passage of the story as it plays; earlier versions stay beside it.

- **Form:** a lilting folk tune in 6/8 with a dotted-quarter pulse of 80, a third faster than v001: a bar every 1.5 s and an eighth every 6 frames at 24 fps. 40 bars make 60 s. `src/timing.ts` holds the grid and the story's passages; the storyboard is cut to them.
- **The tune:** one melody in D that reaches up a sixth, like a hand toward the moon, and settles back by step. The clarinet sings it over the piano's bounce while the solo violin weaves a second line. High piano plays it like a music box once the moon is in the bucket. The violin mourns it in minor as the moon dims, and it comes home a step higher, in E, when the moon rises, with the violin soaring an octave above the clarinet.
- **Instruments:** recorded samples from Versilian Studios' [VSCO 2 Community Edition](https://github.com/sgossner/VSCO-2-CE) (CC0): clarinet, solo violin, upright piano, violin and cello sections, plucked cellos and double bass, and a harp for the two magic sweeps. A soft sea of filtered noise runs underneath. No glockenspiel, drums or effects.
- **Sound effects** (the reel, the splash, drips, the fish, the cat) come with the animatic, timed to picture.

| Bars | Time | Passage | Story | Music |
| --- | --- | --- | --- | --- |
| 1 | 0:00 | intro | Night sea, the float in the moon's reflection | The piano's bounce and a plucked bass |
| 2–9 | 0:01.5 | tune | Nothing bites | Clarinet tune over the piano; the violin weaves below |
| 10–11 | 0:13.5 | doze | He dozes off | A lazy falling clarinet line over slower piano |
| 12 | 0:16.5 | tug | A tug on the line | Everything stops for two plucks and a low piano jolt |
| 13–15 | 0:18 | haul | He hauls on the snagged reflection | Driving plucked strings, piano stabs, a climbing violin |
| 16 | 0:22.5 | catch | The moon comes out; the sky goes dark | Harp sweep through G Lydian to a shimmering chord |
| 17–21 | 0:24 | wonder | The moon in the bucket lights his face | The tune in octaves on high piano over soft strings |
| 22–25 | 0:31.5 | dimming | It fades like a fish out of water | The violin sings the tune in minor, ending unresolved |
| 26 | 0:37.5 | release | He tips it back | The harp sinks through A7 |
| 27 | 0:39 | darkness | A held beat of darkness | Only the sea |
| 28–30 | 0:40.5 | rise | The moon rises | C, D and B lead to E; the clarinet reaches up the opening sixth |
| 31–36 | 0:45 | finale | Silver light, a fish, the cat | The tune's second half in E, violin above clarinet, then its last phrase again; a fish leaps up the B chord in the piano and lands on the home note |
| 37–40 | 0:54 | coda | The last shot mirrors the first | The piano's lilt carries on, quieter; the tune reaches up and settles; a plucked ta-dum and a last high note |

The assistant cannot listen, so v003 was checked by measurement before Olof's listen:

- **The tune:** pitch tracking of the dry clarinet matches all 56 of its notes. The solo violin matches 36 of 42; at the other six, high in the finale, the tracker hears an octave low, and a spectrum shows the written note as the strongest pitch.
- **The shape:** integrated loudness per passage (LUFS): intro −18.8, tune −15.5, doze −19.0, tug −17.8, haul −14.7, catch −14.4, wonder −20.3, dimming −19.5, release −20.1, darkness −29.0, rise −14.8, finale −13.7, coda −19.8. The coda fades steadily, with no gap between the finale and its last notes.
- **Master:** −16 LUFS integrated with a −2 dBFS sample peak: one fixed gain and a fast limiter for rare transients, so each passage keeps its level relative to the others. That is quieter than the usual −14 for Reels, suiting a calm film.

The library's file names number octaves one lower than scientific pitch, except the harp's and the solo violin's, so samples are mapped by sounding pitch, checked by spectrum analysis; one clarinet file sounds a semitone off its name. Its instruments are recorded at levels up to 19 dB apart and are calibrated to a common level before mixing.

## Storyboard

v003, 2026-10-01, awaits Olof's review. Nineteen shots are cut on the score's bars, so every cut lands on the music; `renders/storyboard/v003/storyboard.png` shows one panel per shot. Panels use the placeholder assets drawn so far. Red arrows mark what travels during a shot, and shake lines mark a shiver. Where a pose does not exist yet (the cat's reaching paw and pounce, his smile), the caption carries the action.

**How the catch works.** The moon and its reflection are one thing: what happens to the reflection happens to the moon. The film plants this rule before it is needed. His line hangs straight down from the rod tip to the float, and the reflection lies beside it, never on it; the float's ripple makes the reflection wobble, and up in the sky the moon shivers, which only the cat notices (03–04). As the night wears on, the moon crosses the sky and its reflection the water: slowly while he fishes, faster while he dozes, until it wanders into his hook and the float plunges on the tug's first pluck (05–06). Hauling on the hooked reflection drags it toward the boat and the moon down the sky, in step (07). The moon sinks below the horizon at the moment it bursts out of the sea on his line (08), so the sky stays empty while he has it. It sets just past the bow, the one stretch of horizon the boat does not hide.

| Shot | Bars | Time | Framing | What happens | Sound |
| --- | --- | --- | --- | --- | --- |
| 01 | 1–4 | 0:00 | Wide | **The boat under the moon.** A tiny boat in the moon's silver path. His line hangs straight down to the float, beside the moon's reflection. | Intro, then the tune. The sea. |
| 02 | 5–7 | 0:06 | Medium | **Nothing bites.** He waits with the rod out; the cat watches the float. | The tune. A creak of the boat. |
| 03 | 8 | 0:10.5 | Close | **A ripple.** The float bobs beside the reflection. Its ripple runs into it, and the reflection wobbles. | The tune's last phrase. A plip, water lapping. |
| 04 | 9 | 0:12 | Close | **The moon shivers.** Up in the sky the moon shivers too. Only the cat looks up. | The tune ends. A faint, glassy shiver. |
| 05 | 10–11 | 0:13.5 | Medium | **He dozes off.** His head sinks; the hat slides over his eyes. Meanwhile the moon drifts on, and its reflection reaches his float. | The doze: a lazy clarinet. |
| 06 | 12 | 0:16.5 | Close | **A tug.** The reflection has wandered into his hook. The float plunges under: it is hooked. | The tug: two plucks. A plop, the reel clicks. |
| 07 | 13–15 | 0:18 | Medium | **He hauls the moon down.** He jolts awake and hauls. Each pull drags the reflection toward the boat and the moon down the sky. The cat stares. | The haul: driving plucks. The reel whirs. |
| 08 | 16 | 0:22.5 | Wide | **The moon comes out of the water.** As the moon sinks below the horizon, it bursts out of the sea on his line. | The catch: the harp sweeps up. A great splash. |
| 09 | 17–18 | 0:24 | Medium | **The moon in his bucket.** The moon glows in the bucket, lighting his face from below. | Wonder: the tune on high piano. Drips. |
| 10 | 19–20 | 0:27 | Close | **Wonder.** His face in the moonlight; a slow smile. | Wonder. |
| 11 | 21 | 0:30 | Close | **The cat reaches.** The cat stretches a paw toward the glow. | The violin answers. A curious chirp. |
| 12 | 22–23 | 0:31.5 | Close | **It dims.** The moon's glow flickers and fades, like a fish out of water. | The dimming: the tune in minor on the violin. |
| 13 | 24–25 | 0:34.5 | Medium | **The empty sky.** He looks up at the black, moonless sky, then back at the fading moon. | The dimming ends, unresolved. |
| 14 | 26 | 0:37.5 | Medium | **He lets it go.** He tips the bucket over the side; the moon slides into the sea. | The release: the harp sinks. A soft plop. |
| 15 | 27 | 0:39 | Wide | **Darkness.** Only the stars and the boat's faint outline. | Only the sea. |
| 16 | 28–30 | 0:40.5 | Wide | **The moon rises.** The sea glows from below; the moon rises out of the water beside the boat and climbs into the sky. | The rise: the clarinet reaches up. A swelling shimmer. |
| 17 | 31–34 | 0:45 | Wide | **Silver light.** The moon rides high again. Fish leap through its silver path. | The finale: home in E. Splashes. |
| 18 | 35–36 | 0:51 | Medium | **A gift.** One fish leaps into the boat; the cat is on it at once. | The last phrase again. A flop, a happy mew. |
| 19 | 37–40 | 0:54 | Wide | **Like the beginning.** The first shot again: the moon high, his float beside its reflection. He smiles; the cat has its fish. | The coda, the plucked ta-dum and a last high note. The sea. |

- **Framing:** four setups do most of the work. The wide shot holds the moon high over a small boat; the medium shot is the style frame's; close-ups frame his face, the cat, the bucket or the float in the water. Most shots are locked off; the camera stays still and the story moves.
- **Mirror:** shot 19 repeats shot 01's framing, so the ending visibly returns to the beginning, with the reflection back beside his float.
- **Motion:** each shot is a scene spec over time in `src/storyboard/shots.ts`, so the animatic plays the same shots. The moon's drift is one function of film time shared by shots 01–06. Many shots already move: the ripple and the wobble in 03, the shiver and the cat's look in 04, the drift into the hook in 05, the tug's two jolts in 06, the haul in 07, which brings the moon down in six heaves on the beat, the catch in 08, the fading glow in 12, the tipping bucket in 14 and the rising moon in 16.
- **Earlier versions:** v001 (2026-09-30, 18 shots) put the float on the reflection, which looked as if the moon were already caught, and the moon simply vanished from the sky at the catch. v002 (2026-10-01) added the rule, but the line slanted out to the float and the tug pulled the reflection toward the hook.

## Plan

| Step | Status |
| --- | --- |
| Premise | The Moon Fisher, chosen 2026-09-29 |
| Brief | Approved 2026-09-29 |
| Style frame | v003: density A with connected forms and more detail; awaiting Olof's verdict |
| Sound | Score v003 approved 2026-09-30, after v001 (too sleepy) and v002 (an odd ending) |
| Pose skeleton | Three key poses and a haul motion test (v001): good enough for the storyboard, polish later (2026-09-29) |
| Storyboard contact sheet | v003: 19 shots; the moon wanders into his hook. Awaiting Olof's review. v001's catch was unclear; v002's logic was good, with a straighter line and the drift still to come (2026-10-01) |
| Asset register | Not started |
| Animatic | Not started |
| Asset upgrade passes | Later phase |

## Rebuild

From this directory:

```sh
npm ci
npm run samples          # the recorded instruments → samples/ (about 120 MB, ignored by Git)
npm run score            # the score → public/score.wav, about 10 s; --stem clarinet renders one instrument dry
uv run --script scripts/check-tune.py clarinet   # pitch-track a dry stem against the notes the score scheduled
npm run score:review -- v004   # a versioned copy of the score and its review video → renders/score/v004
npm run preview          # fast PNG previews of every scene, without Remotion → renders/preview
npx tsx scripts/storyboard-preview.ts   # fast storyboard panels and a tiled sheet → renders/preview/storyboard
npm run storyboard -- v004   # the captioned storyboard sheet through Remotion → renders/storyboard/v004
npm run stills -- v004 renders/style-frame/v003/key.png   # Remotion still, ambient loop and before/after sheet → renders/style-frame/v004
npm run poses -- v002    # the three key poses, the haul motion test and a sheet → renders/poses/v002
npm run dev              # Remotion Studio (the port comes from $PORT under Devrun, else 3000)
npm run lint             # ESLint with Remotion's rules, then tsc
```

`npm run stills` refuses to overwrite an existing version.

## Code map

- `src/pixel/`: the palette, the low-resolution indexed image and its camera, lit and blended shapes, detail strokes, the skeleton (`rig.ts`), the film's density and the Remotion canvas that enlarges it.
- `src/world/`: the film's assets behind fixed interfaces, such as `fisherman({ x, y, pose, facing })`, `cat({ x, y, pose, facing, look })` and `bucket({ x, rimY, moon })`, plus the boat, the moon, sky, sea and light in the air. A better version of an asset replaces its drawing without touching the scenes.
- `src/stills/`: the boat scene every shot is drawn from (`boatScene.ts`), the key image, the poses, the motion test and the Remotion component.
- `src/storyboard/`: the film's shots on the score's bars (`shots.ts`) and the storyboard sheet.
- `src/audio/`: the score (`score.ts`), its instruments and their calibration (`instruments.ts`, `samples.json`), and the browser entry that renders it offline.
- `src/timing.ts`: the beat grid and the story's passages, shared by the score and the picture. `src/ScoreMap.tsx` is the score's review video.
- `scripts/`: previews without Remotion, versioned renders, sample download and pitch measurement, the score renderer and its tune check, the palette strip and a small PNG encoder.
