# Serverless continuation and 3D practice — 2026-09-06

Three serverless jobs completed: an eight-frame continuation, a depth-camera guide, and an eight-frame 3D repaint. Two 3.5-second cuts preserve the same opening and choose different continuations. The workflow works, although the first GPU host failed before starting the container. Cached requests on its replacement were much faster.

## Outputs and editorial state

- [v001: 2D continuation](../cuts/v001.md) is the current practice cut, pending Olof's playback review.
- [v002: 3D continuation](../cuts/v002.md) preserves the same opening and tests a camera change at the join. It is an alternative, not a replacement for v001.
- [Aligned camera-only guide](../exports/2026-09-06-serverless-study/guide-aligned/preview.mp4) starts on the selected anchor and uses eight existing depth warps. Its `sources.json` records every source and hash.
- [Review images and validation](../exports/2026-09-06-serverless-study/) contain contact sheets, landmark measurements and video checks. Media is local and Git-ignored.

Both cuts take parent `20260906T082559925877Z-denoise-0.40-40f` frames `[0,20)` and continuation frames `[1,9)`. They retain 28 source frames at 8 FPS, encoded as 84 delivery frames at 24 FPS, 1024×576. Every copied frame matches its source SHA-256. Both feedback runs return an anchor with pixels identical to parent frame 19; the cuts exclude that duplicate. All six new previews decode without errors.

## Runs and timing

| Run under `runs/` | Purpose | Queue delay | Handler execution |
| --- | --- | --- | --- |
| `20260906T200455570281Z-continuation-9f` | 2D continuation, absolute frames 19–27 | 1,638.118 s | 37.922 s |
| `20260906T203404890273Z-3d-parallax-9f` | Camera-only depth guide | 1.160 s | 3.731 s |
| `20260906T203510716011Z-3d-parallax-9f` | 3D feedback repaint | 1.164 s | 23.434 s |

Times come from final RunPod job responses. Handler execution includes API/model work and archive handling; it is not an isolated diffusion benchmark. All three jobs ran once on the successful replacement worker, with no job retries. Each returned nine main frames; guides also saved depth and coverage masks, and the repaint saved depth.

The first image build took 15 minutes 41 seconds. Its model hashes and CPU startup check passed; all 40 Difforum nodes and the depth nodes imported. The first host then spent about 17.5 minutes pulling/unpacking the image and failed to create its container: the Docker API returned `context deadline exceeded`. One restart did not resolve the host stall, so that owned worker was deleted. A replacement host completed its pull/start and handled the original queued request. This is a confirmed host startup failure, not a model or handler failure. The first request's queue delay includes both hosts and intervention; do not describe it as a normal cold-start benchmark or as billed GPU time.

## Visual and camera findings

Sampled join frames in v001 preserve the cathedral layout and colors; morphing and accumulated softness continue. This validates replaceable continuations, not a better final quality recipe. The color anchor resets at the selected frame, and the newer runtime means this is a creative branch rather than exact replay.

The depth map places the foreground foliage nearer than the dark central doorway. For eight camera steps, local patch matching measured approximately 20 pixels of rightward doorway displacement versus 52 pixels for left foreground and 49 pixels for right foreground. These measurements use the original guide's first and last frames and support differential parallax. They are small patch checks, not full-scene correspondence or calibrated geometry.

The camera-only guide exposes borders and disocclusions; 11.2% of its last mask is uncovered. That original guide starts at +0.02 scene X and ends at +0.18 because Difforum accumulates delta zero into pose zero. The client now uses `0:(0), 1:(0.02)` for previews, giving identity through +0.16 across nine frames. The pinned upstream schedule/camera code confirms those poses. The aligned review preview reuses the anchor plus original guide frames `[0,8)`; no generation was discarded or overwritten. The corrected graph has a local mathematical check, not an additional hosted render.

The 3D repaint produces the intended lateral move but develops visible edge artifacts and substantial morphing. It reuses initial depth on evolving images; it does not establish consistent 3D geometry over longer shots. Review findings are based on sampled frames and the depth/mask data. Smoothness and artistic preference still need Olof's playback review.

## Runtime, cost and cleanup

Hosted diagnostics confirm ComfyUI 0.34.0, Python 3.12.3, PyTorch 2.11.0+cu128 and RTX 4090. The base worker, Difforum, depth nodes, SDXL and depth weights are pinned in the [worker Dockerfile](../../../serverless/Dockerfile). The original Pod used ComfyUI 0.26.2 and PyTorch 2.10.0+cu128.

The worker limit was 0 active / 1 maximum, idle timeout 5 seconds, FlashBoot on, job timeout 600 seconds, 80 GB container disk, and a 10 GB standard archive volume in EU-RO-1. After each job, health returned to zero running workers with one idle/ready cached entry. Before teardown, all 53 cloud objects (37,135,304 bytes) were downloaded/read back and matched against local copies, including every manifest and auxiliary image.

The endpoint is retained but paused with **minimum and maximum workers both zero**. Its volume was detached and deleted; the final resource inventory showed no Pods, workers or network volumes. The account spend rate subsequently settled to $0/hour. The active local deployment file was moved into the ignored session receipts to prevent accidental reuse of a deleted volume. Observed balance changed from $49.729760 to $49.699250, approximately **$0.03** for this session at the cleanup snapshot; this is not a finalized invoice. No automatic funding setting was changed.

Keep the built image and paused endpoint for reuse. Before the next GPU session, create/attach a fresh volume, verify S3 access, write the new local deployment receipt, and then restore maximum workers to one. A push to the connected `main` branch can trigger a new image build; maximum workers remains zero while paused. See the [runbook](../../../serverless/README.md).

## Next practice

Review v001 and v002 in playback. Then choose a deliberate prompt/keyframe change for the next branch, or reduce the lateral step to investigate border artifacts. Keep SDXL and the small clip length while refining this workflow. New models, refreshed depth and longer assemblies remain separate experiments.
