# Project and experiment workflow

Living convention, 2026-09-07. Start with the [project index](../apps/deforum/projects/README.md). Explicit frame continuation and source-range assembly have completed hosted validation. They do not restore a saved GPU process. See the [serverless runbook](../apps/deforum/serverless/README.md).

## Folder ownership

```text
apps/deforum/
  experiment.py                 shared submission/collection client
  workflows/                    reusable ComfyUI API graphs
  projects/
    README.md                   project index
    <project>/
      README.md                 intent, experiment index, current cut
      references/
        README.md               source and reference manifest
        assets/                 original images/videos, ignored by Git
      experiments/*.md          question, comparison, findings, run links
      runs/<run-id>/            frozen settings, frames, receipts, preview
      cuts/v001.md              ordered source ranges and editorial intent
      exports/v001/             assembled previews, when available
  work/                         private temporary infrastructure receipts
```

A **project** is a film or a coherent creative study. An **experiment** asks one question inside it. A **run** is one actual render attempt. A **cut** selects and orders ranges from runs. An **export** is a rendered version of a cut. Reference images and guide videos belong to their project; shared code and workflow recipes stay at app level.

## Shared code

All projects use the same app-level implementation and Python environment:

| Location in `apps/deforum/` | Responsibility |
| --- | --- |
| `experiment.py` | Project scaffolding, ComfyUI submission/collection and preview encoding. |
| `serverless_client.py`, `editing.py`, `workflow_recipes.py` | Shared RunPod transport, preserved cuts and reusable graph construction. |
| `video_review.py` | Local overviews, every-frame windows, matched comparisons and paginated frame extraction; [usage and evidence limits](video-review.md). |
| `setup-pod.sh` | Shared installation of the pinned ComfyUI node/model recipe. |
| `workflows/` | Reusable starter graphs; each render stores its exact configured copy in its run folder. |
| `pyproject.toml`, `uv.lock` | Shared Python environment. |
| `test_experiment.py` | Shared project/archive behavior checks. |
| `work/`, `.env` | Ignored infrastructure scratch files and credentials, kept out of creative project assets. |

Keep project-specific references, decisions, outputs and frozen render settings inside the project. Do not copy the runner or dependencies into each film. The current SDXL starter graph contains the botanical example prompts; it is a starting recipe, while each saved run graph is the authoritative record of that generation. If shared code grows, extract modules with clear responsibilities such as a ComfyUI client or video encoding when they are actually reused. There is no separate `utils` package yet.

The first session follows this structure too: six attempts in the botanical project’s `runs/`, its comparison in `exports/`, and the report in `experiments/baseline-results.md`. Existing receipts and media remain unchanged; project membership is recorded in the experiment index.

## Working loop

1. Create a project with `uv run python experiment.py init-project PROJECT`. Add it to the project index and write the intent in its README.
2. Write an experiment note in `experiments/`. State the question, what changes, what stays fixed, cost boundary, and the shortest useful test. The scaffold includes `baseline.md`.
3. Save original reference media in `references/assets/`. Record provenance, purpose, and SHA-256 in the reference manifest. A working crop or edited keyframe gets a new filename.
4. Submit a run with explicit `--project` and `--experiment`. The runner records those identities and the exact graph in a unique run folder. Save human review in the experiment note after collection.
5. Use `video_review.py` for an overview, selected every-frame windows and matched comparisons. Record progression, useful source ranges, camera behavior, detail loss and structural change separately; state what was inspected. Follow the [review and feedback agreement](review-and-feedback.md): the assistant screens results, then presents a small inline-video shortlist with plain-language explanations and one useful taste question. Keep review versions beside project media; record Olof's playback verdict without inferring understanding.
6. Draft a cut as a new `cuts/vNNN.md`, selecting source ranges. Point “current cut” in the project README to the selected version. Reordering a cut never changes its sources.
7. To change the movie, retain the selected prefix and create a new continuation run. Record parent run, source-frame index, and changed settings. The `continue` and `assemble` CLI commands implement this image-based branch and cut workflow.
8. Verify local originals and exports before deleting experiment-owned cloud resources. Keep rejected takes. Never use cleanup to prune creative assets.

For a new experiment, copy the short headings from `experiments/baseline.md` into a descriptively named Markdown file. Use lowercase hyphenated IDs. The runner requires that note to exist, so every render has a question to return to.

## Cuts and frame numbers

The v0 cut format is a Markdown table: order, source path relative to the project, source FPS, in-frame (inclusive), out-frame (exclusive), and intent. Preserve each reviewed version under a new number. Do not overwrite an existing export when revising the edit.

Be explicit about the source: generated PNG sequences are currently 8 FPS; their delivered MP4s are 24 FPS with repeated frames. Generated frame 19 corresponds to delivery frames 57–59. A range `[0, 40)` at 8 FPS lasts five seconds. A range `[0, 120)` in the 24 FPS preview also lasts five seconds. Source-frame numbers are distinct from movie timeline positions.

Continuation also needs a global schedule frame: when branching from generated frame 19, frame 19 is the initial state, and new rendering begins at frame 20. A cut may use that frame only once at the join. Never silently reset a camera/prompt schedule or seed sequence when starting a new chunk. See [continuation research](research/continuation-and-editing.md).

## Preserve versus back up

Completed run media and settings are treated as immutable. New generations always get new IDs. Collection of an unfinished run can add missing artifacts; collection of a completed run returns its existing preview without contacting the expired Pod. No automatic media deletion is provided.

`runs/`, reference assets and exports are ignored by Git. Git can preserve their small indices but cannot recover ignored media after disk failure. For moves within the same disk, rename without overwriting and verify file counts and hashes before and after. When transferring to another disk, copy originals and manifests, verify the copy, and update the archive location before considering removal of the old copy. Keep a separate backup. No external-disk backup has been configured or performed yet. Local originals currently occupy the Mac's disk.

## Boundaries

Cut assembly now takes a minimal JSON list of `{run, in, out}` ranges and saves source hashes beside its export. Keep OTIO and editing UI deferred. Exact continuation requires separate validation; a saved image alone does not guarantee reproduction of the same subsequent frames.
