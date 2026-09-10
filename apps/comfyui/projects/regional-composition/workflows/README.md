# Workflows

The subsequent [two-stage experiment](../experiments/refinement.md) adds a whole-image refinement pass to regional generation: [editable graph](regional-global-refinement-sdxl.json), [API graph](regional-global-refinement-sdxl.api.json). These are exact executed exports from `20260910T102022890750Z-refinement-refine-s21001-2048-d0.60`, using bislerp latent enlargement to 2048 and global refinement at denoise 0.60. The graph includes diagnostic saves and retains fixed seeds and original output prefixes. It has no third generation/upscale stage and requires no custom nodes. The frontend-open verification below refers to the three earlier baseline graphs.

These are exact copies of the executed seed-21001 graphs using feathered mask conditioning and background strength 0.25. They use SDXL base 1.0 and built-in ComfyUI nodes. See the [results](../experiments/results.md) for quality limitations and the [upstream reference](../references/README.md) for the original composition mechanism.

| Method | Editable ComfyUI graph | API graph | Source run |
|---|---|---|---|
| Regional prompting | [regional-sdxl.json](regional-sdxl.json) | [API](regional-sdxl.api.json) | `20260910T080602645918Z-regional-seed21001` |
| Noisy composition | [noisy-sdxl.json](noisy-sdxl.json) | [API](noisy-sdxl.api.json) | `20260910T080619226077Z-noisy-seed21001` |
| Incremental painting | [layered-sdxl.json](layered-sdxl.json) | [API](layered-sdxl.api.json) | `20260910T080700770230Z-layered-seed21001` |

Open the editable JSON in ComfyUI, with `sd_xl_base_1.0.safetensors` installed. All three opened in the deployed frontend without missing-node/model dialogs. API execution was verified separately; opening a UI graph is not a second render. Outputs also embed the editable workflow in PNG metadata.

Original output prefixes and fixed seeds are preserved. Change output prefixes for a new session. Region dimensions, mask placement, text, conditioning strength and sampler settings are editable in the graph. The runner generates and validates these graphs against the live node schemas:

```sh
uv run --script apps/comfyui/projects/regional-composition/experiments/run_baseline.py run \
  --deployment PATH_TO_ACTIVE_DEPLOYMENT_JSON \
  --variant regional --conditioning mask --background-strength 0.25
```

Use `noisy` or `layered` for the other methods, and `--seed-offset 100` for the second seed set. Defaults retain the original area-conditioned control, so include both conditioning flags to reproduce the final recipe. The closed Sweden receipt cannot be reused. An active receipt needs `pod_id`, `base_url`, `remote_output`, `ssh_identity`, `ssh_host` and `ssh_port`; private infrastructure receipts stay in ignored `apps/comfyui/work/`.

If collection is interrupted after submission, use `collect --deployment ... --folder EXISTING_RUN` to collect the same prompt ID. Do not blindly resubmit an ambiguous request.
