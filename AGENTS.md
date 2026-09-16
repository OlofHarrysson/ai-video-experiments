# AI Video Experiments

## Project brief

A public notebook and working environment for AI-assisted filmmaking. We explore how to create expressive videos with intentional visual style, movement, transformation and storytelling, and develop practical tools and workflows for doing so.

The project combines creative experiments, reusable tooling and reproducible records. Work proceeds through research, generation, inspection and iteration, with the ability to preserve successful material and explore alternatives. Learning filmmaking, model behavior and effective human–agent collaboration are explicit outcomes. Olof sets artistic direction and judges taste; the assistant researches, implements, experiments and screens results.

## Finding context

Use the documentation index below to find the relevant project, workflow or research. When resuming ongoing experiments, read [current state](docs/current-state.md) and the owning project's brief. Treat historical findings as evidence with a specific scope, rather than general defaults. Read further only where the task needs it.

## Working rules

- Keep experiments aligned with the agreed artistic intent and question. Consult the owning project's workflow before changing its generation method or interpretation of inputs.
- Preserve original references, unique generations and versioned creative decisions. Verify preservation before cleanup; follow the [storage policy](docs/storage.md) and relevant runbooks.
- Record enough configuration, provenance and evidence to understand and reproduce an experiment. Distinguish hypotheses, observed results, assistant judgments and human preferences.
- Screen results before asking Olof to judge taste. Present a small visual shortlist with plain-language explanations. Keep collaboration and learning notes evidence-based; follow the [review agreement](docs/review-and-feedback.md).
- Use the repository's tooling and code-ownership conventions, documented in the [workflow](docs/workflow.md) and app guides. Reusable mechanics and project-specific experiments have separate owners.
- Protect credentials, respect spending boundaries, track resource ownership and clean up completed work according to its runbook. Log consequential communication, workflow and tool problems with `log-agent-friction`.

## Documentation Index

Start here for repository documentation. Add shared explanations as separate `docs/*.md` pages and link them here. Research lives under `docs/research/`; app runbooks and project-specific briefs, experiments and cuts stay beside their owners. Link research through its index and experiments through theirs instead of expanding this entry point with each result.

### Purpose and orientation

- [AGENTS.md](AGENTS.md): project brief, operating rules and canonical documentation index.
- [README.md](README.md): public introduction and workspace overview.
- [Creative vision](docs/vision.md): artistic aims, workflow priorities and deferred hypotheses.
- [Current state](docs/current-state.md): active recipe, latest result, open questions and next-session pointers.
- [Project index](apps/deforum/projects/README.md) and [experiment notebook](apps/deforum/projects/EXPERIMENTS.md): preserved studies, films, attempts and supporting reports.

### Create, inspect and collaborate

- [Project workflow](docs/workflow.md): folder ownership, shared code, generation records, continuation and cuts.
- [Motion palette](docs/motion-palette.md): choose supported pans, zooms, plane turns, waves, shear and spirals.
- [Review and feedback](docs/review-and-feedback.md): first-pass screening, human comparisons and collaboration conventions.
- [Lessons learned](docs/lessons-learned.md): cross-project critique, evidence, second opinions and implications for the next film.
- [Learning journal](docs/olof-learning-journal.md): explicit preferences, demonstrated understanding and open learning questions.
- [Frame inspection](docs/video-review.md): timestamp extraction, dense windows and comparison sheets.
- [Media reviewer](apps/deforum/media_review/README.md): linked playback, frame/painting stepping and generation details.
- [Deforum concepts](docs/deforum.md): the feedback loop, cadence and spatial controls.
- [Research index](docs/research/README.md): filmmaking, models, sampling, motion, references and ComfyUI studies.

### Develop and operate

- [Deforum app](apps/deforum/README.md): workspace and development entry points.
- [ComfyUI Pods](apps/deforum/POD.md): GPU execution and resource lifecycle.
- [RunPod setup](docs/runpod.md): repository-scoped tools and authentication; [serverless runbook](apps/deforum/serverless/README.md) for serverless operation.
- [Media storage](docs/storage.md): preservation, shared copies and verified duplicate cleanup.
- [Refactor plan](docs/refactor-plan.md): package migration, legacy boundaries and remaining work.
- [ComfyUI studies](apps/comfyui/README.md), [Blender animation](apps/blender-animation/README.md), [stop-motion](apps/stop-motion/README.md): other areas of this workspace, each with its own brief.
- [Archived agent context](docs/archive/agent-context-2026-09-15.md): historical summaries removed from this entry point; not current instructions.

## Keeping this entry point useful

Keep this file focused on the project's enduring purpose, working principles and documentation map. Update it when those change. Priorities, selected models, settings, budgets, resource conditions and recent results belong in linked status pages, project briefs and runbooks. Record findings in experiment reports and explicit user feedback in the learning journal. Routine experiments should not require edits here; maintain links without copying their changing contents into this entry point.
