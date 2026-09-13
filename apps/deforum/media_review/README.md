# Linked media review

Review one, two or three vertically stacked videos with shared play/pause, speed, scrubbing, frame stepping and painting stepping. This is the reusable human-facing companion to `video_review.py`'s extracted-frame/contact-sheet review.

The initial session compares intermediate scene descriptions with a direct city prompt. An optional third video is the earlier gentler-noise experiment; its label identifies that it ran on a different GPU/runtime and is not a matched control.

## Build a review

From `apps/deforum/`:

```bash
uv run python media_review.py media_review/sessions/prompt-bridges.json \
  --output projects/modern-model-study/exports/media-review-v001 \
  --inline /ABSOLUTE/THREAD-VISUALIZATION-DIRECTORY/media-review.html
```

Use the active task's writable visualization directory for `--inline`. The builder produces a conversation fragment there and `full-quality.html` plus `receipt.json` in the output directory. Neither output needs a server, cloud inference, or remote media requests. Preview compression is cached in ignored `work/media-review/cache`.

Edit a saved JSON session to use a new set of existing videos. Each clip has `id`, `label`, `note`, and an MP4 `source` relative to `apps/deforum/`. `selected` sets the initial one to three videos. The dropdown library can contain more, subject to the inline size limit. Use descriptive labels and mark unmatched comparisons explicitly. New reviews should use a fresh output directory; rebuilding a named review replaces its generated HTML and receipt, never its source media. Interactive dropdown selections are temporary; update the JSON to retain them.

Present the inline file with the visualization content reference, alongside a normal absolute file link to the full-quality HTML. Inline fragments must stay below 1 MB. The default preview is 480px wide, H.264 CRF30, with every source frame and timestamp retained. For longer clips, choose a shorter review window first or deliberately reduce `--width`; oversized reviews fail instead of silently dropping frames. Preview compression can obscure texture and grain. Use original media in the full-quality review for detail judgments.

## Controls and timing

- Play/pause and speed apply to every selected video. No autoplay or audio.
- The shared slider and previous/next frame use the **top video's actual decoded timestamps**, not assumed FPS. Other videos align by elapsed time; a shorter video holds its last frame. Changing the top video changes the shared timeline. There is no automatic semantic or scene alignment.
- Frame stepping seeks to the middle of each frame's display interval to avoid rounding onto a neighboring frame. Linked playback uses the top video's clock and corrects secondary drift; it is not guaranteed frame-locked playback across decoders.
- Previous/next painting uses only the adjacent completed interpolation manifest when its video hash and every timestamp match. Missing/stale metadata supplies no painting labels; a contradictory matching manifest fails. Cadence is never guessed from image differences or FPS.
- Left/right arrows step frames; Shift + left/right steps paintings; Space toggles playback when focus is on a button or other non-editable part of the review. Native slider/select keyboard behavior takes precedence.
- Frame and painting indices are zero-based. A painting is an archived anchor in the export, an in-between is a synthesized intermediate frame, and a final hold follows the last anchor.

The first version accepts zero-start MP4s. It deliberately rejects nonzero start timestamps rather than giving uncertain seek labels. Source files are read-only; the full-quality page embeds their original bytes. The receipt records source and preview hashes, frame counts, dimensions and provenance verification.

## Validation

```bash
node --test media_review/timeline.test.cjs
uv run --with pillow python -m unittest test_media_review test_video_review
```

The initial three clips each have 156 frames, 13 certified paintings and 6.5 seconds at 24 fps. Preview decoding, timestamp preservation and source hashes are checked during every build. The pure timeline tests include fractional/variable timing and irregular painting intervals.

**Browser QA remains pending:** the 2026-09-13 run could not inspect the live interface. The browser URL policy rejected opening the local sandbox preview; no alternate URL or browser route was used after that rejection. Central incident: AF-20260913-103154. Automated media/unit checks do not certify native browser presentation or layout.

Pending interaction inventory: two clips load paused on frame zero; next/previous frame and painting; slider forward/backward and rapid seeks; playback/pause at each speed; replay after the end; adding a third/removing to one; changing selections during loading; shorter-secondary final hold; keyboard controls; visible frame presentation matching labels; layout at 736px and 320px. Inspect initial, playing, paused and three-video states. Keep this status explicit until those checks are actually completed.
