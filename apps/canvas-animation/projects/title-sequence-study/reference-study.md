# Enter the Void: first visual study

2026-10-09. Reference supplied locally by Olof; provenance and SHA-256 are in [reference-source.json](reference-source.json). Source timestamps below refer to the local file, not a derived clip.

## What was inspected

- Twelve overview frames across 0–138 seconds, including eight from 110 seconds onward.
- Twelve additional style samples from 110.5–129 seconds.
- Every displayed frame in three requested windows: 111.8–112.3, 114.8–115.3 and 126.8–127.3 seconds. The extractor includes the frame already on screen at each start; exact decoded timestamps and frame numbers are in each review manifest.
- All four contact-sheet pages for those dense windows, plus the overview and style-range sheets.
- Automated visual/audio measurements on a derived 105–135-second clip. No listening-based musical or precise beat-synchronization claim is made.

Local inspection artifacts are under `references/inspection/{overview,type-range,transitions,shortlist}/v001/`. Each includes extracted images, contact sheets and a `review.json` with exact decoded timestamps. These files contain reference pixels and remain ignored by Git.

The supplied file is 141.033 seconds, 1280×544, 24000/1001 fps (~23.976). Its filename says 1080p, but the decoded dimensions are smaller. The original was preserved with a verified independent APFS copy. All completed extraction manifests confirm the source was unchanged.

## Observations

**Typography is the main image.** Most inspected cards use a black ground, with names occupying much of the wide frame. Faces and scenery are not needed to make the credit section visually varied. The 138-second sample has moved into live action; the 132-second sample is black.

**A name keeps its meaning while its visual identity changes.** Around 111.8–112.3, PAZ / DE LA HUERTA moves through outlined slab lettering, parallel-line geometric capitals, the surname alone, a combined block composition, decorative script with stars, and multicolored contours. This is a succession of designed cards, rather than one font with a universal glitch effect.

**The treatments are deliberately heterogeneous.** Samples include blackletter at 110.5 and 114 seconds, circular dot construction at 111.25, large Japanese lettering at 112.5, angular outlined lettering at 115.5, dense contour echoes at 118.5, rainbow outlines near 120, overlapping geometric outlines at 123, and dense multicolor dots around 127.17. Japanese and Latin lettering sometimes function as overlapping graphic layers with different scale and prominence.

**The frame windows show hard replacement and brightness alternation.** In the PAZ window, frame 2681 changes to a new parallel-line design, 2682 dims it, 2683 switches to the surname, 2684 holds it, and 2685 changes the layout again. A two-frame interval here is approximately 83 ms. Other sampled pairs similarly retain a layout while changing brightness or color. This cadence is directly observed in the selected windows, not established as a rule for the whole sequence.

**Scale and layering create additional impact.** Around 114.8–115.3, large serif lettering gives way to heavy rounded lettering, overlapping Latin/Japanese versions and a compact central pile of those layers, before the next name arrives. Around 126.8–127.3, tall condensed lettering shifts placement and scale, overlays a contrasting thin serif treatment, changes to contours, then to a tilted dot pattern.

**Black provides a recurring visual anchor.** Magenta, red, green, violet, yellow and white are used in changing combinations. Neon outlines are one part of the vocabulary; solid white and colored letterforms are equally important in the sampled range.

## Measurements and limits

The Animate analyzer reported three candidate cuts and zero after its stepped/flicker filtering on the 30-second derived clip. The dense frame windows visibly contain many abrupt layout replacements, so those counts do not describe this sequence's editorial rhythm. Its adaptive threshold is poorly suited to treating persistently high frame-to-frame variation as discrete cuts; that explanation is an interpretation of the method, not a calibrated benchmark.

The per-second analysis shows substantial continuous image change through most of the credit section, then an almost static, very quiet interval around source 132–134 seconds. Source 105 seconds is zero in the analysis report; timing is approximate because the tool rounds the fractional frame rate. The derived-clip extraction also emitted an H.264 reference-frame warning during the seek. Use the exact original-file frame manifests for timing evidence; do not treat the derivative as a frame-exact timing master.

Sparse images and short frame windows establish graphic treatments and local switching patterns. They do not establish perceived normal-speed rhythm, emotional response, exact synchronization to the score or which treatments Olof most wants to borrow.

## Implications for our original piece — proposals

- Start with a small set of short, meaningful words. Keeping a word recognizable across transformations can provide continuity despite large visual changes.
- Design distinct typographic compositions first, then sequence them. Changing a glow color alone would capture only a small part of the reference.
- Use differences in density, scale and brightness as compositional choices. Determine our own pacing and intensity after the theme is clear.
- A theme involving identity or transformation could use the same word changing visual identities. A meaningfully different direction is an external world of signs, places and encounters. These are discussion prompts, not selected themes.
- Font selection, language, source music, duration, aspect ratio and renderer remain undecided. No borrowed soundtrack or reference imagery is an approved output asset.

Next human decision: what the original piece should express, and which part of this reference matters most to Olof—typographic variety, rapid switching, layered complexity, color or the overall feeling.
