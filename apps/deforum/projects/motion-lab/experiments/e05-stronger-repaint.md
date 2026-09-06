# E05: stronger repainting

Chosen after E02's late frames lost texture. Change only denoise .25 → .4; retain flat zoom 1.008, 40 frames, CFG 5, no added noise/sharpening, cadence 1 and incremented seeds. Does stronger diffusion reconstruct detail, and how much does it alter the original scene?

Compare timestamps against E02 and E04. Temporal variation and scene preservation are separate from single-frame sharpness. Authorized learning balance covers this short run; retain all results.

## Completed result

Six sampled frames show that .4 denoise does not solve late softness in this no-noise/no-sharpen configuration. It also changes the distant dome into a pointed building and reinterprets vegetation/lantern shape. More diffusion freedom adds scene drift; compare the first second against E02 before judging only the final blur.

[Video](../exports/e05-stronger-repaint-v001/preview.mp4) · [Frozen run](../runs/20260906T232110786115Z-e05-stronger-repaint-40f/workflow.api.json) · [Timestamped review](../exports/e05-review/v001/contact-sheet.jpg). 40 source frames / five seconds / 24 FPS delivery repeats the 8 FPS source. Review evidence is sampled decoded frames, not a full-playback quality judgment.
