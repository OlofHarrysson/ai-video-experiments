# Read-only visual critique

Claude Code 2.1.280, resolved `claude-opus-5-5`, high effort, included subscription path. Reviewed the early capped-strip prototype, before the returning-loop and authored-profile revisions. This was a still/source review, not a playback judgment.

## Diagnosis

The main gap is the cross-section. Every sample uses the same 11-lane, roughly 50/50 barcode from edge to edge, so each letter looks like a candy-striped tube. In the reference, a stroke has structure: a cobalt rim, a broad cobalt field (often with fine darker hatching), then a bundle of 3–5 ivory ribbons in varied widths separated by ink hairlines.

The terminals show that the reference strokes are **folded**. Look at the H stems, the I, the L top and the U tops. Each is a set of nested racetrack loops: the lane at +d on one side turns around and comes back as the lane at −d on the other side. The current cap is a triangle fan whose lane coordinate comes from angle (`at(p, Math.sin(a))`), so the straight stripes look clipped by a semicircle.

The crossovers have a different problem. The `*-weave` accents are narrow and use a different stripe ratio, so they read as a foreign material. Their roll budgets also exceed π/2: H-cross is roughly .2+.75+.65+2×.4 ≈ 2.4 rad. That's why H-cross, L-weave and O-weave pinch into bow-ties. Reference crossovers stay wide and only foreshorten.

## Suggested changes, by impact

1. **Folded lanes plus a concentric cap** (this fixes the terminals)
   - In the shader, take stripes from `d = abs(u)`, where 0 is the fold slot at the centre and 1 is the rim, instead of from `(u+1)*.5`.
   - Replace the fan with an annular half-disc: rings `r = k/N` and angles `a ∈ [-π/2, π/2]`, with `pos = C + R·r·(sign·T·cos a + Nrm·cosRoll·sin a)` and `uv.x = r·sign(sin a)`.
   - Lanes then flow through as nested returning loops, and the centre becomes a thin dark slot, as in the reference H.
   - For the I and the L top you could go further and generate the doubled path in geometry. Offset the authored path by +w/4, add a U-turn, come back at −w/4, and render one half-width ribbon. Each half can then roll on its own, which gives the reference I's diagonal crossover for free.

2. **Authored band profile instead of `fract(lane)`**
   - Give each shape a cross-section table, e.g. `[rim .08 cobalt, field .30 cobalt+hatch, ivory .07, ink, ivory .10, ink, ivory .06, …, fold slot]`. Pass it to the shader as a small uniform array or a procedurally built 1D data texture. That's data, not a bitmap, so runtime stays image-independent.
   - Target about 30–35% ivory coverage instead of the current ~47%.
   - Always end with a cobalt rim and dark outline. Right now `travel` makes the edge lane flicker between ivory and blue, which produces the grey candy edge.

3. **Curvature decides where the cobalt goes**
   - The reference follows a consistent rule: the broad cobalt field sits on the **convex outside** of bends and the ivory bundle on the concave inside. You can see it in the outer fields of D, O, U and the R bowl.
   - Compute smoothed signed curvature per sample and shift the profile origin, `u' = u − b·tanh(k·κ)`.
   - On straight folded stems it stays symmetric. This one rule replaces most hand-tuning of hierarchy.

4. **Rebuild crossovers from the parent bundle and cap the roll**
   - Give each weave its parent's width (or a clean sub-bundle of its lanes) and the same profile. Start and end it tangent to the parent at matching z, so it reads as the same ribbon passing over.
   - Clamp total roll to about |roll| ≤ 1.1 rad except where another surface hides it, so twists show as lanes bunching on one side rather than pinching.
   - The H crossbar in particular should be a full-width S-sweep, not a narrow strap.

5. **Stop per-lane lateral `travel` in the stills**
   - `.62*sin(s*2-…)` added to `lane` is what makes the I/H/U stems wavy. The reference stems are dead straight.
   - For motion, move the whole profile offset along `s` (bands travel) rather than wobbling lanes against each other.

I'd do 1 and 2 together first: they're one shader change and one cap rewrite. Then 3. Leave 4 until the stems and terminals read correctly, because the weaves are where the R and W are messiest. That's a centreline problem in `geometry.js` (W's stray top-left loop, R-bowl/leg overlap), not a shading one.

I judged from the full-frame stills only; I didn't crop or zoom the reference.

## Adopted

Returning centre lines for the straight stems, concentric terminal bands on other open strokes, explicit ivory-band widths and cobalt outer fields, smoothed curvature bias, wider crossing bundles and limited roll. Shadows no longer write depth and incorrectly occlude their own ribbon surfaces. The final design remains more regular and symmetric than the generated reference.
