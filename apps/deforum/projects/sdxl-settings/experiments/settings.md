# Sampling effort and guidance

Plan written before rendering, 2026-09-06; findings appended after collection and image inspection. Status: COMPLETED. Parent owns endpoint lifecycle and final cleanup.

## Question and comparison

Can fewer steps preserve useful scene structure, and does lower CFG improve the balance between painterly atmosphere and crisp lantern/boardwalk detail?

| Saved frame | Variant | Steps | CFG | Comparison |
| --- | --- | ---: | ---: | --- |
| `frames/0000.png` | baseline | 28 | 6.5 | Current reference settings |
| `frames/0001.png` | fewer-steps | 20 | 6.5 | Change only steps; 28.6% fewer sampling steps |
| `frames/0002.png` | lower-guidance | 28 | 5.0 | Change only CFG; test softer guidance without changing step count |

These are hypotheses, not quality claims. Three outputs allow one independent change per comparison; they do not estimate step/CFG interactions or establish a general best setting across seeds. The 20-step Karras schedule is resampled, not a truncated 28-step trajectory.

Fixed: checkpoint `sd_xl_base_1.0.safetensors`, seed 143 independently supplied to each sampler, `dpmpp_2m`, `karras`, denoise 1.0, one empty 1024×576 latent, identical positive/negative conditioning and checkpoint VAE. Positive text is copied verbatim from `lantern-marsh/experiments/overscan.py`; negative text comes from the shared SDXL starter graph. Exact strings are frozen in the graph and settings manifest. Model revision/hash and worker pins are documented in the app README and serverless Dockerfile; actual runtime must come from this job's archived diagnostics.

Only existing standard ComfyUI nodes are used: CheckpointLoaderSimple, CLIPTextEncode, EmptyLatentImage, KSampler, VAEDecode, ImageBatch and SaveImage. Each sampler receives batch size one and the same seed, avoiding automatic per-batch noise variation. Two ImageBatch nodes append decoded baseline → fewer-steps → lower-guidance images; SaveImage node `11` writes that order. These stills have no feedback, camera warp, depth inference or postprocessing.

## Parent execution

From `/Users/olof/git/ai-video-experiments/apps/deforum/`:

```bash
uv run python projects/sdxl-settings/experiments/settings.py check
uv run --env-file .env python projects/sdxl-settings/experiments/settings.py submit
```

The second command submits **one job, three final PNGs, 76 total sampling steps** through `serverless_client.submit`. The settings manifest is embedded in `submission.json`, with the prepared graph SHA-256. Each attempt archives its executed graph, diagnostics and all images. Do not rerun `submit` to recover a timeout: collect the existing run instead:

```bash
uv run --env-file .env python experiment.py collect projects/sdxl-settings/runs/RUN_ID
```

The shared collector also creates a 0.375-second preview at eight source FPS. That is a transport artifact; compare the full-resolution PNGs individually. Worker archive filenames are rewritten, so identify variants by the recorded frame index, not the SaveImage prefix.

## Cost estimate before rendering

Planning assumption: 15–45 seconds warm execution for three full-denoise SDXL stills, including encoding and saving. At the repository's indicative 4090 Flex rate of $0.00031/second, this is about **$0.005–$0.014 GPU execution**, or roughly **$0.01–$0.03** allowing modest load/idle overhead. This is an unmeasured estimate using the rate in `docs/research/serverless-rendering.md`, not a live price quote. Parent must verify its current rate. Cold startup, storage, retries and existing session costs are separate; a 600-second execution alone would be $0.186 at that assumed rate. Target below $0.05 incremental warm-job cost, investigate before further attempts if it exceeds $0.10. No automatic additional experiments.

Lowering CFG leaves the number of steps unchanged and is not expected to materially reduce inference work. The 76-step batch has 9.5% fewer steps than three 28-step renders; that is not a measured wall-time saving. Single-job aggregate timing cannot isolate each variant's speed without node timings.

## Local verification and results

Prepared graph and metadata are checked locally for exact settings agreement. The local review also traces ImageBatch order and compares both frozen prompts against the parent recipe/shared starter. No remote node validation or GPU generation is claimed by these checks.

Submitted job `79f63e28-03a7-4e82-980e-d25e4a385818-e2`; preserved run `20260906T214908281394Z-settings-3f`. Final API status: COMPLETED. Prepared graph SHA-256: `e9e9c17d384b711c2bfa690b8a9e661d43f2dc7bb5a7c6abe9ac3f9577784943`.

All three PNGs are 1024×576. All six manifest-listed archive files passed size and SHA-256 verification; each collected PNG matches its corresponding node-11 original byte-for-byte. Cloud attempt: `f452a650010c4eeaab390ea4bcc0eeb7`. The worker runs with `--disable-metadata`; use the preserved graph, `submission.json` and `verified-images.json` for per-image provenance, rather than expecting embedded PNG settings.

Actual runtime from archived diagnostics: ComfyUI 0.34.0, Python 3.12.3, PyTorch 2.11.0+cu128, NVIDIA GeForce RTX 4090. No manifest or diagnostic error. Final status recorded **103.914 seconds queue delay and 6.859 seconds execution**. At the preflight's assumed $0.00031/second, that execution component is approximately **$0.0021**; it is not a billed total. Startup/idle/storage charges and final session accounting remain with the parent. Queue delay must not be counted as measured billable worker time. Execution was faster than the deliberately conservative 15–45-second estimate; no per-node timing was returned, so individual variant speed is unmeasured.

## Visual findings

Inspected each full saved PNG directly, in manifest order:

| Image | Observation |
| --- | --- |
| [28 steps / CFG 6.5](../runs/20260906T214908281394Z-settings-3f/frames/0000.png) | Crisp reeds, planks and bright amber pavilion windows; strong cyan-blue water and sky. The right boardwalk railing includes an extended diagonal rail, and a small dark floating shape appears near the middle-left sky. Foreground, marsh and distant hills separate clearly. |
| [20 steps / CFG 6.5](../runs/20260906T214908281394Z-settings-3f/frames/0001.png) | Reeds and planks remain detailed at this viewing size. Boardwalk rails and the pavilion base change visibly; the central path is more enclosed by rails, while the dark floating sky shape is absent. Strong cyan-blue water and bright windows remain. There is no obvious broad detail collapse from reducing steps in this one sample. |
| [28 steps / CFG 5.0](../runs/20260906T214908281394Z-settings-3f/frames/0002.png) | Water and sky look less intensely cyan, with gentler distant-hill contrast and a more atmospheric moon glow. More small warm reflections appear on the water. Foreground reeds remain distinct. The boardwalk rail remains irregular; lower CFG did not resolve structural or prompt-adherence issues. |

All three preserve the broad marsh/boardwalk/amber-versus-blue scene, but merge the requested hanging foreground lantern and distant domed observatory into a large lit pavilion on the left. The moon is round rather than crescent. Tiny lanterns along the boardwalk, luminous blue mushrooms and low violet mist are not clearly realized. Therefore these comparisons establish useful still-image setting variation, not faithful delivery of the planned scene hierarchy.

My preference for this painterly brief is **28 steps / CFG 5.0**, based on its calmer color balance. **20 steps / CFG 6.5 remains a viable lower-step candidate**; this sample does not justify paying for 28 steps solely to preserve visible detail. Treat both as local observations, not a general recipe decision. Olof's preference and any animation test remain separate. Before animation depends on a distant observatory and a close hanging lantern, a future scene reference should establish those objects explicitly. No additional generation was submitted.

Original image SHA-256s:

- `0000.png`: `cbd7598f4a6a3d88d9b3fdc0e8e3f01df40dbf2c76871821a9b3ad20f108c268`
- `0001.png`: `531abb269fac01ce902a47c1e65e4c5d5937926cff457527aafc9812e18641ec`
- `0002.png`: `96a9195cad703e0e4306b7c65c1beb27359ca6012e4c83aa59fa6c776500f1de`

The review covered the planned foreground lantern/reeds, boardwalk/observatory hierarchy, amber versus teal/indigo balance, retained detail and structural artifacts. Fixed seed did not preserve identical geometry across settings. These stills cannot establish animation flicker or temporal quality. All generations and local archives are retained; this agent made no endpoint/storage changes, shared-code edits, commits or pushes. Parent can include this completed run in final archive verification and resource cleanup after all other agents finish.
