# Continue from a chosen frame

Status: proposed; not implemented or rendered. [Research](../../../../../docs/research/continuation-and-editing.md).

## Question

Can we preserve a selected opening and replace only its continuation, while finding every earlier attempt and cut?

## Comparison

Pick an exact frame from the middle baseline after playback review. Retain the original; create a short branch with the same model/camera first, then a deliberate prompt change. Record parent run, original PNG hash, generated frame index, and absolute schedule frame. The existing runner does not yet support this branch operation.

## Evidence to collect

A join with no duplicated anchor frame; inspectable seed/camera/prompt timing; preserved originals; a versioned cut selecting old prefix and new continuation. A second cut should be able to choose a different continuation without modifying the first. Color-anchor reset must be addressed or explicitly accepted as creative drift.

## Cost boundary and result

Start with eight new frames, using the SDXL cost reference. No allocation or paid resource is active for this proposal. Result and run links: pending.
