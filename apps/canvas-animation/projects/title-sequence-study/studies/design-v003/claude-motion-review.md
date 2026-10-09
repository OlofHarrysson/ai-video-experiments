# Claude motion consultation

2026-10-09. Claude Code 2.1.280, resolved model `claude-opus-5-5`, high effort, existing Pro login. Read-only consultation completed successfully. The following is Claude's external critique, preserved as advice rather than instructions or verified project facts. Its broad-range numerical claims were not independently reproduced. Source frames support the local material-change and brightness-alternation observations. No real-time viewing or audio listening was performed.

# Night Fever motion: second opinion

**Bottom line:** You're half right. The cuts aren't what's wrong. The reference is almost entirely abrupt cuts, but at about 10× our tempo, and what it changes between frames is the *material* of the letters, not the framing. v003 cuts at the wrong speed and changes the wrong thing. Smooth tweening (GSAP, wobble, zoom) would take us further from the reference, not closer.

## What the reference actually does (measured, 110–131.5 s)

I streamed per-frame luma stats from the original file to stdout, without writing any files:

- **It changes every frame.** 507 of 528 frames differ substantially from the frame before. In our motion test, 199 of 216 frames are identical to the one before, which works out to about 2 changes per second versus about 23.
- **It strobes the whole time.** Luma flips bright/dim/bright on 88% of frames, and the dim frame averages about 0.65× the bright one. For example, 121.20–121.50 s reads 55, 29, 56, 32, 61, 29, 53, 27. The reference study called this a local pattern; it actually runs through almost the entire range.
- **Designs come in 2-frame pairs.** Each pair is the same layout shown twice, with the second frame dimmer and in a different palette. Examples: PAZ block 2685→2686 is pixel-registered, hot pink then crimson; ROY 2752→2753 goes red then pink. A new treatment follows after 2 frames, sometimes after 4. That's about 6–12 treatments per second.
- **Within a card, the lettering stays put and the rendering changes.** The PAZ script lockup (2687→2689→2691) keeps its geometry but goes filled lacquer → dim → filled → dim → multi-line contour echo (mint/red/violet). The stars switch from filled to outlined.
- **There is some motion, but it's stepped, never tweened.** Between bright frames 2687 and 2689 the script grows about 5% (on twos), and the star field is completely re-scattered every frame. So the word creeps forward while its surroundings boil.
- **It stacks earlier treatments.** Frame 2758 superimposes earlier CYRIL ROY treatments (grey rounded, Japanese, purple outline) shrunk to about 60% in the centre.
- **It has rests.** 109.86–110.07 and 110.61–110.82 are true holds, and around 120.7–121.2 is a low-intensity stretch.

## Why v003 reads as "pretty crap"

`art.js:89-90`: six phases held for 8–15 frames each, with whole-plate scale (1–1.25×) and offsets up to 110 px.

1. **Tempo puts it in the wrong perceptual category.** At 2-frame holds, successive states probably fuse into one shimmering, unstable object. At 12-frame holds, each state reads as its own shot, so the result looks like a jumpy slideshow. This is an inference from the frame data; I can't watch it at speed.
2. **It changes the wrong variable.** Reframing a fixed picture reads as a cheap camera punch-in. It also crops the N swash and the r flourish, which are the best parts of the design. The reference keeps the footprint and changes what the letters are made of.
3. **There's no strobe and no boil.** Luma is flat and the stars never move.
4. **The `variant` path is almost invisible.** It adds a 24 px translucent bar at `art.js:34`, so in practice there is only one rendering of Night Fever.

## Night Fever as artwork

**What it gets right:**
- The diagonal, interlocking two-word lockup fills the wide frame. The Night descenders tangle into the Fever F, and the flourishes connect to real strokes. Compositionally it's the closest we've come to the PAZ card.
- It's built in real layers in code: a 19-pass offset mass, an 18 px dark separator, a pink edge, a cream bevel and a gradient face (`art.js:28-30`). That layering is the most useful thing here (see the experiment below).

**Where it's still simplistic:**
- **The extrusion is a solid violet slab.** The reference uses a few separate coloured echo copies (pink, violet, blue). Those copies are exactly what turn into the contour-echo frame. A slab can't do that.
- **The stars are sparse and static.** The reference has a dense field of five-point stars in several colours, re-scattered every frame.
- **The polish is a stylistic choice.** The glossy 80s-logo chrome is more refined than the reference's flat white fill. Each reference card is fairly crude; the richness comes from the succession of cards. Don't spend more time polishing a single plate.

## Proposed next experiment: "Night Fever render cycle" (about 4 s, silent)

- **Lock the geometry.** Keep the lockup exactly as it is, with no crop, pan or zoom of the plate. Allow at most a stepped scale creep of about +2% per pair within a held treatment, reset when the treatment changes.
- **Derive 5–6 renderings from the existing `draw(dx,dy,fill,stroke,lw)` layers:**
  1. Lacquer (the current design)
  2. Flat cream fill plus 3 separate coloured echoes
  3. Contour echo only: 4–6 stroked offset copies in different colours, no fill
  4. Hollow line: separator plus bevel strokes only
  5. Extrusion silhouette only
  6. Dot fill, reusing the overprint `dotMask` technique
- **Pair the frames.** Bright frame, then a dimmed (about 0.6×) and hue-shifted partner.
- **Boil the stars.** Re-seed the star field from the frame number every frame, and make it much denser.
- **Add one stacked frame:** 2–3 earlier renderings superimposed at about 0.6× scale.
- **Run the same cycle three times back to back with 6-, 4- and 2-frame holds.** This tests the main hypothesis directly: at what tempo does it stop looking like a slideshow and start looking like a vibrating sign?
- **Acceptance:** first check that the luma alternation and change rate measure close to the reference numbers above. After that, only your real-time viewing counts.

## Limits

- I haven't watched anything at full speed or heard the audio.
- The local file is a re-encoded 544p upload. The alternation is regular and carries palette changes, so it looks deliberate rather than like an encoding artifact, but I can't prove that.
- Beyond the existing dense windows I only checked luma statistics, not every frame visually.

⚠️ **RISK OR DEVIATION:** a full-frame 12 Hz bright/dim flicker falls in the photosensitive-epilepsy range and would likely fail broadcast flash limits (no more than about 3 large flashes per second). That's fine for the study. If the film goes public, we'll need a softer or partial-frame strobe and possibly a warning.

🧭 **DECISION:** I recommend the render-cycle-at-three-tempos test over any smooth-motion revision. Olof, your call on whether to approve it as the next experiment.
