# Independent painting screening: ten-dollar session

**Show clock-pulse and parasol first; owl-lion is a worthwhile optional third. Do not show ordinary clock as another finished winner.** The pulse is a clear improvement in recognizable transformation and subject composition. This ranking is based on paintings, not finished-video playback.

## Evidence and scope

Inspected all nine supplied painting sheets with image viewing: two each for clock, clock-pulse and owl-lion, and three for parasol. These cover every half-second painting: clock variants 0–7.5s, parasol 0–9.5s, owl-lion 0–6.5s. Also inspected native 1536×1024 anchors for both clock variants at 3s (`0072.png`) and 7.5s (`0180.png`), parasol at 9.5s (`0228.png`), and owl-lion at 6.5s (`0156.png`). Timestamps are local shot time, confirmed from sheet labels and frame numbering at 24 fps.

Read each saved `config.json` to establish the actual prompt switch and pulse recipe. No motion, prompt success or material quality is inferred from configuration alone. No RIFE videos or their intermediate frames were inspected; this review makes no claim about flicker, interpolation artifacts, transition smoothness or final playback pacing. Only this new Markdown file was written.

## Clock versus clock-pulse

Sources: [clock opening/transition sheet](../exports/ten-dollar-v001/clock/paintings-01.jpg), [clock ending sheet](../exports/ten-dollar-v001/clock/paintings-02.jpg), [pulse opening/transition sheet](../exports/ten-dollar-v001/clock-pulse/paintings-01.jpg), [pulse ending sheet](../exports/ten-dollar-v001/clock-pulse/paintings-02.jpg).

| Time | Clock | Clock-pulse |
| --- | --- | --- |
| 0–2s | Readable brass watch, chain, dark ledge and layered ochre dunes. | Same preserved opening; no independent opening-quality improvement. |
| 2.5s | Dial/hands remain prominent; a small red body-like shape appears behind the watch. | A substantial red snail body and projecting head/feelers appear below and to the right; the chain is no longer the dominant foreground object. |
| 3–3.5s | Still mainly a watch face, with small stalks protruding behind its right edge. | The dial becomes a clear spiral by 3s. Shell, broad textured foot and extended head read together as one snail. |
| 4–4.5s | Hands largely disappear, leaving a radial sunburst disc. Snail anatomy remains partly hidden behind the disc. | Convex coiled shell, grounded foot and long feelers remain readable. The old winding crown becomes a shell-like spire. |
| 5–7.5s | Red chain-like material elongates across the foreground; a small head/stalk cluster remains awkwardly attached behind the shell's right side. | The large spiral shell and head remain the focal subject; the red body has coherent placement beneath the shell rather than reading mainly as an abandoned chain. |

**Transformation:** the original clock concept only partly succeeded in the ordinary branch. Its ending is a watch/snail hybrid with a radial decorative disc, hidden anatomy and a rope-like foreground extension. The pulse produces a plainly recognizable snail by about 3s and maintains it through the ending. It is more than adding shell texture to the watch.

**Material depth:** both openings have convincing metallic rim highlights and a cast shadow grounding the watch. Both later sequences retain a graphic etched treatment, so their broad color areas should not automatically be called degradation. The pulse's spiral has modeled curvature, directional hatching and shaded coils; the body has glossy raised texture and a grounded shadow. There is no obvious collapse into flat blur in the inspected pulse paintings. Ordinary clock retains curved-shell shading too, but its radial face reads more like a decorated disc than a coiled shell. Pulse improves structural legibility without an obvious still-image depth penalty.

**Composition and remaining defects:** pulse places the head visibly in the available right-hand foreground and removes the competing chain trajectory. Its extremely long feelers and oversized shell are stylized rather than naturalistic. The inherited crown/spire remains an odd silhouette and crowds/clips the upper edge in late paintings; the subject is not perfectly framed. The original's upper silhouette also becomes crowded, so this is not solely a pulse defect. The underlying desert/ledge composition survives in both.

**What changed in the recorded recipe:** config retains the same seed, prompts, duration and motion, with a saved prefix through frame 48 (2s). From 2.5s the pulse uses `[0.7, 0.5983181, 0.3627179, 0]`, returning to `[0.6, 0.5128441, 0.3109011, 0]` at 4.5s. All three nonzero sigma values rise during the pulse; this is not an isolated first-sigma change. The visible result supports this pulse for this shot, not a universal recommendation to increase noise. Whether its larger early change interpolates pleasantly remains a playback question.

**Verdict:** choose clock-pulse over clock. The important finished-video comparison is 2–4.5s; retain enough of the watch opening for the transformation to have meaning. Native evidence: [clock at 3s](../exports/ten-dollar-v001/clock/anchors/0072.png), [pulse at 3s](../exports/ten-dollar-v001/clock-pulse/anchors/0072.png), [clock at 7.5s](../exports/ten-dollar-v001/clock/anchors/0180.png), [pulse at 7.5s](../exports/ten-dollar-v001/clock-pulse/anchors/0180.png).

## Parasol

Sources: [0–3.5s](../exports/ten-dollar-v001/parasol/paintings-01.jpg), [4–7.5s](../exports/ten-dollar-v001/parasol/paintings-02.jpg), [8–9.5s](../exports/ten-dollar-v001/parasol/paintings-03.jpg), [native 9.5s ending](../exports/ten-dollar-v001/parasol/anchors/0228.png).

- **0–2.5s:** unmistakable red umbrella with fine ribs, translucent fabric and a rigid hooked handle. The large solitary canopy is readable against dark water, with sand ripples establishing the space below.
- **3–3.5s:** after the 3s prompt switch, the handle breaks into thin irregular trailing forms and the canopy edge softens. This is an intermediate umbrella/jellyfish hybrid, not yet a fully resolved jellyfish.
- **4–5.5s:** ruffled membranes, hanging tissue and separate fine strands develop; the rigid hooked handle is gone. Residual radial lines still recall umbrella ribs.
- **6–9.5s:** a transparent domed bell, scalloped fleshy rim, long tentacles and broader ruffled central appendages read as a jellyfish. At native size, the final image has visible internal red canals and layered translucent tissue. This is a successful subject change, not simply an umbrella with a new surface pattern.

**Material/depth:** the opening's shiny fabric becomes a softer, more painterly translucent body. Fine textile contrast decreases, but visible membranes overlapping dark water and sand, modeled rim folds and the seabed shadow preserve volume and separation. I do not see a general collapse of depth. Sparse elongated tentacles are a finishing risk to inspect, not an observed RIFE defect.

**Composition:** the bell and main appendages remain identifiable with room around them; a few very fine trailing strands approach or reach the frame edges. The sand and dark water provide a much calmer field than the cathedral portraits. The large canopy/bell silhouette changes less than clock-pulse's anatomy, so the transformation is subtler at thumbnail size, but the disappearing rigid handle and emerging biological appendages provide concrete endpoint differences.

**Verdict:** primary shortlist. It provides a distinct subject, setting and material treatment. Prioritize finished-video inspection from 2.5–6s and check whether the later resolved jellyfish needs its full duration. Do not infer that a repetitive-looking sheet means the video is boring.

## Owl-lion

Sources: [0–3.5s](../exports/ten-dollar-v001/owl-lion/paintings-01.jpg), [4–6.5s](../exports/ten-dollar-v001/owl-lion/paintings-02.jpg), [native 6.5s ending](../exports/ten-dollar-v001/owl-lion/anchors/0156.png).

- **0–1s:** recognizable accepted owl within layered ivory/cyan architecture.
- **1.5–2.5s:** after the 1.5s prompt switch, the hooked beak broadens into a dark feline nose and muzzle; forehead/cheek feathers begin becoming curled locks. The early intermediate remains a hybrid.
- **3–4s:** paired muzzle pads, whisker dots, a broad nose and a surrounding curled mane make the head clearly feline. The endpoint increasingly reads as the requested mechanical lion.
- **4.5–6.5s:** a legible stylized lion head with modeled golden brow/nose planes and an ivory curled mane. The former foreground ornament persists as a prominent forehead plate, eventually with a central inset resembling an extra eye/jewel; this can compete with the two actual eyes.

**Material/depth:** strong glossy ceramic and metal modeling lasts through 6.5s. Curved highlights, recessed rings and deep cavities are especially convincing. Some feather complexity becomes smoother curls and plates, but the face is not flattened or washed out. The structural feline change is real despite substantial inheritance of the owl's eye placement and setting.

**Composition:** the main face stays readable inside the circular frame; the forehead ornament obscures part of the head and the architectural border remains busy. It is polished but less novel within this project: cyan eyes, ivory machinery and another animal portrait repeat the accepted Oracle/owl vocabulary.

**Verdict:** worthwhile optional third for a clear additional animal transformation and strong material depth. Do not rank it above the more distinct concepts merely because it repeats a visually reliable recipe. Inspect the finished 1–4s transition before declaring its morph smooth.

## Shortlist to show

1. **Clock-pulse** — strongest improvement over its control and a clearly readable watch-to-snail change. Watch for body emergence at 2.5s and the spiral at 3s. Keep ordinary clock available only as a diagnostic comparison if the pulse itself is being discussed.
2. **Parasol** — different palette, spacious setting and translucent material; a readable umbrella-to-jellyfish change with a subtler silhouette transition. Watch the rigid handle disappear and biological appendages develop across 3–6s.
3. **Owl-lion, optional** — coherent feline anatomy and retained glossy depth, but familiar imagery and a persistent forehead ornament. Include when three examples help demonstrate breadth; two primary clips are enough for a concise first showing.

This is a painting shortlist, not a final film ranking. Main should make the final selection after the 24 fps RIFE deliveries are ready, particularly checking the pulse's larger transition, parasol's thin strands, and the repeated facial features in owl-lion. No additional generation is requested by this review.
