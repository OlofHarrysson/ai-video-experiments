# Overscan and a lateral camera move

Status: completed on 2026-09-06. Full generations and derived crops are preserved locally.

## Question

Can a fixed center crop hide border artifacts during a three-second 3D camera move while retaining the scene's important objects? Compare full and cropped views of the same generated frames, not two different diffusion runs.

## Recipe

Use existing SDXL, Difforum and Depth Anything V2 Small on the retained RunPod Serverless worker. Generate a new moonlit marsh reference at 1280×720, seed 143, 28 steps, CFG 6.5, DPM++ 2M/Karras. Keep the prompt fixed while the image repaints at denoise 0.40 with incrementing seeds. The intended scene has close reeds/lantern, a boardwalk, and a distant observatory; inspect the actual reference and estimated depth before proceeding.

Generate 24 source frames at 8 FPS, including the anchor, with 23 lateral scene-X steps of +0.004 (camera left). No zoom or rotation. FOV 45°, relative near/far 1/10, bright depth near. Preview identity at frame zero before cumulative warping. First render a camera-only guide, then the feedback version, which continues to reuse its initial depth.

The delivered viewport is the 1024×576 center crop at x=128, y=72: 10% margins on each side. It retains 64% of the render area; the source contains 1.5625× as many pixels as the delivered viewport. This is a pixel-count overhead, not a measured cost multiplier. The crop narrows the horizontal field of view from 45° to about 36.7°; it does not preserve identical framing.

Crop after generation. Keep the full PNGs and both exports. Compare raw coverage masks over the full image, delivered viewport and outer border; black or uncovered regions inside the crop would falsify the simple border-margin hypothesis. Cropping cannot restore newly revealed scene content or fix interior geometry, and a coverage mask does not measure aesthetic repaint artifacts.

## Execution

From `apps/deforum/`, with a fresh attached archive volume and the endpoint restored to max workers 3 (minimum 0):

```bash
uv run --env-file .env python projects/lantern-marsh/experiments/overscan.py reference
uv run --env-file .env python projects/lantern-marsh/experiments/overscan.py guide --parent-run REFERENCE_RUN
uv run --env-file .env python projects/lantern-marsh/experiments/overscan.py feedback --parent-run REFERENCE_RUN
```

Inspect each result before the next phase. The scene recipe remains in this project; shared camera construction, continuation, transport and collection stay at app level.

## Cost and evidence

Olof authorized using the remaining RunPod balance for parallel learning; starting observed balance $49.699250. The shared endpoint now allows three concurrent 4090 workers, with zero active workers, 5-second idle timeout and 600-second job timeout. Olof explicitly authorized parallel experiments within the remaining RunPod balance. Archive everything locally, verify copies, pause the endpoint and delete the temporary volume afterward.

Session-wide billing and cleanup are recorded in the [parallel experiment report](../../../../../docs/research/parallel-experiments-session.md). Playback preference remains Olof's decision.


## Results

| Phase | Preserved run | Queue seconds | Execution seconds |
| --- | --- | ---: | ---: |
| Reference | `20260906T214815368534Z-overscan-1f` | 147.007 | 8.532 |
| Depth guide | `20260906T215248071614Z-overscan-24f` | 1.193 | 8.833 |
| Feedback | `20260906T215334143141Z-overscan-24f` | 1.156 | 88.069 |

All three jobs completed. The 24-frame guide and repaint each encode to three seconds at 24 delivery FPS (72 repeated frames). The guide's first image is pixel-identical to the reference, verifying the corrected identity schedule remotely. Runtime: ComfyUI 0.34.0, PyTorch 2.11.0+cu128, RTX 4090; exact graph and diagnostics are archived with every run. The worker image and model/node pins are documented in the app README and serverless Dockerfile.

The reference renders a sunset-colored marsh with a large round moon and lit pavilion, rather than the requested small observatory and separate hanging lantern. It does contain useful foreground trees/reeds, middle-distance boardwalk and distant hills. The depth estimate puts bright reeds closest, trees next and the pavilion/hills farther away. This is plausible relative ordering, not measured real geometry.

The guide reveals gaps around tree trunks, reeds and the frame border as it moves. At frame 23, raw uncovered area is **10.849% of the full image**, **7.609% of the center crop**, and **16.607% of the discarded border**. Cropping reduces the uncovered fraction by about 30% relative, but significant holes remain inside the viewport. Frame zero has zero uncovered pixels. The border-margin hypothesis helps but does not solve disocclusion. Mask coverage measures the raw warp, not the visual quality of filled or repainted pixels.

Inspected full-size reference, depth, last guide and sampled guide/repaint frames 0, 11 and 23. Repainting fills the obvious geometric gaps but changes the scene: the pavilion shifts and simplifies, railings rearrange, moon/cloud boundaries change, birds appear, and painterly line work becomes coarser. The motion cannot be interpreted as a rigid 3D camera alone. A crop changes framing and hides outer edges, but does not recover the original interior structure. Full-motion smoothness/flicker preference still needs Olof's playback review.

## Review exports

Export directory: `exports/overscan-20260906T215334143141Z-overscan-24f/`.

- [Painted crop](../exports/overscan-20260906T215334143141Z-overscan-24f/feedback-crop.mp4).
- [Painted full view left / crop right](../exports/overscan-20260906T215334143141Z-overscan-24f/feedback-full-left-crop-right.mp4).
- [Camera guide full view left / crop right](../exports/overscan-20260906T215334143141Z-overscan-24f/guide-full-left-crop-right.mp4).
- [Guide / feedback samples](../exports/overscan-20260906T215334143141Z-overscan-24f/guide-feedback-contact.jpg).
- `review.json` records every source-frame hash, crop rectangle and all 24 coverage measurements.

Run the export recipe with `uv run --with pillow --with numpy python projects/lantern-marsh/experiments/review.py GUIDE_RUN FEEDBACK_RUN`. It refuses to overwrite an existing export. Source PNGs are untouched; no optical-flow interpolation or inpainting is added by this local export step.

A first submission immediately after endpoint activation returned HTTP 409 without a job ID. Endpoint health showed no new queued/running job before the later accepted request. The exact rejection cause was not captured. That attempt folder remains; the shared client now records the HTTP response body and a submission-error receipt, and still never retries automatically. The regression check verifies one rejected call and the retained error.
