# Motion within a stationary view

## Question

Olof likes the moving patterns inside the thirty-second Glass Tide film and wants to distinguish repainting-driven evolution from authored spatial movement. This is a matched two-clip comparison, independent of the selected film.

## Controls and change

Both three-second clips begin with the saved painting at source frame 1392 of `gt-prismatic-vault-e` (about 12.89 seconds into the film). Its existing crystalline-city prompt stays constant. Krea 2 Turbo, noise 0.72, three Euler intervals, CFG 1, reference conditioning off, and seed sequence 1041617–1041642 remain matched. Each new painting initializes from the previous painting; no masks, copyback, fixed-opening reference or detail pass.

- **Repainting only (`gt-internal-repaint-a`):** all authored spatial transforms are off.
- **Local curl (`gt-internal-curl-b`):** the same loop with one smoothly eased radial twist, 50 degrees at its center, radius 0.33 image heights, centered on the right patterned shelf at `[1.22, 0.55]` in image-height coordinates. Global zoom and travel are zero. There is no global pan, roll or perspective turn.

The twist decays continuously with distance; it is not a hard region boundary or object mask. The model can still redraw objects or drift the composition in either clip. Matching seeds does not make diverging recurrent images identical.

Each case retains 27 paintings, including the shared starting painting, at 1536×1024. RIFE 4.25 places them at the established 4.5× delivery pace, 24 fps. The same two terminal held frames complete both 72-frame clips. RIFE stays outside feedback.

Frozen matrix: [internal-motion.json](internal-motion.json). The source clock explicitly resets to zero for this isolated comparison; this is not a continuation cut. The starting seed is offset to the selected original source painting.

## Execution and review

The native starting painting and six-frame motion-only overview were inspected before inference. The preview curls the right shelf while preserving the broad position of the glass arch and left towers. Two cases require 52 new paintings. Use one short-lived RTX 4090 with the retained model volume; download and verify all results before deleting owned compute. The selected thirty-second film remains preserved.

## Results

[Compare the two clips](http://localhost:3028/glass-tide-internal-motion). Both are three seconds, 72 frames and 1536×1024, with all 27 paintings retained. The selected thirty-second film is unchanged.

**Repainting alone produces substantial movement.** The cyan arch changes curvature and apparent scale, circular openings expand, slender towers gain stairs and larger bases, and the starburst patterns spread into longer thin spokes. There is no authored zoom behind this apparent change of viewpoint. It is composition drift and structural reinterpretation within the recurrent painting chain, bridged by RIFE. This is useful evolving imagery, but not isolated animation of an otherwise fixed scene.

**The local curl gives the right shelf a clearer directional sweep.** Its starbursts bend and become dark circular inlays; coral clusters and small openings move with the deforming shelf. The broad cyan arch remains recognizable, while towers elsewhere still redesign themselves. The curl's influence decays spatially, but the model's response is not confined to that region.

Both retain crisp large silhouettes, narrow spokes, engraved tower faces and saturated cyan/purple colors. Raised starburst relief becomes flatter linework and broad pale surfaces remain smooth. Neither test establishes improved detail retention or object preservation. Olof prefers the local curl and authorizes a longer passage combining it with varied camera movement and overlapping internal deformations. The assistant's tentative preference agrees with his playback choice. These two short runs establish behavior for this painting and seed sequence, not a universal recipe.

## Screening and verification

- Inspected the native starting painting, motion-only overview, six original paintings per case across the whole sequence, cropped right-shelf comparisons and both native final paintings.
- Reviewed six delivery overview frames per clip and every displayed frame at 1.25–1.50 and 2.50–2.75 seconds in the matched comparison. Also inspected repaint-only frames at 0.875–1.125 seconds. No conspicuous duplicated major contours in those windows; fine lines change/fade as paintings evolve. This frame screening does not establish full-speed rhythm preference.
- [Painting overview](../exports/internal-motion-review/painting-comparison.jpg), [matched review metadata](../exports/internal-motion-review/matched/v001/review.json). In the review harness's generated sheets, A is the curl and B is repaint-only; the linked player uses descriptive labels.
- All 52 jobs passed exact initialization-warp, parent/output hash, requested/executed/embedded graph and successful-job checks. The empty transform path was separately checked for pixel identity. The two configs differ only in case ID and the local curl phrase.
- All remote files and runtime evidence were downloaded and hash-checked. Both deliveries passed retained-painting, interpolation provenance, frame count, size, duration and complete-decode checks. The original thirty-second MP4 hash remains unchanged.
- The linked reviewer selects both clips and serves the original videos with verified HTTP range responses. The assistant did not automate browser playback. Olof later watched the comparison and preferred the local curl.
- The owned GPU is deleted; the existing model volume remains. Estimated compute **$0.19**, including startup and verification, excluding retained storage. [Execution and cleanup receipt](execution-internal-motion.json).
