# Opening keyframes — first still study

2026-11-10. Four frames ready for Olof’s review. No animation or audio generated.

![Opening keyframes](../exports/stills-v001/opening-keyframes.jpg)

## Method and provenance

Fal’s live recommendation selected `google/nano-banana-2.1`; follow-up image edits used `google/nano-banana-2.1/edit`. Requests used high thinking, 2K, 16:9 and PNG. All five outputs are 2752×1536; this is the service’s returned approximation to the requested aspect ratio, not an exact 16:9 raster. Choose a common exact delivery crop when animating.

The first room image was generated from text describing the source’s visual qualities. Source film frames were inspected by the assistant but were **not** supplied to the image model. The remaining images use our own prior outputs as visual references: A → A2 → B → C → D. Consequently this tests a verbally reconstructed look plus reference continuity, not direct source-frame style transfer.

The initial A image showed only a unicorn head and a relatively plain room. A2 corrected the full-body sketch and added green/teal room accents, but did not fully follow the requested frontal reframing or richer background rendering. It remains the selected room candidate for this first complete visual test.

## Selected frames and screening

| Frame | Local original | Assistant observation |
| --- | --- | --- |
| A2 — artist | [PNG](../runs/still-a2-v001/image.png) | Warm illustrated girl, natural drawing gesture, violet shirt and coherent room. Still flatter, darker and less lush than the original film. Camera remains largely side-on despite the refinement request. |
| B — sketch | [PNG](../runs/still-b-v001/image.png) | Clearly readable full unicorn, graphite strokes, plausible pencil contact and consistent sleeves. Book is viewed more squarely from above than the source. |
| C — dimensional | [PNG](../runs/still-c-v001/image.png) | Strong change from pencil to shaded ivory horse while page, hands and desk appear closely aligned. Good candidate for a controlled transition; this is visual alignment, not a claim of pixel-identical surroundings. |
| D — outdoors | [PNG](../runs/still-d-v001/image.png) | Convincing naturalistic woodland lighting and white horse with a horn. Mane and tail are shorter/straighter than the drawn design; identity continuity is approximate. |

Inspected returned image pixels for all five generations, then decoded the four selected local originals and checked dimensions. All five originals and their exact per-run receipts are preserved locally; SHA-256 and byte counts are recorded. Preview inspection supports composition screening, not a guarantee of fine anatomical accuracy or successful animation.

## Review decision

The sketch-to-dimensional pair is the strongest mechanism result. The room’s visual richness is the main remaining taste question: whether this softer illustrated treatment is close enough, or whether to push it toward the source’s luminous, densely painted environment before animation. Do not infer Olof’s preference from successful generation.

**Subsequent feedback:** Olof says the stills look close enough. He personally prefers space/galaxy imagery and feels the forest is less fitting, but accepts the forest for this test if it matches the original opening. The first animation proceeded within that scope; see [video v001](video-v001.md).

After Olof reviews the stills, animate the artist shot, bridge B to C with a model supporting both frames, and animate D as a separate outdoor shot; assemble roughly ten seconds with a hard cut to the landscape. Music remains later.

## Records

- [Exact prompts, endpoints, request IDs and output URLs](stills-v001-receipt.json).
- [Local files, byte counts and SHA-256](stills-v001-files.json).
- [Original creative prompt drafts](still-prompts.md).

Five billable image-generation requests completed. Actual charged cost was not returned. The recommendation exposed a generic USD-per-unit rate without a resolved resolution-specific charge, so no exact total is claimed. No video/audio jobs or infrastructure were started.
