# Serverless rendering

Research date: 2026-09-06. Status: proposed; no endpoint deployed or serverless render verified. The next continuation and depth-camera experiments remain pending.

## Recommendation

Use a queue-based RunPod Serverless endpoint for clip generation. Submit one complete ComfyUI graph per clip; run the camera-warp/image-diffusion feedback loop within that job. Keep project authoring, source selection, cuts and downloaded archives on the Mac. This moves worker shutdown to RunPod instead of relying on the Mac staying awake to stop a Pod.

Start with these endpoint settings:

| Setting | Proposed value | Purpose |
| --- | --- | --- |
| Active/minimum workers | 0 | Allow GPU compute to scale to zero |
| Maximum workers | 1 | Bound simultaneous GPU use |
| GPUs per worker | 1 | SDXL fits the existing 24 GB baseline |
| Idle timeout | 5 seconds | Release idle compute after a clip |
| Execution timeout | 600 seconds | Bound a short clip job; review before longer jobs |
| FlashBoot | Enabled | Reduce startup overhead when available |

These settings bound concurrency and job duration, not total account spend. Startup, model loading, execution and the idle timeout are billed until the worker fully stops. Persistent network volumes are billed separately even at zero workers. See [endpoint settings](https://docs.runpod.io/serverless/endpoints/endpoint-configurations) and [billing](https://docs.runpod.io/serverless/pricing).

## Existing implementation to reuse

RunPod maintains [worker-comfyui](https://github.com/runpod-workers/worker-comfyui), which accepts a ComfyUI API workflow and optional base64 input images. Extend its version-pinned image with the already-pinned Difforum nodes and the depth-estimation nodes needed for the next experiment. Keep those additions in this repository. The [customization guide](https://github.com/runpod-workers/worker-comfyui/blob/main/docs/customization.md) supports a derived Dockerfile; a network volume by itself does not install custom nodes.

The local runner must submit through RunPod's authenticated asynchronous `/run` API, save the job ID, and collect through `/status`. This is a transport change: the ComfyUI feedback graph remains the generation mechanism. There is no persistent interactive ComfyUI editor in this queue-worker arrangement.

## Preserve every generation

Do not rely on worker-local files or the job response as the permanent archive. Workers disappear, and asynchronous results have a limited retention period. Full-resolution PNG sequences can exceed the response payload limit. See the [operation reference](https://docs.runpod.io/serverless/endpoints/operation-reference) and [handler limits](https://docs.runpod.io/serverless/workers/handler-functions).

Resolve durable output storage before a multi-frame deployment: save every attempt under a unique job/attempt prefix before the worker stops, return a small manifest, and download the frames and receipts into the existing project run directory. Preserve failed/retried attempts as well. The upstream worker supports S3 image uploads; verify private authenticated retrieval and retention rather than treating a temporary URL as a backup. Storage credentials and retention policy are still to be selected.

## Cost and validation

Published 4090 Flex pricing is approximately $1.10/hour of worker lifetime; the endpoint documentation lists $0.00031/second (about $1.12/hour). The Pod catalog checked in this session quoted $0.74/hour before storage. These are different products and published figures are rounded; verify the endpoint's actual rate before provisioning. Sources: [August price update](https://www.runpod.io/blog/runpod-slashes-gpu-prices-more-power-less-cost-for-ai-builders), [endpoint GPU table](https://docs.runpod.io/serverless/endpoints/endpoint-configurations).

At these indicative rates, serverless GPU time is roughly 1.5 times the Pod rate, before startup and storage. It may cost less overall when human review leaves long gaps between renders. A cold short job can cost more than a warm Pod render. Measure cold startup, warm execution, worker shutdown and durable-output transfer separately; keep the original $50 budget and comparable-render cost boundary.

Implementation sequence:

1. Resolve the image build/registry path and durable output storage. The Docker CLI is installed locally, but its daemon was not running during this check.
2. Package pinned ComfyUI worker, nodes and models without per-job dependency installation.
3. Add the RunPod job transport while preserving the existing project/run receipts and archive behavior.
4. Verify a small real render, output recovery after worker shutdown, and scale-to-zero without a Mac-side timer.
5. Run the selected-frame continuation and depth-camera experiments; compare their full costs against the baseline.

No paid resource was created during this investigation. The previous Pod had already been deleted.
