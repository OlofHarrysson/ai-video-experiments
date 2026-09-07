# Motion guide walkthrough

See what happens between a motion guide and the next generated artwork. Two archived artworks receive the same measured displacement. The original, warped input, and real ComfyUI img2img output remain separate.

- [Experiment and results](experiments/walkthrough.md)
- [Runnable study](experiments/walkthrough.py)
- [Same model, fixed versus changing seed](experiments/seed-comparison.md): two matched six-second branches from a fresh SDXL opening; [runner](experiments/seed_comparison.py).

Local media is preserved under `references/`, `runs/` and `exports/`. The original walkthrough isolates guide flow and repainting; its follow-up compares seed policies with a small ordinary 2D zoom. Neither reproduces the full Evolve Zoom Slow preset or uses depth, guide compositing or interpolation.
