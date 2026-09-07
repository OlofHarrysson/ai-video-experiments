# Local video review

Use `apps/deforum/video_review.py` to inspect the beginning, development and ending of a video, then every frame in selected intervals. It saves full-size decoded PNGs, small contact-sheet pages, and `review.json` with timestamps, frame numbers, selection reasons and hashes. Matching shots can be compared at the same elapsed time. It makes no network requests and uses local `ffmpeg`, `ffprobe` and Pillow. Follow the [review and feedback agreement](review-and-feedback.md) when selecting what to show Olof.

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

## Every-frame windows and matched comparisons

```bash
# Inspect each displayed frame in a quarter-second transition, including both endpoints.
uv run --with pillow python video_review.py \
  projects/brain-entity-study/exports/p03-rife-24fps/preview.mp4 \
  --overview 0 --window 5.0 5.25 --columns 4 --page-size 8

# Same timestamps side by side: finished P3 versus the preserved original P3.
uv run --with pillow python video_review.py \
  projects/brain-entity-study/exports/p03-rife-24fps/preview.mp4 \
  --overview 0 --window 5.0 5.25 --window 5.5 5.625 \
  --compare projects/brain-entity-study/exports/p03-cfg-45/preview.mp4 \
  --label 'P3 + RIFE' --compare-label 'P3 original' --page-size 8

# Locate a few separated changes for closer examination; this does not rank video quality.
uv run --with pillow python video_review.py \
  projects/brain-entity-study/exports/p03-rife-24fps/preview.mp4 \
  --overview 6 --scene-threshold 0.08 --max-scenes 3 --scene-gap 1 \
  --before 0.083333 --after 0.083333
```

`--window START END` is repeatable. It includes the frame displayed at the start, all intervening decoded frames, and the frame displayed at the end. At 24 FPS, `5.0 5.25` selects seven images. It preserves repeated frames: identical-looking images can be the delivery behavior being investigated. Variable frame rates use actual PTS, not assumed FPS. Reversed windows and non-finite times fail.

Comparisons select timestamps from the primary video, then retrieve the frame displayed at each of those elapsed times in the comparison. A/B pairs are adjacent on each sheet; default columns are four. A held B frame may serve several A timestamps; it is extracted once and referenced repeatedly. Both actual decoded timestamps and the matching requested time are recorded. Sources whose final displayed timestamps differ by more than one of their final frame intervals are rejected; this is a same-shot review tool, not an editor or automatic semantic alignment system.

## Image budget and pages

The default is **12 images per page**, with a limit of **64 displayed images per call**, counting both sides of an A/B comparison. Use `--page-size` and `--max-frames` to change these deliberately. These are workflow defaults, not a model's context-window specification. An over-budget request fails before creating a review; it never silently drops requested frames. Select shorter windows or fewer candidates, then inspect one page at a time. A full six-second 24 FPS clip can be requested with `--overview 0 --window 0 6 --max-frames 144`, but produces 12 separate pages rather than one giant sheet.

`contact-sheet.jpg` remains the first page. Additional pages are `contact-sheet-002.jpg`, etc.; `contact_sheets` in the CLI output and metadata lists every page. Comparison columns and page sizes must be even so pairs stay together. Full-size images remain available for fine detail. `review.json` schema 2 retains the previous primary-source fields and adds pages, windows, image budget, verified frame provenance and optional comparison-source metadata.

Each call creates a new `v001`, `v002`, etc. beneath `VIDEO_DIRECTORY/reviews/VIDEO_STEM/`, or the supplied `--output-root`. Existing versions and source media are never overwritten. An interrupted/failed version may remain incomplete; a successful version contains `review.json`. The source SHA-256 is checked before and after extraction. Full-size PNGs are preserved separately from the resized contact sheet.

## Timestamp and frame meaning

Selection uses `ffprobe`'s decoded frame timestamps, not `seconds × FPS`. The selected frame is the one displayed at the requested time: the latest frame whose start time is at or before it. Times are relative to the first displayed video frame. `review.json` also stores the original integer PTS and stream time base, which together specify the timestamp exactly. The contact sheet prints relative time to six decimal places and a zero-based decoded video frame number. Non-increasing or missing timestamps fail instead of producing guessed labels.

Extraction uses FFmpeg's frame-number `select` filter with passthrough timing. It does not interpolate, resize, or synthesize frames. PNG decoding can involve color conversion; these are frames decoded from the selected video, not byte-identical copies of the original model's PNG assets. Rotation metadata is not applied. For our 8 FPS renders delivered at 24 FPS, a video frame number is a delivery-frame index and can refer to a repeated image. Use the source run/cut manifest to identify generation frames; never treat the 24 FPS export as 24 new generated images per second.

The [RIFE finishing study](../apps/deforum/projects/brain-entity-study/experiments/rife-results.md) has a different frame provenance: each original source frame appears at delivery index `3 × source_index`, with learned intermediate images between anchors. Its `manifest.json` labels each output as an anchor, interpolation or final hold. The final two holds keep the original six-second duration. Inspect intermediate frames explicitly; a sheet sampling only original anchor timestamps would hide the interpolation's effect. Do not feed these 24 FPS processed sequences into the current `editing.assemble` function, which expects collected 8 FPS generation runs.

The harness now reads an adjacent completed interpolation manifest when it certifies the exact source-video SHA-256 and agrees with every decoded timestamp. It labels original anchors, interpolation fractions/source pairs and final holds on the sheet. An unrelated/stale manifest is marked unverified and supplies no labels; a matching-video manifest with inconsistent frame timing fails. Raw exports without that provenance retain decoded video-frame labels, without inferred generation IDs.

## What automatic detection means

`--scene-threshold` enables FFmpeg's pixel-change heuristic. A score above the threshold marks a candidate; `--max-scenes` retains the strongest candidates separated by at least `--scene-gap` seconds (default 0.5), then presents them in time order. This avoids spending the whole selection on one cluster. Try `0.3`, then lower it if subtle transitions are missed. Flashes, repaint flicker and abrupt cuts can all trigger it. Gradual motion or a meaningful action can be missed. A candidate is **not a detected semantic event**. A named event is an annotation supplied by the reviewer, not a model-generated interpretation.

## Review practice

1. Open the contact sheet and inspect the full-size frames for changes in subject, composition, camera position, edge holes, and texture. State which samples support each observation.
2. Add an every-frame window where something interesting or broken appears. Compare the same time range with the baseline, and inspect a representative successful transition too. Follow the page index and open full-size extracted frames when small artifacts need inspection.
3. Review playback to judge rhythm, flicker and whether movement feels good. Sparse frames alone cannot establish those properties. Report when only sampled frames were inspected.
4. Keep the review beside the experiment and choose a small human shortlist with a plain-language explanation and a specific viewing cue. The sheet supports the review; it does not replace the inline video.

The CLI prints absolute paths to the review directory, contact sheet and metadata. Open the image with the local image-view tool. Read the metadata when choosing further timestamps or referencing exact frames. It is a sampling harness, not an automatic video-quality judge.

## Verification

```bash
uv run --with pillow python -m unittest test_video_review -v
```

Tests generate tiny local videos and verify variable frame rates with nonzero initial timestamps, selected pixels against an independent complete decode, every-frame windows, timestamp-matched comparisons with held frames, budgets before writing, complete page coverage, separated change candidates, matching/stale/inconsistent frame provenance, version preservation, source hash/mtime preservation, CLI behavior and invalid inputs.
