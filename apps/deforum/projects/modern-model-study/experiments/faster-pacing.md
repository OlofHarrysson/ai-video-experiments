# Faster motion and morphing at 24 fps

Olof clarifies that all diffusion paintings should be kept; retaining every interpolation frame is unnecessary. He approves twice the overall pace while keeping 24 fps delivery. Faster spatial movement and faster morphing are both intended. This is the next timing recipe; playback taste remains open to further iteration.

## Timing recipe

| Control | Earlier owl source | Faster recipe |
|---|---:|---:|
| Working/delivery FPS |24|24|
| Seconds per repaint |1|0.5|
| Cadence |24|12|
| Spatial motion time multiplier |1|2|
| RIFE frames strictly between paintings |23|11|
| Shot duration |14s|7s|
| Opening plus diffusion repaints |14|14|

Keep the Krea noise 0.6/three-interval recipe, prompts, seed sequence and RIFE 4.25 scale 1 unchanged. Scale all shot-time events together: ease motion during 3–4s, hold spatial motion after 4s, start interpolating toward the owl after 4s, first owl-conditioned painting at 4.5s, and final native hold 6.5–7s.

For future execution, pass `FeedbackTiming(repaint_seconds=Fraction(1,2), duration_seconds=Fraction(7))` explicitly. Evaluate the original motion path at twice elapsed shot time. With this experiment's global 3s start, the reference-time adapter is `3 + 2 * (t - 3)`; do not double the global offset. Advance seeds and select prompts by repaint index so the thirteen repaint inputs follow the same intended sequence. Preserve historical runners and their defaults.

Doubling motion speed and halving time between repaints preserves the spatial transformation between corresponding paintings. Thus this particular change can reuse all saved paintings. Merely repainting more often without scaling movement and prompt timing is a different experiment.

## Current result

The existing [seven-second 24 fps cut](../cuts/v003.md) already meets the clarified request. It selects the required intermediate samples from the saved RIFE output; none of the fourteen paintings is omitted. There is no reason to regenerate those paintings or recompute those same interpolation fractions.

[Painting/timing verification](../exports/owl-transition-speed-v003/painting-timing-verification.json) confirms all fourteen anchor PNGs match their selected source-frame pixels before normal lossy delivery encoding, with output positions 0,12,…156. The completed video has 168 frames at 24 fps and lasts seven seconds. No new diffusion or RIFE inference was performed during this clarification. Existing generation records continue to describe the original timeline; this document records the faster delivery and next-run recipe.
