# E02: flat push-in

Question: can gentler feedback preserve the preferred reference while producing a readable five-second push-in?

Seedream reference; SDXL feedback; 40 frames at 8 fps; 1280×720; seed 143 incremented; denoise .25, CFG 5, 28 steps, no added noise or sharpening, color coherence .8. Flat zoom 1.008 per step, no rotation. Compare E03 with the same rendering settings but depth translation. Apparent travel is not calibrated between methods.

Preserve every generation. Learning session budget: existing authorized RunPod balance, no top-up. This recipe is one of ten experiments; versioned export and timed-frame review follow execution.

## Completed result

The seven sampled frames (including the first repaint at 0.125s) show a recognizable push-in but progressive texture loss. By roughly 2–3 seconds, the lantern, clouds and boardwalk are substantially smoother; the last frame is heavily blurred. Lower denoise does not by itself preserve texture over repeated feedback cycles.

[Video](../exports/e02-flat-push-v001/preview.mp4) · [Frozen run](../runs/20260906T231720032177Z-e02-flat-push-40f/workflow.api.json) · [Timestamped review](../exports/e02-review/v001/contact-sheet.jpg). 40 source frames / five seconds / 24 FPS delivery repeats the 8 FPS source. Review evidence is sampled decoded frames, not a full-playback quality judgment.
