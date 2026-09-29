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

Proposed 2026-09-29; Olof's choice between the two pixel densities is pending. The key image shows the moon in the bucket lighting the fisherman and the cat from below while the sky stands empty. `renders/style-frame/v002/` holds both stills, a comparison sheet with the palette, and a four-second loop of the ambient motion.

- **Pixel grid:** scenes are authored on a 270×480 design frame and drawn at one of two densities, both enlarged to 1080×1920: A at 180×320, six times, or B at 270×480, four times. B is recommended, because the fisherman's wonder and the cat's curiosity live in a few facial pixels and read better there. Shapes and light are computed, so both densities cost about the same to make; the choice is about the look.
- **Palette:** 24 colors in `src/pixel/palette.ts`. There are seven night blues for sky, sea and shadow, five moonlight colors from silver to the moon's cream, and twelve warm colors for the oilskins, wood, skin and the cat. Nothing is drawn outside it: glows brighten a pixel by climbing its own color family.
- **Light:** the moon is the only light. Every part of an object has a surface (a dome, tube, bevelled edge or upright cylinder), so the scene can be relit from wherever the moon is. The light picks a step on each material's ramp of four to seven colors.
- **Outlines and shading:** there are no black lines. A silhouette's edge is one step darker than its fill, and lit edges keep their color. Overlapping parts cast a one-step contact shadow. Characters and props are shaded in clean bands, with stray single pixels removed.
- **Dithering:** only in the air and sky, with an ordered 4×4 pattern: the seams between sky colors, the moon's halo and the light shaft.
- **Water:** still water mirrors whatever floats on it, one or two steps darker, broken into ripples about two world units tall.
- **Frame rate and cadence:** 24 fps. Poses and ambient motion hold for three frames, eight drawings a second; quick actions such as the haul hold for two. Everything moves in whole pixels, like the boat's one-pixel bob on a two-second swell.

Weak spots for the upgrade passes: the near-black hull, the broad flat back of the coat, the cat's stiff legs and the dark tin of the bucket.

## Plan

| Step | Status |
| --- | --- |
| Premise | The Moon Fisher, chosen 2026-09-29 |
| Brief | Approved 2026-09-29 |
| Style frame | Proposed: the key image at two densities and an ambient loop (v002); awaiting Olof's choice |
| Sound decision | Before the storyboard's timing is locked |
| Storyboard contact sheet | Not started |
| Asset register | Not started |
| Animatic | Not started |
| Asset upgrade passes | Later phase |

## Rebuild

From this directory:

```sh
npm ci
npm run preview          # fast PNG previews of the style frame, without Remotion → renders/preview
npm run stills -- v003   # Remotion stills, the ambient loop and a comparison sheet → renders/style-frame/v003
npm run dev              # Remotion Studio (the port comes from $PORT under Devrun, else 3000)
npm run lint             # ESLint with Remotion's rules, then tsc
```

`npm run stills` refuses to overwrite an existing version.

## Code map

- `src/pixel/`: the palette, the low-resolution indexed image and its camera, lit shapes, the two densities and the Remotion canvas that enlarges them.
- `src/world/`: the film's assets behind fixed interfaces, such as `fisherman({ x, y, pose, facing })`, `cat({ x, y, pose, facing })` and `bucket({ x, rimY, moon })`, plus the boat, the moon, sky, sea and light in the air. A better version of an asset replaces its drawing without touching the scenes.
- `src/stills/`: the key image and its Remotion component.
- `scripts/`: previews without Remotion, versioned renders, the palette strip and a small PNG encoder.
