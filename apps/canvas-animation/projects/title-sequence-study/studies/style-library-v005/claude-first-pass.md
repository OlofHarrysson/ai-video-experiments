# Claude first-pass review

Read-only visual critique, 2026-10-09. `opus`, high effort, returned `claude-opus-5-5`, exit 0, `is_error: false`. Still-design opinion, not a normal-speed playback review.

**Bottom line:** about half the library has real construction variety. The rest is a licensed font with ornament placed around it. The biggest problem across the set is that nothing emits light. `library.js` uses no `shadowBlur` and no blur `filter`, so every card reads as flat vector print. The All of the Lights frames depend on bloom: the red LED "THIS", the magenta "THE" and the chromatic "TO". Enter the Void is neon.

## Strongest
1. **Depth engine / Spectrum tunnel.** This is a real constructed perspective and the closest to Enter the Void. The vanishing point between H and O gives it energy. White vanishing point is a strong second state.
2. **Overprint / Misregistered blue.** It has real print craft: halftone, a two-plate offset and a confident poster crop. The crop works, and the orange stock is also good.
3. **Collision press / Giant ground.** The scale contrast between the solid N and the hairline "NOW" is the most graphic composition in the set. Three voices is good too.
4. **Counterform / Split geometry and Solid vermilion.** Keep these as quiet cards. They're clean, flat and confident. Don't add ornament.
5. **Pinboard / Incandescent.** It's the closest to the reference, but without bloom it reads as a dot pattern, not lamps.

## Weakest
- **Orbit dial.** The word is small and drawn only as an outline. The rings pass straight through R, B and T with nothing hiding them, and contrast is low, so it looks like a screensaver. The four states are near-identical recolours. Cut it or rebuild it.
- **Razorwire.** The custom wire alphabet is a decent skeleton. The triangle shards are random confetti that don't relate to the letters. The 1px hairlines will vanish or alias after video compression, and Cross-current is illegible. The I's top bar nearly runs into the T's, so it reads close to "VELOCTTY".
- **Wingline.** The wings aren't attached to the letters: their inner tips stop short of F and Y or poke into them unevenly. The thin arc underneath looks like a stray line. Stamped foil is the only state that holds together.
- **Electric palace.** This is essentially Night Fever's sibling rather than a new identity, and it's busy. Specific collisions:
  - The "A" of After overlaps the top of the H.
  - The "f" descender crashes into the H.
  - The lower-left of the H crosses the oval ring.
  - The dot lattice runs under the letters with no knockout.
- **Mercury sport.** It's competent, but it's the stock 80s chrome look, the closest thing here to an "effect font". The four states are colourways.
- **Gilt relic / Fine seal** is nearly invisible: dark on dark. **Pinboard / Dim pins** is too dim to read as a state.

## Variety: real or superficial?
- **Real construction:** Pinboard, Split frequency, Depth, Razorwire, Overprint, Collision and Counterform.
- **Font plus surrounding decoration:** Orbit, Wingline, Relic and Palace. In none of them does the ornament interact with the glyphs. Nothing occludes, weaves, anchors or knocks out.
- **States:** mostly recolours. Collision and Counterform are the exceptions, with genuinely different structures per state.

## Clipping and layout
- **Overprint:** the M and E are cut at the frame edges. That's intentional and fine.
- **Split frequency / Vertical comb:** this reads as two words, "SIGNAL" stacked on "SIGNAL", which looks like a rendering error rather than a torn word. Vertical 1px combs will also moiré in H.264.
- **Counterform / Nested counterforms:** the nested O rings spill past the letter edge into the D, and the D's inner copies overflow too. It reads as a mistake.
- **Palace and Wingline:** the collisions listed above.

## Five improvements, in priority order for 40 minutes
1. **Add a shared emission pass.** Draw the glyph layer to an offscreen canvas, then composite it back with `'lighter'` at `filter='blur(4px)'` and again at `blur(18px)` with lower alpha.
   - Apply it to Pinboard, Split frequency, Depth, Razorwire and Wingline.
   - For Pinboard, give each dot a hot white core plus a coloured halo, and show unlit pins at about 8%, as in the reference "THIS".
   - This is the single biggest lift in sophistication.
2. **Make ornament interact with the letters.**
   - Orbit: split each ellipse into back and front halves. Draw the back half, then the letters with a solid black knockout fill, then the front half.
   - Palace: knock the dot lattice and ring out under the letters, using `destination-out` with a dilated mask.
   - Wingline: anchor the wing roots to the glyph bounding-box edges and delete the arc.
3. **Fix scale and line weight.** Push Orbit, Wingline and Razorwire to 70–85% of frame width and set a 2px minimum stroke at 1280. In Razorwire, replace the confetti with shards that break off the letter vertices along one direction.
4. **Fix the collisions.**
   - Palace: shift "After" up and right, and clear the f's descender.
   - Nested counterforms: clip each letter's nested copies to its own mask.
   - Split frequency: shift only the top half-slice of one word, so it reads as one torn SIGNAL.
5. **Make at least one state per family structural, not a recolour.** Only if there's time. Example: Chrome with a horizon-split reflection, or Orbit as a single tick-mark dial.

## One missing construction: neon tube
Reuse the Razorwire single-stroke alphabet as glass tubing:
- a dark tube core with a saturated glow,
- small unlit gaps where the tube bends behind itself,
- electrode caps at the stroke ends and two mounting clips.

It uses code you already have, fills the missing-light gap and is the most direct Enter the Void signal. It's also distinct from Night Fever's enamel script.

**If time runs short:** do #1 and #2, and cut Orbit rather than polish it.
