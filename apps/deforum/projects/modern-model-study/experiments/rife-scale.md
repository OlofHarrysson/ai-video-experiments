# RIFE motion-estimation scale

## Plan recorded before rendering

Olof selects the one-second repaint branch from [the interval comparison](repaint-intervals.md): “I prefer the right one” and “a bit more morphing.” Keep its six saved paintings, three native Krea sampling intervals, time-based motion and native 24 fps timeline. Compare existing RIFE 4.25 scale 1.0 against scale 0.5 locally on MPS. No new diffusion or cloud resources.

The author implementation divides its five motion-estimation scales by this parameter: `[16,8,4,2,1]` becomes `[32,16,8,4,2]`. It estimates motion at smaller internal resolutions but warps the full-resolution endpoint images. Output stays 1536×1024, 144 frames, six seconds at 24 fps. The author padding rule changes from multiples of 128 to 256; these images need no padding at either setting. This is not an output-resolution or diffusion-strength change.

Hypothesis: coarser motion estimates might favor broad shape movement over tiny unstable correspondences. They might also miss fine movement or distort edges. Review actual middle-of-transition frames and selected consecutive windows before making a recommendation. Keep full-scale as the accepted setting until evidence supports a change.

Reuse the full-scale delivery unchanged. First inspect a half-scale pair; then process all five pairs. Preserve each anchor at seconds 0–5 and copy the identical native warp-only final second into the new delivery. RIFE remains outside recurrent generation. Deliver a synchronized comparison and individual clips.

Implementation evidence: installed unmodified Practical-RIFE commit `bbfd2ea90910789a860ea3e2b32a240cd577b75e`, `train_log/RIFE_HDv3.py:56–59`, `train_log/IFNet_HDv3.py:78–87,119–160`, and `inference_video.py:193–196`. The runner records code/model hashes, scale, padding, source hashes, timing and output hashes in each receipt.

## Results

Both versions are complete and verified. **The assistant's tentative audition pick is half-scale**, based on less doubled architecture in the full-size 3.5s and 4.5s transition samples. The first 0.5s midpoint is mixed: both settings retain translucent/doubled contours and half-scale does not solve them. Broader forms and the central amber object remain recognizable in both. These are sampled-frame findings, not a proven reduction in playback flicker. Olof's scale preference is pending; the default remains 1.0.

![Full-scale left, half-scale right](../exports/rife-scale-v001/comparison/preview.mp4)

Individual clips: [current full-scale](../exports/repaint-intervals-v001/cadence-24/interpolated/preview.mp4) · [test half-scale](../exports/rife-scale-v001/half-scale/interpolated/preview.mp4).

Watch the pale tower and its small openings left of the amber object around 3–5 seconds. Some doubled small openings in the full-scale midpoints become more coherent holes/arches in the half-scale samples. This changes the inferred route between identical endpoints; it creates no new diffusion paintings. The last second deliberately matches exactly and cannot distinguish these settings.

## Verification

- Inspected full-resolution matched midpoints at 0.5, 3.5 and 4.5 seconds, plus six overview samples and every frame from 3.416667 to 3.583334 seconds in the synchronized comparison. Review sheets/receipts are beside the comparison in `reviews/preview/v001/`.
- All six source hashes and mtimes, model/code hashes and non-scale settings match the preserved baseline. Half-scale uses `[32,16,8,4,2]`; both have zero actual padding. All 144 raw output hashes and all baseline finished-frame hashes passed validation.
- All six paintings remain pixel-identical at their original timestamps. The final 24 frames are byte-identical copies of the accepted native warp-only tail. Individual output is 1536×1024; the labeled comparison is 1536×554. Both new videos fully decode to 144 frames, 24 fps, six seconds.
- The modified runner's default first pair reproduces all 25 previous first-pair PNGs byte-for-byte with identical settings and source inventory. The nine existing timing/inventory tests pass. The initial bare `uv run` test command lacked Pillow; the documented temporary dependency command below passes without changing project dependencies.
- Half-scale inference took 27.61 seconds across five pairs, versus 36.31 seconds in the earlier full-scale run (about 24% less). These are observed runs rather than a controlled hardware benchmark and exclude setup, encoding, review and the first-pair check. Everything ran locally; no new cloud resource or diffusion call was used.

## Reproduce

Run from `apps/deforum/`, with fresh output directories if repeating. The existing RIFE environment and pinned model are prerequisites; no install is performed here.

```sh
work/rife-session/.venv/bin/python interpolate.py projects/modern-model-study/exports/repaint-intervals-v001/cadence-24/rife-sources projects/modern-model-study/exports/rife-scale-v001/half-scale/rife-pair --source-frames 6 --source-fps 1 --multiplier 24 --motion-scale 0.5 --pair-only
# Inspect that pair before the full run.
work/rife-session/.venv/bin/python interpolate.py projects/modern-model-study/exports/repaint-intervals-v001/cadence-24/rife-sources projects/modern-model-study/exports/rife-scale-v001/half-scale/rife-raw --source-frames 6 --source-fps 1 --multiplier 24 --motion-scale 0.5 --validated-pair projects/modern-model-study/exports/rife-scale-v001/half-scale/rife-pair/manifest.json
uv run --with pillow python projects/modern-model-study/experiments/rife_scale_review.py
uv run --with pillow python -m unittest test_interpolate.py
```

[Assembly and verification script](rife_scale_review.py). Immutable manifests and regression receipt are under `exports/rife-scale-v001/`. Keep model and runner unchanged between a validated pair and its full run. The default-regression pair uses the same command without `--motion-scale`, with its separate preserved `default-regression-pair` directory.
