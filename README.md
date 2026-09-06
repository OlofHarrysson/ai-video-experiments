# AI Video Experiments

A public notebook for experiments with AI-assisted video creation.

The main interests are controllable camera movement, frame-by-frame diffusion workflows, and expressive motion that does not have to look perfectly temporally consistent.

The current focus is an iterative filmmaking practice: preserve every generation, continue from chosen frames, and assemble the best ranges into versioned cuts. [Creative direction](docs/vision.md) · [Working convention](docs/workflow.md) · [Project index](apps/deforum/projects/README.md).

## Documentation

Start with the [documentation index](docs/index.md).

Agent working context and conventions are in [AGENTS.md](AGENTS.md).

## Experiments

- [Deforum](apps/deforum/README.md): camera warping and image-to-image feedback using ComfyUI on RunPod.

## Status

Repository-scoped RunPod skills and MCP configuration are installed. The CLI is authenticated, and the first SDXL feedback renders have run successfully through existing Difforum nodes on a RunPod RTX 4090. See the [first experiment report](apps/deforum/projects/botanical-cathedral/experiments/baseline-results.md) for comparisons, quality limitations, and resource cleanup.

Project folders and project-aware render receipts are implemented. Continuation, 3D camera validation and modern-model comparison are documented next experiments; a movie-editing harness is not yet implemented.
