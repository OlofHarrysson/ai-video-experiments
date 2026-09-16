# Doorway approach — planner trial

Created 2026-09-16 in the local reviewer. This is a tool-validation draft, not a replacement film or a completed crossing.

- Parent: Beyond the Threshold, delivery frame 320 (13⅓ seconds), source painting 480.
- Preserved: 41 original paintings, recorded and verified by hashes in `prefix.json`.
- Intent: approach the doorway smoothly, then release forward movement into a gentle sideways drift.
- Proposed move: two playback seconds, 1.8× final enlargement, fitted incoming pan/zoom/roll speed, forward speed settling to zero, ending sideways drift 0.02 screen widths per playback second.
- Prompt/noise: retain the doorway-and-harp description; noise 0.56 from the first new painting. Neither has been run in this draft.
- Preview: `motion-preview.mp4`, one second of original footage followed by two seconds of direct spatial deformation. End framing still contains the doorway and harp; it does not reveal the world behind them.

The first preview used three seconds and 1.5× final enlargement. Its inherited approach speed caused enlargement to peak at 1.75× before returning to 1.5×. The planner exposed this overshoot. The saved two-second alternative peaks at 1.8012× and ends at 1.8×, reducing the remaining reversal to about 0.07%.

Browser inspection covered the saved painting, branch join, final framing, playback completion, scrubbing, changed-setting save invalidation and successful preservation. The next use is to choose an intentional passage on the artwork, preview its motion and then render a short diffusion continuation. The selected trial does not prove that subsequent repainting or RIFE will preserve the same perceived movement.

`config.json`, `draft.json` and `prefix.json` are versioned records. PNGs and the MP4 are local ignored media; Git cannot restore them.
