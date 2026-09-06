# E04: repaint every third frame

Chosen after E02's timestamped review showed progressive smoothing and loss of texture. Keep E02's anchor, flat push-in, .25 denoise, CFG 5 and all other settings; change only cadence from 1 to 3. The existing Difforum node warps every frame but only runs diffusion on frames divisible by three. This reduces VAE/diffusion round trips; it does not interpolate new motion.

40 source frames at 8 fps, five seconds. Inspect whether detail lasts longer and whether repaint frames cause periodic jumps. Cost covered by the authorized session balance; preserve every run.

Node behavior verified in the pinned [sampler source](https://github.com/chillithebillis/Difforum/blob/1d750efd3c1d1dda792b8ef6c14b06a14a69f879/nodes/sampler_nodes.py).

## Completed result

Six overview frames retain more of the lantern lattice, reeds and boardwalk than E02 at equal timestamps, but smoothing remains by five seconds. A second review samples 2.875/3.0/3.125 seconds around a known repaint step. Pixel scene detection at threshold .08 found no candidates; that does not prove absence of flicker or judder.

[Video](../exports/e04-sparse-repaint-v001/preview.mp4) · [Frozen run](../runs/20260906T232109589389Z-e04-sparse-repaint-40f/workflow.api.json) · [Timestamped review](../exports/e04-review/v001/contact-sheet.jpg). 40 source frames / five seconds / 24 FPS delivery repeats the 8 FPS source. Review evidence is sampled decoded frames, not a full-playback quality judgment.
