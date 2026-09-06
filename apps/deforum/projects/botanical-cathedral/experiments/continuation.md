# Continue from a chosen frame

Status: CLI implemented and locally tested; serverless build/deployment and rendering pending. [Research](../../../../../docs/research/continuation-and-editing.md) · [Execution runbook](../../../serverless/README.md).

## Question

Can we preserve a selected opening and replace only its continuation, while finding every earlier attempt and cut?

## Comparison

Use frame `0019.png` of `20260906T082559925877Z-denoise-0.40-40f`. Its cathedral structure is coherent in the inspected still. Preserve parent frames `[0,20)` (2.5 seconds). Generate eight new frames with the same SDXL checkpoint, 0.40 denoise and camera/prompt schedules: absolute frames 20–27. The nine-frame returned batch includes the selected frame at index 0; the cut takes only `[1,9)` from it. The assembled cut will contain 28 source frames (3.5 seconds).

The incrementing seed and absolute schedule positions carry forward. Color coherence anchors to the selected parent frame, an accepted creative reset for this branch. The newer serverless ComfyUI/PyTorch runtime also prevents claiming exact replay of the old Pod. A deliberately changed prompt can follow after the first continuation is reviewed.

## Evidence to collect

A join with no duplicated anchor frame; inspectable seed/camera/prompt timing; preserved originals; a versioned cut selecting old prefix and new continuation. A second cut should be able to choose a different continuation without modifying the first. Color-anchor reset must be addressed or explicitly accepted as creative drift.

## Cost boundary and result

Start with eight new frames, using the SDXL cost reference and the original $50 budget. Measure cold startup, execution and actual shutdown independently. The prepared worker returns a durable volume manifest; retrieve it after GPU shutdown to test recovery. No allocation or paid resource is active yet. Result and run links: pending.
