# Project and experiment workflow

Living convention, updated 2026-09-14. Start with the [project index](../apps/deforum/projects/README.md) and [experiment notebook](../apps/deforum/projects/EXPERIMENTS.md). Current Krea work uses [short-lived ComfyUI Pods](../apps/deforum/POD.md). Earlier explicit frame continuation and source-range assembly completed hosted validation; they do not restore a saved GPU process.

## Folder ownership

```text
apps/deforum/
  src/deforum_lab/               shared Python package, installed with uv
  experiment.py                 earlier project/SDXL CLI
  pyproject.toml / uv.lock       shared local environment
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
      branches/branch-<id>/     continuation drafts, retained paintings and lineage
  work/                         private temporary infrastructure receipts
```

A **project** is a film or a coherent creative study. An **experiment** asks one question inside it. A **run** is one actual render attempt. A **cut** selects and orders ranges from runs. An **export** is a rendered version of a cut. Reference images and guide videos belong to their project; shared code and workflow recipes stay at app level.

## Shared code

Use `uv sync --locked` from `apps/deforum/`, then `uv run --locked python ...`. New shared mechanics belong in the `deforum_lab` package; projects import it without modifying `sys.path` or another experiment's globals. [Early-settle](../apps/deforum/projects/modern-model-study/experiments/early_settle.py) is the first migrated runner. Earlier scripts remain available while the [small refactor](refactor-plan.md) proceeds in stages.

| Location in `apps/deforum/` | Responsibility |
| --- | --- |
| `src/deforum_lab/infrastructure/` | ComfyUI requests/collection and `PodClient`, with explicit deployment and output inputs. |
| `src/deforum_lab/image/` | Lanczos resampling and composed time-based spatial transforms. |
| `src/deforum_lab/rendering/` | Model graphs, prompt/noise schedules, timing, recurrent painting and graph validation. |
| `src/deforum_lab/media/` | Painting sheets, RIFE preparation/subprocess adapter and saved delivery validation. |
| `src/deforum_lab/paths.py`, `records.py` | Caller-supplied workspace locations, hashes and immutable records. |
| `experiment.py`, `pod_client.py`, `serverless_client.py` | Legacy project/SDXL CLI and transports still used by earlier experiments. |
| `editing.py`, `workflow_recipes.py`, `interpolate.py` | Existing cut, legacy graph and pinned RIFE entry points awaiting later migration. |
| `video_review.py` | Local overviews, every-frame windows, matched comparisons and paginated frame extraction; [usage and evidence limits](video-review.md). |
| `setup-pod.sh` | Shared installation of the pinned ComfyUI node/model recipe. |
| `workflows/` | Reusable starter graphs; each render stores its exact configured copy in its run folder. |
| `pyproject.toml`, `uv.lock` | Shared Python environment. |
| `test_*.py` | Local tests, including isolated package execution and archive behavior. |
| `work/`, `.env` | Ignored infrastructure scratch files and credentials, kept out of creative project assets. |

Keep project-specific references, decisions, outputs and frozen render settings inside the project. Shared functions take explicit config, output paths and clients; image transforms do not import network clients, and the package does not import project scripts. Add reusable code to the area that owns its behavior instead of a catch-all `utils` folder. Each saved run graph is the authoritative record of that generation.

The first session follows this structure too: six attempts in the botanical project’s `runs/`, its comparison in `exports/`, and the report in `experiments/baseline-results.md`. Existing receipts and media remain unchanged; project membership is recorded in the experiment index.

## Working loop

1. Create a project with `uv run python experiment.py init-project PROJECT`. Add it to the project index and write the intent in its README.
2. Write an experiment note in `experiments/`. State the question, what changes, what stays fixed, cost boundary, and the shortest useful test. The scaffold includes `baseline.md`.
3. Save original reference media in `references/assets/`. Record provenance, purpose, and SHA-256 in the reference manifest. A working crop or edited keyframe gets a new filename.
4. Run the experiment-owned script with its explicit config, output directory and deployment client. The earlier SDXL CLI uses `--project` and `--experiment`. Preserve identities, graph, input hashes, parent lineage and receipts in the run folder. Save human review in the experiment note after collection.
5. Use `video_review.py` for an overview, selected every-frame windows and matched comparisons. Record progression, useful source ranges, camera behavior, detail loss and structural change separately; state what was inspected. Follow the [review and feedback agreement](review-and-feedback.md): the assistant screens results, then presents a small inline-video shortlist with plain-language explanations and one useful taste question. Keep review versions beside project media; record Olof's playback verdict without inferring understanding.
6. Draft a cut as a new `cuts/vNNN.md`, selecting source ranges. Point “current cut” in the project README to the selected version. Reordering a cut never changes its sources.
7. To change the movie, retain the selected prefix and create a new continuation run. Record parent run, source-frame index, and changed settings. The `continue` and `assemble` CLI commands implement this image-based branch and cut workflow.
8. Verify local originals and exports before deleting experiment-owned cloud resources. Keep rejected takes. Never use cleanup to prune creative assets.

For a new experiment, copy the short headings from `experiments/baseline.md` into a descriptively named Markdown file. Use lowercase hyphenated IDs. The runner requires that note to exist, so every render has a question to return to.

For current Krea movies, the assistant uses the [motion-preview CLI](../apps/deforum/MOTION_PREVIEW.md): inspect a saved painting, write the story purpose and motion in an editable JSON plan, preview the incoming film and proposed movement together, then save a separate draft. Inspect motion, framing, next prompt and noise timing together before running diffusion. The short-plan interface covers pan, zoom and roll with an incoming-speed fit; regional choreography remains available through the shared renderer. Saving a draft does not generate paintings. Keep the original prefix and generate only the future portion; if the resulting artwork changes the route, branch again from an earlier painting. Present screened films to Olof through the media reviewer.

## Cuts and frame numbers

The v0 cut format is a Markdown table: order, source path relative to the project, source FPS, in-frame (inclusive), out-frame (exclusive), and intent. Preserve each reviewed version under a new number. Do not overwrite an existing export when revising the edit.

Current feedback uses a 24 fps motion and delivery timeline. Half-second repaints produce painting anchors at frames 0, 12, 24, …; RIFE fills the intervening delivery frames and never feeds back into generation. Keep painting timestamps, motion and finishing explicit.

Earlier SDXL sequences used 8 generated FPS and delivered 24 FPS by repeating frames. In those archives only, generated frame 19 corresponds to delivery frames 57–59. A range `[0, 40)` at 8 FPS lasts five seconds, as does `[0, 120)` in its 24 FPS preview. Interpret each cut using its recorded source FPS.

Continuation also needs a global schedule frame: when branching from generated frame 19, frame 19 is the initial state, and new rendering begins at frame 20. A cut may use that frame only once at the join. Never silently reset a camera/prompt schedule or seed sequence when starting a new chunk. See [continuation research](research/continuation-and-editing.md).

## Preserve versus back up

Completed run media and settings are treated as immutable. New generations always get new IDs. Collection of an unfinished run can add missing artifacts; collection of a completed run returns its existing preview without contacting the expired Pod. No automatic media deletion is provided.

Use `copy_verified` when reusing media: supported Mac volumes share storage through independent copy-on-write clones. Verify session archives as streams and retire redundant unpacked scratch copies only after checking every file against a retained archive. See [storage conventions and cleanup](storage.md). Unique generations, original references and cut versions remain preserved.

`runs/`, reference assets and exports are ignored by Git. Git can preserve their small indices but cannot recover ignored media after disk failure. For moves within the same disk, rename without overwriting and verify file counts and hashes before and after. When transferring to another disk, copy originals and manifests, verify the copy, and update the archive location before considering removal of the old copy. Keep a separate backup. No external-disk backup has been configured or performed yet. Local originals currently occupy the Mac's disk.

## Boundaries

Cut assembly now takes a minimal JSON list of `{run, in, out}` ranges and saves source hashes beside its export. Keep OTIO and editing UI deferred. Exact continuation requires separate validation; a saved image alone does not guarantee reproduction of the same subsequent frames.
