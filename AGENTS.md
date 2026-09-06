# Repository guidance

## Active project

AI Video Experiments is a public notebook and workspace for controllable AI animation. The creative interest is explicit camera movement combined with surreal morphing and visible frame-by-frame repainting. Perfect temporal consistency is not the goal.

- Current experiment: `apps/deforum/`, using existing Difforum nodes in ComfyUI on RunPod.
- Mac: authoring, controls, previews, and local copies of results. RunPod: model inference and the camera-warp/img2img feedback loop.
- First milestone complete: three five-second SDXL clips with the same initial image, seed sequence, and camera path at different denoise strengths. Outputs are local; the experiment Pod was deleted.
- Runnable path: `uv run python experiment.py` in `apps/deforum/`; `setup-pod.sh` installs pinned nodes and SDXL in the official ComfyUI image. Use the CLI for infrastructure until MCP tool execution is verified.
- Seed finding: incrementing the feedback seed retained more detail than a fixed seed in the first short test. Review full-length quality in the session report before choosing the next recipe.
- Main unknown: how to retain fine detail while producing compelling morphing. Denoise 0.50 was the strongest first comparison, but detail still fades. Verify a short render before extending it or changing models.
- Budget: $50 total for the initial experiments; target under $10 for initial setup and comparisons. Check current resource prices and account state before provisioning.

## Working conventions

- Start with the [documentation index](docs/index.md) and the relevant app README. Shared explanations belong in `docs/`; runnable experiments belong in `apps/`.
- Prefer existing nodes and workflows. Add custom code only for a concrete missing capability.
- Use the repository's RunPod skills in `.agents/skills/` for RunPod work. Keep RunPod skills and MCP configuration scoped here; the CLI may be installed globally.
- Keep credentials in ignored local files or the credential store. Never commit keys, OAuth tokens, or private account responses.
- Inspect Git status and preserve unrelated work. Keep changes on the existing branch unless asked otherwise.
- Record workflow/model versions, settings, and outputs for each experiment. Distinguish source inspection, local checks, remote execution, and visual review.
- Check for an existing user-created Pod before provisioning. Track the resources owned by this experiment and shut down paid compute when finished; retained storage can still cost money.

## Documentation

- [Documentation index](docs/index.md): canonical map of shared notes and app runbooks.
- [Deforum mechanism and creative direction](docs/deforum.md).
- [RunPod tools and repository setup](docs/runpod.md).
- [Deforum experiment](apps/deforum/README.md): current state and next execution steps.
- [First session results](apps/deforum/results/2026-09-06.md): execution, visual findings, and cost.
