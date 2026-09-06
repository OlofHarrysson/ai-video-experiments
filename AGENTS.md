# Repository guidance

## Active project

AI Video Experiments is a public notebook and workspace for controllable AI animation. The creative interest is explicit camera movement combined with surreal morphing and visible frame-by-frame repainting. Perfect temporal consistency is not the goal.

- Current experiment: `apps/deforum/`, using existing Difforum nodes in ComfyUI on RunPod.
- Current priority: establish a usable iterative filmmaking workflow, then intentional 3D camera movement and quality improvements. Build toward 30-second, one-minute and five-minute assemblies from manageable clips; avoid a one-shot long render.
- Mac: authoring, controls, previews, and local copies of results. RunPod: model inference and the camera-warp/img2img feedback loop.
- First milestone complete: three five-second SDXL clips with the same initial image, seed sequence, and camera path at different denoise strengths. Outputs are local; the experiment Pod was deleted.
- Runnable path: `uv run python experiment.py init-project NAME`, then `run --project NAME --experiment EXPERIMENT ...` in `apps/deforum/`. Write the experiment note before rendering. Serverless is the selected next path; its worker and client are prepared, but deployment and GPU verification are pending. See `apps/deforum/serverless/README.md`. MCP endpoint listing is now verified; the CLI also works.
- Seed finding: incrementing the feedback seed retained more detail than a fixed seed in the first short test. Review full-length quality in the session report before choosing the next recipe.
- Playback feedback: 0.30 is too smooth; 0.50 flickers too much. Frame sharpness alone does not establish video quality. Keep detail, flicker, structure and camera control separate in reviews.
- Next experiments: branch from frame 19 of the middle-denoise baseline, assemble the preserved opening, then prove depth-based parallax. Continuation/cut commands and a depth-camera graph are locally implemented; hosted execution is pending. Current 3D feedback reuses initial depth through the loop and does not establish long-shot scene consistency.
- Budget: $50 total for the initial experiments; target under $10 for initial setup and comparisons. Check current resource prices and account state before provisioning.
- Recurring cost should remain near SDXL; reconsider before approaching 3× a comparable render. Separate warm inference cost from setup/idle time and rejected attempts.

## Working conventions

- Start with the [documentation index](docs/index.md) and the relevant app README. Shared explanations belong in `docs/`; runnable experiments belong in `apps/`.
- Prefer existing nodes and workflows. Add custom code only for a concrete missing capability.
- Use the repository's RunPod skills in `.agents/skills/` for RunPod work. Keep RunPod skills and MCP configuration scoped here; the CLI may be installed globally.
- Keep credentials in ignored local files or the credential store. Never commit keys, OAuth tokens, or private account responses.
- Inspect Git status and preserve unrelated work. Keep changes on the existing branch unless asked otherwise.
- Record workflow/model versions, settings, and outputs for each experiment. Distinguish source inspection, local checks, remote execution, and visual review.
- Preserve every generation, original reference and cut version. All project media belongs under `projects/PROJECT/`, including the first session. Shared runner, setup code and reusable workflow recipes stay at app level. A working cut references source ranges and never overwrites a generation. Git ignores media; no separate-disk backup is configured yet.
- Keep the product vision and research living. Defer automatic editing/branching infrastructure and the simple-3D-scene-to-stylization hypothesis until short experiments justify them.
- Check for an existing user-created Pod before provisioning. Track the resources owned by this experiment and shut down paid compute when finished; retained storage can still cost money.

## Documentation

- [Documentation index](docs/index.md): canonical map of shared notes and app runbooks.
- [Creative direction](docs/vision.md) and [working convention](docs/workflow.md).
- [Project index](apps/deforum/projects/README.md): project briefs, experiments and current cuts.
- [Deforum mechanism and creative direction](docs/deforum.md).
- [RunPod tools and repository setup](docs/runpod.md).
- [Deforum experiment](apps/deforum/README.md): current state and next execution steps.
- [First session results](apps/deforum/projects/botanical-cathedral/experiments/baseline-results.md): execution, visual findings, and cost.
