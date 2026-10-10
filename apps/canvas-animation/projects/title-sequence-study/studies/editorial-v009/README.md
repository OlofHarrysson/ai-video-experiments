# Make it Move — silent editorial study (v009)

A 12-second typography edit built around eight selected compositions. [Watch the film](review.html) or [explore the editable renderer](index.html). This tests whether stronger selection, changes in scale and deliberate cutting can improve on the isolated v006–v008 loops. “MAKE IT MOVE” is test copy, not the final film theme.

Olof authorized this experiment after discussing the production processes behind the two references. He explicitly requested silence. No soundtrack, music generation or audio analysis was used.

## What changed

Twenty candidate layouts were drawn across ten construction families. Eight were selected after two visual revisions and a [read-only Claude consultation](claude-review.md). The discarded candidates remain in the interactive preview and immutable output folders.

The main edit uses 20 shots lasting 6–21 frames (0.25–0.875 seconds). The opening spells out MAKE → IT → MOVE through an enormous red/black card, a tiny red word in black space, and a metallic hero. The same words return in changing compositions, with occasional complete-phrase anchors. The pace varies locally rather than accelerating toward a chaotic ending.

| Selected construction | Role in the edit | Movement |
| --- | --- | --- |
| Monument | Immediate scale and weight; the verb MAKE | Static image, editorial replacement |
| Small signal | Brief negative space; the word IT | Static image, short hold |
| Redline metal | Wide, dimensional MOVE | Specular light crosses the fixed letters |
| Cut-pressure | Dense flat lime typography | Horizontal letter sections slide into registration |
| Rose blackletter | A complete, compact phrase | Held artwork, selective light spread |
| Lamp wall | Luminous sign construction | Whole letters dim in succession |
| Carved interference | Fine pattern inside heavy glyphs | Concentric bands travel through the fixed silhouette |
| Cathedral depth | Receding repeated word outlines | Contours move through perspective |

The serif/ornament candidates were excluded because they were comparatively polite and repeated a supporting face already overused in the first pass. The giant purple slab candidate was excluded in favour of true negative space. The orange blackletter and alternate metal sign were not added merely to increase the count.

## Visual revisions

- Removed most repeated italic supporting copy. Individual words now carry the phrase across cuts.
- Corrected gradient placement so metal reflects broad light bands rather than becoming a nearly uniform striped surface. Removed the heavy hatching.
- Gave blackletter an ivory face and violet edge, separating its material from chrome.
- Added restrained bloom only to luminous cards, keeping flat print and metal sharp.
- Reduced depth layers and palette, with a centred vanishing point for the selected tunnel.
- Increased optical line travel and simplified its palette.
- Built the final lamp word from four separately positioned glyph masks. Dimming now follows exact glyph membership rather than arbitrary columns through a letter.

## Implementation and provenance

Everything visible in the film is rendered in Canvas 2D from vector paths and procedural shapes. No reference-video pixels or generated raster images enter the render. Existing local fonts are converted to path data by `prepare.mjs`; fonts are not loaded at playback. The [font provenance](../../fonts/README.md) and adjacent SIL OFL files cover Anton, Audiowide, Cormorant Garamond, Alfa Slab One and Racing Sans One. UnifrakturCook and its licence remain under `../typography-v001/fonts/`. The two razor candidates use authored polygon lettering.

`art.js` owns drawing, `edit.js` owns shot order and duration, and `viewer.js` owns playback. `build.mjs` combines them and the vector data into the self-contained `index.html`. Browser time only selects preview frames; each artwork frame is a deterministic function of its explicit frame number. The media export has no network or external image dependency.

The existing project Playwright/FFmpeg path is used for rendering and validation. Native Animate sound/story-arc checks are not applicable to this silent typography cut. No new rendering framework, package, dev server, paid API generation or cloud resource was introduced.

## Delivery and verification

Selected media: `output-delivery/make-it-move.mp4`. Earlier candidate sheets and cuts remain preserved. Render and screening reports are local beside their artifacts. `delivery.json` records the selected media hash.

The renderer checks deterministic seeking, exact frame-0/frame-288 equality, visible content on all 288 frames, zero network requests, runtime errors, frame count, duration, silent video streams and full FFmpeg decoding. The separate screening harness decodes 27 frames around the chrome/slat transition, lamp illumination and loop boundary. It also exercises browser video playback to completion, preview playback, a PNG download and mobile overflow.

The first contact-sheet compositor produced blank thumbnails despite nonblank individual renders. Review sheets now compose the saved PNG frames, rather than repeatedly copying a mutable staging canvas. Local-file image security initially blocked canvas export in the screening page; the harness now passes its already-decoded frames as in-memory image data. These are review-tool corrections, not extra artwork assets.

Assistant screening covers the candidate sheets, selected full-size stills, the complete edit contact sheet and the three dense decoded windows. Browser playback completion is a technical check, not a human judgment of rhythm. Human taste review of the final silent cut is pending.

## Limits and next decision

This is a test of art direction and editing, not proof of parity with either reference. The chrome and slat constructions are still relatively conventional, and the final set relies substantially on existing typefaces. The hand-built razor alternative remains available, but was not selected simply because its implementation was more elaborate. Without sound, the edit's perceived intensity remains a deliberately incomplete test of a finished film.

Judge whether the interplay of giant/small, dense/open, flat/luminous designs is closer to the intended feeling before adding more effects or length. No film subject, hackathon story or soundtrack has been chosen.

## Reproduce

From the repository root:

```sh
node apps/canvas-animation/projects/title-sequence-study/studies/editorial-v009/prepare.mjs
node apps/canvas-animation/projects/title-sequence-study/studies/editorial-v009/build.mjs
node apps/canvas-animation/projects/title-sequence-study/studies/editorial-v009/render.mjs output-new --motion
node apps/canvas-animation/projects/title-sequence-study/studies/editorial-v009/screen.mjs output-new output-screen-new
```

Output directories are immutable: choose a fresh name for each run. The selected review page points to `output-delivery`; the screening command explicitly loads whichever output directory it receives.
