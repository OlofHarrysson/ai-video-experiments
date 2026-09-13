# One-repaint Krea reference screen

Completed 2026-09-13: three new single-repaint jobs and a reused baseline, all verified from local source/output hashes and recorded executed graphs/history. The screen stops after one repaint per arm.

## Result

The added reference has a visible local effect, but no clear preservation advantage over the current baseline. The encoder-only arm looks similar to baseline. The style adapter produces most of the reference arm's architectural restyling even without a reference; adding the image restores some vehicles that the adapter alone loses. Baseline already retains that traffic. We stopped this branch after the screen rather than extending it through fifteen repaints.

[View the paintings](../exports/reference-screen-v001/reference-comparison.jpg) and [detailed visual review](../exports/reference-screen-v001/assistant-review.md). This tests one image, one seed and a style-trained adapter through the native Comfy route. It does not rule out identity/editing adapters or demonstrate temporal behavior. The 457 MB adapter loaded successfully on the existing FP8/RTX4090 setup and was removed after verified local archiving.

## Recorded recipe

`continuity_controls.graph(config, 0)` is the exact control: Euler, seed **918273**, source city at `continuity-controls-v001/source/seed.png`, anchor 0006 at 0.25 seconds, CFG1, unchanged three sigma intervals. Every arm initializes from the same source through `VAEEncode`. C additionally references the same fixed opening through node **30**, as required by `pod_client.submit(reference=...)`.

| Arm | Conditioning | Adapter | Reference |
|---|---|---|---|
| A0 | Original CLIPTextEncode | None | None; reuse control run |
| A1 | Qwen Edit Plus | None | None |
| B | Qwen Edit Plus | Style LoRA 1.0 | None |
| C | Qwen Edit Plus | Style LoRA 1.0 | Common city opening |

Outputs: `projects/modern-model-study/exports/reference-screen-v001`. `prepare` freezes config, graphs, input hashes and runner hashes. Each successful arm archives the source/output paintings and a receipt hashing all transport artifacts, including the uploaded inputs, declared/executed graphs and server history. A0 reuse verifies the original control's receipt and copies its complete run archive. It does not infer a duplicate.

Commands below run from `apps/deforum` using the prepared runtime. Supply the **main-owned deployment path**, not a default session:

```sh
python projects/modern-model-study/experiments/reference_screen.py prepare
python projects/modern-model-study/experiments/reference_screen.py reuse-a0
python projects/modern-model-study/experiments/reference_screen.py render --arm A1 --deployment /absolute/path/to/deployment.json
python projects/modern-model-study/experiments/reference_screen.py render --arm B --deployment /absolute/path/to/deployment.json
python projects/modern-model-study/experiments/reference_screen.py render --arm C --deployment /absolute/path/to/deployment.json
python projects/modern-model-study/experiments/reference_screen.py verify --arm C
```

Run `reuse-a0` once the continuity Euler-0.6 anchor-0006 receipt and complete run archive exist in that filesystem. Other arms may be run independently. `verify --arm A0|A1|B|C` reads local files only. Repeating `render` reconnects to one accepted attempt; an uncertain/rejected attempt is an explicit error and never automatically resubmitted. Each render command submits at most one single-frame job.

No download or restart code is included. Main must make `krea2_style_reference.safetensors` readable to `LoraLoaderModelOnly` before B/C:

- [Pinned weight URL](https://huggingface.co/ostris/krea2_turbo_style_reference/resolve/269e1e4266b89bbabdc64a4f8cebfa0b7254078a/krea2_style_reference.safetensors)
- Bytes: **457111760**
- SHA-256: `f50df5a9e62e4be8aa926a63dd5bb1a64770c4004f763c1208007ae13daa82b8`

Review the four source-matched paintings before any further inference. A1−A0 isolates the encoder route; B−A1 isolates the no-reference adapter; C−B measures the complete reference-conditioning addition. Background persistence and detail retention remain separate judgments; the adapter was trained for style transfer.

Local validation: graph parity against the current control, unchanged source/seed/sampler wiring across all four arms, node30 reference routing, synthetic accepted archive verification, and rejection of a changed executed seed. No inference was performed. For local execution the repository runtime lacks NumPy; the existing experiment imports work with `uv run --no-project --with numpy --with pillow --with opencv-python python` in place of `python`, without editing project dependencies.

2026-09-13 patch: `render` now creates `OUT/runs` before calling `pod_client.submit`, which creates its run directory without creating parents. The first real C attempt failed before submission; main created the remote parent and restarted C without duplicating a render. The earlier mocked transport created parents itself and missed this precondition. Existing manifests and A0 receipts remain unchanged: their runner hash identifies the prepared original, whose remote code is preserved in the archive. A focused offline check now requires the parent to exist at transport entry.
