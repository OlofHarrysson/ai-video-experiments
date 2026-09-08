# Deforum experiment

Work from `apps/deforum/`. The Mac submits workflows and retains results; existing Difforum custom nodes run the camera-warp/img2img feedback loop inside ComfyUI on RunPod.

Start with the [project index](projects/README.md), [working convention](../../docs/workflow.md), and [filmmaking direction](../../docs/vision.md). The current priority is practicing continuation and expressive spatial image movement while preserving every attempt. The [Safety Marc spatial-control study](../../docs/research/bonsai-spatial-motion.md) maps existing effects to camera transforms, guide flow and guide compositing. The completed [Move-Warp test](projects/motion-guide-study/experiments/move-warp.md) adds a Mac-orchestrated guide-flow loop using existing ComfyUI repaint nodes. The [parallel experiment report](../../docs/research/parallel-experiments-session.md) indexes earlier model, settings, overscan and guide-redraw results.

Latest direct-motion result: [sampling steps and input noise](projects/motion-guide-study/experiments/noise-steps.md). Olof selects denoise 0.45 and rejects regional protection artifacts. The completed 18/36-step tests found no convincing grain-removal benefit from doubling steps; half the added noise is a candidate for playback review. All five short clips are local and cloud resources are cleaned up.

Shared code stays here: `experiment.py`, `editing.py`, `serverless_client.py`, `workflow_recipes.py`, `serverless/`, `setup-pod.sh`, `workflows/`, tests and the Python environment serve every project. Each project owns its references, experiment reports, runs, cuts and exports. See [shared-code responsibilities](../../docs/workflow.md#shared-code).

Current study: [Brain Entity temporal continuity](projects/brain-entity-study/experiments/continuity.md) compares diffusion-seed continuity, pixel noise and separate flow/interpolation finishing. The generation tests reuse the existing worker; local finishing keeps cloud resources off. See the [project index](projects/brain-entity-study/README.md) for all preserved comparisons and playback findings.

Current creative baseline: **P3 + RIFE**, tentatively preferred by Olof. The [review harness practice](projects/brain-entity-study/experiments/review-harness.md) now supports bounded, paginated overviews, every-frame time windows and timestamp-matched comparisons. Follow the [review and feedback agreement](../../docs/review-and-feedback.md): screen results first, explain changes plainly and show a small shortlist of inline videos.

Current learning exercise: [motion-guide walkthrough](projects/motion-guide-study/README.md), with measured local optical-flow warps and six real native ComfyUI img2img outputs. It shows the intermediate pixels separately from diffusion, before integrating that mechanism into the feedback loop. Continue with ComfyUI; A1111/Forge is deferred.

Latest: [ten adaptive video experiments](../../docs/research/ten-experiments-session.md) compare story cuts, camera/settings, independent redraw, native Seedream per-frame editing and masked repairs. [Local video review](../../docs/video-review.md) extracts timestamped frames and event context into preserved review versions. See the [filmmaking guide](../../docs/research/filmmaking-for-ai-animation.md) for visual storytelling, shot design and editing practice.

## Verified execution: Serverless

Serverless ran the continuation, depth guide and 3D repaint. The [worker runbook](serverless/README.md) owns deployment, S3 credentials, scale-to-zero settings, continuation, cut assembly and the depth-camera test. The [first session report](projects/botanical-cathedral/experiments/serverless-results.md) records three successful jobs and two preserved cuts; the [parallel round](../../docs/research/parallel-experiments-session.md) adds five custom-worker jobs and three public image API calls. The endpoint is now paused with min/max workers zero, and the archive volume is deleted.

`run` without `--url` uses Serverless. `continue` and `camera-preview` use the same transport. Load `.env` with `uv run --env-file .env` for submission/collection. A maximum of three GPU workers, zero active workers and a five-second idle timeout are the current experimentation configuration. A 10 GB archive volume costs approximately $0.70/month while retained; none is currently retained. Recreate and attach one before restoring max workers to three.

## Create a project

```bash
uv run python experiment.py init-project my-film
```

Edit `projects/my-film/README.md` and its `experiments/baseline.md`, then add the project to the index. The command creates reference, run, cut and export folders and refuses to overwrite an existing project. Further experiment notes are Markdown files with lowercase hyphenated names.

## Earlier verified Pod comparison

Requirements: `uv`, `ffmpeg`, the global `runpodctl` CLI, a RunPod API key in ignored `.env`, and an accessible ComfyUI Pod with the checkpoint and nodes below. See [RunPod setup](../../docs/runpod.md) for repository-scoped tools and authentication.

```bash
uv sync
uv run --env-file .env runpodctl pod list
```

Before provisioning, inspect existing Pods and current pricing. The verified configuration was the official ComfyUI template `cw3nka7d08`, image `runpod/comfyui:cuda12.8`, RTX 4090 24 GB, 150 GB container disk, 50 GB Pod volume mounted at `/workspace`, and ports `8188/http,22/tcp`. Add your SSH public key as `PUBLIC_KEY`. The first session used secure cloud in EU-RO-1 at $0.74/hour before storage; availability and rates can change. The session target is under $10 against a $50 initial budget.

Run the installer over SSH using the Pod's current IP and mapped SSH port:

```bash
ssh -i ~/.ssh/id_ed25519 -p SSH_PORT root@POD_IP 'bash -s' < setup-pod.sh
```

The installer checks the image's Python path, installs pinned Difforum and its requirements, and downloads checksum-verified SDXL. Check `/object_info` after startup; restart the Pod if ComfyUI loaded before the nodes were installed. Wait until `/system_stats` responds and `/object_info` contains `DifforumFeedbackSampler` before submitting.

```bash
uv run python experiment.py run --project botanical-cathedral --experiment baseline --url https://POD_ID-8188.proxy.runpod.net --frames 8 --denoise 0.4
uv run python experiment.py run --project botanical-cathedral --experiment baseline --url https://POD_ID-8188.proxy.runpod.net --frames 40 --denoise 0.3
uv run python experiment.py run --project botanical-cathedral --experiment baseline --url https://POD_ID-8188.proxy.runpod.net --frames 40 --denoise 0.4
uv run python experiment.py run --project botanical-cathedral --experiment baseline --url https://POD_ID-8188.proxy.runpod.net --frames 40 --denoise 0.5
```

Each run saves its exact API graph, submission receipt, runtime information, ComfyUI history, numbered PNG frames, and `preview.mp4` in a unique ignored `projects/PROJECT/runs/RUN_ID/` directory. Its receipt identifies the project and experiment. Both the project and experiment note must exist before submission. `workflows/sdxl-feedback.api.json` is the editable canonical graph in ComfyUI API format. Change prompts and camera schedules there; each run freezes its own copy. The first session is stored in the botanical cathedral project alongside new runs.

To reconnect to an already submitted job after a client interruption:

```bash
uv run python experiment.py collect projects/PROJECT/runs/RUN_ID
```

`collect` polls the existing job and downloads its outputs; it does not resubmit or resume GPU computation. Completed archives, including migrated first-session runs, return their existing preview offline without rewriting assets. Missing assets in a completed archive raise an error rather than triggering regeneration. Worker checkpoint/resume is not verified. The feedback node returns the frame batch after rendering finishes, so keep initial runs short. A client timeout does not stop remote compute.

After saving outputs locally, delete the experiment's own Pod to remove compute and attached storage charges:

```bash
uv run --env-file .env runpodctl pod delete POD_ID
uv run --env-file .env runpodctl pod list
```

Stopping a Pod retains billable storage. CLI 2.12.0 does not expose the `--terminate-after` option mentioned in some skill examples; consult live help and explicitly clean up the session. Do not assume an automatic provider-side shutdown is configured.

## Workflow

- SDXL base 1.0, 1024×576, 28 steps, CFG 6.5, DPM++ 2M / Karras.
- Seed 21 for the initial image; increment the seed each feedback frame.
- Forty frames at eight generated FPS; five-second H.264 export at 24 FPS by repeating frames, without optical-flow interpolation.
- A botanical cathedral prompt blends toward an underwater coral cathedral by frame 39.
- Per-frame 2D zoom 1.015 and rotation 0.4 degrees; cadence 1.
- Denoise comparison 0.30 / 0.40 / 0.50, with the same seed sequence and camera path.
- Existing node controls: LAB color coherence 0.8, noise 0.02, sharpening 0.2.

Difforum's strength schedule is denoising directly. The one-second smoke test covers only the beginning of the 40-frame prompt schedule. Reusing a fixed seed produced rapid artifacts in this scene; incrementing seeds retained substantially more detail in the smoke comparison.

## Versions and provenance

- [Difforum](https://github.com/chillithebillis/Difforum/tree/1d750efd3c1d1dda792b8ef6c14b06a14a69f879), version 0.6.0, commit `1d750efd3c1d1dda792b8ef6c14b06a14a69f879`. The graph adapts `examples/_smoke_render_sdxl.py`; upstream MIT license is in `DIFforum-LICENSE`. No custom ComfyUI nodes or animation engine are implemented here.
- [SDXL base 1.0](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/tree/462165984030d82259a11f4367a4eed129e94a7b), revision `462165984030d82259a11f4367a4eed129e94a7b`, checkpoint `sd_xl_base_1.0.safetensors`, SHA-256 `31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b`. Model use is governed by its model card and license; weights are not committed.
- Verified remote runtime: ComfyUI 0.26.2, frontend 1.45.19, Python 3.12.3, PyTorch 2.10.0+cu128, RTX 4090.
- Image digest observed in Pod pull logs: `sha256:498e3c4ac7ef5071214badb1681d82ab3a8f922b1055742ae692fa02cd3b59ff`. The installer expects this image layout; the mutable CUDA tag may change.

## Results

[First session, 2026-09-06](projects/botanical-cathedral/experiments/baseline-results.md) records render outcomes, visual findings, timing, cost, and cleanup. Rendered media lives in each project’s ignored `runs/` and `exports/` folders. Private infrastructure receipts stay in app-level `work/`; small scripts, workflow files, and reports are tracked.

Project references, run media and exports are ignored by Git. Original media is retained on the Mac; a separate disk backup has not been configured. Continuation, explicit-range cut assembly and depth-camera rendering have passed their first hosted session. The preview schedule starts with identity; the lantern-marsh guide verified its first image pixel-identical to the reference on the GPU. FLUX.1 Dev and Seedream 4.0 still comparisons are now complete; using them for per-frame animation remains untested. See [continuation](../../docs/research/continuation-and-editing.md), [3D motion](../../docs/research/3d-camera-and-motion.md), and [model/cost research](../../docs/research/models-and-cost.md).

## Local checks

`uv run --with pillow python -m unittest -v` runs 30 local checks covering project/archive behavior, immutable cuts, continuation indices, rejected submissions, interpolation timing, selective frame review, matched comparisons, pagination and provenance. They use temporary media and mocked submissions; they do not allocate a GPU or validate a new model.
