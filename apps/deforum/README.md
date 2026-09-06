# Deforum experiment

Work from `apps/deforum/`. Use existing Difforum custom nodes with standard ComfyUI model-loading and image nodes. The feedback loop runs on the RunPod GPU; the Mac controls the experiment and retains results.

## First render

- Model family: SDXL; select and record the exact checkpoint before downloading.
- Resolution: 1024×576.
- Duration: five seconds, eight generated frames per second, 40 frames total.
- Camera: slow 2D zoom and rotation.
- Comparison: same seed, initial prompt, and camera path; denoise 0.30, 0.40, and 0.50.
- Diffuse every frame (cadence 1), with no optical-flow smoothing. Export at 24 FPS by repeating frames.
- Save workflow JSON, model/node versions, generated PNGs, timing, and resource cost alongside the preview.

Settings are a starting experiment, not a verified quality recipe. Difforum's strength schedule controls denoising directly; do not apply classic Deforum's inverse-strength convention without checking the selected node.

## Current state

Repository scaffolding, the official RunPod skills, and the repository MCP configuration are installed. MCP OAuth sign-in succeeded; loading the tools into this active Codex session and verifying a Pod listing remain pending. The global CLI is installed but needs an API key. No GPU has been provisioned by this task, and no video has been rendered.

Source inspected: [Difforum](https://github.com/chillithebillis/Difforum) commit `1d750efd3c1d1dda792b8ef6c14b06a14a69f879`, including `examples/_smoke_render_sdxl.py` and `nodes/sampler_nodes.py`. This provides an existing SDXL graph to adapt after the Pod is accessible. It does not establish runtime compatibility.

## Next execution steps

1. Finish [RunPod authentication](../../docs/runpod.md) and inspect existing Pods. Olof is setting up the account; reuse a suitable Pod if he has already created one.
2. Inspect the live official ComfyUI template, GPU availability, price, and storage settings. Prefer an on-demand RTX 4090; establish a bounded paid session within the experiment budget.
3. Install the pinned Difforum node pack into that Pod's actual ComfyUI environment, install the selected checkpoint, and verify node registration through `/object_info`.
4. Adapt the upstream SDXL graph and run a short smoke render before the three comparisons. Use RunPod/ComfyUI APIs and existing nodes; no custom animation engine.
5. Download and visually review results. Verify checkpoint/resume behavior before longer renders, then stop paid compute and record any retained storage.

Place generated assets in ignored `outputs/` and temporary setup receipts in ignored `work/`. Keep small reusable workflow files and scripts in this directory as they are validated.
