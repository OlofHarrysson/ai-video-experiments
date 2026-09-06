# E07 — native Seedream frame repaint

## Question and planned test

Can native Seedream 4 Edit repair small depth-warp gaps while retaining the preferred Seedream marsh appearance better than previous SDXL redraws? This is an independent-frame sequence, with no previous edited output fed into the next request.

- Source: preserved preferred Seedream marsh still, prepared at 1280×720.
- Guide: 32 frames, 8 source FPS, four seconds; identity frame zero, horizontal translation 0.002 per subsequent step, initial DepthAnything V2 small depth, near 1/far 10, FOV 45°.
- Repaint: original frame zero plus 31 Seedream 4 Edit requests, each receiving its own guide PNG. Same repair prompt for every frame; hosted API exposes no deterministic seed in the documented schema.
- First validate frames 1 and 31, then complete remaining edits with at most four public calls in flight. Budget ceiling $4; no automatic retry of uncertain submissions.
- Preserve original outputs at actual returned dimensions; normalize by explicit Lanczos resize only for the 1280×720 video, with no crop or optical-flow interpolation. Deliver at 24 FPS by repeating each source frame three times.
- Inspect timestamped overview frames and targeted context around the first repaint. Sampled frames do not establish playback quality.

RunPod [Seedream 4 Edit documentation](https://docs.runpod.io/public-endpoints/models/seedream-4-edit), checked 2026-09-07, specifies `prompt`, `images` URL array, `size` and safety checker, with $0.027 per image. Exact managed model revision is not exposed. Request and response URLs remain in ignored run receipts; images are downloaded immediately.

## Results

The guide completed remotely: 2.284 seconds queued and 11.144 seconds execution. Its final frame visibly tears the foreground lantern/reeds even at this modest lateral displacement.

The first two public edit requests using presigned network-volume URLs failed before generation with HTTP 401 from the image fetcher. RunPod's [S3 compatibility table](https://docs.runpod.io/storage/s3-api) explicitly excludes presigned URLs. Both failed jobs and their receipts remain preserved. The corrected requests carry the owned guide PNGs as inline data URLs to the same endpoint, without creating new storage objects.

All 31 inline edits succeeded: each returned a 2560×1440 JPEG despite requesting 2048×1152, response URLs under `output.result`, reported cost $0.027 each. The full sequence is rendered and preserved. This is an exploratory comparison with prior SDXL results, not a controlled model-only A/B: camera trajectory and repair instruction also differ.

### Video outputs

- [Native Seedream video](../exports/e07-native-seedream-v001/preview.mp4): four seconds, 1280×720, 32 source images (one original anchor and 31 distinct model outputs), 96 delivery frames at 24 FPS. Every generated image was normalized by Lanczos resize without cropping.
- [Guide left / Seedream edit right](../exports/e07-native-seedream-v001/guide-left-edit-right.mp4): same four-second sequence, two 640×360 panels. The left side contains only camera warps; the right side contains the native model edits.
- [Overview samples](../exports/e07-native-seedream-v001/reviews/preview/v001/contact-sheet.jpg) and [early event context](../exports/e07-native-seedream-v001/reviews/preview/v002/contact-sheet.jpg).

### Visual findings

The lantern, domed observatory, winding path, blue mushrooms and teal/amber/violet palette remain recognizable across the inspected start, middle and end samples. This avoids the wholesale tower/mushroom redesign seen in the earlier strong SDXL feedback test. Native editing is worth pursuing for this visual style.

The edit introduces an irregular pale bare-canvas border that changes between frames. At 0.125 seconds the first native frame already changes surface texture and some lantern geometry; at 0.375 and 0.5 seconds the pale border becomes large, then shrinks at 0.625 seconds. At 0.791667 seconds the top edge is especially conspicuous. The final 3.958333-second sample retains the important objects but changes texture and foreground details. The node-generated warped guide is repaired through a whole-image instruction, not a hard spatial mask, so the request does not constrain Seedream to alter only missing pixels.

Verdict: useful style-preservation result, unfinished animation. The next targeted refinement would constrain border handling and unchanged image regions. Scene identity is encouraging; stable motion and pleasant flicker are not established by this frame review. Full playback still needs Olof's judgment. No optical-flow interpolation or automatic aesthetic scoring was used.

### Timing, cost and preservation

| Item | Observed result |
| --- | --- |
| Native edits completed | 31, all distinct output hashes |
| Failed transport probes | 2 terminal failures, both preserved separately |
| Public API reported cost | $0.837 total for the 31 successful edits |
| Per-edit execution | 16.670–70.118 seconds; median 19.410 seconds |
| Sum of public execution times | 667.766 seconds across concurrent jobs |
| Public queue time, summed | 14.863 seconds |
| Inline first submission to final local collection | 281.832 seconds including two-frame review and staged launch |
| Custom depth guide | 2.284 seconds queue, 11.144 seconds execution |
| Source and delivery rate | 8 new/anchor images per second; 24 FPS by triplication |

The $0.837 is the sum of public job response costs; it excludes shared guide compute/storage and does not assert billing treatment for the two failed probes. The parent session owns the account-level cost and infrastructure cleanup record.

The guide's 69 manifest-listed archive files passed local byte-count and SHA-256 checks. All 31 original model images and normalized PNGs passed their recorded hashes. Frame zero is pixel-identical to the preserved reference, and FFprobe verified 96 delivery frames over exactly four seconds. Every guide frame was archived under the usual owned project prefix; no extra S3 objects, external hosts or infrastructure were created. Original responses and signed URLs remain in ignored run folders.

Run inventory:

- Guide: `20260906T232451717224Z-e07-native-edit-32f` (custom job `91fefe01-816a-48f6-85f9-fde3bf078406-e2`).
- Failed presigned probes: `e07-native-20260906T232451717224Z-e07-native-edit-32f`.
- Successful edits: `e07-native-inline-20260906T232451717224Z-e07-native-edit-32f`; each `frame-NNNN/` holds request, submission, job status, original image and result hashes. Exact executed inline recipe is frozen here as `recipe.py`.
- Export manifest: `exports/e07-native-seedream-v001/cut.json`, with all 31 job IDs, costs and lineage; `verification.json` contains the final media checks.

## Reproduce

From `apps/deforum/`, with the shared deployment already attached by the parent session:

```bash
uv run --env-file .env --with pillow python projects/seedream-repaint/experiments/native_edit.py guide
uv run --env-file .env --with pillow python projects/seedream-repaint/experiments/native_edit.py smoke --guide-run GUIDE_RUN
# Inspect both returned frames before the remaining requests.
uv run --env-file .env --with pillow python projects/seedream-repaint/experiments/native_edit.py complete --guide-run GUIDE_RUN
```

The adapter collects existing jobs when their submission response is present. A saved request with no response is treated as an uncertain submission and is never automatically reposted. Existing successful frames are reused. Failed transport receipts remain in a separate immutable run directory.
