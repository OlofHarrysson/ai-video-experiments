# Graybox motion and separate appearance reference

**Paused 9 October 2026 at Olof's request.** Inputs remain preserved. Do not upload or submit the prepared request unless Olof resumes this study. The billing observations below describe the earlier preparation session.

2026-10-01. Olof finds the guided Krea result "pretty good" and says it restyles the input well. He wants the sketch to act as a graybox. He approves testing the same four-second motion with a neutral structural guide and a separate finished style image in a video model with structural control.

## Question

Can the approved profile-to-horse movement survive whole-clip video generation while appearance comes from a separate painted image, without carrying the sketch's flat colors and ink contours into the result?

## Inputs and scope

- Geometry and timing: the immutable `profile-morph-v002` SVG sequence and landmarks, 96 frames at 24 fps. Preserve its silhouette, mane sections, ear movement, eye and nostril positions. No head turn, camera move or full-body reveal.
- Neutral guide: uncolored shallow relief derived from the original filled SVG paths. Stroke-only decorative details are omitted. This is authored 2.5D relief, not measured depth or a complete 3D model. Save both shaded graybox and near-bright depth videos.
- Appearance: the same Krea opening used by the approved guided clip, copied byte-for-byte as a separate image. Its existing comic-print treatment is held fixed for this mechanism test.
- Baseline: `guided-n040-a012/rife/preview.mp4`. The new candidate uses whole-clip generation; it does not feed each generated painting into the next. Olof explicitly approved this architecture comparison in his response annotation.

## Routing and status

Live catalog checked 2026-10-01. Seedance 2.5 reference-to-video supports a four-second guide video plus a separately named image reference. Its documented clay-render workflow assigns structure to the video and appearance to the image. This is reference-based guidance, not a guarantee of pixel-locked geometry.

During preparation, Fal's authenticated account readiness check reported `balance_exhausted`, so no upload or paid request was submitted. Olof initially selected adding Fal credit for Seedance, then paused this project on 9 October. No RunPod resource was provisioned.

The Seedance US endpoint quotes $0.02568 per 1,000 tokens at 720p. Its published formula includes input and output video duration and multiplies by 0.6 for video references. For 1280×720 and four input plus four output seconds, the estimate is $2.73; this is not a final invoice. No new compute has been started.

## Sources

- [Seedance clay-render and image reference example](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5)
- [Seedance 2.5 US endpoint and price formula](https://fal.ai/models/bytedance/seedance-2.5/us/reference-to-video)
- [LTX structural control adapters](https://docs.ltx.io/open-source-model/integration-tools/ic-lo-ra-adapters)

## Prepared inputs and screening

[Neutral guide](../exports/graybox-video-v001/inputs/graybox.mp4), [depth guide](../exports/graybox-video-v001/inputs/depth.mp4) and [appearance reference](../exports/graybox-video-v001/inputs/style-reference.png) are preserved with 197 verified file hashes. Both videos decode to 96 frames, 24 fps, 1280×720 and exactly four seconds. The appearance image matches the baseline's source bytes. The [renderer](graybox.py) passes scoped Ruff checks.

Screened eight overview frames and every displayed frame from 1.625 to 1.875 seconds. The muzzle, ear and mane retain the approved continuous motion; the neutral relief is faceted and intentionally omits ink outlines, colors and facial decorative strokes. This establishes the input preparation, not model adherence.

`exports/graybox-video-v001/` also contains the retrieved schema, prices and `planned-request.json`. That request assigns the neutral video to shape/timing and the painted image to appearance. Uploaded URLs, submission/result receipts, generated media, comparison and output screening are still pending. No generation cost has been incurred in this preparation.
