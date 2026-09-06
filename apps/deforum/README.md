# Deforum experiment

Work from `apps/deforum/`. The Mac submits workflows and retains results; existing Difforum custom nodes run the camera-warp/img2img feedback loop inside ComfyUI on RunPod.

Start with the [project index](projects/README.md), [working convention](../../docs/workflow.md), and [filmmaking direction](../../docs/vision.md). The current priority is practicing continuation and intentional 3D movement while preserving every attempt. The [botanical cathedral project](projects/botanical-cathedral/README.md) indexes the first renders and next experiments.

Shared code stays here: `experiment.py`, `setup-pod.sh`, `workflows/`, tests and the Python environment serve every project. Each project owns its references, experiment reports, runs, cuts and exports. See [shared-code responsibilities](../../docs/workflow.md#shared-code).

## Create a project

```bash
uv run python experiment.py init-project my-film
```

Edit `projects/my-film/README.md` and its `experiments/baseline.md`, then add the project to the index. The command creates reference, run, cut and export folders and refuses to overwrite an existing project. Further experiment notes are Markdown files with lowercase hyphenated names.

## Run a comparison

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

Project references, new run media and exports are also ignored by Git. Original media is retained on the Mac; a separate disk backup has not been configured. Branching from a selected frame, automatic movie assembly, and new 3D/model workflows remain proposed experiments. See [continuation](../../docs/research/continuation-and-editing.md), [3D motion](../../docs/research/3d-camera-and-motion.md), and [model/cost research](../../docs/research/models-and-cost.md).

## Local checks

`uv run python -m unittest -v test_experiment` checks project scoping, separate render attempts, refusal to overwrite projects, and offline preservation of completed archives. These tests use temporary files and mocked submissions; they do not allocate a GPU or validate a new model.
