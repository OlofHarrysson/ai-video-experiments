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

## Plan

| Step | Status |
| --- | --- |
| Premise | The Moon Fisher, chosen 2026-09-29 |
| Brief | Approved 2026-09-29 |
| Style frame | v003: density A with connected forms and more detail; awaiting Olof's verdict |
| Sound decision | Before the storyboard's timing is locked |
| Pose skeleton | Three key poses and a haul motion test (v001); awaiting Olof's verdict |
| Storyboard contact sheet | Not started |
| Asset register | Not started |
| Animatic | Not started |
| Asset upgrade passes | Later phase |

## Rebuild

From this directory:

```sh
npm ci
npm run preview          # fast PNG previews of every scene, without Remotion → renders/preview
npm run stills -- v004 renders/style-frame/v003/key.png   # Remotion still, ambient loop and before/after sheet → renders/style-frame/v004
npm run poses -- v002    # the three key poses, the haul motion test and a sheet → renders/poses/v002
npm run dev              # Remotion Studio (the port comes from $PORT under Devrun, else 3000)
npm run lint             # ESLint with Remotion's rules, then tsc
```

`npm run stills` refuses to overwrite an existing version.

## Code map

- `src/pixel/`: the palette, the low-resolution indexed image and its camera, lit and blended shapes, detail strokes, the skeleton (`rig.ts`), the film's density and the Remotion canvas that enlarges it.
- `src/world/`: the film's assets behind fixed interfaces, such as `fisherman({ x, y, pose, facing })`, `cat({ x, y, pose, facing })` and `bucket({ x, rimY, moon })`, plus the boat, the moon, sky, sea and light in the air. A better version of an asset replaces its drawing without touching the scenes.
- `src/stills/`: the boat scene every shot is drawn from (`boatScene.ts`), the key image, the poses, the motion test and the Remotion component.
- `scripts/`: previews without Remotion, versioned renders, the palette strip and a small PNG encoder.
