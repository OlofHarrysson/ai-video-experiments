# ComfyUI experiments

Still-image experiments using ComfyUI on RunPod, with explicit control over composition and successive edits.

## Projects

- [Regional composition](projects/regional-composition/README.md) — construct a scene from background and foreground prompts, using rectangles first and arbitrary masks afterward. Research and a proposed first test are ready; no project renders have run.

## Working layout

Each `projects/NAME/` owns its brief, `experiments/` notes, `workflows/` graphs, `references/assets/`, `runs/` and `exports/`. Track small workflow/source files and notes. Preserve original reference assets and every generated image locally in the ignored media directories. Each run should freeze prompts, regions, seeds, model hashes, actual API graph, runtime information, intermediate outputs and their hashes.

Private deployment receipts belong in `apps/comfyui/work/`. Use a project-specific remote output prefix and session receipt.

## RunPod reuse

Follow the existing [Pod runbook](../deforum/POD.md) for the retained volume and official ComfyUI runtime. Its name, `deforum-models`, does not restrict it to animation. Keep the authorized volume; delete finished owned Pods after verified local collection.

The retained-volume trial verified **Krea assets**, not SDXL. Inspect the actual model inventory and free space before adding the proposed SDXL checkpoint. The runbook's `--krea-only --verify-only` check does not validate SDXL readiness.

Reuse the established HTTP submission/history/download protocol. The existing [Pod client](../deforum/pod_client.py) imports the Deforum runner and defaults to a Deforum deployment receipt; it is a reference, not yet a general ComfyUI client. Do not point this project at that default receipt or start an animation runner. No transport refactor, custom node installation or GPU allocation is part of this research scaffold.
