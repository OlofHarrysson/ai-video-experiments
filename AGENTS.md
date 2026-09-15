# AI Video Experiments

## Project brief

A public notebook and working environment for learning to make controllable AI films. We want surreal, visually rich scenes with recognizable forms that gradually transform, supported by deliberate spatial movement. The aim is to build longer films from short, reviewable sections: generate, inspect, preserve a good prefix, and branch or continue from a chosen frame.

The immediate product is a useful creative workflow, a library of working effects and reproducible experiments—not a complete video editor. Learning filmmaking, model behavior and effective human–agent collaboration are part of the work. Olof sets artistic direction and judges taste; the assistant researches, implements, experiments and screens results.

## Current brief

Active work is in `apps/deforum/`, especially the [modern-model study](apps/deforum/projects/modern-model-study/README.md). It uses a recurrent Krea/ComfyUI workflow: warp the previous painting, initialize another diffusion repaint from it, then interpolate for presentation. The latest focus is continuous, varied spatial motion and visual storytelling; the artwork is promising, but repetitive movement, crowded framing and abrupt redraws remain. Storage work is deferred until disk pressure returns.

Read [current state and recipe](docs/current-state.md) before choosing a baseline or resuming an experiment. It identifies the latest results, unresolved questions and dated resource/budget records. Historical experiment settings are not global defaults.

## Working rules

- Preserve recurrent feedback when changing models, prompts or conditioning. Image initialization and optional reference-image conditioning are different inputs; align before changing the loop.
- Preserve unique generations, references and cut versions. Verify local collection before removing owned cloud media/compute. Media is ignored by Git, and there is no external backup. Follow [storage rules](docs/storage.md); do not infer permission to purge artwork.
- Use `uv` and the app's `pyproject.toml`/`uv.lock`. Shared Python mechanics belong in `apps/deforum/src/deforum_lab/`; experiment configs, runners and results belong to their project. See [workflow and code ownership](docs/workflow.md).
- Review images and selected frame sequences first. Show Olof one recommendation and one meaningful alternative as playable videos in chat, with plain-language explanations. Separate assistant findings from his taste judgments; do not infer understanding from exposure. Follow [review and feedback](docs/review-and-feedback.md).
- Manage the local reviewer through Devrun/shared terminal; obtain its current URL there. Avoid Chrome integration for routine delivery. Keep compared frames visible together on a 14-inch laptop.
- For GPU work, read [POD.md](apps/deforum/POD.md) and the repository-scoped RunPod skills. Check current resources, track ownership and spend, remove completed owned Pods, and preserve the authorized shared model cache. Credentials and private account receipts stay ignored.
- Record exact configurations, provenance and validation scope. Keep unreviewed ideas distinct from tested findings. Log consequential workflow/tool/communication problems with `log-agent-friction`.

## Documentation Index

Start here for repository documentation. Add shared explanations as separate `docs/*.md` pages and link them here. Research lives under `docs/research/`; app runbooks and project-specific briefs, experiments and cuts stay beside their owners. Link research through its index and experiments through theirs instead of expanding this entry point with each result.

### Direction and current work

- [AGENTS.md](AGENTS.md): project brief, operating rules and canonical documentation index.
- [README.md](README.md): public introduction and workspace overview.
- [Creative vision](docs/vision.md): artistic aims, workflow priorities and deferred hypotheses.
- [Current state](docs/current-state.md): active recipe, latest result, open questions and next-session pointers.
- [Project index](apps/deforum/projects/README.md) and [experiment notebook](apps/deforum/projects/EXPERIMENTS.md): preserved studies, films, attempts and supporting reports.

### Create, inspect and collaborate

- [Project workflow](docs/workflow.md): folder ownership, shared code, generation records, continuation and cuts.
- [Motion palette](docs/motion-palette.md): choose supported pans, zooms, plane turns, waves, shear and spirals.
- [Review and feedback](docs/review-and-feedback.md): first-pass screening, human comparisons and collaboration conventions.
- [Learning journal](docs/olof-learning-journal.md): explicit preferences, demonstrated understanding and open learning questions.
- [Frame inspection](docs/video-review.md): timestamp extraction, dense windows and comparison sheets.
- [Media reviewer](apps/deforum/media_review/README.md): linked playback, frame/painting stepping and generation details.
- [Deforum concepts](docs/deforum.md): the feedback loop, cadence and spatial controls.
- [Research index](docs/research/README.md): filmmaking, models, sampling, motion, references and ComfyUI studies.

### Develop and operate

- [Deforum app](apps/deforum/README.md): active Python workspace and entry points.
- [ComfyUI Pods](apps/deforum/POD.md): current GPU execution and cleanup runbook.
- [RunPod setup](docs/runpod.md): repository-scoped tools and authentication; [serverless runbook](apps/deforum/serverless/README.md) for earlier deployments.
- [Media storage](docs/storage.md): preservation, shared copies and verified duplicate cleanup.
- [Refactor plan](docs/refactor-plan.md): package migration, legacy boundaries and remaining work.
- [ComfyUI studies](apps/comfyui/README.md), [Blender animation](apps/blender-animation/README.md), [stop-motion](apps/stop-motion/README.md): other areas of this workspace, each with its own brief.
- [Archived agent context](docs/archive/agent-context-2026-09-15.md): historical summaries removed from this entry point; not current instructions.

## Keeping this entry point useful

Keep the project brief and working rules short. Replace the current brief when focus changes; put settings and dated status in `docs/current-state.md`, findings in the experiment report, and explicit user feedback in the learning journal. Do not append successive session recaps here. Maintain a link to each shared documentation entry point without duplicating its contents.
