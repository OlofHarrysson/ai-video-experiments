# Repository guidance

## Active project

AI Video Experiments is a public notebook and workspace for controllable AI animation. The creative interest is explicit camera movement combined with surreal morphing and visible frame-by-frame repainting. Perfect temporal consistency is not the goal.

- Current experiment: `apps/deforum/`, using existing Difforum nodes in ComfyUI on RunPod.
- Current priority: establish a usable iterative filmmaking workflow, then intentional 3D camera movement and quality improvements. Build toward 30-second, one-minute and five-minute assemblies from manageable clips; avoid a one-shot long render.
- Current visual task: [Brain Entity reproduction](apps/deforum/projects/brain-entity-study/README.md). **P3 + RIFE** is the creative baseline: Olof likes its morphing and wants more interesting camera movement. SDXL is acceptable for now, with a newer-model audition wanted later. C01/C03 were boring; avoid overwhelming Olof with similar variants. [RIFE finishing](apps/deforum/projects/brain-entity-study/experiments/rife-results.md) runs locally on MPS in about 16 seconds per six-second clip; interpolated noise during generation remains untested.
- Next reference: [The BonsAi Effect](docs/research/bonsai-effect-workflow.md), especially the supplied Evolve Zoom Slow chapter. Both videos are archived and visually sampled; creator replies, original motion presets and hybrid guide videos are preserved. These are WebUI presets, not importable ComfyUI graphs. Keep guide-driven motion, seed mixing, camera/depth warp and final interpolation distinct when adapting them.
- Mac: authoring, controls, previews, and local copies of results. RunPod: model inference and the camera-warp/img2img feedback loop.
- First milestone complete: three five-second SDXL clips with the same initial image, seed sequence, and camera path at different denoise strengths. Outputs are local; the experiment Pod was deleted.
- Runnable path: `uv run python experiment.py init-project NAME`, then `run --project NAME --experiment EXPERIMENT ...` in `apps/deforum/`. Write the experiment note before rendering. Serverless is verified: continuation, depth guide and 3D repaint completed. Its endpoint is paused (min/max workers 0); the archive volume was deleted after verified local downloads. See `apps/deforum/serverless/README.md`. MCP endpoint listing is now verified; the CLI also works.
- Seed finding: incrementing the feedback seed retained more detail than a fixed seed in the first short test. Review full-length quality in the session report before choosing the next recipe.
- Playback feedback: 0.30 is too smooth; 0.50 flickers too much. Frame sharpness alone does not establish video quality. Keep detail, flicker, structure and camera control separate in reviews.
- Current practice cuts: v001 preserves parent frames 0–19 and selects a 2D continuation; v002 selects a 3D continuation from the same anchor. Review playback before choosing the next branch. Depth-guide parallax is measured; 3D repaint has edge artifacts. Current 3D feedback reuses initial depth through the loop and does not establish long-shot scene consistency.
- Budget: Olof authorized using the remaining roughly $50 RunPod balance for parallel learning. Multiple workers are allowed; the latest round used a maximum of three. Check current account state before provisioning and clean up owned resources afterward.
- Long-term recurring cost should remain near SDXL, but the current learning budget permits model/workflow exploration. Separate warm inference cost from setup/idle time and rejected attempts.
- Iteration speed matters: the expanded worker took 19 minutes to build and 6.5 minutes for its first cold start, versus 13 seconds for three warm stills and about three minutes per six-second feedback clip. Reuse a prepared image across settings/workflow tests; those changes require no rebuild. Uncached workers can still incur setup delay. Keep a bounded warm session for review, then pause and clean up. The Dockerfile removes the intermediate QR model within the download layer; that packaging fix was not used in the first study runs.
- Earlier: [ten video experiments](docs/research/ten-experiments-session.md) completed. Fixed-seed independent SDXL redraw is a candidate for preserving the scene; masked repairs produce interesting but inaccurate morphs. Native Seedream per-frame editing works with inline image data, but introduces variable canvas borders. Feedback still progressively softens. These are sampled-frame findings; Olof's playback preferences remain unconfirmed. All resources are cleaned up and media is local.

## Working conventions

- Start with the [documentation index](docs/index.md) and the relevant app README. Shared explanations belong in `docs/`; runnable experiments belong in `apps/`.
- Prefer existing nodes and workflows. Add custom code only for a concrete missing capability.
- Use the repository's RunPod skills in `.agents/skills/` for RunPod work. Keep RunPod skills and MCP configuration scoped here; the CLI may be installed globally.
- Keep credentials in ignored local files or the credential store. Never commit keys, OAuth tokens, or private account responses.
- Inspect Git status and preserve unrelated work. Keep changes on the existing branch unless asked otherwise.
- Record workflow/model versions, settings, and outputs for each experiment. Distinguish source inspection, local checks, remote execution, and visual review.
- Treat learning filmmaking/tooling and improving human–agent collaboration as explicit project outcomes. Follow the living [review and feedback agreement](docs/review-and-feedback.md), update it from experience, and never infer understanding just because an explanation was shown.
- Do the first-pass review before asking Olof to judge taste. Default to one recommendation and one meaningful alternative, shown as playable videos in chat; preserve and index every result, and show the full set when requested. Explain what changed, why, what to watch for and what happened in plain language. Define unfamiliar tools such as RIFE; IDs/node names alone are insufficient. Human playback preferences take precedence over assistant rankings.
- Inspect clips with `apps/deforum/video_review.py`: evenly spaced overview, selected every-frame windows, then timestamp-matched comparisons. Use small pages and a bounded image budget; open full-size frames only where useful. Keep artifacts beside project media. Pixel-change candidates locate intervals, not semantic events; sampled frames alone do not establish playback quality. See [local video review](docs/video-review.md).
- Consult and maintain [Olof's learning journal](docs/olof-learning-journal.md) when preferences or learning affect the next step. Separate explicit preferences, demonstrated concepts and unconfirmed exposure; never infer understanding from merely presenting information. The Seedream marsh still was the earlier model-comparison preference; the supplied art references set the current target.
- Preserve every generation, original reference and cut version. All project media belongs under `projects/PROJECT/`, including the first session. Shared runner, setup code and reusable workflow recipes stay at app level. A working cut references source ranges and never overwrites a generation. Git ignores media; no separate-disk backup is configured yet.
- Keep the product vision and research living. Defer automatic editing/branching infrastructure and the simple-3D-scene-to-stylization hypothesis until short experiments justify them.
- Check for an existing user-created Pod before provisioning. Track the resources owned by this experiment and shut down paid compute when finished; retained storage can still cost money.

## Documentation

- [Documentation index](docs/index.md): canonical map of shared notes and app runbooks.
- [Review and feedback agreement](docs/review-and-feedback.md): assistant screening, a small human shortlist, plain-language experiment explanations and iterative collaboration.
- [Feedback parameter research](docs/research/feedback-parameters.md): pinned node behavior, explicit distinctions between image noise, denoise, sampling steps and previous-frame influence.
- [Filmmaking guide](docs/research/filmmaking-for-ai-animation.md): image-led storytelling, directing, composition, lighting, camera craft, editing and later music.
- [Olof's learning journal](docs/olof-learning-journal.md): evidenced preferences, demonstrated concepts and open learning questions.
- [Creative direction](docs/vision.md) and [working convention](docs/workflow.md).
- [Project index](apps/deforum/projects/README.md): project briefs, experiments and current cuts.
- [Deforum mechanism and creative direction](docs/deforum.md).
- [RunPod tools and repository setup](docs/runpod.md).
- [Deforum experiment](apps/deforum/README.md): current state and next execution steps.
- [Parallel experiment results](docs/research/parallel-experiments-session.md): model samples, settings, overscan and independent redraw.
- [Serverless session results](apps/deforum/projects/botanical-cathedral/experiments/serverless-results.md): cuts, parallax, startup failure, cached timings and cleanup.
- [First session results](apps/deforum/projects/botanical-cathedral/experiments/baseline-results.md): execution, visual findings, and cost.
