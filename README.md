# AI Video Experiments

A public notebook for experiments with AI-assisted video creation.

We are learning to make surreal films with recognizable forms, gradual transformations and deliberate spatial motion. The goal is to combine artistic direction with the unexpected images a model produces.

## Selected films

Three experiments in painted worlds, continuous movement and surreal transformation. These are full films, all silent; press play to watch.

### The Cartographer’s Dream · 75 seconds

A blue ink river escapes an atlas, travels through paper canyons and waterfalls, and folds into a world of its own.

https://github.com/user-attachments/assets/f0574704-5bd0-4e8b-8e6c-4b16ad72b879

[How it was made](apps/deforum/projects/cartographers-dream/README.md) · [Selected cut and lineage](apps/deforum/projects/cartographers-dream/cuts/v002.md)

### The Open Dream · 19 seconds

A whale carries a railway station across the sea. A red train, a moon and a clock become a passage into another dream.

https://github.com/user-attachments/assets/730b1694-2404-4fc6-bcc6-17c1f4716596

### A Sky of Lanterns · 19 seconds

A small lantern boat finds shelter beneath a wave. Its light becomes a beacon, then a constellation.

https://github.com/user-attachments/assets/2f8c0e65-7f52-4960-b249-f722e32d84e1

[Storytelling experiments and what we learned](apps/deforum/projects/modern-model-study/experiments/storytelling-lab/README.md)

## How we work

We preserve every generation, continue from chosen frames, and assemble the best ranges into versioned cuts. These films use recurrent image diffusion: move and reshape the previous painting, repaint it, then interpolate between paintings for playback.

[Creative direction](docs/vision.md) · [Working convention](docs/workflow.md) · [Project index](apps/deforum/projects/README.md)

## Documentation

Start with [AGENTS.md](AGENTS.md): the project brief, working guidance and canonical documentation index. Read [current state](docs/current-state.md) for the active workflow and latest results, or the [research index](docs/research/README.md) for a specific technical or creative question.

[Lessons learned](docs/lessons-learned.md) brings together a cross-project critique of the films and artwork, technical findings, recorded preferences and independent second opinions. Its [evidence index](docs/reviews/2026-09-16-retrospective.md) identifies the media actually inspected and the limits of the review.

## Experiments

- [Music workbench](apps/music/README.md): original Strudel composition, rendered audio inspection, spectrograms and OpenRouter listening trials.

- [Avatar studio](apps/avatar-studio/README.md): paused study of controllable 3D performance and AI video restyling, with source/style and motion comparisons.
- [Deforum](apps/deforum/README.md): recurrent image diffusion, spatial controls and film experiments using ComfyUI on RunPod.
- [ComfyUI](apps/comfyui/README.md): still-image composition, regional prompts and layered painting on RunPod.
- [Blender animation](apps/blender-animation/README.md) and [stop-motion](apps/stop-motion/README.md): separate studies with their own project briefs.
- [Canvas animation](apps/canvas-animation/README.md): TypeScript motion graphics with synthesized scores, starting with a promo Reel for AI Filmhack.
- [Remotion](apps/remotion/README.md): React-based programmatic video with Tone.js scores, starting with a high-energy cut of the same promo.

## Status

The active [modern-model study](apps/deforum/projects/modern-model-study/README.md) produces recurrent Krea films with time-based motion, staged prompts and RIFE interpolation. We can preserve openings, create continuations, assemble source ranges and compare films with a local frame-stepping reviewer. A broader editing application remains outside the current scope.

Code, small configurations and documentation are tracked in Git. The showcase above uses compressed viewing copies hosted as GitHub attachments. Original references, generated frames and full-quality videos live locally in ignored project folders; this repository is not their backup. See [media storage](docs/storage.md).
