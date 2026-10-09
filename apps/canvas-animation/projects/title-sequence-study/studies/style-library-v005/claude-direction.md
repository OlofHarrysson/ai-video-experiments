# Claude visual direction

Read-only consultation, 2026-10-09. Claude Code `opus`, high effort; returned model `claude-opus-5-5`, exit 0, `is_error: false`. Model opinions are independent advice; approximate change counts are not our verified timing measurements.

# Visual direction for the v005 typography library

**My recommendation:** the reference gets most of its variety from building each letterform differently. It gets very little from changing colour. Night Fever's variety comes from switching materials on fixed geometry. Build the library on both axes:

- **Construction family:** how the letters are made.
- **Material state:** how a fixed construction is rendered at a given moment.
- **Composition device:** layering and scale tricks that drive the chaos.

Treat these as three separate layers. Don't render every combination; give each family its own few native materials.

## 1. What the frames show (direct observations)

I looked at both overview sheets, all four style-range sheets and 15 full-resolution frames from 81–120 s.

**Layout and colour**
- Nearly every card is one word on black, roughly centred, with large black margins.
- Word size varies enormously: a tiny "LIGHTS" at 117.5 s, a small "UNTIL ITS" at 106.5 s, and "IGH" cropped past the frame edge at 97.5 s.
- Most cards use only one or two hues.
- Many cards are deliberately dim: the dark green and indigo outlines of BABY, KNOW and SHOOTING STARS. That makes the bright cards hit harder.

**About half the strongest cards are constructions, not fonts.** Each of these could be rebuilt as code:

| Time | Device |
|---|---|
| 88.5 THIS | LED grid. T, I and S are fully lit; the H is only dim small pins. So one word mixes two lighting states. |
| 89.5 THE | Horizontal slats. Some rows are offset sideways, so the letters look misregistered. |
| 115 YOU | Letters filled with vertical hairlines like a barcode. The lower half is shifted. |
| 116.5 OF | Built from a ring and rectangles. The hole of the O is half filled in a second colour. |
| 99.5 FAST | Thin parallelogram strokes that overshoot and join neighbouring letters. Blurred blue bars sit behind. |
| 100.5 CARS | Three-line inline strokes, plus a small outline copy and a horizontally blurred ghost. |
| 83.5 here | Three outlines in magenta, yellow and blue, slightly misaligned, with a strike line through the word. |
| 90.5/91.5 BABY | Two outlines offset diagonally, like a ghost of an extrusion. |
| 96.5 | Many copies of an outline receding into a tunnel, ramping red → yellow → green → white. |
| 113 LIGHTS | The same word stacked three times in three different treatments (solid magenta, white hairline, red stencil), all overlapping. |
| 111.5 LIGHTS | A huge solid violet glyph behind a thin cyan outline word. |
| 94.5 EVERYTHING | A halo of outlined triangle shards around italic tech lettering. |
| 106.5 UNTIL ITS | Chrome lettering with a flipped reflection underneath. |
| 107 VEGAS, 103.5 LIGHTS | The word sits inside a sign structure: bulb flourishes, concentric arcs, stripe bands, a lozenge frame. |
| 97 LIGHTS | Marquee bulb letters. |
| 109.5 | The one maximal card: a condensed italic serif, mint fill with a dark keyline, over a dense photo of lights. |

💡 **WORTH KNOWING — the chaos comes in pulses.** I ran a frame-to-frame change measure over 81–120 s (output to the terminal only).
- Changes cluster in bursts of 1–2-frame gaps at 93–99, 108–111 and 114–117 s.
- Between bursts there are holds of 8–23 frames and near-static stretches at 90–93, 99–102 and 117–120 s.
- Caveat: the measure probably undercounts swaps between dim outlines.

**What stills can't tell us:**
- How it feels at normal speed.
- How it syncs with lyrics or beat. The words seem to follow the vocal, but that's my inference.
- Whether the tunnel and swirl cards zoom or rotate.
- Whether this section uses bright/dim alternation the way Enter the Void does. I didn't sample a dense frame window here.

## 2. Why Night Fever works (my judgment)

- It's a designed lettering piece, not text set in a font. The custom swashes and layered gradients make it an object.
- The material cycle works because the shape never moves, so only the surface changes. That's legible and hypnotic.

**What to carry over:** give every new family a fixed geometry with 4–6 native material states. Don't add a crop or a camera move.

**One new idea the THIS card suggests:** let individual letters sit in different material states, and run the material cycle as a wave across the letters instead of swapping the whole word at once.

## 3. Proposed library (ideas, not selections)

These are grouped by how they're built. Native materials are listed for each.

**A. Sampled from a raster mask** (render any font to a hidden canvas, then sample a grid)
1. **LED board.** Cells are lit, dim or off. Materials: full, dim pins, ghost grid, inverted (grid lit, letters dark), per-letter mix. Motion: row scans, letters light in sequence.
2. **Slats / barcode.** Horizontal bars with per-row offsets, or vertical hairlines. Materials: even, jittered, barcode, half-sliced. Motion: row offsets step every 2 frames, like a venetian blind.
3. **Print halftone on a coloured paper ground.** This continues All at Once's strongest trait. It's also the main escape from black backgrounds.

**B. Stroked font paths** (opentype.js is already installed)
4. **Inline tube.** Draw stacked strokes (wide colour → narrower black → colour) to get double or triple rounded lines. Materials: three lines, two lines, core only, filled tube.
5. **Misregistered outlines.** Three offset outlines blended together, plus a strike rule. Materials: aligned, spread, single.
6. **Extrusion stack.** N outline copies stepping toward a vanishing point. Materials: two-step ghost, 12-step colour tunnel, solid extrusion, wireframe. Motion: only the depth count changes, never the position.

**C. Custom alphabets built from primitives**
7. **Primitive kit** (rings, half-discs, rectangles on a module grid). Materials: split fill, solid, rings only, half lit.
8. **Wire stencil** (single-line parallelograms whose strokes overshoot into each other).

*Practical shortcut:* hand-code one grid skeleton alphabet. It can drive 7, 8 and an alternative LED renderer. If time is short, cover only the sample words' letters.

**D. Premium lettering** (Night Fever grade)
9. **Lacquer script.** This is the existing benchmark.
10. **Condensed italic serif sign.** Two lines in a high-contrast italic serif with a keyline, over our own procedural field of lamp diamonds and arcs. It's the library's one full-frame, maximal card.
11. **Blackletter foil.** Materials: foil, engraved hatching, outline, red initial.
12. **Chrome with mirror reflection.** This extends Overload.

**E. Composition devices** (they act on any family and drive the escalation)
- A giant solid block or letter behind a hairline word.
- The same word stacked in three families.
- A sign frame around the word: bulb chasers, arcs, stripe bands.
- A seeded shard halo.
- An extreme crop with an RGB split.
- A tiny word in a huge void.

**Escalation ladder:**
1. One word, one family, held.
2. Material cycle on fixed geometry.
3. Same word, different family each beat.
4. Two layers: block + hairline, or word + frame.
5. Three families stacked.
6. A pile: earlier cards left as dim layers, plus crop and shards.

Escalate by shortening the holds and adding layers. Keep the black and empty beats.

## 4. Traps that would make it generic

- **Glow on everything.** Most reference cards have no bloom (BABY, the orange LIGHTS, CARS, FAST, here). Use glow on at most about a third of cards.
- **Colourways of one look.** Test: each family must be recognisable in greyscale.
- **Always black, always centred, always the same size.** Use a red, blue or paper ground, a full-bleed crop, and a tiny word.
- **Retrowave pastiche.** Chrome + magenta grid + sunset. Overload is already near that edge.
- **Novelty effect fonts that do the design for you** (Monoton, Orbitron, Bungee Shade). Construct the effect from plain fonts instead.
- **Glitch as a universal sauce.** The reference uses RGB split on very few cards.
- **Copying images instead of devices.** Don't recreate the Vegas sign, the logo, or CJK used as decoration; use our own giant glyph.
- **Uneven polish.** Get breadth first, screen it, then deepen two or three families. Polishing one family for the whole hour defeats the sprint.
- **Non-deterministic noise.** Seed everything by word, family, state and frame, so material cycles repeat exactly.

## 5. Practical order for the hour

1. A shared interface: `draw(ctx, word, family, state, frame, seed)`. Plus two utilities: mask sampling and stacked strokes.
2. Families in order of distinctiveness per minute: LED → slats/barcode → inline tube → extrusion stack → triple stack and giant block (composition devices) → serif sign → primitive kit (sample letters only) → sign frame.
3. Fonts: use what we have (Anton, UnifrakturCook, Snell Roundhand). Add at most 2–3 open-licensed fonts with source records: one high-contrast italic serif, one wide heavy grotesk for the outline families, one rounded geometric for the tubes.
4. Sample words with an O, an S, a diagonal letter, and lengths from 2 to 9 letters. That stresses the custom alphabets.

I didn't write any files. The frame-change counts are approximate and don't replace real-time viewing. Choosing which families to keep is Olof's call.
