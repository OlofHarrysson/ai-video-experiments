# Motion guide walkthrough

See what happens between a motion guide and the next generated artwork. Two archived artworks receive the same measured displacement. The original, warped input, and real ComfyUI img2img output remain separate.

- [Experiment and results](experiments/walkthrough.md)
- [Runnable study](experiments/walkthrough.py)
- [Same model, fixed versus changing seed](experiments/seed-comparison.md): two matched six-second branches from a fresh SDXL opening; [runner](experiments/seed_comparison.py).
- [B with a small 3D camera move](experiments/seed-3d.md): depth preview, sideways parallax and a slight turn using the selected repaint recipe.
- [Stronger and combined effects](experiments/motion-effects-2.md): stronger ring expansion, turbulent deformation and rotating unfolding.
- [Three spatial effects](experiments/motion-effects.md): turn and bank using fresh depth, kaleidoscope unfolding, and localized ring expansion; [motion vocabulary](../../../../docs/research/motion-control-vocabulary.md).
- [Move-Warp-inspired feedback](experiments/move-warp.md): the actual wave guide deforms each preceding frame before B's ComfyUI repaint; Mac orchestration preserves every intermediate.

Local media is preserved under `references/`, `runs/` and `exports/`. The original walkthrough isolates guide flow and repainting; follow-ups compare seed policies with a small 2D zoom, then add depth-based camera motion to the selected recipe. These do not reproduce the full Evolve Zoom Slow preset or use guide compositing or final frame interpolation.
