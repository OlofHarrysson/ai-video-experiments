# The Storm Engine: shorter movement durations

Olof confirms that stronger motion means completing the same smooth camera movement sooner, like shortening an animation duration. The original film still feels too gradual. Conservative passage durations were an assistant choice; no experiment established a technical ceiling at the requested pace.

[Compare the timings](http://localhost:3028/storm-engine-timing). The original and 2× version open together; 4× is available in the clip selector. Playback is linked by elapsed seconds, so the faster versions reach later scenes sooner and finish earlier. Keep the reviewer speed at 1× for these labels to apply.

| Version | Duration | Frames at 24 fps | Paintings |
| --- | --- | --- | --- |
| Original | 60 s | 1440 | 180 |
| 2× | 30 s | 720 | 180 |
| 4× | 15 s | 360 | 180 |

Both copies select from the existing lossless RIFE frame sequence, preserving each painting and the original path in time-compressed form. They use no new diffusion or interpolation. The selected clean ending remains the source; its brief final hold is shortened proportionately. Frame hashes, all 180 painting roles, timestamps, duration and full video decode are checked. The original remains unchanged.

This compares timing, including the faster passage of painting transformations and story. Existing redraws become quicker; fewer intermediate frames remain at 24 fps. It does not measure how increased geometric displacement per repaint would affect a newly generated film. A new one-minute film at the selected pace would need more journey, with transitions planned around that timing.

Reproduce from `apps/deforum` with `uv run --locked python projects/storm-engine/timing_audition.py`. Versioned local outputs and provenance manifests are under `exports/timing-v001/2x` and `exports/timing-v001/4x`. Human preference between the speeds is pending.
