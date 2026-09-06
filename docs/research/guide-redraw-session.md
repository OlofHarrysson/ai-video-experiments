# Independent guide-redraw session — 2026-09-06

Status: completed. Eight independent redraws generated and collected; all eight guide/redraw/feedback positions inspected as a contact sheet, with frame 7 side by side and redraw frame 0 at full size. No further jobs planned. The comparison MP4 is encoded and verified; real-time playback preference remains for Olof to review.

The bounded experiment is [guide-redraw](../../apps/deforum/projects/guide-redraw/README.md). It uses the existing shared Serverless client and worker, with eight independent SDXL img2img branches. Current authorization permits this agent to submit/collect its experiment; parent retains endpoint/storage ownership and final cleanup.

## Source/interface checks

- Local `serverless_client.py`: accepts a single source image, preserves it as `anchor.png`, and collects SaveImage output node `11` in filename order. No transport changes.
- Local `serverless/handler.py`: rewrites LoadImage input to a unique attempt filename, archives inputs/workflow/diagnostics/output PNGs and verifies the main frame count.
- ComfyUI v0.26.2 primary source verifies [`ImageCrop`](https://github.com/Comfy-Org/ComfyUI/blob/v0.26.2/comfy_extras/nodes_images.py) slices the requested pixel rectangle. [`VAEEncode`, `KSampler`, `VAEDecode` and `ImageBatch`](https://github.com/Comfy-Org/ComfyUI/blob/v0.26.2/nodes.py) provide the required graph contracts; ImageBatch concatenates image1 then image2. Crop and batch nodes are deprecated but still implemented in this version. The earlier local object-info snapshot omits several of these classes and does not prove current worker registration. Remote execution remains the decisive check.
- Pinned [Difforum sampler source](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py) computes incrementing seeds as `seed + f`, matching original guide index mapping here.

## Local validation

`uv run --with pillow python -B -m unittest discover -s projects/guide-redraw/experiments -p test_redraw.py -v` passed four checks: pixel-exact strip crops and original PNG hashes; graph traversal proving guide-to-output order and global seeds; rejection of incomplete/non-RGB inputs; and tampered-input/uncertain-submission protection. The CLI help runs in the existing app environment plus temporary Pillow. These are offline checks with synthetic fixtures and a mocked shared submission, not GPU evidence.

## Executed run

| Item | Evidence |
| --- | --- |
| Original lantern reference | `lantern-marsh/runs/20260906T214815368534Z-overscan-1f` |
| Guide | `lantern-marsh/runs/20260906T215248071614Z-overscan-24f`, positions 0–7 |
| Feedback comparator | `lantern-marsh/runs/20260906T215334143141Z-overscan-24f`, positions 0–7 |
| Frozen input bundle | `guide-redraw/references/assets/20260906T215331837248Z-guides-0000` |
| Redraw run | `guide-redraw/runs/20260906T215343267321Z-independent-redraw-8f` |
| RunPod job | `eff89190-74c1-4e35-92ed-cc5e280042d1-e2`, COMPLETED |
| Successful archive attempt | `f45d7e7bdaf4483693a192283a493af4` |
| Settings | SDXL base, 1280×720, seeds 143–150, 28 steps, CFG 6.5, denoise 0.4, DPM++ 2M/Karras |
| RunPod timing | `delayTime=79303` ms; `executionTime=31824` ms |
| Actual worker | ComfyUI 0.34.0, Python 3.12.3, PyTorch 2.11.0+cu128, NVIDIA RTX 4090 |

Paths above are relative to `apps/deforum/projects/`. Runtime is from the archived worker diagnostics; it is newer than the earlier v0.26.2 source/interface reference. This successful job directly verifies all nine required node types on the current worker. No infrastructure or shared transport changes were made by this experiment.

The original reference SHA-256 is `485958a94b85bf726c9a1fed21b15286b2fbded3b0fa23f52d26d5ab88405024`. The frozen input strip is 10240×720, 2,914,541 PNG bytes. Eight byte-identical copies of the original guide PNGs, the pixel-verified strip, graph, recipe and complete frame mapping remain in the bundle. Rechecked SHA-256 for all 12 archive files; all eight numbered outputs match the archive's sorted node-11 sequence and are 1280×720. One successful attempt, no rejected GPU attempt in this experiment.

Provider execution time includes eight independent branches and job handling; it is not isolated warm sampling time. Queue delay is separate. Shared account balance also includes other agents, so no dollar cost is attributed from its aggregate change. Parent owns pausing workers and final storage cleanup; all required artifacts here are already local.

## Findings

The actual reference contains a large illuminated pavilion left of center, a round bright sky disk, water reflections, a foreground dock and right-side trees/reeds. It does not literally realize every requested prompt object. Compare those visible structures.

- **Guide retention:** independent redraw remains close to the guide's pavilion roof, windows, reflection, cloud outlines and dock across frames 1–7. At frame 7, feedback has noticeably changed the pavilion proportions/reflection, simplified the sky shapes and altered foreground vegetation. The guide-driven branch avoids that accumulated change in this short span.
- **Variation:** independent redraw frame 0 has much stronger outlines, small bright specks and more exaggerated contrast than frames 1–7. That first transition stands out. Later frames retain similar layout but repaint reeds and small details. Feedback changes more gradually in the sequence while progressively departing from the guide.
- **Edges and quality:** narrow right-side vegetation still looks stretched or stippled in places; independent redraw does not establish a solution for depth-warp artifacts. Nothing here establishes long-shot stability or objectively better video quality.

Descriptive measurements on the same frames support the visual reading:

| Measurement, RGB levels out of 255 | Independent redraw | Feedback |
| --- | ---: | ---: |
| Mean difference from guide after BOX reduction to 64×36, frames 1–7 | 5.35 | 9.41 |
| Difference from guide at frame 7, same reduction | 5.49 | 12.00 |
| Mean adjacent-frame difference after BOX reduction to 256×144, transitions 1→2 through 6→7 | 10.71 | 9.67 |
| First transition 0→1, same reduction | 17.17 | 9.66 |

Reduced RGB difference includes color and spatial displacement; it is not a geometry metric. Adjacent-frame difference includes camera motion and is not a perceptual flicker score. Feedback frame zero is untouched, so the means exclude frame zero and its outgoing transition. Feedback also applies LAB coherence, extra noise and sharpening; successive camera warps differ from direct guide reprojection. This compares practical workflows, not feedback alone.

**Conclusion:** the small trial supports independent guide redraw as a useful structure-retention control, with greater frame-to-frame variation and a conspicuous first-frame style jump. Preserve both approaches: their visible tradeoff matches different amounts of intentional morphing. Real-time playback and a longer shot are untested here; no further rendering was requested or submitted.

## Review artifacts and reproduction

- [Guide / redraw / feedback comparison MP4](../../apps/deforum/projects/guide-redraw/exports/20260906T215605650227Z-comparison/preview.mp4): left to right, eight positions at 8 source FPS, 24 repeated delivery FPS. ffprobe verifies 1920×384, 24 frames, exactly one second.
- [All eight positions contact sheet](../../apps/deforum/projects/guide-redraw/exports/20260906T215605650227Z-comparison/contact.png).
- [Frame 7 comparison](../../apps/deforum/projects/guide-redraw/exports/20260906T215605650227Z-comparison/frames/0007.png).
- [Source paths and SHA-256 mapping](../../apps/deforum/projects/guide-redraw/exports/20260906T215605650227Z-comparison/comparison.json) and [descriptive measurements](../../apps/deforum/projects/guide-redraw/exports/20260906T215605650227Z-comparison/metrics.json).
- [Original redraw MP4](../../apps/deforum/projects/guide-redraw/runs/20260906T215343267321Z-independent-redraw-8f/preview.mp4).

The original run used these exact commands from `apps/deforum/` (the existing bundle is already submitted and refuses another submission):

```bash
uv run --with pillow python projects/guide-redraw/experiments/redraw.py prepare --guide-run projects/lantern-marsh/runs/20260906T215248071614Z-overscan-24f
uv run --env-file .env --with pillow python projects/guide-redraw/experiments/redraw.py submit --bundle projects/guide-redraw/references/assets/20260906T215331837248Z-guides-0000
```

To create a new immutable local comparison only:

```bash
uv run --with pillow python projects/guide-redraw/experiments/compare.py --redraw-run projects/guide-redraw/runs/20260906T215343267321Z-independent-redraw-8f --feedback-run projects/lantern-marsh/runs/20260906T215334143141Z-overscan-24f
```
