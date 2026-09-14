# Linked media review

The local reviewer keeps one, two or three videos visible together, side by side on laptop-sized windows, with shared play/pause, speed, scrubbing, frame stepping and painting stepping. This is the reusable human-facing companion to `video_review.py`'s extracted-frame/contact-sheet review.

The current session compares the existing shell-to-city descriptions with finer descriptive stages; a third selectable clip uses those same stages and gentler final repaints. All three retain the same actual painting timestamps, motion, CFG1, three Euler intervals and eight-second 24 fps/RIFE delivery. The preceding repaint-frequency comparison remains at `/transition-frequency`, and the earlier settling comparison at `/early-settle`.

## Run locally

The default human review path is a dedicated browser window. Olof primarily uses a 14-inch MacBook; the initial vertical stack inside Codex did not keep both frames visible. The local layout fits the available viewport, keeps shared controls compact, and offers Full screen. At widths below 600px it uses fitted rows. Source aspect ratios are preserved without cropping.

Devrun service `media-review` runs `uv run python media_review_server.py` from `apps/deforum/`. The current assigned URL is `http://localhost:3028/`; inspect Devrun's `effectiveUrl` before future handoffs. The server binds only to loopback and serves the generated review document at `/` or `/full-quality.html`, with no repository directory listing or arbitrary file routes. It rebuilds the default saved session on startup. Restart through Devrun after source/session edits; the service remains running for Olof's review until stopped.

The full-quality local version has no 1 MB chat limit and does not need preview transcoding. The inline version remains optional for compact demonstrations, not the default close-comparison surface.

The allowlisted `/state-replay` route serves the separately built `media-review-state-replay-v001/full-quality.html`. It leaves the default session available for concurrent experiment reviews. Rebuild that output from `sessions/state-replay.json` when its data changes; missing named outputs return 404.

## Build a review

The `/history-recurrence` route serves `media-review-history-recurrence-v001/full-quality.html`, built from `sessions/history-recurrence.json`. Its default pair uses identical RIFE finishing; all four raw recurrent cases remain selectable, with painting versus hold labels preserved.

From `apps/deforum/`:

```bash
uv run python media_review.py media_review/sessions/prompt-bridges.json \
  --output projects/modern-model-study/exports/media-review-v002
```

Optionally pass `--inline /ABSOLUTE/THREAD-VISUALIZATION-DIRECTORY/media-review.html` to also build a compact chat fragment. Use the active task's writable visualization directory for that output. The builder produces a conversation fragment there and `full-quality.html` plus `receipt.json` in the output directory. Neither output needs a server, cloud inference, or remote media requests. Preview compression is cached in ignored `work/media-review/cache`.

Edit a saved JSON session to use a new set of existing videos. Each clip has `id`, `label`, a brief `note`, optional longer `details`, and an MP4 `source` relative to `apps/deforum/`. `selected` sets the initial one to three videos. The dropdown library can contain more, subject to the inline size limit. Use descriptive labels and mark unmatched comparisons explicitly. New reviews should use a fresh output directory; rebuilding a named review replaces its generated HTML and receipt, never its source media. Interactive dropdown selections are temporary; update the JSON to retain them.

Present the inline file with the visualization content reference, alongside a normal absolute file link to the full-quality HTML. Inline fragments must stay below 1 MB. The default preview is 480px wide, H.264 CRF30, with every source frame and timestamp retained. For longer clips, choose a shorter review window first or deliberately reduce `--width`; oversized reviews fail instead of silently dropping frames. Preview compression can obscure texture and grain. Use original media in the full-quality review for detail judgments.

## Controls and timing

- Play/pause and speed apply to every selected video. No autoplay or audio.
- The shared slider and previous/next frame use the **first video's actual decoded timestamps**, not assumed FPS. Other videos align by elapsed time; a shorter video holds its last frame. Changing the first video changes the shared timeline. There is no automatic semantic or scene alignment.
- Frame stepping seeks to the middle of each frame's display interval to avoid rounding onto a neighboring frame. Linked playback uses the first video's clock and corrects secondary drift; it is not guaranteed frame-locked playback across decoders.
- Previous/next painting uses only the adjacent completed interpolation manifest when its video hash and every timestamp match. Missing/stale metadata supplies no painting labels; a contradictory matching manifest fails. Cadence is never guessed from image differences or FPS.
- Left/right arrows step frames and Shift + left/right steps paintings across the page when no interactive control is focused. Space toggles playback. Focused buttons, links, sliders, dropdowns and editable fields retain their own keyboard behavior; click the artwork or page background to return to review shortcuts. Alt/Ctrl/Command combinations are left to the browser.
- The ⓘ button beside a brief description shows optional generation details on hover or keyboard focus. Click to pin it, then click again, elsewhere or press Escape to dismiss. Details include the important prompt stages, recipe and comparison caveats; they do not expand the permanent layout.
- Frame and painting indices are zero-based. A painting is an archived anchor in the export, an in-between is a synthesized intermediate frame, and a final hold follows the last anchor.
- Diagnostic sample sequences can certify ordinary `hold` frames as well. These repeat a generated painting and are excluded from painting-step navigation; they are not interpolation frames.

The first version accepts zero-start MP4s. It deliberately rejects nonzero start timestamps rather than giving uncertain seek labels. Source files are read-only; the full-quality page embeds their original bytes. The receipt records source and preview hashes, frame counts, dimensions and provenance verification.

## Validation

```bash
node --test media_review/timeline.test.cjs
uv run --with pillow python -m unittest test_media_review test_video_review
```

The initial three clips each have 156 frames, 13 certified paintings and 6.5 seconds at 24 fps. Preview decoding, timestamp preservation and source hashes are checked during every build. The pure timeline tests include fractional/variable timing and irregular painting intervals.

Browser checks for the user-requested localhost version passed on 2026-09-13: complete two-video view at 1360×740, complete three-video view at 1100×650, shared frame step to frame 1 with decoded presentation metadata matching both panels, painting step to frame 12, add/remove third clip, shared scrub to frame 60 with both presented frames matching, half-speed playback and fullscreen entry. Screenshots confirmed complete uncropped images and all controls visible without scrolling at those tested sizes. The earlier file-URL block remains historical (AF-20260913-103154); localhost testing followed Olof's separate request for a local web app.

Broader edge-case coverage remains pending: different clip lengths, rapid source changes during loading, end/replay, every speed, and very narrow layouts. Native linked playback remains approximate; paused frame checks do not establish permanent frame locking during playback.

The page-wide keyboard follow-up was browser-checked: no-focus Right steps both videos to frame 1, Shift + Right to painting 1/frame 12, focused info-button arrows leave the timeline unchanged, and the details panel opens and dismisses without shifting the video layout.

The transition-frequency session was browser-checked on 2026-09-14 in the existing dedicated Chrome window (1456×858 captured viewport): both complete frames and controls fit without scrolling; frame 54 correctly shows an in-between on the control and painting 5 on the treatment; next-painting advances to frame 60 with different painting counts; linked playback reaches frame 191 and correctly labels final holds 15/19. The comparison is left paused at frame zero. No layout or keyboard behavior was changed in this experiment.

The transition-stages session was browser-checked on 2026-09-14 in the existing dedicated Chrome window (1456×858 captured viewport): both complete frames and controls fit without scrolling; frame 84 labels painting 10 on both sides; the capped third variant is selectable, and next-painting advances to frame 90/painting 11. Its details explain which two noise values change. Linked playback reaches frame 191/final hold 19 on both panels. The default control/stages pair is left paused at frame zero. No layout or shortcut code changed.
