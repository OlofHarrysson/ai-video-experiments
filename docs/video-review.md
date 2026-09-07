# Local video review

Use `apps/deforum/video_review.py` to inspect the beginning, development and ending of a video, then sample around a specific change. It saves full-size decoded PNG frames, a labeled contact sheet, and `review.json` with timestamps, frame numbers, selection reasons and hashes. It makes no network requests and uses the local `ffmpeg` and `ffprobe` executables plus Pillow.

Run from `apps/deforum/`. The first example uses an existing export; substitute any new project's actual video path in the others.

```bash
# Six samples spread across an existing five-second video.
uv run --with pillow python video_review.py \
  projects/seedream-motion/exports/v001-feedback/preview.mp4

# Compact single-row review of the new experiment, once its export exists.
uv run --with pillow python video_review.py \
  projects/motion-lab/exports/e02-flat-push-v001/preview.mp4 \
  --overview 6 --columns 6

uv run --with pillow python video_review.py \
  projects/motion-lab/exports/e03-depth-push-v001/preview.mp4 \
  --overview 6 --columns 6

# Explicit moments, plus context around a manually identified event.
uv run --with pillow python video_review.py \
  projects/PROJECT/exports/CUT/preview.mp4 \
  --overview 0 --at 0 --at 00:02.5 --at 4.9 \
  --event 'lantern begins breaking=2.5' --before 0.25 --after 0.5

# Overview plus the strongest visual-change candidates and their context.
uv run --with pillow python video_review.py \
  projects/PROJECT/exports/CUT/preview.mp4 \
  --scene-threshold 0.3 --max-scenes 6 --before 0.125 --after 0.25

# Keep reviews together under a project's ignored exports directory.
uv run --with pillow python video_review.py \
  projects/PROJECT/runs/RUN/preview.mp4 \
  --output-root projects/PROJECT/exports/review-EXPERIMENT
```

`--at` and `--event NAME=TIME` are repeatable. Times accept decimal seconds, `MM:SS`, or `HH:MM:SS`. `--overview 0` disables the default overview. Context applies to named events and automatic scene candidates, not bare `--at` samples. Negative decimal timestamps and requests beyond the final frame are clamped; requested and clamped times are both recorded. Negative context and non-finite numbers are rejected.

Each call creates a new `v001`, `v002`, etc. beneath `VIDEO_DIRECTORY/reviews/VIDEO_STEM/`, or the supplied `--output-root`. Existing versions and source media are never overwritten. An interrupted/failed version may remain incomplete; a successful version contains `review.json`. The source SHA-256 is checked before and after extraction. Full-size PNGs are preserved separately from the resized contact sheet.

## Timestamp and frame meaning

Selection uses `ffprobe`'s decoded frame timestamps, not `seconds × FPS`. The selected frame is the one displayed at the requested time: the latest frame whose start time is at or before it. Times are relative to the first displayed video frame. `review.json` also stores the original integer PTS and stream time base, which together specify the timestamp exactly. The contact sheet prints relative time to six decimal places and a zero-based decoded video frame number. Non-increasing or missing timestamps fail instead of producing guessed labels.

Extraction uses FFmpeg's frame-number `select` filter with passthrough timing. It does not interpolate, resize, or synthesize frames. PNG decoding can involve color conversion; these are frames decoded from the selected video, not byte-identical copies of the original model's PNG assets. Rotation metadata is not applied. For our 8 FPS renders delivered at 24 FPS, a video frame number is a delivery-frame index and can refer to a repeated image. Use the source run/cut manifest to identify generation frames; never treat the 24 FPS export as 24 new generated images per second.

The [RIFE finishing study](../apps/deforum/projects/brain-entity-study/experiments/rife-results.md) has a different frame provenance: each original source frame appears at delivery index `3 × source_index`, with learned intermediate images between anchors. Its `manifest.json` labels each output as an anchor, interpolation or final hold. The final two holds keep the original six-second duration. Inspect intermediate frames explicitly; a sheet sampling only original anchor timestamps would hide the interpolation's effect. Do not feed these 24 FPS processed sequences into the current `editing.assemble` function, which expects collected 8 FPS generation runs.

## What automatic detection means

`--scene-threshold` enables FFmpeg's pixel-change heuristic. A score above the threshold marks a candidate; `--max-scenes` retains the strongest candidates and presents them in time order. Try `0.3`, then lower it if subtle transitions are missed. Flashes, repaint flicker and abrupt cuts can all trigger it. Gradual motion or a meaningful action can be missed. A candidate is **not a detected semantic event**. A named event is an annotation supplied by the reviewer, not a model-generated interpretation.

## Review practice

1. Open the contact sheet and inspect the full-size frames for changes in subject, composition, camera position, edge holes, and texture. State which samples support each observation.
2. Add a named event where something interesting or broken appears; inspect the before/after frames. For example, narrow a suspected jump at 2.5 seconds to samples at 2.375, 2.5 and 2.625 seconds.
3. Review playback to judge rhythm, flicker and whether movement feels good. Sparse frames alone cannot establish those properties. Report when only sampled frames were inspected.
4. Keep the review version beside the experiment and present the video itself in chat with a short finding. The sheet supports the review; it does not replace the output video.

The CLI prints absolute paths to the review directory, contact sheet and metadata. Open the image with the local image-view tool. Read the metadata when choosing further timestamps or referencing exact frames. It is a sampling harness, not an automatic video-quality judge.

## Verification

```bash
uv run --with pillow python -m unittest test_video_review -v
```

Tests generate tiny local videos and verify variable frame rates with nonzero initial timestamps, selected pixels against an independent complete decode, a known hard cut and its context, named-event clamping, version preservation, source hash/mtime preservation, and invalid inputs.
