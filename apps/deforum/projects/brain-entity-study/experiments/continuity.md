# Temporal continuity study

Started 2026-09-07. Follow-up to Olof's playback feedback and the [architecture comparison](../../../../../docs/research/deforum-architecture-comparison.md).

Subsequent human review: C01/C03 were boring; the other outputs were pretty good, with **P3 + RIFE the tentative favorite**. Differences between similar variants were difficult to judge. This replaces the assistant's earlier C02 recommendation as the creative baseline. The [review harness follow-up](review-harness.md) records a smaller human shortlist and clearer comparison process. The sampled findings below describe the original assistant review.

Keep the graphic SDXL artwork and separate postprocessing from generation. P03 is the generation baseline because Olof called it “really good”; P01 supplies a second interpolation source with interesting but abrupt morphing. The first question is whether transitions become more gradual without losing the art's evolution.

## Generation comparisons

All three new runs inherit P03 (`20260907T075457156677Z-p03-cfg-45-48f`): same anchor, prompts, camera, model/LoRA, 48 frames at 8 FPS, denoise 0.82, CFG 4.5 and 30 steps. They use the previously executed worker image `f106834b7` to avoid a runtime change.

| Label | Diffusion seed | Added pixel noise | Change from P03 |
| --- | --- | --- | --- |
| P03, preserved control | Increment | 0.025 | None |
| C01 | Fixed | 0.025 | Hold diffusion noise seed |
| C02 | Increment | 0 | Remove separate pixel noise |
| C03 | Fixed | 0 | Combine both; compare with C01 and C02 to isolate each effect |

This is a small two-factor comparison. Fixed seed alone does not fix pixel noise: Difforum seeds that operation with the base seed plus frame index. These tests therefore distinguish two noise sources. They do **not** implement interpolated noise tensors or a temporal model.

Run using `parameters.py`, explicitly selecting the P03 parent. Preserve every run and receipt. Record timings separately from queue/setup, inspect timestamped frames, and present each complete clip in chat. No winner is established before review.

## Postprocessing comparisons

Run author RIFE interpolation on original P01 and P03 PNGs at three times their source rate. Preserve six seconds: 48 originals produce 142 endpoint/intermediate frames, followed by two explicit final-frame holds at 24 FPS. Preserve originals and document model/code pins, runtime, frame hashes and timing. See the separate RIFE results note when execution completes.

## Review criteria

- More gradual transitions across formerly abrupt frame pairs.
- Retained ink detail and legible forms, without duplicated contours or excessive blur.
- Interesting progression through the midpoint and ending.
- Distinguish timestamped frame inspection from normal-speed playback preference; Olof's playback feedback remains authoritative.

## Generation results

All three jobs completed on the existing SDXL worker, without rebuilding it. The saved graphs differ from P03 in exactly the fields above. Packed input PNG hashes and first-frame PNG hashes match across all four runs. Every new run has 48 source PNGs and a six-second, 144-frame, 1024×576 H.264 export at 24 FPS. These raw exports still repeat frames; RIFE exports are separate.

| Result | Preserved run | Queue/setup delay | Job execution | Sampled-frame findings |
| --- | --- | ---: | ---: | --- |
| [C01: fixed diffusion seed](../exports/c01-fixed-seed/preview.mp4) | `20260907T094842689697Z-c01-fixed-seed-48f` | 68.754 s | 124.518 s | The mechanical ring persists, but simplifies into a flat teal/orange emblem. Little visual progression in the second half. |
| [C02: no added pixel noise](../exports/c02-no-pixel-noise/preview.mp4) | `20260907T094844636087Z-c02-no-pixel-noise-48f` | 157.158 s | 133.301 s | Retains the portal longer than P03; still simplifies in the middle, then produces new root/tree forms toward the end. The most interesting new generation candidate for interpolation. |
| [C03: fixed seed, no pixel noise](../exports/c03-fixed-no-pixel-noise/preview.mp4) | `20260907T094844754296Z-c03-fixed-no-pixel-noise-48f` | 192.988 s | 118.706 s | The same flattening tendency as C01, with an even more settled ending. Keeping the noise fixed is not sufficient for desirable morphing. |

Review sheets: [C01](../exports/c01-review/v001/contact-sheet.jpg), [C02](../exports/c02-review/v001/contact-sheet.jpg), [C03](../exports/c03-review/v001/contact-sheet.jpg). Twelve overview samples and the 2.875/3.000/3.125-second neighborhood were inspected for each. This is sampled-frame evidence; Olof's normal-speed playback verdict is pending.

For diagnosis only, median adjacent mean RGB change at 256×144 is 0.1171 for P03, 0.0224 for C01, 0.0982 for C02, and 0.0242 for C03 (normalized 0–1). In the latter half C03 falls to 0.0063. The metric supports the observed reduction in change, but is not a quality ranking: a frozen picture would score extremely low. One seed/anchor/artwork was tested; do not generalize a universal preference for zero pixel noise.

The comparison motivates an intermediate option between frozen and independent diffusion noise. Interpolated noise tensors remain untested; this round deliberately uses the existing sampler interface to establish the two endpoints first.

## Flow Stabilize, separately

[P03 with Flow Stabilize](../exports/p03-flow-stabilize/preview.mp4) uses the existing Difforum node's exact core implementation at pin `1d750efd3c1d1dda792b8ef6c14b06a14a69f879`. Its default settings are strength 0.5, flow scale 0.5 and error gate 0.15. [Local experiment wrapper](flow_study.py) downloads/checks the pinned source and calls that function directly; no replacement optical-flow algorithm or ComfyUI installation is introduced on the Mac.

Processing the 48 images took **1.369 seconds on CPU**, excluding dependency setup, PNG I/O and encoding. The source/delivery timeline stays 8/24 FPS: it still repeats processed frames rather than creating intermediate states. Runtime versions and all source/output hashes are in `exports/p03-flow-stabilize/processing.json`.

The [overview](../exports/p03-flow-review/v001/contact-sheet.jpg) and [original/processed comparison around 5 seconds](../exports/p03-flow-stabilize/paired-event.jpg) retain the same broad forms and the abrupt 40→41 shape change. The effect is modest at these defaults: median adjacent RGB change drops from 0.1171 to 0.1105, while that large pair changes from 0.1629 to 0.1576. This is consistent with the photometric gate limiting blending when images differ substantially. It is not a demonstrated cure for abrupt semantic morphs.

Reproduce once in this project (the script refuses to overwrite its preserved export):

```bash
uv run --script projects/brain-entity-study/experiments/flow_study.py
```

## RIFE interpolation

See [RIFE execution and review](rife-results.md) for independent P01/P03 comparisons. C02 was subsequently selected for the same interpolation as a combined candidate, because its sampled ending retained more visual development than either fixed-seed variant. This selection is an assistant hypothesis, not a recorded user preference.

## Execution and preservation

Three initial submissions received explicit HTTP 409 `ENDPOINT_PAUSED` rejections immediately after the control API reported max workers 3. No job IDs were accepted then. The rejected local receipts remain intact; after checking endpoint state and an empty runtime queue, fresh submissions succeeded. This is evidence of a short control/runtime propagation delay, not an uncertain job POST retry.

The three jobs used two RTX 4090 workers; C01/C03 reused one worker, with C02 on the other. Maximum workers was 3, minimum 0. Capacity-throttled startup attempts were observed. All executed on image `f106834b7`, ComfyUI 0.34.0 and PyTorch 2.11.0+cu128. Job execution includes handler/archive work, not only denoising. Private receipts, matching-graph audit and diagnostics are under `work/brain-continuity-session/` and the individual runs.

After collection, all workers were stopped and **159 cloud objects / 133,351,453 bytes** were checked byte-for-byte and by SHA-256 against local copies. A second object inventory confirmed that storage had not changed during verification. The volume was detached with verified REST readback, then deleted. Final inventory showed zero Pods, zero workers and zero network volumes; endpoint min/max workers are both 0.

The observed account balance moved from **$47.5414 to $47.4156**, approximately **$0.126** during this session, with reported ongoing spend **$0/hour** afterward. This is a balance snapshot difference, not a finalized per-job invoice. The three successful source runs, rejected submission receipts, cuts, processed exports and all cloud attempts remain local. The active deployment receipt was moved into this session's closed records. No separate-disk backup is configured.
