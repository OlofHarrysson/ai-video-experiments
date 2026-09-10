# A 24 fps working timeline with interpolation by default

## Plan before execution

Olof requests 24 fps for source and delivery, time-based spatial motion, and interpolation by default. Preserve cadence as a frame-count description while exposing seconds between repaints. A higher FPS means smaller movement per frame for the same speed; do not double deformation over a second.

First run a local timing-migration experiment using the accepted three-second cadence-3 paintings. At 24 fps they belong six frames apart, with unchanged seeds, sampling graphs, diffusion inputs and timestamps. Replay the recorded successful diffusion responses through the actual recurrent runner and verify every new warped input against its recorded predecessor. This is a recorded-run replay, not fresh GPU inference. Preserve all historical outputs. Verify all 36 shared motion instants and all 12 anchors. Finish with existing RIFE pixels at unchanged timestamps and fresh native-24fps warps in the final quarter-second. No new visual-quality claim is expected from renumbering the timeline.

New timing defaults: 24 fps source/delivery, 0.25 seconds per repaint (cadence 6), interpolation enabled. Existing experiments retain their explicit 12 fps clock. Warp APIs accept absolute start/end times in seconds, so translation, twist and expansion schedules evolve at the same speed regardless of sampling rate. The model still receives a warped previous painting, and RIFE remains display-only. Diffusion settings remain tunable, but are held fixed in this migration.

[Runner](timebase24.py), shared [timing settings](../../../feedback_timing.py), [recurrent runner](turbo_smoothing.py), and [time-based motion](turbo_transitions.py).

## Result

The migration passes. Every one of the 11 recorded repaint requests has the same model graph, seed and parent hash, and its new warped input matches the archived input. All 12 anchor files remain byte-identical. All 36 original motion timestamps match the corresponding even-numbered 24 fps samples; the 36 additional samples differ from their preceding frame, so the raw 24 fps path actually calculates intermediate warps rather than duplicating frames.

All display frames before 2.75 seconds reuse the exact previously accepted RIFE pixels. At and after 2.75 seconds, the final warp-only interval uses fresh 24 fps samples. All 12 displayed anchor images match the original decoded pixels, including the final anchor re-encoded by the raw-frame writer. PNG serialization hashes are not used as a substitute for pixel equivalence there. The raw, RIFE-finished and comparison videos are all 72 frames at 24 fps for exactly three seconds.

![Old and new timelines, identical repaint rhythm](../exports/timebase24-v001/compare-timing/preview.mp4)

[New 24 fps finished clip](../exports/timebase24-v001/interpolated/preview.mp4) · [native 24 fps raw control](../exports/timebase24-v001/cadence-6/preview.mp4). The comparison should look essentially the same: changing the clock is not a new image-quality technique. RIFE still invents the motion between generated endpoints; it does not receive the explicit warp curve.

Verification included 12 passing timing/inventory tests, exact coordinate-map comparisons against the previous Git version for every anchor in all four historical cadence schedules, full recurrent recorded-response replay, and frame inspection. Visually inspected three overview moments and every delivered frame in the final 2.75–2.958334-second window. The two sides retain matching composition and repaint timing; only the tail's extra motion samples change. This proves local timing/input equivalence, not deterministic fresh diffusion across different GPU hardware.

New experiments should construct `FeedbackTiming()` and pass it as `timing` to `turbo_smoothing.render`. That renderer creates recurrent anchors and raw diagnostic frames; RIFE remains a separate required finishing stage by default, using the existing validated-pair workflow. Historical calls with no timing argument retain the original 12 fps convention. The local migration runner consumes the interpolation default and supports `--no-interpolation` for raw diagnosis. Its recorded-response replay and reused RIFE frames are explicitly identified in `timing-verification.json` and the finished manifest. It does not provide a new cloud provisioning path.

To replay this check from `apps/deforum/`:

```sh
uv run --with numpy --with pillow --with opencv-python python projects/modern-model-study/experiments/timebase24.py
```

The model recipe is unchanged: three native Turbo intervals, the same prompt, Euler/simple settings and increment-per-repaint seeds. No GPU was provisioned, no new diffusion images were generated, and no RIFE inference was repeated. The existing raw and finished studies remain preserved. For a subsequent quality experiment, vary repaint interval or RIFE settings independently while retaining the 24 fps timeline; the diffusion recipe remains another possible control if interpolation alone cannot give the intended morphing.
