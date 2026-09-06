# AI Video Experiments

A public notebook for experiments with AI-assisted video creation.

The main interests are controllable camera movement, frame-by-frame diffusion workflows, and expressive motion that does not have to look perfectly temporally consistent.

## Documentation

Start with the [documentation index](docs/index.md).

Agent working context and conventions are in [AGENTS.md](AGENTS.md).

## Experiments

- [Deforum](apps/deforum/README.md): camera warping and image-to-image feedback using ComfyUI on RunPod.

## Status

Repository-scoped RunPod skills and MCP configuration are installed. The CLI is authenticated, and the first SDXL feedback renders have run successfully through existing Difforum nodes on a RunPod RTX 4090. See the [first experiment report](apps/deforum/results/2026-09-06.md) for comparisons, quality limitations, and resource cleanup.
