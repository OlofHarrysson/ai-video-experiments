# Using the library in a real sequence

Choose the words before polishing their hero artwork. The examples establish construction methods and a visual vocabulary; the final words will change counterspaces, joins, ornament placement and the balance of each card.

## Build a phrase

1. Pick a construction from `catalogue.json` using its character range and reuse limits. Render the actual phrase as a still first. Font-based families accept more characters; the original alphabets accept A–Z and spaces. Wild is one bespoke path, not a script font.
2. Decide what should dominate: the word, its surrounding sign, a giant background glyph, or empty space. Use `compositions.js` as examples of authored placement, not an automatic layout engine.
3. Fix the silhouette and spacing at full size and at the intended viewing size. A luminous core, a dark outline and a reflection cannot rescue a cramped counter or an ambiguous letter.
4. Design a small related set of states. Lit/unlit, solid/outline, enamel/engraving and flat/deep are useful changes. Four palette swaps do not automatically constitute four graphic identities.
5. Animate the relevant parts: lamp groups, gas along a tube, depth contours, reflections, slices or individual glyphs. Some cards should hold. Use the earlier v002 outline/GSAP tools when actual glyph choreography is the selected intent.
6. Place the phrase in the edit, then judge its neighbours. Simple print beside ornate script, a tiny word beside an oversized crop, and a black interval between dense cards can add more contrast than extra decoration on every card.

A minimal deterministic shot:

```js
const frame = Math.floor(seconds * 24);
const treatment = [0, 2, 1, 3][Math.floor(frame / 6) % 4];
TypeLibrary.render('tube', 'Wild', treatment, frame, canvas);
```

This cycles four treatments per second while native motion receives a continuous local frame. Adjust timing to the chosen sound and phrase. It is an example, not the selected cadence for the film. For film export, use an explicit timeline such as `cut.js`; the browser's real-time preview clock is not an export clock.

## Extend a construction

Keep new drawing logic beside this study until another project needs the same mechanism. A family in `library.js` needs a stable ID, default word, four named states and a pure draw function. Add corresponding provenance/reuse notes to `catalogue.json`; the renderer checks that its IDs match. A word-specific identity belongs in `lettering.js` or a new project-owned lettering file. Preserve any previously selected path before replacing it.

Render to a fresh output directory. Inspect all states, a dense motion interval, and the compressed result. Check an out-of-order seek if state/cache logic changes. Keep the render's source snapshot and update the selected delivery pointers only after screening. No need to make a generalized editor, alphabet or GPU pipeline before a chosen shot needs it.

## Focused next experiments

- **Real hero lettering:** draw the chosen film phrase with deliberate joins and optical spacing. The Wild W can read like an l plus u; a future hero word should be judged for its own letter identities rather than inheriting this ornament blindly.
- **Reflective crossings:** try an explicitly ordered over/under stroke at one junction before expanding the surface engine. Current smooth unions fuse tubes and still leave pinches; physical depth is unproved.
- **Sign construction:** align the marquee fan with the facade, and place bulbs optically on a chosen word. A mask-based sampler is a starting point, not an exact bulb-spacing designer.
- **Rhythm with sound:** compare the strongest few cards against an actual pulse and energy curve. The silent showcase proves a cut structure, not musical timing.

Select among these after Olof's review. None is authorization to choose a theme, start paid generation or replace the current film workflow.
