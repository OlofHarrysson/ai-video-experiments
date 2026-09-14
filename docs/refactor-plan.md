# Deforum development experience: audit and small refactor plan

2026-09-14. **First package migration complete, managed with uv.** The inventory below records the pre-migration baseline. Steps 1 and 2 are complete; broader entry-point moves and historical guidance cleanup remain deferred. See the [implementation and verification](#first-package-migration--2026-09-14).

## Recommendation

Create one internal Python package, `deforum_lab`, with four areas: infrastructure, image manipulation, rendering, and media. Keep project assets and previous outputs where they are. Extract the current recurrent runner's shared mechanics before reorganizing all historical scripts. Avoid a catch-all `utils` directory: `warps`, `records`, `graphs` and `comfyui` describe their purpose more clearly.

The first implementation should prove one existing experiment still behaves identically after extraction. It should not turn this notebook into a generalized animation framework.

## What the repository actually contains

Tracked-file inventory at `e82e93c`, excluding ignored media, environments and scratch:

| Area | Finding | Implication |
| --- | --- | --- |
| App root | 32 tracked files, including 24 Python files; seven are tests | Moving tests and separating runtime setup removes some clutter immediately. |
| Entire Deforum app | 145 Python files, all parse successfully | Most code is already project-owned; root cleanup alone will not address reuse. |
| Projects | 14 project directories, 89 experiment notes; 47 notes belong to modern-model-study | A catalogue is useful, but notes include plans and independent reviews, not just completed experiments. |
| Imports | 21 Python files contain `sys.path` manipulation | Script location and working directory are part of the implicit execution contract. |
| Shared environment | `pyproject.toml` declares only `boto3` | Frequently used NumPy, Pillow and OpenCV currently rely on temporary `uv --with` environments or remote installations. |
| Discovery | Project index, app README, project README and root AGENTS repeat historical status | Old 8/12 fps and model defaults can appear alongside current 24 fps guidance. |

[The new notebook index](../apps/deforum/projects/EXPERIMENTS.md) links every tracked experiment note and provides a small set of useful starting points. It leaves detailed findings and media links in their existing reports.

### The main dependency problem

The latest experiment follows this chain:

```text
early_settle.py
  → dynamic_journey.py
    → ten_dollar.py
      → pod_client.py
        → experiment.py
```

`ten_dollar.py` now supplies hashing, immutable JSON writes, transforms, graph construction and submission reuse to seven directly importing files. `dynamic_journey.py` supplies composed motion, prompt/noise scheduling and recurrence to seven directly importing files. These import counts exclude indirect and subprocess users.

`dynamic_journey.py` changes `ten_dollar.OUT` at import time. Later experiments change `journey.OUT`, `base.OUT` and `pod_client.DEPLOYMENT`. This works in isolated processes, but makes reuse dependent on initialization order. Two experiments in one process could redirect each other's outputs or deployment. This is an architectural risk, not evidence that our archived renders were mixed.

Finishing has similar coupling: `dynamic_journey_finish.py` supplies reusable RIFE preparation but also contains the specific 24-second film join. Checks and review builders import earlier experiment modules too. Extract reusable functions; keep film-specific decisions with the film.

### Boundaries a move must respect

- `pod_client.py` imports general collection/request helpers from the older `experiment.py` CLI. Make ComfyUI transport independent of that CLI and of serverless/S3 dependencies.
- `history_noise.py`, `replay_noise.py` and the node classes in `noise_sequence.py` execute inside ComfyUI. Zero normal local imports does not make these files dead code. They need a distinct remote-node installation boundary.
- RIFE uses a separate pinned environment under `work/rife-session`; retain that runtime initially. Do not mix its Torch stack into the main local environment just to rearrange folders.
- `media_review.py` resolves templates, sessions and cache relative to its current file. The reviewer has a module and asset directory sharing the same name; package moves must make those paths explicit.
- `serverless/modern-models.json` is also used by `apps/comfyui/projects/regional-composition/experiments/run_krea.py`. Leave the manifest and serverless Docker context in place during the first slice.
- Saved receipts, references, exports and source hashes are archive records. Moving code must not rewrite them or regenerate their media.

## Proposed structure

This is the target responsibility map, not an instruction to create every directory immediately. Add a package area when its first implementation moves there.

```text
apps/deforum/
  README.md                    short current start page
  POD.md                       current GPU runbook
  pyproject.toml / uv.lock      one local application environment
  src/deforum_lab/
    paths.py                   explicit app/project/output locations
    records.py                 hashes and immutable receipts
    infrastructure/            ComfyUI requests, Pod client, serverless transport
    image/                     time-based warps and resampling
    rendering/                 model graphs, schedules, recurrent execution
    media/                     frame inspection, RIFE, cuts and linked reviewer
  tools/pod/                   scripts executed on a Pod during setup
  comfy_nodes/                 optional diagnostic nodes installed in ComfyUI
  tests/                       local shared-code tests
  media_review/                existing browser assets and session descriptions
  workflows/                   existing reusable API graphs
  serverless/                  existing worker/build context, initially unchanged
  projects/
    README.md                  project briefs and current cuts
    EXPERIMENTS.md              canonical notebook catalogue
    <project>/
      experiments/             experiment-owned plans, configs and scripts
      references/ runs/ cuts/ exports/    preserved locations
  work/ .env                   ignored scratch and credentials
```

One package gives scripts stable imports such as `from deforum_lab.image.warps import warp_at_time`, rather than importing a previous experiment. PyPA documents the isolation benefit and the installation requirement of a `src` layout. An editable install managed by uv is appropriate for this local application; no package publishing is proposed. [PyPA layout guidance](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/), [uv build-system and editable installation guidance](https://docs.astral.sh/uv/concepts/projects/config/).

Declare the actual recurring local dependencies in the existing project and lock them. Keep optional serverless and model-specific execution dependencies separate where imports allow it. uv distinguishes persistent project dependencies from one-off `--with` additions; use that existing mechanism rather than creating an environment for every film. Preserve currently verified numerical-library versions during the migration. [uv project environment guidance](https://docs.astral.sh/uv/concepts/projects/layout/).

### Concrete ownership

| Existing code | Proposed owner |
| --- | --- |
| `pod_client.py`, HTTP/collection pieces of `experiment.py` | `infrastructure/comfyui.py` and `infrastructure/pod.py`; deployment passed explicitly |
| `serverless_client.py` | `infrastructure/serverless.py`, after the first migration |
| `spatial_warp.py`, transforms in `ten_dollar.py`, composition in `dynamic_journey.py` | `image/warps.py`; pure functions with unchanged coordinate conventions and precision |
| `modern_workflows.py`, `workflow_recipes.py`, current `repaint_graph` | `rendering/graphs.py`; model recipes remain explicitly separate |
| `feedback_timing.py`, current time-based prompt/noise evaluation | `rendering/timing.py` and `rendering/schedules.py` |
| Recurrent loop and resume logic | `rendering/feedback.py`; explicit config, output directory and client |
| Hashes, frozen JSON records, source lineage | `records.py`; preserve existing record formats |
| `interpolate.py`, `editing.py`, `video_review.py`, reviewer builder/server | `media/`; existing UI and frame roles remain intact |
| Setup scripts and three diagnostic-node files | `tools/pod/` and `comfy_nodes/`, after remote references are inventoried |

Dependency direction: project scripts call the package; package code does not import projects. Image transforms do not import network clients. Rendering calls the provided client; finishing consumes recorded paintings and timestamps. Pass context as ordinary function parameters or a small dataclass, without a plugin system or dependency-injection framework.

## Implementation sequence

1. **Navigation and baseline — this review.** Save the catalogue, dependency findings and migration plan. Record the latest feedback in the experiment note. Identify historical recipe references without changing their outputs.
2. **One working vertical slice — complete.** Set up the importable package and declared local image dependencies. Extract the current Lanczos motion, graph/schedule functions, receipt helpers and explicit Pod client. Make the early-settle runner use them without importing `dynamic_journey` or `ten_dollar`, and make its checks/review functions independent of unrelated experiment globals. Preserve its current CLI arguments and paths. Update all tracked consumers of any moved module in the same checkpoint; avoid permanent forwarding modules. Earlier experiment scripts can remain at their existing paths and keep their experiment-specific algorithms.
3. **Organize remaining shared entry points.** Move shared tests to `tests/`, then media tools, setup scripts and diagnostic nodes with their documented callers. Give the reviewer a session argument so a new comparison changes session data rather than Python constants. Update the Devrun command through its normal workflow; browser-check the same two-video laptop layout. Preserve the pinned RIFE runtime and validate its subprocess paths.
4. **Simplify current guidance.** Root AGENTS should hold collaboration rules, current recipe, active task and links. App README should identify one current execution path. Full history belongs in linked experiment reports and the notebook catalogue. Update old statements that present 8 fps, Klein, SDXL or serverless as current defaults; retain historical recipes within their reports.

Stop after step 2 and review the developer experience before doing step 3. Keep each checkpoint small enough to compare against the preceding implementation.

For new experiments, a compact directory is useful when several files belong together:

```text
experiments/<experiment-id>/
  README.md       question, controls, findings and output links
  config.json     prompts, motion and sampling values
  run.py          thin experiment orchestration, when needed
  review.py       only if the experiment needs a custom review
```

Do not move all 89 historical notes into this format in the first pass. Their current links and relative paths are valuable. New directories must not import another experiment's `run.py`; reusable behavior belongs in the package. A generic experiment DSL, database, new reviewer UI and monorepo-wide library are outside this refactor.

## Verification and definition of done

The first migration succeeds when the current early-settle path uses explicit shared modules and its existing behavior is reproduced locally:

- Keep frozen ComfyUI graph dictionaries, sigma schedules, prompts, seeds, painting timestamps and lineage equal to the saved run. Compare warped image pixels exactly, including unchanged prefix frames. Preserve distinct graph-field serialization if hashes depend on it.
- Replay saved model responses through the refactored recurrent loop; verify the next input and parent lineage. This establishes orchestration equivalence, not fresh GPU numerical equivalence. No paid render is necessary for this check.
- Check completion/resume behavior, changed-config rejection and no automatic resubmission after an uncertain remote response with a fake client.
- Run the existing app tests and selected migrated experiment checks. A normal `uv sync --locked` plus documented commands should suffice for ordinary local tools. Verify imports from the app root and a nested experiment directory, and check packaged assets if a wheel is built.
- After media tools move, use the existing RIFE environment for a saved pair, verify anchor timestamps and final hold behavior, and browser-check synchronized frame/painting controls at the current viewport.
- Keep all old media/source hashes unchanged. Update imports, subprocess commands, model-manifest references, node installation instructions and Devrun paths when their owner moves. Do not mark remote setup validated until its actual deployment path has been checked; it can remain outside step 2.

No new quality tuning should accompany the code migration. This lets a changed image indicate a refactor regression rather than a deliberate artistic change.

## Audit checks and dispositions

- AST inspection: **145 tracked Python files parsed**, no syntax failures. Static import counts do not discover runtime imports, shell copies or subprocess references; those boundaries were inspected separately above.
- Baseline tests: **43 app-level unittest tests pass** using `uv run --locked --with pillow --with numpy --with opencv-python python -m unittest discover -v`. Default discovery does not recursively cover the historical experiment scripts. This is not a GPU/model or browser validation.
- Static analysis: **warn**, Ruff **0.16.2**, check-only on all 145 tracked Python files. It reported 185 existing diagnostics: I001 142; F401 18; RUF007 6; C408 4; SIM117 3; ISC004 2; C401 2; SIM115 2; B023, RUF059, PLC0206, F841, TRY004 and BLE001 one each. Rules follow the locally resolved configuration, not a newly committed project policy. Full findings are saved under `apps/deforum/work/refactor-audit-20260914/ruff.json`.
- **Track:** import ordering, unused imports/variables and idiom/resource-handling findings. Review only touched modules during migration; unused imports may be intentional exports or dependency checks. No bulk autofix is proposed.
- **Reviewed, no current behavior defect established:** B023 in `brain-entity-study/experiments/render.py:46` closes over a loop variable, but its lambda is consumed immediately inside the same iteration. ISC004 in `lantern-marsh/experiments/review.py:43` and `video_review.py:43` constructs deliberate FFmpeg/ffprobe argument strings. BLE001 in `serverless/handler.py:70` converts worker exceptions into recorded job errors. Keep these as documented advisory findings until the owning module is edited; no suppression or semantic change was applied.
- Formatter, broader experiment execution, cloud inference and browser tests were not run: this is a documentation/planning change. AST, lint and the current local suite supply the relevant baseline. No JavaScript or React analyzer was used because no reviewer code changed.

## First package migration — 2026-09-14

Olof approved the first slice and specified uv. [The existing app project](../apps/deforum/pyproject.toml) now builds an internal `deforum_lab` package using Hatchling, installed through `uv sync`. The distribution retains its existing name, `deforum-experiment`; nothing is published. NumPy 2.5.3, Pillow 12.3.0 and OpenCV 5.0.0.93 match the local versions used for the baseline checks. Ruff 0.16.2 is a locked development dependency. The source-distribution allowlist includes only package source, project metadata, lockfile and README, so ignored videos and runtime caches cannot enter a build.

The [package](../apps/deforum/src/deforum_lab) contains the explicit Pod client and ComfyUI collection, Lanczos resampling and composed timed warps, model graphs and schedules, recurrent painting, immutable records, painting sheets and the existing RIFE finishing adapter. App paths come from the caller; the installed package never guesses the repository location. The package does not import a project script, the older CLI, or serverless transport. RIFE still runs in its existing pinned environment.

[Early-settle](../apps/deforum/projects/modern-model-study/experiments/early_settle.py), its checker and its review builder now use the package. Their CLI stages and archive paths stay the same. `render_paintings` takes config, output and client explicitly; `PodClient` owns a copy of its deployment settings. The three completely moved root modules are `spatial_warp.py` → `image/resampling.py`, `modern_workflows.py` → `rendering/graphs.py`, and `feedback_timing.py` → `rendering/timing.py`. All tracked Python callers were updated. Historical runners retain their other algorithms and legacy client; their later migration remains step 3.

### Verification

- **48 local unittest tests pass**, including five new tests for recurrent parent use, completed-run reuse, changed-config/output rejection, separate outputs/deployments, and accepted or uncertain remote submissions. Accepted jobs resume collection; uncertain submissions are not automatically resubmitted.
- The existing archive checker returns **identical JSON before and after extraction**, covering the eight generation jobs, the 192-frame delivery and its preserved prefix. Original graphs, paintings, preserved prefix and final video hashes remain unchanged.
- [Offline replay](../apps/deforum/projects/modern-model-study/experiments/early_settle_replay.py) feeds the saved model responses through the new runner. It verifies **16 identical paintings, seven identical warped input pixel arrays, and eight identical graphs and parent lineages**. Running it again creates zero new paintings. This tests orchestration with recorded responses, not fresh GPU numerical equivalence.
- The seven newly encoded input PNGs have different file hashes from the historical Pod PNGs. Their decoded RGB pixels are exactly equal; re-encoding the original pixels with the local encoder produces exactly the replay bytes. The replay records the actual new input hashes and reports these encoding differences. Original archive files are untouched.
- `uv sync --locked`, imports from a nested experiment directory, and `uv build` succeed. The built wheel imports all 18 submodules from a separate environment outside the repository. Wheel/source archive contents were checked for the package allowlist.
- Ruff **0.16.2** passes for the package, new tests and migrated early-settle scripts. The 22 remaining findings in import-only historical consumers (18 I001, three F401, one RUF007) are pre-existing and tracked with the baseline audit; no new findings remain. No JavaScript analyzer or browser test was run because the reviewer was unchanged. No fresh GPU inference, remote package installation or RIFE render was performed; the existing archived RIFE delivery was validated.

Reproduce the local checks from `apps/deforum/` (archive commands require this Mac's preserved media):

```bash
uv sync --locked
uv run --locked python -m unittest discover -v
uv run --locked python projects/modern-model-study/experiments/early_settle_check.py delivery
uv run --locked python projects/modern-model-study/experiments/early_settle_replay.py --output work/package-refactor/replay-new
uv build --out-dir work/package-refactor/dist
```

Use a new replay output directory for each diagnostic. Verified local evidence lives under ignored `apps/deforum/work/package-refactor/`: `before-check.json`, `after-check-final.json`, `unittest-final.log`, `replay-v002/replay-check.json` and `dist/`. The replay directories contain recorded responses explicitly labelled as replay evidence, not new ComfyUI job histories.

The subsequent [transition-frequency experiment](../apps/deforum/projects/modern-model-study/experiments/transition-frequency/README.md) verified remote installation through `uv sync --locked --no-dev` in a separate runner environment, then completed 28 real ComfyUI jobs; see [the Pod runbook](../apps/deforum/POD.md). Tests, remaining media CLIs, setup scripts, diagnostic nodes, serverless packaging and the reviewer service have not moved. No model recipe, cadence, interpolation policy, media file or cloud resource was changed by this migration.

## Deferred creative question: diffusion only when change is wanted

Olof observes that the new low-noise ending barely transforms and may offer little visible benefit over warping alone. He considers either warp-only holds or low-noise holds reasonable, and wants to revisit this after the refactor. This is not evidence that they are pixel-equivalent or that diffusion never repairs accumulated warp artifacts.

A later matched test can branch from painting 96: warp-only versus the existing low-noise ending, with identical motion and timing. At native 24 fps, warp-only motion can render each timestamp directly; it need not invent new paintings just to feed RIFE. If diffusion resumes later, its initialization should be the current warped state of the last accepted painting. The feedback loop still applies whenever a repaint occurs.

Keep motion, repaint scheduling and finishing separate in the refactor so optional holds can be explored later. Do not implement irregular painting events, an automatic completion detector, or new interpolation policy in this migration; the current cadence and RIFE assumptions must remain explicit until that separate experiment.

### Explicit painting times — 2026-09-14

The transition-frequency follow-up adds an optional ordered `painting_frames` list to the shared recurrent runner. Each repaint consumes the immediately preceding painting and warps over its actual time interval. The existing uniform cadence path is preserved. RIFE finishing accepts matching explicit timestamps and interpolates each interval without moving its anchor paintings. No new model dependency was added. The 51-test local suite covers irregular parent/timing/resume behavior and equivalence with the former uniform interpolation plan; the historical early-settle graph/warp replay still passes.
