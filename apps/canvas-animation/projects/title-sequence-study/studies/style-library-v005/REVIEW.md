# Screening record · v005

2026-10-09. Assistant judgments below are provisional; Olof has not reviewed this library's new outputs. The earlier Night Fever still and v004's fixed-composition material cycling remain the known positive feedback.

## Deliveries

| Local artifact | Format | Purpose |
| --- | --- | --- |
| `output-delivery-showcase/showcase.mp4` | 25.417 s, 610 frames, 1280×720, 24 fps | Calm opening, native material motion, unlike constructions, denser layouts, brief peak and release |
| `output-release-library/catalogue.mp4` | 34 s, 816 frames, 1280×768, 24 fps | Seventeen labelled constructions; each first holds, then cycles four states |
| `output-review-layouts/composition-catalogue.mp4` | 14 s, 336 frames, 1280×768, 24 fps | Seven labelled layout studies with four treatments each |

A fourth, 16-second native-motion comparison holds eight chosen treatments for two seconds each, isolating internal movement from state cycling: `output-native-review/native-motion.mp4` (384 frames, 1280×768).

All are H.264 / yuv420p with no audio. File hashes and exact export checks are in [release.json](release.json). The [review page](review.html) links these current outputs. Earlier outputs are preserved; names containing `first`, `expanded`, `final` or `reviewed-pass` are historical iterations, not the canonical delivery pointers.

## Observed visual results

- Opening the W–i join removed a knot that affected neon, resin and compound lettering. The serif/script hierarchy is clearer than the crowded wall of signs.
- The brush treatment changes stroke thickness and silhouette. Cream with compound borders and engraved gold give a useful alternative to the cold/hot monoline tube. It remains a designed single word.
- A small smooth union improved reflective crossings; silver no longer has the conspicuous horizontal cut across the l stem. Pinches remain at some loops and joins. Rose resin is still the safer long-hold material.
- Large cropped depth, tiny chrome and a giant letter behind a hairline word provide genuine changes of scale. The print family supplies a bright, flat counterpoint to black-ground emissive artwork.
- Three exposures and the sign wall are crowded by design. The lowest exposure and some peripheral sign fragments are cropped. These are peak accents, not the preferred readable holds. The sign wall remains a collage of systems rather than one fully art-directed location.
- Marquee bulbs now follow interior distance ridges instead of filling a uniform grid. Spacing and the fan's relation to the plaque remain optical refinement opportunities.
- A wider smooth-union trial made the metal look swollen and introduced new ridges, so it was preserved as an experiment and rejected. Silver remains in the slow catalogue for inspection, but was removed from the showcase in favour of a longer ornate serif sign.
- The sparse orbital dial and darkest comb/slat variants can become faint after reduction. Thin lines and the busiest modular weave require checking at final delivery size.

## Visual evidence inspected

- Actual supplied All Of The Lights source: 20 overview frames, 38 offset style samples, and 28 dense transition frames. [Source observations](../../reference-all-lights-study.md) retain the times and evidence boundaries.
- All 68 construction states on three readable sheets, followed by revised full-size neon and reflective-script stills. Current sheets: `output-release-inspection/states-{1,2,3}.png`.
- All 28 layout treatments on `output-review-inspection/composition-states-{1,2}.png`, including the added brush sign.
- The encoded construction catalogue's overview and dense depth/tube/marquee/material windows under `output-motion-reviewed-pass/inspection/`; final artwork changes were additionally inspected as full-size stills and in the release showcase.
- Final encoded showcase: 12 distributed frames and every displayed frame in 8.625–9.125 s and 21.583333–22.083333 s. The first window shows a held brush plate changing to engraving without drifting; the second shows the intended pairs of held frames in the peak. `output-delivery-showcase/inspection/v001/` contains the final overview/peak sheets; `inspection/brush/v001/` contains the brush window. Both retain exact timestamps.
- Native-motion reel: all eight overview cards and every frame in the tube (2–2.25 s), slats (10–10.25 s) and compound brush (14–14.25 s) windows under `output-native-review/inspection/v001/`. Gas segments advance on twos; slices and brush stripes move while the card placement stays fixed.
- Preview and review pages at desktop and 800×700, including actual loaded video frames. Controls remain visible and artwork is undistorted.

These inspections establish composition, registration, cuts and export integrity. They do not establish the perceived rhythm of normal-speed playback, musical synchronization or an audience response. No audio review occurred because the studies are silent.

## Functional checks

- All 17 families rendered four unique states; out-of-order seeks returned byte-identical images. Short and long sample words rendered without browser errors.
- Native frame 0 versus 11 differed in 25 of the 68 states. This is a change-detection sample, not a motion quality score. Many states deliberately hold and rely on material edits.
- Each of seven layouts passed repeatable-seek checks and exported its four states. Fixed-layout word controls are hidden.
- UI family/state selection, explicit invalid-alphabet errors, play/pause, native-only playback preserving the selected state, and PNG download passed.
- All four videos loaded, sought and briefly played in headless Chromium. The review-page images loaded and its layout did not overflow at 800 px.
- FFprobe decoded all 2,146 delivered frames. Video rate, dimensions, duration and absence of audio match the export specifications. Every one of the showcase's 40 black frames matches a deliberate black interval in its timeline; there are no unexpected blank frames.
- The independent distance-transform oracle passed 18 masks / 1,489 pixels with maximum error 2.42e-8. This checks one numerical primitive, not the appearance of the materials.
- JavaScript syntax checks and `git diff --check` passed. No dev service or paid media job was started.

## Review decisions still open

Which four to six identities feel worth carrying into a film; how aggressive the fast cuts should be; whether the brush or neon script is preferable; and what words/theme/sound should give the escalation meaning. These remain human artistic decisions. Do not treat this experimental edit as the approved film storyboard.
