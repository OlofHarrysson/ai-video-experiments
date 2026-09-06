# Ten video experiments

Session dated 2026-09-07. Olof authorized ten adaptive experiments, parallel work where useful, and use of the existing RunPod balance. The purpose is practical learning about filmmaking and controllable animation. Every generation and cut remains local; results are also surfaced as individual videos in chat.

## How this round developed

The first pair compared flat magnification with depth translation using gentle SDXL feedback on the preferred Seedream image. Timestamped review showed progressive smoothing. That led to E04's reduced repaint frequency and E05's stronger denoise. E06 combines sparse repainting with a camera approach after E03 exposed the node's Z direction convention. Independent branches explore a three-shot story, native Seedream editing and guide-based redraw. These are ten creative experiments, with additional guide/batch jobs inside them.

## Videos and findings

| ID | Experiment and video | Finding from inspected frames |
| --- | --- | --- |
| E01 | [Invitation → signal → reveal](../../apps/deforum/projects/marsh-story/exports/e01-v002/preview.mp4), 5s; [original](../../apps/deforum/projects/marsh-story/exports/e01-v001/preview.mp4), 12s | Three distinct story states read clearly. A revised cut selects earlier, clearer ranges; full shots progressively soften. |
| E02 | [Flat push, gentle feedback](../../apps/deforum/projects/motion-lab/exports/e02-flat-push-v001/preview.mp4), 5s | Camera movement is readable; repeated gentle repainting erases fine texture. |
| E03 | [Depth pullback](../../apps/deforum/projects/motion-lab/exports/e03-depth-push-v001/preview.mp4), 5s | Foreground shrinks and breaks up; positive Z moves scene points away. Frozen run name predates direction verification. |
| E04 | [Repaint every third frame](../../apps/deforum/projects/motion-lab/exports/e04-sparse-repaint-v001/preview.mp4), 5s | Retains more lantern/reed detail than E02 at equal times, but still softens. |
| E05 | [Stronger repainting](../../apps/deforum/projects/motion-lab/exports/e05-stronger-repaint-v001/preview.mp4), 5s | Higher denoise adds structural drift and does not solve late blur in this configuration. |
| E06 | [Depth approach, sparse repaint](../../apps/deforum/projects/motion-lab/exports/e06-depth-approach-v001/preview.mp4), 5s | More scene structure survives; nearby branches and lantern contours remain unreliable. |
| E07 | [Native Seedream per-frame edits](../../apps/deforum/projects/seedream-repaint/exports/e07-native-seedream-v001/preview.mp4), 4s | Preserves the recognizable painting and avoids progressive feedback blur, but invents irregular pale canvas borders and changes surfaces between frames. |
| E08 | [Independent SDXL redraw](../../apps/deforum/projects/redraw-lab/exports/e08-v001/preview.mp4), 5s | Scene layout and detail survive; torn foreground edges and frame variation remain. |
| E09 | [Independent redraw, fixed seed](../../apps/deforum/projects/redraw-lab/exports/e09-v001/preview.mp4), 5s | Promising preservation baseline; same guide with less measured pixel variation, still damaged foreground geometry. |
| E10 | [Repaint only gaps](../../apps/deforum/projects/redraw-lab/exports/e10-v001/preview.mp4), 5s | Preserves pixels outside the mask but invents a small architectural structure around the lantern. Creative morph, unsuccessful faithful repair. |

Start with **E01** for visual storytelling, **E09** for scene preservation, **E07** for native Seedream appearance, and **E10** for an unexpected surreal transformation. These are working candidates; Olof has not yet given playback feedback on this round.

Detailed notes: [story](../../apps/deforum/projects/marsh-story/experiments/story.md), [camera/settings](../../apps/deforum/projects/motion-lab/README.md), [Seedream](../../apps/deforum/projects/seedream-repaint/experiments/e07-native-edit.md), [redraw workflows](../../apps/deforum/projects/redraw-lab/README.md).

## What the comparison establishes

E02/E04 change only repaint cadence. E02/E05 change only denoise. E02/E03 use the same repaint settings but different camera methods and unmatched apparent travel. E06 combines several changes as a practical recipe. E01 is a filmmaking exercise using three new SDXL animations and two new Seedream Edit keyframes; the signal and reveal happen through cuts, not continuously generated object action.

In this sample, fewer feedback cycles retained more detail. This does not establish that low denoise or sparse repainting always wins. No added noise/sharpening was used in E02–E06; the previous recipes included those controls. All custom-worker image inference in this round uses the existing SDXL checkpoint and Depth Anything V2 small where needed. Native Seedream per-frame inference is a separately identified experiment.

E08/E09 change only the seed policy on the same guide. E09's mean unregistered RGB change, excluding the anchor transition, is .014424 versus .030690: 53% lower. That measures image variation, not perceptual flicker or better camera movement. E10 combines fixed seed, full-denoise masked sampling and masked compositing. Outside the expanded mask, all 40 frames retain their guide pixels exactly; scattered holes expand to a 38% repair region in the final frame. Restricting edits spatially does not supply missing scene geometry.

E07 uses the original anchor plus 31 new Seedream 4 Edit images, with no SDXL repainting or feedback from earlier edits. Its repair instruction and camera guide differ from some SDXL tests, so this is not a model-only controlled comparison. Two initial requests failed because RunPod network-volume S3 does not support presigned URLs. The successful requests sent inline owned images to the same API; no new storage service was introduced. All failures and originals remain archived. See [RunPod's S3 compatibility table](https://docs.runpod.io/storage/s3-api) and the [Seedream endpoint schema](https://docs.runpod.io/public-endpoints/models/seedream-4-edit).

The pinned [Difforum sampler](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py) diffuses only every Nth frame when cadence is N; intervening frames still receive the camera warp. Its [3D warp](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/core/warp.py) transforms scene points, so negative Z approaches and positive Z recedes. Depth is relative and reused from the initial image; these are not metrically reconstructed scenes.

## Local review harness

[video_review.py](../../apps/deforum/video_review.py) extracts full decoded frames at requested timestamps, evenly spaced positions, named events with before/after context, and optional FFmpeg scene-change candidates. Each review has immutable versioned frames, actual frame timestamps/numbers, hashes, a labeled contact sheet and JSON metadata. [Usage](../video-review.md).

Six focused harness tests pass, including variable frame rate/nonzero timestamps, actual selected pixels, a known hard cut, event context/clamping and source/prior-review preservation. The combined root suite passes 17 tests. Real clips were inspected using this harness, including E01's cuts at 4s/8s and E04's repaint step at 3s.

These findings are sampled-frame visual reviews. Pixel-change scores are diagnostics, not perceptual flicker scores or semantic events. Normal-speed playback remains necessary to judge rhythm and whether motion feels good. Delivery is 24 FPS with repeated source frames, not optical-flow interpolation. Original model PNGs remain separate from decoded MP4 review frames.

## Provenance and resources

Every custom run freezes its API graph, anchor hash, submission receipt, full frame sequence and worker archive. Story edits preserve their exact requests and original returned images. The existing endpoint was resumed with min 0/max 3 and its previously verified image; a fresh 10 GB archive volume is owned by this session. Infrastructure receipts and credentials remain ignored under app `work/` and `.env`.

- **25 custom-worker jobs completed and collected**, with 1,336.979 seconds aggregate job execution; several workers ran concurrently. Queue/setup/idle time is separate. The endpoint has 40 completed custom jobs across four sessions, with no failed custom jobs.
- **33 successful public Seedream edits:** two story keyframes ($.054 reported) and 31 E07 frames ($.837 reported), totaling $.891 in returned image-cost fields. Two earlier E07 URL-transport failures are preserved separately.
- **689 cloud objects / 607,048,699 bytes** verified byte-for-byte against local copies, followed by a second key/size/ETag inventory confirming no archive change during verification.
- The endpoint is paused at min/max 0, its volume attachment cleared and the temporary volume deleted. Final inventories show no Pods, workers or network volumes. Account current spend is 0. The active deployment file was moved into ignored closed-session receipts.
- Observed balance: **$49.4153457132 → $48.0695209725**, a decrease of **about $1.346** at the final check. A prior check was higher before more charges appeared. This is an account observation, not an itemized or guaranteed settled invoice; public model-reported costs and execution time should not be added to this delta as additional charges.
- All ten delivered previews verified at 1280×720 and 24 FPS, with expected durations/frame counts. Conventional cut frame hashes match the preserved run frames; native Seedream originals and normalized frame hashes have their own manifest. The original 12-second story cut also remains available.

Detailed private verification and resource receipts are under `apps/deforum/work/ten-experiments-session/`. Media remains on the Mac and ignored by Git; no separate-disk backup has been configured.
