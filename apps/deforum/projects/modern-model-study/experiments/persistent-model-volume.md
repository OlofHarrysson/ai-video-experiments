# Persistent model volume trial

Completed 2026-09-10 (Stockholm). The retained **deforum-models** volume is **50 GB standard storage in EU-RO-1**, approximately **$3.50/month**. A fresh Pod reused all three pinned Krea files and the ComfyUI runtime without model downloads or package installation. Use [the Pod workflow](../../../POD.md).

## Verified result

| Measurement | Initial EU preparation / RTX 4090 | Fresh Pod / L4 |
| --- | --- | --- |
| Model files | Three files, 18,638,004,998 bytes | Same files, all three SHA256 values matched |
| Model preparation | 140.819 s download + verification | 28.330 s verification; zero downloads |
| Runtime preparation | 381.693 s | Existing ComfyUI 0.34.0 environment started automatically; no setup script or pip install |
| Container start | About 41 s after creation | About 3 s after creation, then application startup |
| First graph | 78.561 s | 13.432 s |
| Warm graph | 1.896 s | 4.972 s |
| First / warm local request + archive wall time | 88.063 / 8.471 s | 22.552 / 13.041 s |

Model downloads and runtime preparation ran concurrently; do not add their elapsed times. Container-start timing comes from RunPod system logs and does not mean the application was already serving. The first EU runtime install waited on network-filesystem operations while unpacking documentation files. That installation was paid once and reused by the second Pod. Model-load and host-cache effects were not independently isolated, and the GPUs differ, so the graph times are observations, not an inference-speed comparison.

The fresh L4 ran `prepare_pod_models.py --krea-only --verify-only`; every receipt reported `downloaded: false`. It mounted the same network volume on a different host and used the template’s existing `.venv-cu128` automatically. It did not run `setup_modern_pod.py`. Both its first and warm images completed successfully.

Two Pods briefly shared the prepared volume for this verification. The 4090 was retained for Olof’s next authorized cadence experiment instead of being deleted between tests. This demonstrates reuse on an independently created Pod and shared mounted storage; it is not an all-compute-deleted/recreated benchmark. S3 reads/writes and model object sizes were independently verified without relying on a Pod API.

## Runtime and outputs

- Official image pinned to `runpod/comfyui:cuda12.8@sha256:498e3c4ac7ef5071214badb1681d82ab3a8f922b1055742ae692fa02cd3b59ff`.
- ComfyUI 0.34.0 commit `12d5279438bfefc058a269eae805ceab6047777f`; PyTorch 2.10.0+cu128. Torch/CUDA stay inherited from the image; the small dependency update lives in the template’s existing environment on the volume.
- Unchanged pinned Krea Turbo FP8, Qwen text encoder and Qwen VAE from `serverless/modern-models.json`. Only Krea assets were populated.
- Every graph preserves cathedral-image sampling initialization, uses the final interval of the eight-step simple/Euler schedule, and changes only the seed between its first and warm request. No motion or creative recipe changes.
- Six 1536×1024 output images are preserved under project `runs/*volume-trial-*`: two initial TX images, two EU 4090 images and two fresh L4 images. All were decoded and their hashes matched remote files. The four EU images were also retrieved and compared through S3.
- Private resource, runtime, archive and timing receipts live in `apps/deforum/work/persistent-model-volume/`. The test runner is [persistent_volume_trial.py](persistent_volume_trial.py).

## Placement correction

The first 50 GB volume was created in US-TX-3 after checking standard storage and low L40S stock. That Pod mounted it successfully and generated two images. Model download + verification took 280.910 s; runtime preparation took 120.371 s concurrently. The container pull/start took approximately 5.5 minutes. First/warm graph times were 14.607 / 2.067 s; local request/archive wall times were 31.556 / 17.932 s.

The runtime was then consolidated into the official template’s existing environment (82 s, recorded separately); the temporary duplicate environment was removed. After Pod deletion, two replacement L40S allocations failed and the region reported no available compatible GPU. TX-3 also lacks S3 access in the official availability table. The conventional S3 hostname failed DNS. No file-level replacement-Pod reuse was claimed for that region.

The final volume was therefore populated in EU-RO-1, which offered a successful 4090 allocation and verified S3 access. When a second 4090 was unavailable, an L4 completed the reuse test. The original TX-3 volume was deleted after the EU model files were checksum-verified and both TX outputs were safely local. Only the final 50 GB EU volume remains. Central record: AF-20260910-000823.

## Cleanup and handoff

The original TX Pod and the L4 verification Pod were deleted. The warm EU RTX 4090 was explicitly handed to the existing cadence experiment task, which acknowledged ownership of its compute lifecycle and final cleanup. That task must preserve this volume after deleting its Pod. The storage trial leaves no separate test GPU running.

Keep the setup simple: one retained model/runtime volume and short-lived Pods. No custom container build, cache service or second serving layer was added. Normal sessions only start the existing environment and verify cached files; initialization and dependency installation are for a new empty volume or an intentional runtime change. Region availability and first model loading remain separate sources of delay.

Sources: [RunPod network volumes](https://docs.runpod.io/storage/network-volumes), [S3-supported data centers](https://docs.runpod.io/storage/s3-api). Live docs and account reads were checked during the trial; capacity and rates can change.
