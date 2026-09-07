# Documentation

This directory contains the durable notes behind the experiments in this repository.

## Topics

- [Reviewing experiments together](review-and-feedback.md) — assistant first-pass review, a small human shortlist, understandable experiment cards and the current preferred recipe.
- [Olof's learning journal](olof-learning-journal.md) — explicit preferences, demonstrated concepts, unconfirmed exposure and the next learning opportunity.
- [Iterative filmmaking direction](vision.md) — creative intent, priorities, constraints and deferred hypotheses.
- [Project and experiment workflow](workflow.md) — references, preserved runs, versioned cuts, exports and archive handling.
- [Local video review](video-review.md) — extract frames at timestamps, inspect event context and preserve labeled review sheets.
- [Deforum: image diffusion as animation](deforum.md) — how its feedback loop, camera transforms, prompts, strength, and cadence create video.
- [RunPod tools and repository setup](runpod.md) — local skills, project MCP configuration, CLI installation, and authentication.

## Experiments

- [Same-model seed comparison](../apps/deforum/projects/motion-guide-study/experiments/seed-comparison.md) — identical opening and model recipe; fixed sampling seed versus a new seed each frame.
- [Motion-guide walkthrough](../apps/deforum/projects/motion-guide-study/README.md) — two guide frames, measured arrows, pixel warping and six matched ComfyUI repaints, with an interactive comparison.
- [BonsAi motion: zoom/morph and 3D reveal](../apps/deforum/projects/reference-studies/experiments/bonsai-motion.md) — next two accepted creative tests and review criteria; not rendered yet.
- [Review harness practice](../apps/deforum/projects/brain-entity-study/experiments/review-harness.md) — selective image review, matched comparisons, timestamped findings and P3 + RIFE as the current preferred baseline.
- [Temporal continuity experiments](../apps/deforum/projects/brain-entity-study/experiments/continuity.md) — matched noise-source comparisons and separate interpolation/flow finishing tests, following the architecture research.

- [Brain Entity style reproduction](../apps/deforum/projects/brain-entity-study/README.md) — original still comparisons, a six-second guided transformation, and measured build/cold-start/warm-render timings.

- [Art references and first reproduction study](../apps/deforum/projects/reference-studies/README.md) — archived Tomorrow and Brain Entity videos, timestamped frame studies, extracted text, reviews and a proposed short style test.

- [Ten adaptive video experiments](research/ten-experiments-session.md) — visual storytelling, camera/settings comparisons, independent redraw, native Seedream repainting and local frame review.

- [Seedream motion](../apps/deforum/projects/seedream-motion/experiments/motion.md) — five-second feedback/redraw outputs, stronger camera travel and foreground reconstruction limits.

- [Parallel models, settings, overscan and guide redraw](research/parallel-experiments-session.md) — four completed studies, review media, actual concurrency, cost and cleanup.

- [Project index](../apps/deforum/projects/README.md) — films/studies and their experiment notes.
- [Deforum working directory](../apps/deforum/README.md) — first render scope, implementation boundaries, and current verification status.
- [Serverless continuation and 3D session](../apps/deforum/projects/botanical-cathedral/experiments/serverless-results.md) — preserved cuts, depth parallax, startup and cached timing, local recovery and cleanup.
- [First SDXL feedback session](../apps/deforum/projects/botanical-cathedral/experiments/baseline-results.md) — short tests, denoise comparison, visual findings, cost, and cleanup.

Add future shared notes as separate Markdown files and link them from this page.

## Research

- [The BonsAi Effect workflow study](research/bonsai-effect-workflow.md) — two visually reviewed references, artist replies across 29 videos, exact motion presets and guide assets, seed/cadence differences, and lessons for our next experiment; [external platforms](research/bonsai-effect-external-sources.md).

- [Deforum architecture and temporal continuity](research/deforum-architecture-comparison.md) — original renderer, Difforum rewrite, official/community ComfyUI nodes, missing temporal mechanisms and next tests.
- [Current ComfyUI animation practices](research/comfyui-animation-practices.md) — official-source workflow guidance and model/temporal compatibility.
- [ComfyUI YouTube workflow study](research/comfyui-youtube-workflows.md) — trusted creators, transcript-backed tutorial notes, dated advice and relevance to feedback animation.

- [Feedback parameters](research/feedback-parameters.md) — pinned Difforum/ComfyUI behavior for denoise, steps, CFG, noise and image feedback; [controlled video comparisons](../apps/deforum/projects/brain-entity-study/experiments/parameters.md).

- [Filmmaking for image-led AI animation](research/filmmaking-for-ai-animation.md) — directing attention, visual storytelling, composition, lighting, classic shots, editing and later music.

Initial research dated 2026-09-06. Recommendations and integration hypotheses are distinguished from tests actually run.

- [Continuation and editing](research/continuation-and-editing.md) — selecting a parent frame, preserving state, branching and editorial cuts.
- [3D camera and motion](research/3d-camera-and-motion.md) — depth, parallax, optical flow, interpolation and current node limitations.
- [Image models and cost](research/models-and-cost.md) — SDXL baseline, Klein, DMD2, Krea, Seedream and a comparable-cost benchmark.
- [Serverless rendering](research/serverless-rendering.md) — selected scale-to-zero architecture, output preservation and cost validation; [implementation runbook](../apps/deforum/serverless/README.md).
- [Structure and style](research/structure-and-style.md) — guide footage, video-to-video translation and the deferred simple-3D-scene experiment.
