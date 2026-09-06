# Independent redraw lab

Three five-second studies compare ways of animating the preferred Seedream 4 marsh painting. A gentle 3D guide gives each frame its camera position; SDXL independently redraws each position using existing ComfyUI nodes. There is no feedback accumulation or video model. Forty source frames play at 8 FPS, repeated to a 24 FPS delivery file without interpolation.

- [E08: low-denoise independent redraw](experiments/e08.md) — incrementing noise seed.
- [E09: fixed noise](experiments/e09.md) — the same guide and settings with seed 143 every frame.
- [E10: masked gap repair](experiments/e10.md) — preserve existing guide pixels and generate only around uncovered regions.

Run `uv run --env-file .env --with pillow python projects/redraw-lab/experiments/study.py --help` from the app directory. `batch.py` submits a maximum of two jobs concurrently. `assemble_review.py` verifies source lineage, assembles immutable cuts and invokes the shared timestamp/event review harness. `metrics.py` optionally reports pixel-change diagnostics with Pillow and NumPy; those measurements do not establish subjective video quality.

Every batch, source reference and export is retained locally. Interrupted collectors must collect their existing job rather than repeating a submission. Shared transport, workflow construction and editing code remain at app level. Infrastructure lifecycle belongs to the parent experiment session.
