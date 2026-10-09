# Claude lettering and layout review

Read-only visual consultation, 2026-10-09. Claude Code Opus with high effort; returned model `claude-opus-5-5`. Advisory judgments; source frames and current full-resolution artwork were inspected.

**Verdict:** The custom script now reads as a real lettered object. The composition set has real range in layout, not just in finish. Before handoff, I'd fix one shared flaw: the **W→i junction** in the "Wild" path. Every script artifact uses that path, so one fix improves about five frames.

I judged everything at native 1280×720 without making crops. Coordinates below are pixel positions in those frames.

## Strongest

- **`tube-0`** is the most convincing piece. One continuous monoline stroke, a separate tube for the i-dot, electrode caps and a restrained glow make it read as a single physical neon sign. Monoline suits neon, so the lack of thick-thin contrast doesn't hurt here.
- **`interlock-0` (neon Wild over gold serif Hours)** is the strongest composition. Pairing a script with a heavy serif follows the reference "PAZ / de la Huerta" pairings (`comparison-1.png`, rows 2–3) without copying them, and the hierarchy reads instantly.
- **`compositions.png`** shows meaningful range. Tiny signal, a cropped giant glyph with a hairline caption, a broken-frame depth tunnel, stacked hierarchy and a crowded wall are different layout ideas, not reskins. The All of the Lights contact sheets support this range: small isolated words (`KNOW`, `LIGHTS` at 117.5s), a word over a giant glyph (111.5s), the tunnel (96.5s) and the dense wall (109.5s).

## Does the script read?

- **At a glance, yes**, especially with context ("Hours", the i-dot). In isolation, two shapes weaken it:
  - **W→i junction (~540–580, 380–440 in `tube-0`/`softmetal-*`):** the W's last downstroke and the short i upstroke run almost parallel with a sliver gap. In the neon, the glow merges them into a knot. In `softmetal-1`, the overlapping tubes crumple into broken highlight fragments. This is the weakest letter join.
  - **d bowl → ascender (~800–865, 315–335):** the bowl's top flattens into a horizontal bar with a small kink where it meets the looped ascender. It's legible, but it's the second-least resolved join.
- **Baseline observation:** the W's two bottoms (~485 and ~470) sit 25–40 px below "ild" (~440–450), so the word tips downhill on the left. That may be intended bounce; whether it looks good is your call.

## Do ornament and lettering cohere?

- **Script pieces: yes.** The lead-in curl and exit swash belong to the same stroke, so ornament and letters form one gesture.
- **`softmetal`: partly.** Self-crossings render as butt seams rather than one tube passing over another. Examples: the swash entering the W loop (~205–235, 280–300) and a horizontal cut across the l stem (~620–650, ~358 in `softmetal-1`). These seams break the inflated-object illusion more than any letterform does.
- **`marquee-0`: mostly.** The bulb-filled slab letters and the bordered plaque belong together. The ray fan behind it (~430–840, 95–215) is the outlier: its rays stand vertical while the plaque tilts and recedes, so it looks pasted behind rather than mounted on the sign.

## Specific collisions in compositions

- **`nightwall-0`:**
  - The W loop (~230–270, 195–260) runs through the "u" of the After Hours emblem, so it reads "Ho rs".
  - The d ascender top (~940, 195) is nearly tangent to DYNAMO's lower rim. They should either clearly overlap or clearly separate.
  - Grounded in the reference: the 109.5s "All of the LIGHTS" frame is one dominant title over an ambient light field. Our wall is five competing title systems with no shared colour or light, so it reads more like a catalogue collage than a single wall. Whether that's acceptable is a taste call.
- **"Interlock" is a stack, not an interlock.**
  - In `interlock-0`, the W's second bottom (~330, 380) nearly touches H's top serif.
  - In `interlock-1`, the H simply covers the W's bottoms (~300–400, 380–410). No stroke passes over and under.
  - It works as hierarchy; it doesn't deliver the woven idea the name promises.
- **Three exposures:** the bottom exposure is cropped by the frame edge, and the swashes tangle where the exposures meet (~850–900, 700–740 in the sheet). The grey middle copy reads as disabled.

## Recommended single refinement

Rework the **W→i join**. Either open a clear counter about one stroke-width wide between the W's exit and the i stem, or turn the W's exit into a single rounded turn into the i. It fixes legibility and the softmetal crumple at once, and propagates to tube, softmetal, interlock, nightwall and triplicate. If time allows one more, softening the d-bowl kink is the same kind of fix.

## What stills can't establish

- Whether the three exposures earn their overlap as a temporal echo.
- Whether the colour blocks and ribbing in `interlock-1` read as a travelling cycle or as arbitrary segmentation.
- Whether the PULSE LED gaps and the marquee bulbs feel alive.
- Whether nightwall's density works as a hold or needs a cut.

## Honest limits

- This doesn't match the reference finish. The reference chromatic signature (`comparison-2.png`, row 1) is a high-contrast script with stacked coloured edging, and the preferred `design-v003/01.png` also has thick-thin contrast. "Wild" is monoline, so it's a different genre: neon or balloon hand-lettering, not calligraphic script.
- The reference evidence is *All of the Lights* frames. That's the right basis here, rather than my earlier memory of Enter the Void.
