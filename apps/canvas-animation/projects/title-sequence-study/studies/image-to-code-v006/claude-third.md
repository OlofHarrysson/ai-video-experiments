# Third visual consultation

Read-only Claude Code consultation, 2026-10-09. Author model: claude-opus-5-5. Reviewed output-finish-01 against the generated reference.

## Verdict

This is now a strong graphic object at actual size. It reads as the same logo, it's legible and clean, and the construction looks intentional. That's a real step up from output-sixth. Next to the reference, though, it still looks materially plainer. The cause is no longer the silhouettes or the edge bands. The ivory, the gold widths and the band stack are now close, so stop spending time on them. The remaining gap is mostly about how dark the image is, how light falls across it, and a few pieces of jewellery:

- The sidewalls are bright, uniform, matte lavender, so it reads as "clean 3D vector text" rather than "lacquered enamel and gilt".
- The plinth is a third hot-pink mass instead of a gold pedestal.
- The pink faces have only tube highlights and almost no light-to-shadow modelling across each stroke.
- The jewellery is underpowered: the glints, the O star, the plinth star and the H/R spurs.

I'd call it about 7/10, up from about 5. The fixes below are all local.

## ⚠️ RISK OR DEVIATION: corrections to my earlier reviews

- **Sidewall direction.** In the first review I said the sidewalls flare outward. You were right that they go down-right. Scanlines at the right edge of the D now show similar sidewall widths in both images.
- **Sidewall brightness.** In the second review I said the sidewalls were "slightly too dark". The opposite is true now:

  | Violet-range pixels | Coverage | Mean colour |
  |---|---|---|
  | Reference | 7.0% | (51,21,62) |
  | Ours | 11.9% | (67,29,86) |

- **Gold.** I said it needed twice the width. That's done: gold is 7.0% of the frame against 8.2% in the reference, and the band widths match on scanlines. Don't widen it further.
- **Pink.** I said it was too dark. Its brightness is fine now. It's slightly too magenta (mean (242,22,90) against (239,39,96)), and the real problem is flat modelling.

## Remaining differences, ranked by impact at actual size

**1. Sidewalls are too light, too uniform and too wide, with crimson glow against the rims.** This is the biggest remaining "luxury and depth" cue.
- In the reference, between I and L, inside the H counter and behind the W, the sidewalls are near-black violet with a few thin glossy lavender streaks.
- At the right edge of the D, the reference goes gold → about 3px of black → about 2px of pink lip → violet. Ours goes gold straight into a red glow and then flat lavender.
- Local changes in `renderer.js:94-99`:
  - **Invert the depth ramp.** `side*=.7+.3*z/depth` makes the back of the sidewall the brightest part. Use something like `side*=1.-.55*z/depth`.
  - **Darken the base.** Use about `mix(vec3(.02,.005,.03), vec3(.16,.06,.22), light)`.
  - **Make the streaks sparse and sharp.** Use a power of about 40 and lower amplitude, so they read as brushed metal rather than haze.
  - **Add a dark seam before the lip.** Black at z 0–2, crimson lip at z 2–5 only. The current lip runs `smoothstep(2,10)` and starts at 0.
  - **Shrink the halo.** Cut the `exp(-pow(best/.75,2))` lavender halo to about a third, or remove it.

  Target: violet coverage about 7% with a mean near (51,21,62).

**2. The plinth reads as a pink banner.**
- `under-Hours` is `material:'pink'` (`geometry.js:59`), which gives a broad hot-pink band under the whole of HOURS. That blurs the WILD/HOURS hierarchy.
- In the reference the plinth is mostly gold bevel with a dark crimson rail. Pink only shows as narrow inlays beside the centre star.
- The centre ornament (`diamond-base`, `geometry.js:104`) is about 28px wide, so it reads as a pencil tip.
- Local changes:
  - Give the plinth a gold-dominant material: wide gold bevel and a dark crimson face, with a pink inlay only within about 120px of centre.
  - Redraw the centre as a faceted gold star, roughly 55–90px wide and about 100px tall, with its point near (713,975).
  - Put a warm glint on the star.

**3. The pink faces have no light-to-shadow modelling.**
- The face colour varies only about ±5% (`vec3(1.,.055,.36)*(.94+.10*dot(...))`). All the variation comes from edge-hugging tube highlights.
- In the reference, each stroke goes from a lit coral shoulder to a raspberry shadow side. Broad diagonal sheens also cross the strokes: look at the big sweep across I/L and on the bowl of the D.
- Local changes:
  - Drive the face colour by a broader normal across the whole half-width, ranging from about (1,.30,.50) lit to (.68,.02,.24) shadow.
  - Add 2–3 soft diagonal sheen bands in screen space, masked to pink, at 0.2–0.3 opacity.
  - Lift the base hue slightly, to about (1,.16,.40).

**4. Glints and the jewellery are underpowered.**
- **Glints** (`renderer.js:230`):
  - Ours are small and cool white.
  - The reference glints are warm gold, with long rays on both axes, shorter diagonal rays, a bloom of roughly 60–80px, and a hotspot on the rim beneath them.
  - Add about 3 more, including the I/L sheen at roughly (700,365) and (890,320), and the plinth star. Check those positions against the reference before committing.
- **O star** (`renderer.js:219-226`):
  - Two of its four planes use pink gradients (`#e82f77`, `#b51755`, `#4c063e`), so it reads rose-coloured.
  - The reference star is bright yellow gold with a warm bloom, and a bit larger.
- **H and R spurs:**
  - Ours are soft ivory kinks that the rim just follows round.
  - In the reference they are faceted gold beads that break into the counter. That's a small authored shape per spur, and very jewel-like.

**5. Smaller items:**
- **Brown outer band on pink letters.** The brown band at s<3 (`renderer.js:127`) still reads as a cartoon outline up close. Replace it with a hairline of about 1px and let the gold reach the silhouette.
- **Ivory chamfer shade looks grey.** `bevelLight` multiplies the cream, which turns it grey. Mix toward a warm shadow of about (.84,.70,.50) instead.
- **Sawtooth artifact.** There's a comb on the sidewall near (375,612), next to the top-left of the H, visible at 1×. A likely cause is the box-edge `continue` at `renderer.js:80`, which only checks the low side of the box. It could also be the padding of 64 being tight relative to depth × 1.25.
- **S join.** Where the lower curl meets the spine, near (1225,800), the bands pinch together.

## Suggested order

1. Sidewall rewrite: about 30–45 min, the biggest gain.
2. Plinth material and centre star: about 45 min.
3. Pink face modelling and sheens: about 45 min.
4. Glints, O star colour and the two spurs: about 45 min.
5. Smaller items as time allows.

After items 1 and 2, re-run the colour statistics and the side-by-side crops. I expect the plain feeling to mostly go after those two.

Side-by-side crops are in `/tmp/wh7/`, outside the repo. The most useful are `Wsidewall.png`, `plinthTip.png`, `I_L.png`, `glint.png`, `Rspur.png` and `artifacts.png`. I didn't change any project files.
