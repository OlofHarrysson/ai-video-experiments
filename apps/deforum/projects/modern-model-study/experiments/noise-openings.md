# Five independent opening-noise probes

Completed with five verified GPU jobs. These are independent text-to-image openings, with no prior image, recurrent animation, inversion or RIFE. Original graphs, actual noise tensors and generated images are archived locally; the temporary recorder node and owned Pod were removed.

## Observed results

[View the four-opening comparison](../exports/continuity-review-v001/openings-four.png). Identical noise on the native and explicit-noise paths reproduced pixels exactly. A tiny actual noise change (measured RMS 0.02000) preserved the broad composition with small architectural variations. A larger change (RMS 0.20009) altered more geometry; independent noise (RMS 1.41603) rearranged the scene much more. Both nearby variants use the same perturbation direction. This is evidence for useful nearby openings in one example, not a guarantee of smooth recurrent animation or control over particular objects.

[Actual verification](../exports/noise-openings-v001/verification.json) checks all five jobs, empty initialization, exact pixel parity, tensor shape and hashes, and the noise mixtures. Marginal standard deviations stayed between 0.99833 and 1.00010. [Visual review](../exports/continuity-review-v001/review-verdict.md) records the separate perceptual observations. Pixel equality does not require equal PNG file hashes, because metadata differs.

## Recorded recipe

All cases use the exact prompt frozen from `continuity-controls-configs/euler-060.json`, Krea Turbo FP8 through the existing model graph, 1536×1024, Euler/simple, eight full-generation steps, CFG1 and denoise1. The base seed is 918273. Keep the same runtime/model assets throughout.

| Ordered case | Sampling path | Actual initial noise |
| --- | --- | --- |
| `native-euler-simple8` | Unmodified core KSampler | Native seed918273 |
| `advanced-same-noise` | BasicScheduler + CFGGuider + SamplerCustomAdvanced | Recorded seed918273, rho0, index0 |
| `nearby-rho-09998` | Same advanced graph | rho0.9998, index1; expected 0.02 RMS displacement |
| `nearby-rho-098` | Same advanced graph | rho0.98, index1; expected 0.20 RMS displacement |
| `fresh-seed-918274` | Same advanced graph | rho0, index1; native draw for seed918274 |

The four advanced cases use the existing `DeforumRecordedNoise` from `apps/deforum/noise_sequence.py`. Both correlated cases combine the same seed918273 baseline and seed918274 innovation through that helper. Correlation values are supplied directly in API graphs, including 0.9998. They are not rounded to the node widget's UI step.

The native KSampler remains unchanged and does not directly record its noise. `advanced-same-noise` records the equivalent draw; exact decoded-pixel parity is required before the perturbation jobs can run. The runner decodes output index0 for both paths. The pinned advanced sampler repairs empty latent channels before generating noise, matching the native preparation path. [Core implementation](https://github.com/Comfy-Org/ComfyUI/blob/12d5279438bfefc058a269eae805ceab6047777f/comfy_extras/nodes_custom_sampler.py#L935-L983).

## Execution by the main agent

Run from `/Users/olof/git/ai-video-experiments/apps/deforum`. This tested invocation supplies temporary local runner dependencies without editing the shared project manifest:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --frozen --no-sync --with numpy --with pillow --with opencv-python-headless python projects/modern-model-study/experiments/noise_openings.py prepare
```

`prepare` has already completed. Repeating it checks that the five configs and five workflow JSONs are identical. It writes only `noise-openings-configs/`. Changes to the source stationary config or prepared graphs fail explicitly.

After the main agent restores the existing temporary recorder node and checks its owned runtime, replace `/absolute/path/to/deployment.json` with that session's deployment file:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --frozen --no-sync --with numpy --with pillow --with opencv-python-headless python projects/modern-model-study/experiments/noise_openings.py render --deployment /absolute/path/to/deployment.json
```

Omitting `--case` runs all five in the listed order, with a parity gate after the second. For explicit staging, use `--case native-euler-simple8`, then `--case advanced-same-noise`, then the three variant case names. The advanced parity case requires the completed native baseline; variants require verified exact parity. A mismatch stops before further variant submissions. Five successful jobs mean 40 denoiser evaluations; no retry jobs are automatically created.

Output root: `projects/modern-model-study/exports/noise-openings-v001/`. Each case gets its descriptively named PNG, immutable config and `opening.json` receipt; original graphs, history and collected frames stay under that root's `runs/`. The submission path is `ten_dollar.submit_once` with a probe-specific name. Complete local receipts are verified without remote calls. A missing final receipt resumes collection from the existing run, rather than making another job. An uncertain or rejected submission must be resolved against its existing receipt by the main agent; the runner does not bypass it.

## Actual-noise archive and local verification

The main agent must archive these files from `<ComfyUI-output>/deforum-noise-study/`, retaining each tag directory:

- `noise-openings-v001-advanced-same-noise/0000.npz` and `0000.json`
- `noise-openings-v001-nearby-rho-09998/0001.npz` and `0001.json`
- `noise-openings-v001-nearby-rho-098/0001.npz` and `0001.json`
- `noise-openings-v001-fresh-seed-918274/0001.npz` and `0001.json`

These tags are exclusive to this probe. The recorder refuses a collision with different tensors. Preserve original generated PNGs and executed graphs alongside the noise archive. The runner deliberately does not perform remote tensor downloads or install the node.

Point `--noise-root` at the local directory immediately containing those four tag directories:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --frozen --no-sync --with numpy --with pillow --with opencv-python-headless python projects/modern-model-study/experiments/noise_openings.py verify --noise-root /absolute/path/to/local/deforum-noise-study
```

Verification is local-only. It checks all five requested/executed/history graphs, successful distinct prompt IDs, original/output hashes and dimensions, exact native/advanced PNG parity, actual recorded tensor hashes and metadata, zero input latents of the expected shape, finite near-unit noise statistics, both correlated mixtures against the shared actual baseline/innovation, and measured correlation/RMS displacement. It writes `verification.json` under the output root. It verifies the configured eight-step scheduler graph, not a separately exported numerical sigma trace or aesthetic quality. Inspect the resulting paintings and roof/shading crops before drawing a perceptual conclusion.

## Local validation completed

Prepared all five graphs and checked empty-latent initialization, identical stationary text and one output per job. A temporary fake-transport exercise passed: missing prerequisites block submissions, five jobs total, completed resume makes no remote calls, interruption before receipt writing reuses the existing run, a pixel parity failure blocks variants, synthetic actual-noise recurrence verifies, and corrupted tensor data fails its checksum. Temporary fixtures were removed. This is local code evidence, not actual ComfyUI execution or model parity.

## Exact files added by this code assignment

- `noise_openings.py`
- `noise-openings.md`
- `noise-openings-configs/native-euler-simple8.json`
- `noise-openings-configs/native-euler-simple8.workflow.json`
- `noise-openings-configs/advanced-same-noise.json`
- `noise-openings-configs/advanced-same-noise.workflow.json`
- `noise-openings-configs/nearby-rho-09998.json`
- `noise-openings-configs/nearby-rho-09998.workflow.json`
- `noise-openings-configs/nearby-rho-098.json`
- `noise-openings-configs/nearby-rho-098.workflow.json`
- `noise-openings-configs/fresh-seed-918274.json`
- `noise-openings-configs/fresh-seed-918274.workflow.json`

All paths in this inventory are relative to `apps/deforum/projects/modern-model-study/experiments/`. No main runner, shared helper, dependency manifest or earlier research note was edited during this code assignment.
