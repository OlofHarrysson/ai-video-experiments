# Linked media review

The local reviewer keeps one, two or three videos visible together, side by side on laptop-sized windows, with shared play/pause, speed, scrubbing, frame stepping and painting stepping. This is the reusable human-facing companion to `video_review.py`'s extracted-frame/contact-sheet review.

The default session is selected by `SESSION` in [media_review_server.py](../media_review_server.py); named comparison routes are recorded there too. See [current state](../../../docs/current-state.md) for the latest experiment, rather than treating a historical validation below as the current playlist. Keep the longest clip first for a shared timeline that can show both full videos. Split embedded pages by experiment family when useful for comparison.

## Run locally

The default human review path is a dedicated browser window. Olof primarily uses a 14-inch MacBook; the initial vertical stack inside Codex did not keep both frames visible. The local layout fits the available viewport, keeps shared controls compact, and offers Full screen. At widths below 600px it uses fitted rows. Source aspect ratios are preserved without cropping.

Devrun service `media-review` runs `uv run python media_review_server.py` from `apps/deforum/`. The last recorded URL is `http://localhost:3028/`; inspect Devrun's `effectiveUrl` before handoff. Use Devrun/shared terminal for routine delivery and verification; Olof prefers this over Chrome integration. The server binds only to loopback and serves the generated review document at `/` or `/full-quality.html`, with no repository directory listing or arbitrary file routes. It rebuilds the default saved session on startup. Restart through Devrun after source/session edits; the service remains running for Olof's review until stopped.

The root page streams the original MP4s through allowlisted local URLs, with range requests for seeking. It avoids embedding large base64 videos in the live page. The standalone `full-quality.html` remains self-contained for offline use. The inline version remains optional for compact demonstrations, not the default close-comparison surface.

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

## Plan a continuation

On the local review page, pause at a useful moment and click **Branch from here** below that video. An interpolated frame snaps backward to the preceding saved painting; the page shows both delivery and source frame numbers. This first planner supports the current 3:2, 24 fps retimed movies with cadence 12 and complete delivery manifests. Older unrelated export formats are rejected explicitly.

1. State the story purpose. Set the move's duration, final enlargement, horizontal/vertical pan, rotation and zoom center. Timing is in playback seconds; duration rounds to a whole painting interval.
2. Keep **Carry incoming speed** selected to fit the previous planned movement's pan, zoom and rotation at the join. The move eases toward the chosen destination with zero final zoom/roll speed; the selected sideways drift continues. Regional warps only admit an approximate fit. An overshoot warning means the path grows or shrinks beyond the requested endpoint before settling; inspect it and change the plan.
3. Open **Next description and repaint strength** to set the next prompt and starting noise. They take effect at the first new painting, not on the retained branch painting. The preview labels that event but does not run diffusion.
4. Click **Preview motion**. It includes up to one second of the actual previous film, followed by a deformation of the selected painting. Play, scrub and step frames across the join. Changing settings invalidates the preview for saving.
5. Click **Save branch** to preserve a separate draft in `projects/<project>/branches/branch-<id>/`. It contains the config, parent hashes, retained painting prefix, intent and motion preview. Saved originals are verified and cloned where the filesystem supports it. Source material is unchanged, and repeated saves of one preview return the same draft.

This is a small planning surface: pan, zoom and roll with one next prompt/noise level. It does not yet provide visual handles, regional-warp editing, a multi-event prompt timeline or a generation button. A motion preview cannot predict repainting or RIFE's perceptual motion. Matching the planned velocity is useful but does not prove the final diffusion join will look smooth.

For agent execution, use the saved config with `render_paintings`, `output=branch_root.parent`, `first_frame=prefix_through+cadence`, and `last_frame=painting_frames[-1]`. Use the owning project's Pod/finishing runbook, preserve the prefix, and generate a short continuation for review. This renderer compatibility is covered by local configuration/preservation tests; a paid generation from a UI-created draft has not been attempted yet.

Preview scratch lives in `work/motion-planner/`. Only small MP4s and JSON are written there, with no new PNG sequence. Saved branch PNGs and preview MP4s are ignored by Git; config/provenance JSON can be versioned. These are local retained copies, not an external backup.

## Validation

Continuation planner checked on 2026-09-16: 81 Python tests and two timeline tests passed; syntax and scoped Ruff checks passed. Coverage includes the new curve's incoming/outgoing velocity and inverse, parent-motion lookup, frame snapping, source-hash refusal, preserved prefixes, idempotent draft saving, MP4 range serving and blocked cross-origin writes. Browser checks at 1280×720 and 390×844 covered layout; the desktop flow covered preview playback, scrubbing, prompt details, stale-preview invalidation, saving a 41-painting doorway branch and reviewer arrow/painting shortcuts. Original movie/config and all 41 retained paintings were reverified afterward. A preview uses no GPU inference.

```bash
node --test media_review/timeline.test.cjs
uv run --locked python -m unittest test_media_review test_video_review test_branching test_media_review_server
```

The initial three clips each have 156 frames, 13 certified paintings and 6.5 seconds at 24 fps. Preview decoding, timestamp preservation and source hashes are checked during every build. The pure timeline tests include fractional/variable timing and irregular painting intervals.

Browser checks for the user-requested localhost version passed on 2026-09-13: complete two-video view at 1360×740, complete three-video view at 1100×650, shared frame step to frame 1 with decoded presentation metadata matching both panels, painting step to frame 12, add/remove third clip, shared scrub to frame 60 with both presented frames matching, half-speed playback and fullscreen entry. Screenshots confirmed complete uncropped images and all controls visible without scrolling at those tested sizes. The earlier file-URL block remains historical (AF-20260913-103154); localhost testing followed Olof's separate request for a local web app.

Broader edge-case coverage remains pending: different clip lengths, rapid source changes during loading, end/replay, every speed, and very narrow layouts. Native linked playback remains approximate; paused frame checks do not establish permanent frame locking during playback.

The page-wide keyboard follow-up was browser-checked: no-focus Right steps both videos to frame 1, Shift + Right to painting 1/frame 12, focused info-button arrows leave the timeline unchanged, and the details panel opens and dismisses without shifting the video layout.

The transition-frequency session was browser-checked on 2026-09-14 in the existing dedicated Chrome window (1456×858 captured viewport): both complete frames and controls fit without scrolling; frame 54 correctly shows an in-between on the control and painting 5 on the treatment; next-painting advances to frame 60 with different painting counts; linked playback reaches frame 191 and correctly labels final holds 15/19. The comparison is left paused at frame zero. No layout or keyboard behavior was changed in this experiment.

The transition-stages session was browser-checked on 2026-09-14 in the existing dedicated Chrome window (1456×858 captured viewport): both complete frames and controls fit without scrolling; frame 84 labels painting 10 on both sides; the capped third variant is selectable, and next-painting advances to frame 90/painting 11. Its details explain which two noise values change. Linked playback reaches frame 191/final hold 19 on both panels. The default control/stages pair is left paused at frame zero. No layout or shortcut code changed.

The two-hour lab shortlist was browser-checked on 2026-09-14 in the dedicated Chrome window (1456×858): both full frames and controls fit without scrolling; painting-step reaches frame 12/painting 1 in both films; at shared frame 267 the fourteen-second film continues while the eleven-second film holds frame 263 and reports its ended state. All six named session routes return HTTP 200. The shorter-clip behavior is verified for this pair; other mixed-timing cases remain untested.

The featured pair also reaches frame 335/final hold 27 on the first film while retaining the shorter film’s final hold 21. Generation details open and close correctly. The reviewer is left paused at frame zero with both films visible; Devrun remains running for Olof’s review.

The motion-hour shortlist was browser-checked on 2026-09-14 in the same dedicated Chrome window (1456×858). Both complete frames and shared controls fit without scrolling. Page-level Right followed by Shift+Right reaches frame8/painting1 on both faster films; linked playback reaches frame223/final hold27 while the shorter film holds frame191/final hold23 and reports its ended state. Generation details explain the faster delivery timeline and recurrent initialization. The reviewer is left at frame zero, with Devrun running for Olof. Named `/motion-paths`, `/motion-travel` and `/motion-pace` pages preserve the original variants; `/two-hour-lab` retains the previous shortlist.
