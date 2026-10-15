# Opening directions

Question: which material world provides both a compelling high-fidelity first image and a useful route for continuous camera movement?

Three distinct compositions are described in [openings.json](openings.json). Native Krea 2 Turbo renders each at 1536×1024, CFG 1 and eight Euler steps. The [runner](stills.py) preserves exact requested/executed/embedded graphs, output hashes and completed job identities. This is a visual exploration rather than an isolated ablation.

Render with `uv run --locked python projects/glass-tide/experiments/stills.py render projects/glass-tide/experiments/openings.json --deployment PATH` from `apps/deforum`. Reuse the frozen cases only; changes require a new candidate. `check` verifies existing outputs without new inference.

Budget and lifecycle: use the owned Crystal Gate finale Pod and the remaining funded account balance. No automatic credit reload or funding change. Preserve originals locally and delete the owned Pod after completion; keep the existing model volume.

## Screening and selection

All three 1536×1024 originals were viewed natively. A has a broad transparent wave and bright open horizon, but its foreground coral and some reflections are softer. B has the richest nacre folds and delicate fan-like organisms; the repeating pale platforms make its route legible but somewhat regular. C has the strongest red/blue contrast, distinct fine branching and a prominent coral-ring silhouette with open space around it. C is selected for the next motion preview; B is retained as a promising alternate material direction. Olof approved C on 2026-10-15, calling it gorgeous, and requested a new video from it.

The three requested/executed/embedded graphs, dimensions, job IDs and output hashes pass the runner checks. Original PNGs and job receipts remain under `exports/v001/openings/`. The stills do not establish temporal consistency or detail retention in a recurrent film.
