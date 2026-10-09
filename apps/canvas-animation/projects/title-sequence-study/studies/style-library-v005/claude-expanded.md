# Expanded library review

Read-only consultation during the resumed hour, 2026-10-09. Claude Opus, high effort; resolved `claude-opus-5-5`, exit 0, `is_error: false`. Advisory still-design judgment, not a playback review.

Everything below comes from stills only, so none of it says anything about motion quality. For the soft-metal study I looked at `output-surface-normals/softmetal-0` and `-1`, which exist. I also compared against the All Of The Lights style-range contact sheets 1–3 and v003 `01.png`. I didn't look at any Enter the Void frames, so comparisons to it are from memory of its general approach.

## Recommendation

Don't add an 18th construction. **Spend the 45 minutes on two levers: drawn letterforms and composition.** Variety in the set now comes almost entirely from surface finish (neon, gold, tiles, bulbs). The letter shapes underneath and the layout are nearly the same every time.

## What I saw

- **Layout is the same everywhere.** 16 of the 17 families put one horizontal word in the centre, about 60–75% of the frame wide, on black. Only Overprint (MORE, cropped at the frame edge) and Collision "Giant ground" (one huge N) break the frame or change scale.
- **The All Of The Lights frames get their range from layout, not finish:**
  - 97.5s: the letters "IGH", cropped huge beyond the frame.
  - 117.5s: a tiny "LIGHTS" alone in black.
  - 111.5s: an outlined "LIGHTS" over a giant solid glyph block.
  - 106.5s: "UNTIL ITS" mirrored.
  - 94.5s: "EVERYTHING" exploding into shards.
  - 96.5s: a full-frame extrusion tunnel.
  - 109.5s: the title surrounded by a whole wall of signage.

  Most of the finishes are plain outlines or flat fills.
- **Three families share one stick-figure alphabet.** In the code, Glass circuit, Folded current and Soft metal all draw from the same `skeleton()` letters. That's why HOT, FOLD, GLOW and the tube SHIFT have the same proportions, the same octagonal O and the same angular joints. Everything else uses stock fonts scaled into a box with `text()`.
- **Night Fever (v003) is still the strongest still.** Its letters are drawn: a connected script, two words that interlock, swashes crossing other strokes, and inline/outline/shadow layers. No v005 family has lettering that was itself designed.
- **The cut uses the tube for 4 of its 11 shots.** The marquee SHIFT is hard to read: the bulb grid blurs the H and I together.
- **Soft metal "Liquid silver" has rendering artifacts:** horizontal banding and white tick marks along the right edges of the W, L and O. "Rose resin" is clean and reads as inflated candy.
- **Orbit dial:** the dark purple letters almost disappear against the dashed ellipses.

## Worth deepening (opinion)

1. **Glass circuit, given a script path.** This is the highest-value change. Hand-draw the centreline of a single word as a few cubic curves: a connected script with an entry and exit swash, in the spirit of Night Fever. Run it through the existing tube renderer. Then:
   - Make it one continuous tube. Where the real thing jumps between letters, paint those segments dark, as neon makers do.
   - Use rounded bends instead of mitred octagon corners.
   - Remove the dangling wire curves. In the still they read as stray hairs.

   The same path then feeds Folded current and Soft metal for free. That gives three drawn-lettering frames instead of three more stick-letter ones.
2. **Grand dynamo.** It has the best object-level richness of the new four, but the bulbs swallow the letters. Changes:
   - Put a single row of larger bulbs along each stroke's centreline instead of filling the letter with a 13px grid.
   - Leave the letter face a solid enamel colour so its silhouette reads.
   - Make the letters about 15% larger inside the shield.
   - Remove the side speed lines. They feel tacked on and add width without adding meaning.
3. **Depth engine, with the frame broken.** It's already the closest to the 96.5s tunnel frame. Crop it so the vanishing point sits off-centre and the near letters run past the frame edge. As it stands it's contained in a tidy box, unlike the reference frame.
4. **Modular riot.** It's the only flat graphic-pattern identity in the set, so it's worth keeping. Changes:
   - The tiles are too small for the circles to join up. Use bigger modules, about one per stroke width, and orient the quarter circles so neighbours combine into larger arcs and round corners. Then the letters feel built from the system rather than patterned with it.
   - Drop the "Two-plane weave" state. In the still it's noise.

Park Orbit dial, Razorwire and Wingline. They read thin or clip-art-like in still frames, and refining them won't change the range of the set.

## Graphic identity still missing

- **Drawn, connected lettering** (covered by item 1). It's the one quality Olof has explicitly responded to.
- **Scale and composition as their own setting, independent of finish.** Four layout modes would cover it: full-bleed crop, tiny word in a black field, word over one giant glyph, and stacked/interlocked two-line. Applied to any finish, these would produce more of the All Of The Lights feeling than new materials would. Stack and Overprint already prove the point.
- **Lower priority: fragmentation and environment.** A word bursting into shards, or a frame densely packed with competing signage, like the "All of the LIGHTS" title frame. Defer both.

## Suggested use of the 45 minutes

- [ ] About 20 min: hand-draw one script word as a path and render it through tube, ribbon and soft-metal (rose resin).
- [ ] About 10 min: the Grand dynamo bulb-along-stroke rework.
- [ ] About 10 min: three layout variants (crop, tiny, over giant glyph) on two existing families, for example Depth engine and Mercury sport. This tests the composition setting without building a framework.
- [ ] Leave the Liquid silver artifacts as a known defect unless the fix turns out to be trivial.
