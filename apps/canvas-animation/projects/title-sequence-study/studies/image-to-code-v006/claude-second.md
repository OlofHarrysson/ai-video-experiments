# Second reconstruction critique

2026-10-09. Resolved model `claude-opus-5-5`, high effort. Advisory review of output-sixth; no human approval.

I'd keep the silhouettes and rewrite the face/rim shader. The gap is mostly at the edges: the reference stacks about six crisp concentric bands at every edge, and ours has two or three, which come out blurry, brown and speckled. That edge detail is what makes the reference look intricate. You don't need meshes or more hand-drawn contours for this. You need one shader that defines the edge bands in pixels.

I compared 4–5× side-by-side crops in `/tmp/wh6/` (outside the repo) and ran colour statistics on both full images.

## Biggest differences, ranked

**1. The band stack is wrong.** In `Oedge.png`, `Hstem.png` and `Ucup.png`, the reference ivory edge runs from the outside in like this:

- crimson, about 4px
- a dark seam
- gold, about 6px, bright along its full length
- a dark seam
- a chamfer, about 10px
- an inline step, a faint light line plus a shade line
- a flat satin face

Ours has a dark-brown outer band, a thinner gold band, a dark groove, and then a soft pillow face.

- Measured gold coverage is **6.7% of the frame in the reference and 3.6% in ours**. The rims need to be about twice as wide.
- Our gold is also paler. Average colour is (220,171,92) against the reference's (217,146,61).

**2. Brown outer ring, hard thresholds and speckle.** In `Itop.png` and `Dtop.png`, every rim has a dark-brown cartoon outline with a dotted light fringe outside it. It comes from three places in `renderer.js:102-104`:

- the `t<.10` brown branch
- the `t∈(.12,.19)*.32` groove
- unsmoothed if-thresholds

On top of that, the gold environment (`renderer.js:25-31`) turns brown on every downward-facing edge. The reference gold has a bright core along every band whatever its orientation. This is the strongest "synthetic" cue up close.

**3. The ivory faces are blurred pillows, not carved.** The reference H spur and serif junctions have crisp mitre creases (`Hstem.png`). Ours has soft grey airbrush blotches at concave corners. The causes:

- 5 blur passes on a distance field built from a hard alpha cutoff (`renderer.js:142`)
- `smoothstep(13,20)` on the slope
- faint horizontal ripples, which look like the distance field's pixel stepping showing through

**4. The highlights look airbrushed.** The authored shine is an 18px stroke blurred by 14px and mixed up to 0.93 (`renderer.js:147,113-115`). That produces the cream smears on D and W. The 1.3px hairline also crosses the I like a wire. Most reference highlights are thin, crisp specular lines just inside the rim, plus gentle tonal shifts.

**5. The pink is too dark.** Reference pink averages (245,40,100). Ours averages (219,23,80), and 10.5% of our frame falls into the crimson-dark range against 4.7% in the reference. The shift to `dark` at `renderer.js:43-45` is too strong.

**6. The plinth and the HOURS sidewall are stepped.** In `plinth.png`, the reference base is one continuous gold rail with a single smooth purple swoosh below it, meeting in a long point. Ours has thin V-shaped ribbons, and each letter has its own block extrusion with vertical cut edges under U, R and S.

**7. The sidewalls are slightly too dark and lack the brushed lavender streaks.** This matters most inside the W curl. It's lower priority than the items above.

## ⚠️ RISK OR DEVIATION: where my earlier advice was wrong, and where it was misread

- **The crimson lip.** I described it as the front of the sidewall, and you implemented it as sidewall `z<5`. That was my mistake. In the U counter's bottom edge (`Ucup.png`), crimson shows where a downward extrusion can't be visible. It's a **front-plane outline band outside the gold**, somewhat wider on downward-facing edges.
- **The centre ridge.** I over-read this. The ivory stems are **flat**, with a narrow perimeter chamfer of about 10–12px and an inline step. The facets come from the creases where that chamfer turns corners, not from a ridge down the middle.
- **"Remove the groove, single gold band."** This was misapplied: the groove is still there, and a brown outer band was added on top. The reference does have a second line next to the gold, but it's crimson, not brown.
- **"Soft streaks along the stroke."** I meant low-contrast shifts. They were implemented as near-white blurred strokes.

## Your four options

| Option | Verdict |
|---|---|
| Different shader construction | **Yes, the main lever.** Replace the `t`-ratio thresholds with one profile function `profile(s)`, where `s` is the absolute distance in px inside the outer silhouette (the existing `.g` field). It returns the material, the height slope `h'(s)` and the band colour. Normal = `normalize(vec3(-normalize(grad)*h'(s),1))`. Smooth every band edge with `fwidth(s)`. |
| Better field quality | **Yes, it's a prerequisite.** Sub-pixel seams need 1–2 blur passes rather than 5. Make the edges more accurate with a coverage correction (seed the edge distance from the antialiased alpha, `0.5-a`), or try `SCALE=3` with 2 passes. Before tuning, check the field with an isoline debug view. |
| Hand-authored contours | **Only in a few places:** the plinth, the sharp H and R spurs (`geometry.js:70` is still a smooth bulge), and optionally a larger O star. The band stack and inline should be offsets, not drawn by hand. |
| Mesh bevels | **No.** Seen head-on, a bevel mesh gives the same normals as the profile function, and offset meshing of sharp Bézier serifs would take the rest of the time. |
| Parameter tuning | Needed, but only after the profile rewrite. |

## Suggested sequence (about 4h of the remaining time)

**1. Profile shader, about 1.5h.** Widths in px measured from the outer edge. These starting values come from the crops:
- **Ivory:**
  - 0–4.5: crimson half-round (#5a0610 at the edges to #c01a32 in the core)
  - 4.5–5.2: seam
  - 5.2–11: gold half-round
  - 11–11.6: seam
  - 11.6–22: chamfer with slope about 0.5
  - about 22: inline as a light/dark pair
  - beyond that: flat satin
- **Pink:**
  - 0–3: muted dark gold
  - 3–11: gold
  - 11–12: crimson seam
  - 12–14: crisp edge specular on light-facing sides
  - inward: rounded shoulder, brighter overall
- **Gold lighting:** about 75% "ring light", meaning bright at the band centre whatever the orientation, and 25% directional.

Check by regenerating `Oedge`, `Itop` and `Hstem` at 5× against the reference.

**2. Field quality, about 0.5h.** Done when the creases at the H spur and serifs come out sharp.

**3. One plinth shape plus a shared HOURS sidewall, about 1h.** Build the sidewall pass from the union field of H, O, U, R, S and the plinth, so the extrusion becomes a single swoosh. Fit the plinth to the reference points: left end about (193,960), gold tip about (713,973), right end about (1260,967).

**4. Highlights and colour, about 0.5h.** Cap the shine at about 0.35 alpha, use a width of about 6px with about 3px of blur, keep the hairlines within about 6px of an edge, and remove shine from ivory. Re-run the colour statistics. Targets: gold about 6–7% of the frame, pink mean about (245,40,100), crimson about 5%.

**5. If time remains:** sharp spurs, the larger O star, and brighter sidewalls with streaks.

If time gets tight, protect steps 1 and 3. Together they cover most of the gap you're seeing.
