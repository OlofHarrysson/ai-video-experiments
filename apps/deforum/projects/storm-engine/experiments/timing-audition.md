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

Reproduce from `apps/deforum` with `uv run --locked python projects/storm-engine/timing_audition.py`. Versioned local outputs and provenance manifests are under `exports/timing-v001/2x` and `exports/timing-v001/4x`.

## Human feedback — 2026-09-17

Olof selects roughly **3–4× the original sixty-second Storm Engine pace**, with approximately **3× as the usual target** and movement rising toward **4× when the movie's rhythm supports it**. He says 4× is sometimes too quick and sometimes perfect. Preserve the smooth floating style while shortening the time taken to complete each movement. A move that took eight seconds would take about 2.7 seconds at 3× or two seconds at 4×.

The reference is the original delivered film at reviewer speed 1×, not the generation clock or the 2× comparison. Three times speed is Olof's stated target inferred between the displayed alternatives; a separate 3× render has not been screened. This selects a direction for shot timing, without requiring one fixed speed across a film or establishing faster-generation artifact limits. Existing exports remain unchanged.
