# Assistant motion-preview CLI

Use this locally to plan and inspect a continuation before inference. The assistant operates it; Olof reviews the resulting films. It needs the uv environment and FFmpeg, with no browser, reviewer session, web server or GPU. Shared implementation: [motion_preview.py](src/deforum_lab/media/motion_preview.py) and [branching.py](src/deforum_lab/media/branching.py).

## Working loop

From `apps/deforum/`:

```bash
uv run --locked python -m deforum_lab.media.motion_preview --help

uv run --locked python -m deforum_lab.media.motion_preview inspect \
  projects/modern-model-study/exports/doorway-revision-v001/d5-beyond-the-threshold/faster/rife-moving-tail/preview.mp4 \
  --frame 321

uv run --locked python -m deforum_lab.media.motion_preview init \
  projects/modern-model-study/exports/doorway-revision-v001/d5-beyond-the-threshold/faster/rife-moving-tail/preview.mp4 \
  --frame 321 --intent 'Approach the opening, then reveal the new surroundings' \
  --out work/doorway-plan.json

# Edit the JSON plan after inspecting the painting.
uv run --locked python -m deforum_lab.media.motion_preview preview work/doorway-plan.json

# Use the returned preview_path with the existing frame-inspection harness.
uv run --locked python video_review.py /absolute/path/to/preview.mp4 \
  --overview 6 --window 0.875 1.125 --max-frames 16

# Only after inspecting the preview; use its returned id.
uv run --locked python -m deforum_lab.media.motion_preview save PREVIEW_ID
```

All commands emit JSON to stdout. Failures print a brief error to stderr and exit nonzero. `--app /absolute/path/to/apps/deforum` before the subcommand allows execution from another directory. Source paths are app-relative or absolute inside the app; plan-file paths are relative to the shell's working directory. `init` refuses to overwrite an existing plan. Edit the working plan and preview again to try alternatives; each preview freezes its own request and configuration.

`inspect` returns the selected painting path, prompt, noise, estimated incoming motion, and both source and delivery times. An in-between frame snaps back to the preceding saved painting. Inspect that actual image before choosing the focal point or route.

## Plan fields

| Field | Meaning |
| --- | --- |
| `source`, `frame` | Parent MP4 and zero-based delivery frame. |
| `intent` | What the move should follow, reveal or change. |
| `duration` | Playback seconds, rounded to a whole painting interval. |
| `zoom` | Final enlargement relative to the branch painting; below 1 pulls back. |
| `pan_x`, `pan_y` | Viewpoint displacement in screen widths/heights; positive is right/down. |
| `roll` | Artwork rotation in degrees. |
| `center_x`, `center_y` | Zoom center, normalized 0…1 across the image. |
| `match_speed` | Fit incoming pan/zoom/roll velocity at the branch. Regional motion is approximate. |
| `end_drift` | Ending rightward viewpoint speed in screen widths per playback second. |
| `prompt`, `noise` | Next description and starting noise from the first new painting onward. |

The curve ends with zero zoom/roll speed and retains the chosen lateral drift. Speed matching can cause overshoot; inspect scale diagnostics, framing and the entire path. The [motion palette](../../docs/motion-palette.md) records other primitives for more complex choreography; this short-plan interface currently covers pan, zoom and roll with one future prompt/noise level.

## Outputs and preservation

`preview` writes a small 24 fps MP4 and frozen JSON under ignored `work/motion-planner/<id>/`, returning absolute media/record paths, the branch time, repaint timing and warnings. It includes up to one second of archived original film before moving the selected painting with the shared spatial renderer. No new PNG sequence is written. Prompt/noise events are recorded for later generation; they are not applied in this motion-only preview. The initial plan is a starting point for editing, not approved choreography.

`save` creates `projects/<project>/branches/branch-<id>/` with the configuration, parent hashes, retained painting prefix, intent and preview. It verifies the source and every retained painting, uses filesystem clones where supported, and returns the existing draft on repeated saves. Source generations remain unchanged. Earlier browser-created drafts remain valid historical records. PNGs/MP4s are ignored by Git; small configurations and provenance can be versioned. Local preservation is not an external backup.

For later generation, use `render_paintings` with the saved config, `output=branch_root.parent`, `first_frame=prefix_through+cadence` and `last_frame=painting_frames[-1]`. Follow the owning project's Pod/finishing runbook. The CLI itself never submits inference. Generate a short passage, inspect the actual paintings and backtrack if their composition changes the intended route.

Current supported input: full 24 fps retimed deliveries, 3:2 artwork, cadence 12, and complete source/delivery manifests with retained painting and lead-in frames. Other historical formats fail explicitly. Matching planned velocity and previewing one deformed painting cannot establish how subsequent repainting or RIFE will look.

## Validation — 2026-09-16

All 83 Python tests and two timeline tests pass. Subprocess tests run the complete inspect → init → edited plan → preview → save sequence without a server, including overwrite refusal and idempotent saving. The CLI reproduced the earlier real doorway preview byte-for-byte; all 41 retained paintings still match their originals. The existing draft is readable through the CLI. Browser inspection confirms that both films remain visible, frame/painting shortcuts work and the authoring controls are gone. No paid inference was run.
