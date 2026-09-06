# Guide redraw

Redraw eight saved lantern-marsh camera-guide frames independently with SDXL. Each frame starts from its own depth-warped guide, never the preceding repaint. Hypothesis: scene layout drifts less, while changing seeds may cause more texture flicker.

First trial complete: eight 1280×720 frames generated and locally archived. Independent redraw stays closer to the guide through frame 7, with more frame variation and a conspicuous first-frame style jump. [View the three-way comparison](exports/20260906T215605650227Z-comparison/preview.mp4) and [contact sheet](exports/20260906T215605650227Z-comparison/contact.png); the session note distinguishes measurements, visual inspection and unreviewed real-time playback.

- [Experiment and runnable commands](experiments/independent-redraw.md)
- [Recipe](experiments/redraw.py)
- [Session evidence](../../../../docs/research/guide-redraw-session.md)

Original guide files, strip, recipe snapshot, workflow and frame mapping are frozen under `references/assets/`. Shared Serverless collection preserves every attempt under `runs/`. No generation is overwritten or automatically selected as a cut.
