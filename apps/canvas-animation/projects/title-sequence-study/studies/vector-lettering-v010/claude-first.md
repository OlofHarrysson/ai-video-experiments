# Read-only visual critique

Claude Opus 5.5, high effort, 2026-10-10. Reviewed proof 01; the subsequent crop correction, part-based mechanical planes and smoother liquid-width field were already in progress. Advice is not human approval.

**Bottom line:** the lettering is the strongest asset this project has had. The code materials are the weak link, and the cause isn't missing effects. Almost every colour decision in `art.js` comes from one input, the distance to the nearest edge. Distance alone can only produce layer-style effects: bevel, inner stroke, inner glow, pillow emboss. The target ties every colour to a stroke, a plane or a designed contour. That gap is why each card looks like a filter applied to a silhouette. The fix is to tie surfaces to the geometry and remove some effects, not to add more.

## The four cards against the target

Ranked from best to worst:

1. **Script (red): good enough.** This is the closest to the target. It still reads a little like a red bevel-and-emboss. The target's gold rim is thick and nested with oxblood. Ours is a hairline (`d<1.35`, roughly 1.3px at output size) that disappears.
2. **Tuscan: correct but polite, and the lines are wrong.** The red edge (`d<1.7`) and blue line (`d≈2.2`) sit directly next to each other, so they blend into lavender. The target has red, then an ivory gap, then blue. That gap is what makes it crisp. The hatching hugs every left edge as a uniform fringe. In the target it is a deliberate wedge of engraving on the shadow side of the stems.
3. **Liquid: right palette, wrong construction.** `t = d/width` stretches every stroke to the full band set and puts the palest yellow along the stroke's centre line. That creates chisel-like ridges (see the W terminals and the R leg), and thin joins become rainbow mush. The `.83+.17*side` shading pushes the yellow core toward olive. The target has fixed-width parallel inline bands with a flat cream core. Thin parts simply show fewer bands.
4. **Machine: the worst, and not only because of the material.** The facets come from `floor((p.x+p.y*.85)/99)`, a screen-space diagonal plaid unrelated to the letters. The orange "rules" are global diagonals that cross everything. The bevel reads as a pillow emboss. And looking at `machine-flat.png`, the trace itself is weak: rounded corners, wobbly straight edges, an uneven baseline. Mechanical lettering cannot survive a spline trace.

## Why code still looks worse, beyond the bugs you're fixing

- **Materials are blind to structure.** The distance field can't tell a stem from a swash, the upper side of a stroke from the lower, or one letter from another. Your paths already have parts (machine 16, script 7, liquid 10, Tuscan 6), but the shader never uses them.
- **Fine detail is sized for the 768-pixel source, not the output.** Gold rim, Tuscan lines and hatch period are 1–3px at 1600 wide. They will shimmer in motion and moiré in any crop.
- **Extrusion is 6–15 stacked fills sharing one canvas-wide gradient.** It has no lit side and no hard edge. A single sharp offset would read better for machine and Tuscan.
- **⚠️ RISK OR DEVIATION: we're chasing the wrong target.** The material board is the look of a rendered AI illustration. Your film references get their energy from graphic construction in one or two colours: concentric outlines (MASATO TANNO, NOBU IMAI), double contours, dot fills, misregistration. Code is good at construction and bad at photoreal finish. Liquid bands, Tuscan contours and flat machine planes all play to that strength. Only the script needs a rendered finish.

## Highest-value changes, in order

1. **Liquid: drop width estimation entirely.** Use fixed bands: `band = floor(d / BAND)`, about 4–5 bands of constant output width, a flat cream core, thin dark separating lines, and no direction-based shading. This fixes the jaggedness at its root and matches the target better than smoother width estimates would. It also gives you a native motion event: `d + phase` makes contours flow inward. That is close to the ETV concentric-outline cards.
2. **Machine: retrace, then flatten.** Re-run `trace.py` for machine only with `mode='polygon'` and a high corner threshold, or snap the edges to 0/45/90°. If that isn't crisp within about 20 minutes, hand-build the ~9 glyphs as polygons on a grid; they're simple. Then:
   - one flat colour per part (silver or lime), assigned by part index, not screen position
   - a single hard cobalt offset
   - orange rules only parallel to the diagonal cuts
   - no bevel

   As a fallback, flat lime with a hard cobalt shadow already beats the current faceted version.
3. **Tuscan: fix the line structure, cut the hatch.** Ivory face, a black or ivory gap, a red outline of at least 2px at output size, a blue inline, and a short hard extrusion. Remove the hatching unless it can be a coarse wedge on one side. This becomes the clean held title card.
4. **Script: one ten-minute pass, then stop.** A thicker gold rim with an oxblood line inside it, and a single light sweep per hold instead of a looping shimmer. Don't spend more here.

Remove alongside these: the machine plaid, the pillow bevel, the liquid direction shading, and all the `variant` palette swaps. Palette swaps are what make a gallery.

## Should an identity be dropped?

Keep all four silhouettes, but with unequal roles. The real redundancy is between **script and liquid**: both are rising stacked italics with a long swash under HOURS. Separate them by role:

- **Script:** the polished hero, mostly held with one light pass
- **Liquid:** the motion card, cropped and with moving bands, rarely shown whole
- **Tuscan:** the readable title-card anchor
- **Machine:** the only angular, flat, hard counterpoint. Without it, all three cards are curvy and ornamental, so fix it rather than drop it.

## What an art-directed cut needs

The danger is four identical centred two-line lockups at 85% frame width. However good the materials, that plays as a logo-reveal reel. The references get variety from scale, position, density and exposure, not just style.

- **Show the full lockup at most 3–4 times**, as held readings of 10–18 frames. Everything else should be:
  - static hard-cut crops, like the Tuscan O with its diamond counter filling the frame, or the liquid swash crossing the frame
  - a tiny lockup in black space
  - WILD or HOURS alone (split the parts by row)

  Keep crops static. Olof already rejected whole-frame crop/scale motion in v003.
- **Each identity needs one construction event of its own**, rather than one camera move applied to everything:
  - **Machine:** parts slam in along 45° and snap into place, then silver and lime swap per stroke twice
  - **Tuscan:** a registered build from flat ivory to red outline to blue inline to extrusion, 2–3 frames each, then four frames of misregistered jitter in the red and blue lines
  - **Liquid:** bands build from 1 to 5, then flow inward
  - **Script:** one directional light pass during the hold
- **Use registered flat-to-material swaps as punctuation.** Cut from the flat white silhouette to the full material in the same position. It's the same mechanism as the v004 material cycle Olof called much cooler.
- **No glow, no shake, no added layers.** Energy comes from the cut rhythm (6–21 frames, as in v009) and the contrast between flat and finished, huge and tiny.

## Time plan (it's 09:42 UTC, deadline 11:30)

- **Until about 10:15:** liquid fixed bands (about 10 min), machine retrace and flat planes (about 20 min), Tuscan line fix (about 10 min), alongside your crop and facet fixes.
- **10:15:** a stills checkpoint against the target. Anything still below the bar becomes a flat-silhouette beat rather than a hero.
- **10:30 to 11:10:** build the cut around the composition and construction events above.
- **11:10 to 11:30:** frame inspection and an honest write-up.

I haven't rendered any of these changes; this is a judgment from the stills and the code, and Olof's taste is the final call.
