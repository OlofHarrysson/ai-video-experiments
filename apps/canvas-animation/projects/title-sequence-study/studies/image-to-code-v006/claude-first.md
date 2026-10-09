# First reconstruction critique

Read-only consultation, 2026-10-09. CLI 2.1.280, resolved model `claude-opus-5-5`, high effort, included subscription path. Reviewed output-second against the generated reference. Advisory judgments; not human approval.

I compared the two images at full size and in side-by-side 2× crops of H, O, R, S, D, I/L, the W swashes and the base.

**Biggest takeaway:** the reference is built like a carved enamel sign. Each letter has chamfered faces with a sharp ridge down the middle, one thin gilt edge, a crimson lip, and a deep violet extrusion that flares outward. The current render reads as inflated vinyl tubes with copper piping. The silhouettes and placement are already close. Most of the gap is in how each letter is built in layers, not in the outlines.

## 1. How the letters are built (biggest gap)

These problems come from the renderer's structure. Tuning colours won't fix them.

1. **The rounded serifs are mostly caused by the renderer, not the outlines.** The gold band sits in `d ∈ [-15, 0]`, which is a 15px *outward* offset of the outline. An outward distance offset always rounds convex corners with a ~15px radius, so every serif tip and spur gets blunted. The extrusion makes it worse: it uses a 32px round-joined stroke (`lineWidth=32`, `lineJoin='round'`).
   - **Fix:** make the authored path the *outer* edge of the gold. Draw gold at `0 < d < rim` and the face at `d > rim`. Insetting keeps convex corners sharp and only softens concave corners, which matches the bracketed serifs in the reference. Drop the stroke on the extrusion layers.
2. **The faces are puffy pillows instead of chamfers.** The reference H, I, L and R stems are two flat facets meeting at a crisp ridge, one lit and one shaded. `slope=pow(1-t,1.4)` produces a rounded dome.
   - **Fix:** use a linear height, `h = min(d, B)`. With a large `B`, the facets meet at the stroke's centre line, where the distance gradient flips and gives a natural sharp ridge. Reduce the 5-pass blur to 1–2 passes so the ridge stays crisp. Use the full ridge on the ivory letters and a slightly softened one on pink.
3. **The gold looks like doubled piping.** The dark groove at `t∈[2.8,4.2]` splits it into two cords. The `sin(...*9)` banding adds a knurled, rope-like texture, and the colour is orange-copper.
   - The reference gold is a single band about 4–7px wide. It's thicker on outer swash edges and thinner inside counters. Its colour is yellow gold: highlight `#fff0b0`, mid `#e0a43c`, shadow `#6b3a0e`. Each band splits cleanly into light and dark depending on which way the edge faces.
   - **Fix:** remove the groove and the banding. Shade the band as a half-cylinder against a horizon-style environment: bright above, dark below, with a sharp transition.
4. **The crimson lip is missing.** On every ivory letter (most visible in the H, O and R counters) and faintly on the pink ones, a red band sits between the gold and the violet. It's the front of the sidewall catching light. It's a large part of what makes the ivory feel set into something. Your current render has no equivalent.

## 2. Extrusion and depth order

5. **The extrusion goes the wrong way.** In the reference it flares outward from the centre and downward. Letters on the left show sidewall on the left (W's top-left curl, H), letters on the right show it on the right (D, S), and everything shows it below. The code shifts every layer down-right (`translate(z*.47, z)`), so the W curl's sidewall is on the wrong side.
   - **Fix:** apply a per-layer transform of scale about a point near `(768, ~350)` plus a downward shift. Measure the sidewall offset at 4–6 points in the reference to fit it.
6. **Draw order flattens everything into a sticker.** All sidewalls are drawn first, then all faces. In the reference, the HOURS extrusion lies over the WILD faces (around H's top-left and O over I).
   - **Fix:** use a back-to-front list: WILD, then the ribbons, then HOURS. Draw each element's sidewall and face together.
7. **The sidewall needs real shading and crisp edges.** The current version has a mauve haze that spills well past the letters (look under H, O and the base). The reference background stays pure black right up to a crisp sidewall edge.
   - The reference sidewall runs from crimson to violet `#3a1650` to near-black `#12051a` with depth. It has long lavender streaks on the sides that face the light.
   - **Implementation I'd use:** do the extrusion in the shader. For each pixel, loop over about 32 depth steps and sample the outline's distance field at the inverse-transformed position. Take the front-most hit, which gives you `z` (for the colour ramp) and the outline normal (for the lighting). This replaces the canvas layer stack and its gradient.

## 3. Shapes that are wrong or missing

8. **The base plinth is missing.** This is the most visible outline difference at full size. Under HOURS, the reference has a continuous gold-edged base running from H to S. Its lower edge is two concave arcs meeting in a long downward point near `(712, 965)`, with the star on top. You only have the left half (`under-Hours`) plus a separate diamond hanging below.
9. **The star in the O is the wrong shape.** The reference has a tall four-point star with concave sides, roughly 120×45px, nearly filling the counter. It has four flat shaded facets and no rim. Yours is a small squat gem with a fat gold border, which reads as a button.
10. **The R has a medallion that isn't in the reference.** Remove `diamond-R`. The reference has a pointed spur built into the R's left stem at bowl height. The H's left stem has the same kind of spur where yours has a small rounded nub. Draw both into the outlines.
11. **The W lacks thick-thin contrast.** Its big strokes taper much harder in the reference, with real hairlines at the turns. Yours is close to monoline. Even a small push on stroke contrast will help it read as calligraphic.

## 4. Lighting

12. **The ivory is blown out and looks like chrome.** The reference is warm satin cream: lit facet about `#f3e7cc`, shaded facet about `#d6bf95`, and almost no specular. Remove the strip reflections on ivory and let the chamfer facets do the work.
13. **The pink is a flat colour.** The reference shifts from coral-pink at top-left to deep raspberry at bottom-right. Its highlights are long soft streaks running *along* the stroke, not thin edge lines. A small amount of fine grain running along the stroke direction (perpendicular to the distance gradient) adds a lot of the high-fidelity feel.
14. **The glints are too small and too dim.** The reference glints are four-point stars with long thin horizontal and vertical rays (about 60–100px) and a warm bloom. Your glint at `(1129, 507)` doesn't match one in the reference. There's one near the L's curl, around `(1060, 385)`.
15. **There's an aliasing artifact.** A dotted or speckled light fringe runs along the outer gold edge (clear in the H and O crops). Use `smoothstep` anti-aliasing on the edge alpha and/or render at a higher scale, and check that edge alpha isn't letting bright colour bleed into the background.

## Suggested order for the remaining ~5h45m

1. Inset rim, sharp corners, linear chamfer with a ridge, single yellow-gold band (#1–3). About 1.5h, and the largest perceived gain.
2. Extrusion in the shader with outward flare, crimson lip, no haze, and per-element draw order (#4–7). About 1–1.25h.
3. Outline fixes: base plinth, O star, R and H spurs, W contrast (#8–11). About 1.5h. Check them against the flat view at 50% overlay before touching materials.
4. Lighting: ivory satin, pink gradient and streaks, glints, grain (#12–15). About 1h.

If time runs short, cut the W contrast and the grain first. The construction fixes, the plinth and the extrusion direction matter much more.

I didn't change any files. The only things I wrote are the comparison crops in `/tmp/wh/`, outside the repo, if you want to look at the same views.
