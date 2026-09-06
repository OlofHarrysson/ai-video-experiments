# More visible motion from the Seedream reference

Plan written 2026-09-07 before rendering. Olof prefers the Seedream marsh still and finds the existing short videos too static. He approved the feedback-versus-redraw comparison and asked for more movement.

Use the preserved Seedream 4.0 original from `model-comparison/runs/20260906T215118Z-seedream-4-f5a8fd86/original-00.jpg`. Keep a byte-identical project copy and derive a 1280×720 RGB PNG with Lanczos resizing, without cropping. This tests SDXL animation from a Seedream-designed reference; no native Seedream video model is involved.

Render 40 source frames at 8 FPS: five seconds, including the unchanged anchor at position zero in both workflows. Deliver at 24 FPS with repeated frames, without interpolation. Use the previous fixed marsh prompt, SDXL base, seed 143 plus global frame index, 28 steps, CFG 6.5, denoise 0.4, DPM++ 2M/Karras.

The lateral scene-X step is +0.012 per generated frame: three times the earlier +0.004 speed, for total +0.468 relative units across 39 steps (about five times the prior three-second move). This moves scene points right, equivalent to moving the camera left. FOV 45°, near/far 1/10, initial Depth Anything V2 Small map, no rotation or zoom. Foreground lantern/reeds should move more than the distant observatory. These are relative, uncalibrated units; actual pixel travel must be measured. Stronger movement can reveal larger holes.

First inspect a camera-only guide and its depth map. Then render recurrent feedback and five independent-redraw batches of eight guide frames, assembled in global order. The redraw at index zero passes the reference through unchanged. Batch boundaries must preserve global seeds and source order. Feedback retains its existing LAB coherence/noise/sharpening and reuses initial depth on evolving images; redraw directly reprojects the original reference. This is a practical workflow comparison, not a one-variable ablation.

Show both full-size five-second video outputs directly in chat with short captions. Preserve guide, depth, coverage masks, original frames, exact graphs, receipts, rejected attempts and exports. Do not use a playback slowdown to claim additional generated motion. Record whether the Seedream look survives, landmark travel, gaps, style drift and any incomplete result. Olof's playback preference remains unconfirmed.

Reuse the retained ComfyUI endpoint, its previously verified worker image, max workers three/minimum zero and a fresh 10 GB EU-RO-1 archive volume. Starting observed balance $49.5480029076. Current authorization covers the remaining roughly $50 for learning. [RunPod billing](https://docs.runpod.io/serverless/pricing), checked 2026-09-07: network storage $0.07/GB/month while retained; worker startup, execution and idle are billed. Verify all archive objects locally before detaching/deleting the temporary volume and pausing workers.

## Commands

From `apps/deforum/`:

```bash
uv run --with pillow python projects/seedream-motion/experiments/motion.py prepare
uv run --env-file .env --with pillow python projects/seedream-motion/experiments/motion.py guide
uv run --env-file .env --with pillow python projects/seedream-motion/experiments/motion.py feedback
uv run --env-file .env --with pillow python projects/seedream-motion/experiments/motion.py redraw --guide-run GUIDE_RUN --start 0
```

Submit remaining redraw batches with starts 8, 16, 24, 32 after the guide is collected. Each command submits once; recover any existing job with `experiment.py collect` rather than repeating a submission. Results are recorded below.


## Completed results

All seven submitted jobs completed with no provider-reported failures or retries. The app crashed during guide startup; the local process disappeared, but the saved job ID allowed a new collector to retrieve the same job without buying a second render. The guide queued for 394.029 seconds and executed for 23.138 seconds. The feedback job queued for 6.557 seconds and executed for 144.999 seconds. Redraw batches executed in 53.791, 30.517, 34.521, 30.915 and 39.314 seconds in global-frame order; queue delays ranged from 146.777 to 172.583 seconds. Several redraw batches ran on different workers with overlapping execution. Queue time is not a measure of billed GPU time.

Archived diagnostics identify ComfyUI 0.34.0, Python 3.12.3, PyTorch 2.11.0+cu128 and RTX 4090. The reused worker image was `registry.runpod.net/olofharrysson-ai-video-experiments-main-apps-deforum-serverless-dockerfile:c35363b92`. Model and node pins are in the [app README](../../../README.md) and serverless Dockerfile. The original Seedream JPEG hash is `db766508898e3de868b589d6d05e6f335cda95f8d81b2f66130b948717e6ea73`; resized anchor hash is `31d03b3b1ff1e4ff9d7abd424c18d5013d5ff83821339e5476053776f45f1e03`.

The guide, feedback and assembled redraw all begin with pixels identical to the resized Seedream reference. Both final videos are 1280×720, five seconds, 120 delivery frames at 24 FPS from 40 source frames at 8 FPS. The redraw cut copies the five batches in global order; every guide-input and output-copy hash is checked. Frame zero is passed through unchanged; frames 1–39 each receive independent repainting with the corresponding global seed. Original frames and both cut manifests are retained.

### What the images show

Reviewed the original, depth map, last guide, last feedback, and paired frames 0, 13, 26 and 39. The depth estimate places the large foreground lantern and reeds near, and the dome/sky far. First-to-last guide template matching finds the dome about 73 pixels rightward (correlation 0.994) and crescent 72 pixels rightward (1.000). A foreground lantern match was unreliable (0.322 correlation) because it is severely distorted; do not treat that match's displacement as a measurement.

The raw guide's uncovered fraction rises from zero to 15.8% at frame 13, 20.9% at 26, and **24.8% at frame 39**. It exposes large black border regions and interior gaps around the foreground. This is a geometric coverage metric, not a perceptual-quality score.

- **Feedback:** fills the conspicuous holes, but the lantern simplifies, the dome becomes a tower, blue mushrooms shift toward purple, and the path becomes a broader green-lit form. The final image is softer and materially different from the preferred Seedream painting. This is substantial transformation, not faithful rigid scene motion.
- **Independent redraw:** preserves more of the boardwalk, distant dome, blue mushrooms and overall layout. It cannot repair the increasingly fragmented lantern or the missing left-edge content. Greater camera travel does not yield a clean version of the original scene.

Neither result establishes a finished-quality animation of the preferred still. The comparison shows a tradeoff between filling gaps through cumulative reinterpretation and retaining structure while exposing a weak guide. User preference for either completed five-second video remains unconfirmed; sampled-frame review does not replace playback judgment.

### Outputs

- [Five-second feedback](../exports/v001-feedback/preview.mp4).
- [Five-second independent redraw](../exports/v001-redraw/preview.mp4).
- [Feedback left / redraw right](../exports/v001-comparison/feedback-left-redraw-right.mp4).
- [Paired sampled frames](../exports/v001-comparison/contact.jpg).

Local export command: `uv run --with pillow python projects/seedream-motion/experiments/review.py`. It requires the one collected guide, one feedback run and five distinct redraw batches; it rejects ambiguous/missing inputs and refuses to overwrite existing cuts. Shared graph construction now lives in `workflow_recipes.py`, reused by the earlier guide-redraw project without changing its settings.

### Cost, preservation and cleanup

Starting balance $49.5480029076; final observed balance $49.4153457132: **$0.1326571944**, about thirteen cents. Final reported spend rate $0/hour. This is an account delta, not an itemized final invoice.

All **197 cloud objects, 215,925,566 bytes**, were compared byte-for-byte with local archives; the subsequent key/size/ETag inventory matched. The endpoint was paused at min/max zero, its temporary volume detached and deleted, and final inventories showed no Pods, workers or volumes. Private account, job, copy-verification and cleanup receipts remain in `work/seedream-motion-session/`; the active deployment file was moved into closed receipts. All generations, inputs and cuts remain on the Mac. Git excludes their media; a separate backup disk remains unconfigured.

Validation: 11 shared tests and four guide-redraw tests pass after extracting the reusable graph recipe. Local checks cover all five global-seed batches and the first-frame bypass; hosted output verifies the unchanged anchor and required nodes. Both delivery videos passed ffprobe dimensions, duration and frame-count checks.

## Creative follow-up

The [filmmaking guide](../../../../../docs/research/filmmaking-for-ai-animation.md) broadens the next step beyond camera parameters. Decide what the viewer should notice and what changes in the shot, then choose a movement that our scene representation can support. Close foreground strengthens parallax but increases exposed hidden content; it is not by itself a cure for a static-feeling film.
