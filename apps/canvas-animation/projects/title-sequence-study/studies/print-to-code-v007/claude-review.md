# Independent critique

Read-only consultation on the second draft, before the final phrase revision. Claude Code 2.1.280, resolved `claude-opus-5-5`, high effort, included subscription path. Reviewed stills and source; did not watch normal-speed playback.

The reconstruction gets the layout right: letter positions, the lime/red ink placement, the combs, the checkers and the D sunburst all line up with the target. It falls short in two places. The defining gesture of the print, a diagonal fracture blasting through both rows, is barely present in the still. And the motion is the same hit sixteen times in a row.

I opened all four images, read `art.js`/`geometry.js`, and checked frames 2, 62 and 137 individually. I didn't watch the MP4. To check the pacing, I measured how far each of the 240 frames differs from `hero.png`.

## The three most valuable improvements

**1. Make the fracture a designed shape, not a hairline crack. This is the biggest gap in the still.**
- **In the target:** the diagonal across WILD is a thick band, a "zipper" of alternating black, red and lime triangles running from the W through the L into the D. HOURS has a similar torn band, and big red diagonal planes cross the letters.
- **In `clean.png`/`hero.png`:** the seam only shows as a black sliver on the W and O. Elsewhere it's a faint 1px anti-aliasing line through the L, D, U, R and S. At rest those lines look like render bugs rather than intent.
- **Why it matters for motion too:** a band with toothed edges gives the motion something to animate. The teeth can flip colour on the beat, and the band can open to reveal itself. Without it, every move is just "slide the two strips apart".

**2. Rebuild the texture as ink that spreads out from the shapes, not dirt sitting on them.**
- **In the target:** the texture lives at the edges and in the black. Dot gradients and spray bleed outward from the letters, which is what makes the colours look fluorescent. The reds also shift tone, from red through orange to a yellow-orange glow near the sunburst.
- **In the reconstruction:**
  - The pinholes are spread evenly over every letter, so it looks like granite or terrazzo.
  - The five halftone fields are dark dots on colour, so on the S, R and O they read as smudges.
  - The fills are flat.
- **The echo effect:** the 28%-alpha "registration echo" (`art.js:130-131`) turns olive/brown over black. You can see it in frame 137 as muddy drop shadows. Real screenprint misregistration is the second ink offset a few pixels at full opacity, with a hard edge.

**3. Give the 8 seconds a phrase instead of a metronome.**
- **What the numbers show (measured, not inferred):** every one of the 16 beats has the same curve. The frame starts exactly at the hero pose, peaks 2 frames later, decays over about 9 frames and sits at rest for about 4. The strongest beat is only about 1.5× the weakest, and 85 of 240 frames are near the hero. The 16 beats differ in direction but not in kind.
- **What's visible at the peaks:** both words lose legibility at the same moment. Frames 2, 62 and 137 read roughly as "WIL / WAT / HOURS / HOUR".
- **The contact sheet misleads:** 10 of its 12 samples land 2 frames after a beat, right on a peak. It makes the loop look more chaotic than it is and can't show the breathing.
- **What I infer about playback (not seen):** it probably plays as a steady 2 Hz glitch stutter that keeps snapping back to the still. That's busy rather than art-directed.
- **What I'd change:**
  - Build a hierarchy, for example: bar 1 WILD tears while HOURS holds, bar 2 the reverse, bar 3 small local motif moves, bar 4 one big full-frame tear on the downbeat, then hold the hero pose for half a bar.
  - Always keep one word readable.
  - Animate the letters' own geometry: step the sunburst in 30° increments, extend the comb teeth on the beat, march the checkers. Right now none of that moves; only the strips do. That's what would make this "editable geometry with meaningful motion" rather than a still sliced into strips.

## Smaller notes (lower priority)
- In the target, the D's sunburst is red on black, its rays reach the edge of the frame, and it eats away the right side of the D. Here it's a small lime/red fan clipped inside the letter.
- The target's letters fill the frame more tightly and have more internal fragments, especially the W. That's worth matching only after #1 and #2.

I'd start with #1. It improves the still on its own and gives #3 a real subject to move.

## Decisions

Adopted the phrase hierarchy, readable-word anchor, crisp ink registration, independent fan/checker movement, less uniform pinhole texture and edge flecks. Kept the reference-derived local wedges instead of applying a uniform toothed fracture to every glyph. Fixed the unintended antialias seam with a subpixel clip overlap. The final design remains an interpretation; the reference has more organic edge wear.
