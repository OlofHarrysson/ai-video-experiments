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

On 2026-09-29 Olof asked for the film's music and sound to be made for it, rather than found or licensed. He found score v001, a slow lullaby, “not bad” but “a bit slow/boring… a little bit sleepy”, and disliked the glockenspiel. He liked what he heard as piano (most likely the harp), the violin, and a “soft trumpet or saxophone” (the clarinet). He called v002, livelier and with a real piano, “good”, but found the end of the finale and the start of the coda “a bit weird”: the tune stopped for a stray piano run and a plucked cadence that sounded like the end, then restarted. v003 makes that ending one continuous close; Olof approved it on 2026-09-30 (“ending works now”). v004 (2026-10-01) is v003 with one held bar after the tug, for the dramatic pause Olof asked for when the moon is hooked; every other note is unchanged, one bar later from the haul on. It is the film's score. `renders/score/v004/` holds the score as WAV and MP3 and a review video that lights up each passage of the story as it plays; earlier versions stay beside it.

- **Form:** a lilting folk tune in 6/8 with a dotted-quarter pulse of 80, a third faster than v001: a bar every 1.5 s and an eighth every 6 frames at 24 fps. 41 bars make 61.5 s. `src/timing.ts` holds the grid and the story's passages; the storyboard is cut to them, and the score places each passage from where its section starts.
- **The tune:** one melody in D that reaches up a sixth, like a hand toward the moon, and settles back by step. The clarinet sings it over the piano's bounce while the solo violin weaves a second line. High piano plays it like a music box once the moon is in the bucket. The violin mourns it in minor as the moon dims, and it comes home a step higher, in E, when the moon rises, with the violin soaring an octave above the clarinet.
- **Instruments:** recorded samples from Versilian Studios' [VSCO 2 Community Edition](https://github.com/sgossner/VSCO-2-CE) (CC0): clarinet, solo violin, upright piano, violin and cello sections, plucked cellos and double bass, and a harp for the two magic sweeps. A soft sea of filtered noise runs underneath. No glockenspiel, drums or effects.
- **Sound effects** (the reel, the splash, drips, the fish, the cat) come with the animatic, timed to picture.

| Bars | Time | Passage | Story | Music |
| --- | --- | --- | --- | --- |
| 1 | 0:00 | intro | Night sea, the float in the moon's reflection | The piano's bounce and a plucked bass |
| 2–9 | 0:01.5 | tune | Nothing bites | Clarinet tune over the piano; the violin weaves below |
| 10–11 | 0:13.5 | doze | He dozes off | A lazy falling clarinet line over slower piano |
| 12 | 0:16.5 | tug | A tug on the line | Everything stops for two plucks and a low piano jolt |
| 13 | 0:18 | hooked | The moon is hooked; he sleeps on | The music holds its breath: the sea and one low cello note |
| 14–16 | 0:19.5 | haul | He hauls on the snagged reflection | Driving plucked strings, piano stabs, a climbing violin |
| 17 | 0:24 | catch | The moon comes out; the sky goes dark | Harp sweep through G Lydian to a shimmering chord |
| 18–22 | 0:25.5 | wonder | The moon in the bucket lights his face | The tune in octaves on high piano over soft strings |
| 23–26 | 0:33 | dimming | It fades like a fish out of water | The violin sings the tune in minor, ending unresolved |
| 27 | 0:39 | release | He tips it back | The harp sinks through A7 |
| 28 | 0:40.5 | darkness | A held beat of darkness | Only the sea |
| 29–31 | 0:42 | rise | The moon rises | C, D and B lead to E; the clarinet reaches up the opening sixth |
| 32–37 | 0:46.5 | finale | Silver light, a fish, the cat | The tune's second half in E, violin above clarinet, then its last phrase again; a fish leaps up the B chord in the piano and lands on the home note |
| 38–41 | 0:55.5 | coda | The last shot mirrors the first | The piano's lilt carries on, quieter; the tune reaches up and settles; a plucked ta-dum and a last high note |

The assistant cannot listen, so the score is checked by measurement before Olof's listen. v004 keeps all 652 of v003's notes, at the same times before the haul and exactly one bar later after it, and adds the cello's held note.

- **The tune:** pitch tracking of the dry clarinet matches all 56 of its notes. The solo violin matches 36 of 42; at the other six, high in the finale, the tracker hears an octave low, and a spectrum shows the written note as the strongest pitch.
- **The shape:** integrated loudness per passage in v004 (LUFS): intro −18.8, tune −15.5, doze −19.0, tug −17.8, hooked −31.1, haul −14.7, catch −14.4, wonder −20.3, dimming −19.6, release −20.2, darkness −28.7, rise −14.8, finale −13.7, coda −19.8. The held bar is the quietest moment of the film, between the tug's plucks and the haul. The coda fades steadily, with no gap between the finale and its last notes.
- **Master:** −16 LUFS integrated with a −2 dBFS sample peak: one fixed gain and a fast limiter for rare transients, so each passage keeps its level relative to the others. That is quieter than the usual −14 for Reels, suiting a calm film.

The library's file names number octaves one lower than scientific pitch, except the harp's and the solo violin's, so samples are mapped by sounding pitch, checked by spectrum analysis; one clarinet file sounds a semitone off its name. Its instruments are recorded at levels up to 19 dB apart and are calibrated to a common level before mixing.

## Storyboard

v005, 2026-10-01: the storyboard Olof approved as v003, carrying the animatics' changes. Twenty shots are cut on the score's bars, so every cut lands on the music; `renders/storyboard/v005/storyboard.png` shows one panel per shot, each the animatic's frame at that moment. Panels use the placeholder assets drawn so far, and red arrows mark what travels during a shot. Where a pose does not exist yet (the cat's pounce, his smile), the caption carries the action.

**How the catch works.** The moon and its reflection are one thing: what happens to the reflection happens to the moon. His line hangs straight down from the rod tip to the float, and the reflection lies beside it, never on it (01–03). He nods off (04). As the night wears on, the moon crosses the sky and its reflection the water: slowly while he fishes, faster while he sleeps, until it wanders into his hook (05). The float twitches on the tug's first pluck and plunges on the second (06). Then everything holds still for a bar: the line taut, the rod bending, while he sleeps on (07). He jolts awake, and hauling on the hooked reflection drags it toward the boat and the moon down the sky, in step (08). The moon sinks below the horizon at the moment it bursts out of the sea on his line, and the sky goes dark (09); it stays empty while he has the moon. It sets just past the bow, the one stretch of horizon the boat does not hide, and rises there again (17).

<!-- generated:storyboard -->
| Shot | Bars | Time | Framing | What happens | Sound |
| --- | --- | --- | --- | --- | --- |
| 01 | 1–4 | 0:00 | Wide | **The boat under the moon.** Out of the dark, a tiny boat in the moon's silver path. His line hangs straight down to the float, beside the moon's reflection. | Intro, then the tune. The sea. |
| 02 | 5–6 | 0:06 | Medium | **Nothing bites.** He waits with the rod out; the cat watches the float. | The tune. A creak of the boat. |
| 03 | 7 | 0:09 | Close | **The float beside the moon.** His float bobs beside the moon's reflection, never on it. | The tune's last phrase. Water lapping. |
| 04 | 8–9 | 0:10.5 | Close | **He nods off.** His eyelids droop, twice. He nods, jerks awake, then nods off for good. | The tune's last phrase. A long, sleepy breath. |
| 05 | 10–11 | 0:13.5 | Medium | **Asleep.** He sleeps. The moon drifts on across the sky, and its reflection wanders into his hook. | The doze: a lazy clarinet. |
| 06 | 12 | 0:16.5 | Close | **A tug.** The reflection has wandered into his hook. The float twitches, then plunges under: it is hooked. | The tug: two plucks. A plop, the reel clicks. |
| 07 | 13 | 0:18 | Medium | **Hooked.** Everything holds still. The line is taut and the rod bends slowly down; he sleeps on. Only the cat looks at the line. | The music holds its breath: the sea and one low cello note. |
| 08 | 14–16 | 0:19.5 | Medium | **He hauls the moon down.** He jolts awake and hauls: on every beat he lowers the rod and heaves it up again, the rod bent double. Each heave drags the reflection toward the boat and the moon down the sky. The cat stares. | The haul: driving plucks. The reel whirs. |
| 09 | 17 | 0:24 | Medium | **The moon comes out of the water.** As the moon sinks below the horizon, it bursts out of the sea on his line. | The catch: the harp sweeps up. A great splash. |
| 10 | 18–19 | 0:25.5 | Medium | **The moon in his bucket.** The moon glows in the bucket, lighting his face from below. | Wonder: the tune on high piano. Drips. |
| 11 | 20–21 | 0:28.5 | Close | **Wonder.** His face in the moonlight; a slow smile. | Wonder. |
| 12 | 22 | 0:31.5 | Close | **The cat reaches.** The cat stretches a paw toward the glow. | The violin answers. A curious chirp. |
| 13 | 23–24 | 0:33 | Close | **It dims.** The moon's glow flickers and fades, like a fish out of water. | The dimming: the tune in minor on the violin. |
| 14 | 25–26 | 0:36 | Medium | **The empty sky.** He looks up at the black, moonless sky, then back at the fading moon. | The dimming ends, unresolved. |
| 15 | 27 | 0:39 | Medium | **He lets it go.** He tips the bucket over the side; the moon slides into the sea. | The release: the harp sinks. A soft plop. |
| 16 | 28 | 0:40.5 | Wide | **Darkness.** Only the stars and the boat's faint outline. | Only the sea. |
| 17 | 29–31 | 0:42 | Wide | **The moon rises.** The sea glows from below; the moon rises out of the water past the bow, where it set, and climbs into the sky. He and the cat watch it go. | The rise: the clarinet reaches up. A swelling shimmer. |
| 18 | 32–35 | 0:46.5 | Medium | **Silver light.** The moon rides high again. Fish leap through its silver path. | The finale: home in E. Splashes. |
| 19 | 36–37 | 0:52.5 | Medium | **A gift.** One fish leaps into the boat; the cat is on it at once. | The last phrase again. A flop, a happy mew. |
| 20 | 38–41 | 0:55.5 | Wide | **Like the beginning.** The first shot again: the moon high, his float beside its reflection. The cat has its fish. Fade to black. | The coda, the plucked ta-dum and a last high note. The sea. |
<!-- /generated:storyboard -->

- **Framing:** four setups do most of the work. The wide shot holds the moon high over a small boat; the medium shot is the style frame's; close-ups frame his face, the cat, the bucket or the float in the water. Most shots are locked off; the camera stays still and the story moves.
- **Mirror:** shot 20 repeats shot 01's framing, so the ending visibly returns to the beginning, with the reflection back beside his float.
- **Motion:** each shot is a scene spec over time in `src/storyboard/shots.ts`, and the animatic plays them through. The moon's drift is one function of film time shared by shots 01–06.
- **Earlier versions:** v001 (2026-09-30, 18 shots) put the float on the reflection, which looked as if the moon were already caught, and the moon simply vanished from the sky at the catch. v002 (2026-10-01) added the rule, but the line slanted out to the float and the tug pulled the reflection toward the hook. v003, approved, planted the rule with the moon shivering in the sky, which Olof cut after the first animatic. v004 followed animatic v002.

## Animatic

v003, 2026-10-01, awaits Olof's review. `renders/animatic/v003/animatic.mp4` plays the 20 shots at final timing over score v004: 61.5 s, 1080×1920 at 24 fps. The sound is the score alone; the effects come later.

Olof found v001 “roughly there but still very rough”: he could not tell the fisherman falls asleep, and did not want the moon to shudder in the sky. v002 added a close-up of him nodding off with Z's, and the assistant's pass over the rough edges: the float twitching before it plunges, a closer catch, a sky that darkens and brightens with the moon, the moon rising past the bow instead of through the cat, a closer finale, blinks and the cat's paw, a flickering moon, fades at both ends and a swaying sea. Of v002 he said the hooking lacked a dramatic pause, the man and rod did not haul convincingly, and the transitions were abrupt and the pacing not good enough. v003:

- **The pause:** a held bar after the tug, with score v004 holding its breath: the line taut, the rod bending slowly down, he sleeps on and only the cat looks at the line (07).
- **The haul:** a pump on every beat. He heaves the rod up and is thrown back as it bends double, then leans in and lowers it to take up the line. The first heave is his jolt awake, and the moon steps down with each heave, landing on the beat (08). The catch begins at the top of the last heave, and the rod springs back as the moon comes free (09).
- **Transitions:** pixel dissolves where time passes: into sleep (05), into the bucket and the wonder (10–11), into the darkness, the rise and the finale (16–18), and into the ending (20). The tug, the jolt and the catch stay hard cuts.
- **Pacing:** the nod-off has twice the time, taken from the shot where nothing bites (02, 04).

How it is made:

- **One timeline:** the animatic, the storyboard and the asset register all draw the film through `filmAt(frame)`, so a storyboard panel is the animatic's frame at that moment. A dissolve draws the shot before as well and shows it through an ordered-dither mask that clears over the dissolve (`src/storyboard/film.ts`).
- **Cadence:** action moves on twos and ambient life on threes, as for the style frame. The boat's bob, the stars, the water and the blinks run on across the cuts.
- **Acting:** the movements within shots are in `src/storyboard/acting.ts`: nodding off, falling asleep, the startle and the haul's pumps, looking up, the leaping fish and the flicker.

## Asset register

v001, 2026-10-01. Every asset the film draws, how a scene calls it, how far along it is and what it still needs, kept in `src/assets.ts`. The status is the assistant's judgment: a placeholder stands in for the real thing, a rough asset has its intended design but needs refinement, and a final one is done. Nothing is final yet.

The screen columns are measured, not estimated. `npm run tables` draws every shot four times a second and counts the pixels each asset shows in the finished frame. *On screen* is how long it is visible, and in which shots. *Share of the picture* is how much of the whole film's picture it covers. *Largest* is its biggest moment, as a share of the frame, and the shot it happens in.

<!-- generated:assets -->
| Asset | Status | On screen | Share of the picture | Largest | Still needs |
| --- | --- | --- | --- | --- | --- |
| **Fisherman** (character)<br>`fisherman({ x, y, pose, facing })` | rough | 56 s in 01–02, 04–05, 07–20 | 5% | 24% in 11 | Poses: fish, doze, haul, heave, reel, holdBucket, lookUp, tip, with tweens for nodding off (04, 05), the waking jolt and the haul's pumps (08, 09) and looking up (14, 17); he blinks. Needs a smile (11, 20), face detail for his close-ups (04, 11), and a reel his hand can wind. |
| **Cat** (character)<br>`cat({ x, y, pose, facing, look, paw })` | rough | 50 s in 01–02, 05, 07–10, 12–20 | 0.8% | 6% in 12 | One pose, peer, with a head tilt and a front paw that reaches out (12, 19). Needs a pounce and a fish in its mouth (19, 20), a startle, and a tail that moves. |
| **Moon** (prop)<br>`moonParts({ x, y, radius, glow, waterline }); spec.moon = { in: "sky" \| "world" }` | rough | 40 s in 01–02, 04–05, 07–09, 15, 17–20 | 2% | 4% in 09 | The style frame's moon; it drifts, sets and rises. Needs a brighter burst as it leaves the sea (09) and water streaming off it. |
| **Bucket, with the moon in it** (prop)<br>`bucket({ x, rimY, moon, tilt, glow })` | rough | 21 s in 10–17 | 0.9% | 7% in 11 | The style frame's hero. The moon drops out as he tips it (15) and flickers as it dims (13); it needs water spilling with it. |
| **Float** (prop)<br>`spec.float = [x, y]` | placeholder | 11 s in 02–03, 05–06, 19 | <0.1% | <0.1% in 03 | Two ovals. Needs a drawn red-and-white float, its bob and its plunge (06). |
| **Rod and line** (prop)<br>`drawRod({ grip, angle, length, bend }); drawLine(from, to, slack)` | rough | 44 s in 01–10, 14, 18–20 | 0.2% | 0.4% in 04 | Its bend follows each heave. Needs a reel for the clicks and the whir (06, 08). |
| **Fish** (prop)<br>`fishParts({ at, angle, size })` | placeholder | 13 s in 18–20 | <0.1% | 0.3% in 18 | A body and a tail, now leaping in arcs (18, 19) and flopping on the deck (19). Needs fins, an eye and a silver sheen, and the one the cat holds (20). |
| **Boat** (set)<br>`boatInterior(BOAT), boatHull(BOAT)` | rough | 62 s in 01–20 | 8% | 23% in 12 | Planks, ribs and rivets from the style frame. Needs a check of the bow where the cat's close-up frames it (12), and a gentle rock beyond the one-pixel bob. |
| **Sky** (set)<br>`drawSky, drawStars, drawMilkyWay` | rough | 56 s in 01–02, 04–05, 07–20 | 47% | 68% in 16 | Near final. It dissolves between moonlit and dark as the moon sets (09) and rises (17); its stars could twinkle more. |
| **Sea** (set)<br>`drawSea({ horizon, bands, swell })` | rough | 62 s in 01–20 | 20% | 66% in 03 | Near final. Its swell lines sway slowly. |
| **Water reflections** (effect)<br>`reflectWater({ waterline, step })` | rough | 56 s in 01–03, 05–10, 12–20 | 9% | 16% in 10 | Near final; Olof likes it. Needs to break up around splashes and the plunging float (06, 09). |
| **Moon's reflection** (effect)<br>`spec.reflection = [x, y], spec.wobble; drawMoonReflection` | rough | 34 s in 01–03, 05–08, 18–20 | 0.2% | 2% in 06 | Drifts and wobbles. Once hooked it only gains a halo; it should stretch and tear as he hauls it in (08). |
| **Moon's glitter path** (light)<br>`drawMoonPath({ x, horizon, halfWidth })` | rough | 37 s in 01–08, 18–20 | 1% | 7% in 06 | Near final. Should change shape with the moon's height as it comes down (08). |
| **Moonlight glow** (light)<br>`drawHalo, drawShaft; spec.seaGlow` | rough | 21 s in 09–15, 17 | 3% | 21% in 11 | Halo and shaft around the caught moon, and the glow under the sea (17). |
| **Splash** (effect)<br>`spec.splash = { at, size }; drawSplash` | placeholder | 7 s in 06, 09, 15, 18–19 | <0.1% | 0.1% in 09 | Scattered droplets and a ring, used for the float, the catch, the moon's release and the fish (06, 09, 15, 18, 19). Needs a crown that rises and falls over a few frames, sized to each. |
| **Sleep Z's** (effect)<br>`spec.zzz = seconds asleep` | rough | 5 s in 04–05, 07 | <0.1% | 0.2% in 07 | Pixel Z's drifting up from his head (04, 05). Could take a hand-drawn letterform. |
| **Ripple** (effect)<br>`spec.ripple = { at, radius }; drawRipple` | placeholder | 2 s in 03, 06 | <0.1% | 0.4% in 03 | Broken rings at one radius. Needs rings that fade as they spread (03). |
<!-- /generated:assets -->

**Where upgrades pay off,** in the assistant's judgment:

1. **Acting.** The fisherman is on screen for nearly the whole film and fills a quarter of the frame in his close-up; the cat is on screen almost as long. Their missing poses (his jolt, heaves and smile; the cat's reach and pounce) carry the story's beats, and the animatic will show each one as a hold.
2. **The turning points.** The float, the splash, the ripple and the fish are placeholders on screen for seconds at a time, but the tug (06), the catch (08) and the finale (17–19) depend on them. They are small and quick to upgrade together.
3. **The scenery.** Sky, sea, boat and water reflections make up about 90% of the picture and are already close to the style frame's finish. What they lack is change over time: the sky darkening as the moon sets and the swell drifting.

Sound effects come after the animatic. The storyboard's cues:

<!-- generated:sounds -->
| Sound | Shots | Status |
| --- | --- | --- |
| The sea | 01–20 | rough, in the score |
| A creak of the boat | 02 | not started |
| A plip, water lapping | 03 | not started |
| A faint, glassy shiver | 04 | not started |
| A plop, the reel clicks | 06 | not started |
| The reel whirs | 07 | not started |
| A great splash | 08 | not started |
| Drips | 09 | not started |
| A curious chirp | 11 | not started |
| A soft plop | 14 | not started |
| A swelling shimmer | 16 | not started |
| Splashes | 17 | not started |
| A flop, a happy mew | 18 | not started |
<!-- /generated:sounds -->

## Plan

| Step | Status |
| --- | --- |
| Premise | The Moon Fisher, chosen 2026-09-29 |
| Brief | Approved 2026-09-29 |
| Style frame | v003: density A with connected forms and more detail; awaiting Olof's verdict |
| Sound | Score v003 approved 2026-09-30, after v001 (too sleepy) and v002 (an odd ending); v004 adds a held bar for the hooked moon (2026-10-01) |
| Pose skeleton | Three key poses and a haul motion test (v001): good enough for the storyboard, polish later (2026-09-29) |
| Storyboard contact sheet | v003 approved 2026-10-01, in which the moon wanders into his hook; v005 carries the animatics' changes in 20 shots. v001's catch was unclear; v002 needed a straight line and the drift |
| Asset register | v001: 16 assets measured on screen across the storyboard, and 13 sound cues (2026-10-01) |
| Animatic | v003: a held bar for the hooked moon, a pumping haul, dissolves and a slower nod-off; awaiting Olof's review. v001 was “roughly there but still very rough”; v002 lacked the pause and its haul was stiff (2026-10-01) |
| Asset upgrade passes | Later phase |

## Rebuild

From this directory:

```sh
npm ci
npm run samples          # the recorded instruments → samples/ (about 120 MB, ignored by Git)
npm run score            # the score → public/score.wav, about 10 s; --stem clarinet renders one instrument dry
uv run --script scripts/check-tune.py clarinet   # pitch-track a dry stem against the notes the score scheduled
npm run score:review -- v005   # a versioned copy of the score and its review video → renders/score/v005
npm run preview          # fast PNG previews of every scene, without Remotion → renders/preview
npx tsx scripts/storyboard-preview.ts   # fast storyboard panels and a tiled sheet → renders/preview/storyboard
npm run storyboard -- v006   # the captioned storyboard sheet through Remotion → renders/storyboard/v006
npm run tables           # regenerate this README's shot list and asset register from the code, about 40 s
npm run animatic -- v004     # the film at final timing with the locked score → renders/animatic/v004, about 2 min
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
- `src/storyboard/`: the film's shots on the score's bars (`shots.ts`), the movements within them (`acting.ts`) and the storyboard sheet. `src/Animatic.tsx` plays the shots through.
- `src/assets.ts`: the asset register. The boat scene labels every pixel it draws with an asset's name, so `scripts/tables.ts` can measure each asset on screen.
- `src/audio/`: the score (`score.ts`), its instruments and their calibration (`instruments.ts`, `samples.json`), and the browser entry that renders it offline.
- `src/timing.ts`: the beat grid and the story's passages, shared by the score and the picture. `src/ScoreMap.tsx` is the score's review video.
- `scripts/`: previews without Remotion, versioned renders, sample download and pitch measurement, the score renderer and its tune check, the palette strip and a small PNG encoder.
