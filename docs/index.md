# Documentation

This directory contains the durable notes behind the experiments in this repository.

## Topics

- [Diffusion starting-noise sweep](../apps/deforum/projects/modern-model-study/experiments/starting-noise.md) — 0.655/0.62/0.60/0.56 with three sampling intervals, identical one-second repaint timing and interpolation.

- [Next diffusion and interpolation experiments](research/diffusion-and-interpolation-next.md) — native three-step tails, lower starting noise, and a current RIFE/GIMM/BiM/SPEED/LDF-VFI/ArbInterp research comparison.

- [RIFE motion-estimation scale](../apps/deforum/projects/modern-model-study/experiments/rife-scale.md) — local interpolation comparison on the selected one-second repaint shot, preserving paintings and full-resolution 24 fps output.

- [Spatial effects browser](../apps/deforum/projects/motion-guide-study/experiments/motion-catalog.md) — 22 direct transforms on one drawing, effect selection, playback and scrubbing; the selected cadence-3/interpolation sequence is linked below.

- [Animated spatial-controls lesson](research/spatial-controls-lesson.md) — a stretchable drawing, measured guide motion, direct controls, and where depth fits.

- [Motion vocabulary: words to controls](research/motion-control-vocabulary.md) — translation, turn, bank, expansion and regional deformation, with the inspectable path from a request to repainting.

- [Spatial image controls and Safety Marc presets](research/bonsai-spatial-motion.md) — full 95-file mechanism inventory, representative effect recipes, wave-guide study, two new BonsAi references and the concrete gap in our ComfyUI loop.

- [Reviewing experiments together](review-and-feedback.md) — assistant first-pass review, a small human shortlist, understandable experiment cards and the current preferred recipe.
- [Olof's learning journal](olof-learning-journal.md) — explicit preferences, demonstrated concepts, unconfirmed exposure and the next learning opportunity.
- [Iterative filmmaking direction](vision.md) — creative intent, priorities, constraints and deferred hypotheses.
- [Project and experiment workflow](workflow.md) — references, preserved runs, versioned cuts, exports and archive handling.
- [Local video review](video-review.md) — extract frames at timestamps, inspect event context and preserve labeled review sheets.
- [Deforum: image diffusion as animation](deforum.md) — how its feedback loop, camera transforms, prompts, strength, and cadence create video.
- [RunPod tools and repository setup](runpod.md) — local skills, project MCP configuration, CLI installation, and authentication.

## Experiments

- [Half-second versus one-second repainting](../apps/deforum/projects/modern-model-study/experiments/repaint-intervals.md) — six-second 24 fps Krea/RIFE shots, varying only repaint interval.

- [24 fps timeline and time-based motion](../apps/deforum/projects/modern-model-study/experiments/timebase24.md) — new 24 fps/RIFE defaults; replay verification preserves the accepted repaint rhythm.

- [Slower cadence: 3, 7, 10 and 15](../apps/deforum/projects/modern-model-study/experiments/cadence-slow.md) — matched raw and RIFE versions with preserved repaint timing; distinguish source, repaint and delivery rates.

- [Cadence 4 and 5 with RIFE](../apps/deforum/projects/modern-model-study/experiments/cadence-spacing.md) — fewer repaints with learned in-between frames, following Olof's preference for interpolation.

- [Three-step morphing controls](../apps/deforum/projects/modern-model-study/experiments/turbo-smoothing.md) — anchor interpolation and cadence 2 versus 3, retaining the selected Krea sampling recipe.

- [Hybrid 2D puppy](../apps/blender-animation/projects/puppy-2d/README.md) — painted mesh rig, replacement drawings, and a three-second 1080p animation.

- [Blender puppy animation](../apps/blender-animation/projects/playful-puppy/README.md) — native skinned character, editable pose keys, a three-second bow and hop, and measured paw controls.

- [Krea lower repaint strengths](../apps/deforum/projects/modern-model-study/experiments/krea-low-repaint.md) — 0.10/0.18/0.24 with the preserved cathedral feedback loop.

- [Initialized feedback plus optional reference](../apps/deforum/projects/modern-model-study/experiments/additive_reference.md) — retain warped-image sampling initialization and test additional native reference conditioning for Klein and Krea.
- [Earlier text-only and native-reference tests](../apps/deforum/projects/modern-model-study/experiments/conditioning.md) — unblended reconstructions and preserved input-mode probes; the new sequences omitted initialized feedback and did not match the intended experiment.

- [Klein and Krea Pod results](../apps/deforum/projects/modern-model-study/experiments/pod-results.md) — two playable clips, model-specific prompting, native editing versus partial repaint, and cleanup.
- [Klein and Krea audition](../apps/deforum/projects/modern-model-study/experiments/baseline.md) — same-model openings and feedback, native editing versus partial repaint, and model-specific prompts.

- [Two sampler alternatives](../apps/deforum/projects/motion-guide-study/experiments/samplers.md) — matched three-second twists informed by creator recipes.

- [Sampling steps and input noise](../apps/deforum/projects/motion-guide-study/experiments/noise-steps.md) — test whether more sampling steps reduce accumulated grain at denoise 0.45.
- [Repaint controls](../apps/deforum/projects/motion-guide-study/experiments/repaint-controls.md) — short matched denoise comparison, sampler protection and regional added noise, with playable comparisons.
- [Twist, turn and ripple](../apps/deforum/projects/motion-guide-study/experiments/spatial-sequence.md) — one sequence with cadence 3 and matched RIFE finishing.

- [Stronger and combined effects](../apps/deforum/projects/motion-guide-study/experiments/motion-effects-2.md) — fourfold ring, turbulence and rotating unfolding; separate camera-gap diagnosis.

- [Three spatial effects](../apps/deforum/projects/motion-guide-study/experiments/motion-effects.md) — turn and bank, kaleidoscope unfolding and ring expansion with the same artwork recipe.

- [Move-Warp-inspired feedback](../apps/deforum/projects/motion-guide-study/experiments/move-warp.md) — actual checker-wave guide, regional image deformation and the selected same-model/changing-seed repaint recipe.

- [B's small 3D camera move](../apps/deforum/projects/motion-guide-study/experiments/seed-3d.md) — depth-only preview and the selected changing-seed repaint recipe with lateral motion and a slight turn.
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

- [Cathedral feedback](../apps/deforum/projects/modern-model-study/experiments/cathedral-feedback.md) — four short clips, two repaint strengths per model, verified initialized feedback and motion-only previews.

- [Opening artwork audition](../apps/deforum/projects/modern-model-study/experiments/opening-art.md) — official Krea control and a small Klein/Krea art-direction study before further animation.

## Research

- [Regional prompting and layered painting](research/regional-composition.md) — native area/mask conditioning, noisy latent composition, staged inpainting and a proposed SDXL experiment in the separate ComfyUI app.

- [AI-controlled animation software](research/animation-software-control.md) — human animation workflows, Blender/Moho/Harmony/OpenToonz scripting, existing agent bridges, and a proposed rigged character test.

- [Ten-second transitions and Turbo tails](../apps/deforum/projects/modern-model-study/experiments/turbo-transitions.md) — longer twist/expansion and a matched one/two/three-step continuation comparison.
- [Matched Turbo schedules](../apps/deforum/projects/modern-model-study/experiments/turbo-schedule.md) — one final interval versus eight small updates at matched noise; cleaner motion candidate, still some drift.
- [Latent-feedback comparison](../apps/deforum/projects/modern-model-study/experiments/latent-feedback.md) — no-motion Krea tests with one encode; degradation persists; followed by the matched schedule study.

- [Repeated repaint degradation](research/repeated-repaint-degradation.md) — why restarting diffusion differs from more steps; no-motion, VAE and warp controls.

- [Modern-model transition](research/modern-model-transition.md) — actual nine-node feedback graph, model-independent motion tools, remaining integration boundaries and a small Klein/Krea audition proposal.
- [Prompting for feedback](research/prompting-for-feedback.md) — opening versus edit instructions, model-specific guidance, prompt expansion and draft prompts for the next study.

- [Model and sampler recipes](research/model-sampler-recipes.md) — exact Civitai versions, creator guidance, distilled-model constraints, conflicting recipes and two controlled sampler alternatives.

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
