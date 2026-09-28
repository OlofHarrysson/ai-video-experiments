# Shape injection before recurrent repainting

Completed 2026-09-28: [results and recommendation](report.md). Eighteen still probes and seven recurrent clips show that shapes can become scene content. The most useful moving-circle recipe combines authored local deformation with strong initial blending reduced on subsequent paintings. All 131 paintings are verified locally and the owned GPU is deleted; estimated compute was $0.65. Human review pending.

Question: can an authored circle, ring or triangle be blended into the previous painting and become scene-appropriate content during Krea diffusion? The requested mechanism is visual structure injection, with no object detector, regional prompt or repaint mask. Shapes may introduce content where no object exists.

Use the existing Krea Turbo model and repaint sampler. Compare untouched initialization with transparent flat/shaded shapes at different blend strengths and repaint noise. Continue a promising setting through a short recurrent sequence with a moving guide; inspect ghost trails, literal guide remnants, semantic integration and trajectory.

Working compute limit: $3, one short-lived owned Pod, delete after verified preservation. Existing retained model volume is untouched if unavailable. No change to the production Deforum recipe is implied by this isolated experiment.

The reference audit found `Shapes-Circles` and `Shapes-Circles-30s` presets with Normal hybrid compositing at alpha 0.8, alongside optical flow at 0.8. The earlier Evolve Zoom Slow expanding-ring example instead disables compositing. The exact spinning-donut clip recalled by Olof has not been positively identified; these mechanisms should not be conflated. See [research](../../../../docs/research/bonsai-spatial-motion.md).
