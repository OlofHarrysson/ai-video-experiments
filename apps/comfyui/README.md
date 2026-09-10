# ComfyUI experiments

Still-image experiments using ComfyUI on RunPod, with explicit control over composition and successive edits.

## Projects

- [Regional composition](projects/regional-composition/README.md) — three SDXL methods executed on RunPod, with two seeds per final recipe. Regional prompting is the initial recommendation; noisy composition and staged inpainting expose useful integration failures. [Results and comparisons](projects/regional-composition/experiments/results.md).
- [Regional composition followed by global refinement](projects/regional-composition/experiments/refinement.md) — the selected method now has a two-stage comparison based on Olof's tutorial reference. All media is local; the experiment's Pod is deleted.
- [Krea 2 Turbo regional comparison](projects/regional-composition/experiments/krea.md) — native eight-step generation and three-interval global refinement. Explicit left/right descriptions improve masked subject placement; all results and workflows are local, and the owned Texas Pod is deleted.

## Working layout

Each `projects/NAME/` owns its brief, `experiments/` notes, `workflows/` graphs, `references/assets/`, `runs/` and `exports/`. Track small workflow/source files and notes. Preserve original reference assets and every generated image locally in the ignored media directories. Each run should freeze prompts, regions, seeds, model hashes, actual API graph, runtime information, intermediate outputs and their hashes.

Private deployment receipts belong in `apps/comfyui/work/`. Use a project-specific remote output prefix and session receipt.

## Region selection

Olof prefers large regions with deep GPU inventory, such as the US, Ireland or Germany when offered. Sweden and Iceland are acceptable when live inventory supports the workload. Choose from actual RunPod availability rather than country size alone. The regional-composition trial is authorized for Sweden; do not provision it in Romania to reuse the existing cache. Preserve the separately authorized Romania volume.

## RunPod reuse

Follow the existing [Pod runbook](../deforum/POD.md) for the retained volume and official ComfyUI runtime. Its name, `deforum-models`, does not restrict it to animation. Keep the authorized volume; delete finished owned Pods after verified local collection.

The retained-volume trial verified **Krea assets**, not SDXL. Inspect the actual model inventory and free space before adding the proposed SDXL checkpoint. The runbook's `--krea-only --verify-only` check does not validate SDXL readiness.

Reuse the established HTTP submission/history/download protocol. The existing [Pod client](../deforum/pod_client.py) imports the Deforum runner and defaults to a Deforum deployment receipt; it is a reference, not yet a general ComfyUI client. Do not point this project at that default receipt or start an animation runner. The regional-composition project now has its own small graph runner with explicit deployment receipts, built-in nodes and local output verification. It does not import the Deforum runner.
