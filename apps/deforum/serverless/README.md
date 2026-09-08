# Serverless worker

## Current worker: modern-model audition

The subsequent [direct ComfyUI Pod session](../projects/modern-model-study/experiments/pod-results.md) completed both model tests. Use its `audition.py`/`pod_client.py` path for that verified recipe. Olof authorizes Pods whenever they are more convenient; the serverless deployment below remains paused and its new-model inference remains unverified.

**Execution status:** both lean images built, but model preparation did not finish. No new-model inference was reached. The endpoint is paused at min/max 0 with no attached volume; zero workers, Pods and network volumes were verified at session cleanup. The deployment receipt is archived in `work/modern-model-session/serverless-deployment-closed.json`. This recipe is prepared, not a GPU-verified render path.

The active `Dockerfile` uses native ComfyUI with **Klein 4B distilled and Krea 2 Turbo**. Follow the [audition runbook](../projects/modern-model-study/experiments/baseline.md) and `audition.py`; the older `experiment.py` SDXL commands below require the preserved **`Dockerfile.sdxl`** image.

The worker uses an 80 GB container disk and an output network volume (10 GB is enough for these short clips). Startup downloads the 34.77 GB of pinned, checksum-verified assets in `modern-models.json` into worker-local `/comfyui/modern-model-cache` using the existing Hugging Face loader, then links them into ComfyUI. A restarted process on the same filesystem can reuse verified assets; a replacement worker may download them again. The job handler starts after preparation finishes. The first baked-weight build exceeded RunPod's 30-minute build limit. A subsequent direct-to-network-volume download fell below 1 MB/s, so the active recipe uses local disk.
Set endpoint environment `RUNPOD_INIT_TIMEOUT=3600` for the first preparation. RunPod documents a seven-minute default cold-start allowance, which is too short for downloading these weights. This is distinct from the 600-second job execution limit and each submitted job's queue-inclusive TTL. See [RunPod optimization](https://docs.runpod.io/serverless/development/optimization). Preserve other environment values when changing this setting.

Keep one worker for the initial sequential audition and idle timeout 120 seconds during active review; a temporary minimum of one can protect first-time preparation from the initial job TTL. Restore minimum zero after preparation and both bounds zero at cleanup. The output/archive contract is unchanged: main SaveImage node 11 and `deforum/projects/PROJECT/` on the volume. At cleanup, verify and preserve every object under that output prefix, including failed attempts; the failed preparation left reproducible public model-cache partials on this session’s volume; those can be deleted with the volume. Pause workers, detach and delete the owned volume after local verification. Record actual infrastructure state in the session report.

## Earlier SDXL worker and sessions

Status: forty-four custom-worker jobs completed and outputs verified locally. The latest [Brain Entity study](../projects/brain-entity-study/experiments/style.md) adds six stills and two six-second videos using the creator-credited SDXL art LoRA and QR ControlNet. All 122 archive objects are local. The endpoint is paused (min/max workers 0), idle timeout restored to five seconds, with no volume or workers retained. Earlier results include the [ten-experiment round](../../../docs/research/ten-experiments-session.md), [Seedream motion/crash recovery](../projects/seedream-motion/experiments/motion.md), and [first serverless session](../projects/botanical-cathedral/experiments/serverless-results.md).

Both recipes extend RunPod's existing ComfyUI worker. The small `handler.py` adapter adds a persistent archive and returns a manifest instead of transmitting an entire PNG sequence through the job response. The original SDXL recipe installs Difforum/depth nodes; later feedback experiments also use standard ComfyUI sampling with local spatial transforms. No new diffusion or depth algorithm is implemented here.

## Resume the existing endpoint

The endpoint named `deforum-experiments` and its built image are retained. Do not create a duplicate endpoint. Check current Serverless GPU availability per region before creating a fresh 10 GB volume, attach it, set the matching endpoint data-center preference, write `work/serverless-deployment.json` with the actual new volume ID, verify S3 access, and restore maximum workers to three (minimum stays zero). The latest closed deployment receipt is in `work/noise-steps-session/`. The noise/steps session moved from throttled EU-RO-1 to US-IL-1, but still needed roughly eleven minutes of initial US queue/image setup. Both temporary volumes are deleted; the paused endpoint currently prefers US-IL-1. Existing run receipts retain their original deployment IDs; completed `collect` remains offline.

After jobs finish, verify all cloud objects against local copies, including auxiliary and partial outputs. Set min/max workers to zero, detach the volume, confirm zero workers, then delete the volume. Verify the final Pod, worker and volume inventories and account spend rate. Keep old local generations and cuts. Moving the active deployment file into session receipts prevents accidental reuse of a deleted volume.

For detachment, the tested MCP update with an empty volume array did not clear the attachment. An explicit REST v2 `PATCH /v2/serverless/ENDPOINT_ID` body `{"networkVolumes":[]}` did, confirmed by readback. Do not assume a successful mutation response means the desired fields changed.

GitHub pushes to `main` trigger builds. The paused endpoint cannot launch GPU workers while its maximum remains zero. Reuse the verified image for experimentation unless worker code or dependencies need a rebuild.

## Initial deployment from this repository

1. In RunPod Settings → Connections, authorize GitHub for only `OlofHarrysson/ai-video-experiments`.
2. Create an S3 API key in RunPod Settings. Fill `RUNPOD_S3_ACCESS_KEY_ID` and `RUNPOD_S3_SECRET_ACCESS_KEY` in the app's ignored `.env`. These stay on the Mac; the worker writes directly to its mounted volume.
3. Create a **10 GB standard network volume** in an S3-enabled data center with 4090 capacity (first candidate EU-RO-1). Storage is approximately $0.70/month while retained, even at zero GPU workers. Check live capacity and price before creating it.
4. In Serverless → New Endpoint → Import Git Repository, select this repository, branch `main`, Dockerfile `apps/deforum/serverless/Dockerfile`, **build context repository root**. RunPod builds and stores the image in its own registry; Docker Hub credentials are not needed.
5. Use endpoint name `deforum-experiments`, type **Queue**, 4090/24 GB Pro, 1 GPU per worker, **active workers 0**, **max workers 3**, idle timeout **5 seconds**, execution timeout **600 seconds**, FlashBoot enabled. Attach the volume. Use an 80 GB container disk for the ComfyUI image and baked models. Container storage is billed while allocated; the network volume is the durable output archive.
6. Write the actual resource IDs into ignored `apps/deforum/work/serverless-deployment.json`:

```json
{
  "endpoint_id": "ACTUAL_ENDPOINT_ID",
  "volume_id": "ACTUAL_VOLUME_ID",
  "data_center": "EU-RO-1",
  "s3_endpoint": "https://s3api-eu-ro-1.runpod.io"
}
```

Use the chosen volume's real data center/S3 URL. Keep private infrastructure responses in `work/`. Endpoint configuration and a successful build do not prove a working render.

## First real test

From `apps/deforum/`:

```bash
uv sync
uv run --env-file .env python experiment.py continue \
  --project botanical-cathedral --experiment continuation \
  --parent-run 20260906T082559925877Z-denoise-0.40-40f \
  --frame 19 --new-frames 8
```

This preserves the parent's absolute frame schedules and incrementing seed. The returned batch includes the anchor at local index 0 and eight new frames. Difforum's color-coherence anchor resets to the selected frame, so this is a creative branch rather than an exact reconstruction of the old run. The serverless base has a newer ComfyUI/PyTorch runtime than the original Pod; record this when comparing images.

The runner checks S3 access before submitting. It never retries a job submission automatically. Reconnect to an existing attempt with:

```bash
uv run --env-file .env python experiment.py collect projects/botanical-cathedral/runs/RUN_ID
```

On the volume, each invocation/retry gets `deforum/projects/PROJECT/runs/RUN/attempts/UUID/`. Input PNGs, exact executed graph, diagnostics/runtime details, rendered outputs and a checksum manifest survive worker shutdown. The local collector downloads every completed attempt found under the run, verifies hashes, and refuses to silently choose if multiple successful attempts exist. The main sequence is SaveImage node `11`; auxiliary depth/mask images retain their node directories under `cloud/UUID/`.

Difforum returns its frame batch at the end. An interrupted diffusion loop does not expose its in-memory intermediate frames; completed SaveImage outputs and the request archive persist. A terminal job without a manifest requires inspecting the partial volume directory and worker logs. Never purge a queue or delete a volume containing the only copy of generated media.

## Assemble the first cut

Create a JSON list with actual source run names:

```json
[
  {"run": "20260906T082559925877Z-denoise-0.40-40f", "in": 0, "out": 20},
  {"run": "ACTUAL_CONTINUATION_RUN", "in": 1, "out": 9}
]
```

Pass that file to `uv run python experiment.py assemble --project botanical-cathedral --version v001 --ranges PATH.json`. Out points are exclusive. The command copies source PNGs unchanged, verifies their hashes, saves exact source ranges in `exports/v001/cut.json`, writes `cuts/v001.md`, and encodes the 28-frame, 3.5-second preview. Existing cut versions are never overwritten. Select the current cut explicitly in the project README after review.

## Then test the camera

Use the same parent/frame with `camera-preview --project botanical-cathedral --parent-run RUN --frame 19 --new-frames 8`. It produces nine depth-warped frames plus the depth map and coverage masks. Preview this before `continue ... --experiment 3d-parallax --camera 3d`.

The initial move is +0.02 scene-space X per frame, which moves scene points right (equivalent to camera translation left). FOV is 45°, relative near/far are 1/10, bright depth means near, `invert_depth=false`, zoom 1 and rotation 0. These are arbitrary relative units, not calibrated meters. The camera-only guide uses a zero first delta (`0:(0), 1:(0.02)`) so its first pose is identity, then reprojects the original anchor at cumulative poses. The original hosted guide was one step ahead; its preserved frames were aligned locally for review, and the corrected schedule was verified against pinned upstream camera code. The later lantern-marsh guide verified the identity frame pixel-for-pixel on the GPU. The diffusion loop reuses its initial depth map on evolving images; keep this test short.

## Validation and billing evidence

Record a real completed job, local frame counts/hashes, the join in playback, and the selected source ranges. Read endpoint health/workers after completion and verify GPU workers actually stop. Then recover the archive from S3 without a GPU. Record cold delay, execution duration, billed worker lifetime, volume cost and the account balance after charges settle. Queue time is not a direct measure of billed startup time.

`workersMin=0` allows scale-to-zero; it is not a total spending cap. New requests and provider retries can still start workers. Delete only owned compute resources if a worker gets stuck. Retain the output volume until its contents are safely copied; explicitly report its ongoing storage charge.

## Versions and sources

- [RunPod worker](https://github.com/runpod-workers/worker-comfyui/tree/5.10.0): 5.10.0, commit `724802b`; amd64 image digest pinned in Dockerfile. Its base targets ComfyUI 0.34.0 / CUDA 12.8; verify actual runtime from the render diagnostics.
- Difforum `1d750efd3c1d1dda792b8ef6c14b06a14a69f879`; same [MIT source](https://github.com/chillithebillis/Difforum) as the baseline.
- [Depth Anything nodes](https://github.com/kijai/ComfyUI-DepthAnythingV2/tree/553187872eeb1d52e50dc53209fa57e569609a72), plus Small FP32 weights, revision `5aa7ab578df757d94c743998b157a0204ff29215`. Small weights use Apache 2.0; larger models have different terms. Exact model SHA-256s are checked during build.
- SDXL checkpoint revision/hash match the original Pod recipe. Weights are downloaded during build and are not committed.
- [GitHub builds](https://docs.runpod.io/serverless/workers/github-integration), [RunPod S3](https://docs.runpod.io/storage/s3-api), [billing](https://docs.runpod.io/serverless/pricing).

Local checks: `uv run python -m unittest -v`. They exercise continuation indexing, immutable cuts, distinct retries, failed-attempt retention, checksum rejection and offline/cloud recovery using temporary data and mocked APIs. A separate local assembly check with 28 real baseline PNGs produced a 1024×576, 3.5-second H.264 preview with 84 delivery frames at 24 FPS; source-frame hashes matched. It reused original footage and did not generate a continuation. These checks do not replace the hosted test.

## Art model package and setup latency

The Brain Entity study adds `xl_more_art-full_v1.safetensors` and `qr-sdxl-comfy.safetensors`. Source hashes and URLs are checked in Dockerfile. The QR source mixes original UNet keys with four Diffusers embedding keys; `convert_qr_controlnet.py` renames these in the safetensors header using ComfyUI’s mapping and copies all tensor bytes unchanged. Both models passed actual GPU inference with native LoraLoader, ControlNetLoader and ControlNetApplyAdvanced, plus Difforum feedback.

Build `f106834` took 18m55s. The first still job had 390.206s queue/startup delay and 20.931s execution; the next had 0.111s delay and 12.581s execution. The two 48-frame videos ran in 174.063s and 172.596s with sub-second queue delay on the warm worker. Build time, cold start and inference are separate costs in time. A new model/node package needs a build; request prompts/settings and graphs using installed nodes/models do not. GitHub pushes currently trigger builds even for documentation, so reuse the recorded GPU-verified image for a session.

The first art package retained the original 5 GB QR weights in a previous container layer after conversion. The revised Dockerfile performs download, conversion and deletion in the same layer, excluding the intermediate from the final layer contents. This packaging revision was not the image used for the first study; its next build remains separate from the verified render evidence. Keep a temporary 120-second idle window when reviewing between jobs, then restore five seconds and pause min/max workers before cleanup.
