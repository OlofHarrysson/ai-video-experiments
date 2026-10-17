# Glass Tide: layered internal movement

## Direction

Olof prefers the local-curl comparison and requests a longer continuous Glass Tide passage combining varied smooth camera movement with playful internal deformation. He wants twisting, turning and pulling to overlap rather than treating local motion as a single curl preset. Crisp, highly detailed digital art and no cuts remain requirements.

The planned twelve-second passage preserves all 27 paintings of the accepted three-second local-curl opening. The next four seconds bank along the cyan arch while two curls at different locations overlap with a broad travelling bend and a perspective turn. Inspect the actual generated painting before directing the final five-second reveal. Keep movement flowing through changes of direction, and preserve useful open spaces.

## Method

Use the existing recurrent renderer: Krea 2 Turbo, noise 0.72, three Euler intervals, CFG1 and reference conditioning off. Each image initializes from its moved predecessor; RIFE is finishing only. The source clock and seed sequence continue from the approved comparison. This study does not introduce masks, fixed-opening references, a different image model or a new detail pass.

The localized twists decay with radius. The travelling wave bends different strips by different amounts; it is not an object-specific pull. Perspective and global translation/scale/roll supply camera-like travel. Their individual timing and strengths are composed around actual artwork. No new motion primitive or model architecture is required.

- `gt-living-arcades-i`: preserves source 0–312, generates 324–744, seven seconds total. [Frozen matrix](layered-i.json).
- `gt-unfurling-current-j`: preserves source 0–744 and generates 756–1284, twelve seconds total. [Frozen matrix](layered-j.json). The actual source744 painting contains large scalloped ivory fans, a clear central opening and a turquoise glass ribbon. Retain the incoming fields and add a pullback/counterbank, opposite curls on upper-right and lower-left regions, and a vertical travelling bend. New effects start with zero velocity; their intervals overlap the still-active prior fields.

## Preservation and review

Preserve the thirty-second film and both original three-second comparison clips. New case IDs and export paths own all new material. Inspect motion-only previews, native painting checkpoints, full delivery overviews and dense windows at joins and active deformation. Retain all original paintings in the delivery; replace terminal holds with motion for the longer result.

One short-lived RTX 4090 used the retained model volume. Outputs and receipts were downloaded and hash-checked before deleting owned compute.

## Screening observations

The two new motion-only previews were inspected before generation. Native paintings at source528, 744, 1008 and 1284, and progression sheets across both continuations, show the regional deformations changing the image beyond a global pan or zoom. The blue arch banks across the frame, the patterned shelves unfurl, and the city gradually becomes an abstract reef of pierced, ribbed shells. Retaining incoming fields at the second continuation lets the new curls overlap rather than reset the movement.

Clear glass edges, radial ribs, carved openings and saturated accents survive the larger deformation. The final three seconds trade miniature architecture for larger, smoother shell surfaces. This is a promising motion study, but not evidence that maximum motion and dense detail are both solved. The authored pullback does not read as a straightforward wider architectural reveal: the combined fields and recurrent repainting produce larger abstract forms.

The initial five-second delivery was screened with an overview and every-frame windows at 2.75–3.125 and 4.25–4.5 seconds. The final twelve-second delivery was screened with eight overview frames and every-frame windows at 6.75–7.125, 9.25–9.5 and 11.75–11.999 seconds. No conspicuous cut or double contour appeared in those sampled windows; small structures continue to reshape between paintings. This is sampled visual evidence, not a claim of flawless interpolation or a substitute for full-speed human rhythm judgment.

The first 70 non-held delivery-frame images match the approved local-curl clip exactly. Human approval applies to the preceding local-curl comparison; this longer passage still needs playback judgment.

## Result and closeout

[Watch The Unfurling Current](http://localhost:3028/glass-tide-layered-motion) · [MP4](../exports/v001/gt-unfurling-current-j/faster/rife-moving-tail/preview.mp4) · [Cut and lineage](../cuts/layered-motion-v001.md) · [Execution receipt](execution-layered-motion.json).

The final delivery contains 108 paintings across 288 frames at 1536×1024, 24 fps and twelve seconds. All original painting anchors, frame timing, full video decode and the two final moving frames passed verification. The original thirty-second film, accepted comparison and repaint-only control remain unchanged. The local reviewer serves both clips, with correct frame/painting counts and verified HTTP byte ranges; browser interaction was not automated.

All 81 new generation jobs and 1,261 remote files were preserved and hash-verified locally. The empty queue and exact hashes were checked before removing 162 owned ComfyUI input/output files. Pod `wjtgj7jwbwsgp2` was deleted and its absence verified at 13:25:41 UTC on 2026-10-17. Model volume `vd3jnbwko1` remains. Estimated compute is $0.37 at $0.89/hour, including startup and transfer through verified absence, excluding retained storage; this is not an invoice.
