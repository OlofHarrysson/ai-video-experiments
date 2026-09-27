# Eight-image depth placement result

2026-09-27. **The tested recipe did not provide useful position or size control.** All eight outputs completed and were preserved, but the six depth-guided watermelons remain large and near the middle of the canvas instead of following the three sphere locations. Do not extend this recipe into animation yet.

![Guides above both matched seeds](exports/v001/comparison.jpg)

## What was tested

The [brief](README.md) and [runner](run.py) define three synthetic sphere inverse-depth maps, two seeds and two unguided baselines. Full eight-step generation uses Krea 2 Turbo FP8, its existing Qwen3VL encoder and Qwen Image VAE, Euler/simple and CFG 1. Guided samples add the pinned community depth adapter at strength 1 and use the custom nodes' grayscale, per-image-minmax normalization without inversion. No previous painting or reference image initializes generation. Prompt and sampling parameters stay fixed across all positions.

The guides are 1024×1024, centre y=512, radius 180, and centre x=256/512/768. They encode sphere surface distance, not light shading or a binary edit mask. Uploaded guide hashes matched local originals.

## Observations

- Every output contains one recognizable whole watermelon, with a coherent painterly surface and dark studio background.
- Both baselines choose a large centrally composed fruit.
- All six guided images retain broadly that composition. Fruit diameter is visually about twice the guide's 360 pixels. Moving the guide left to right does not move the fruit correspondingly.
- Guided outputs differ from the baseline and from one another in stripes, surface details and small contour/position changes. They are not duplicate cached image files, but variation alone does not establish useful control.
- The pink circles in the overlays mark the requested silhouette, making the placement and size mismatch explicit. All eight originals were screened through the comparison sheet; the first baseline, first left and first centre images were additionally inspected at full resolution.

[Seed 21001 target overlays](exports/v001/overlay-21001.jpg) · [Seed 21101 target overlays](exports/v001/overlay-21101.jpg)

These findings apply to this synthetic guide, FP8 base, adapter and ComfyUI recipe. They do not establish that Krea depth control generally fails, nor that an edge-conditioned model would fail. The adapter author's photo/render examples are not a reproduction of this experiment.

## Wiring and evidence limits

The adapter's model file matched its published SHA256. The three custom node classes loaded in the existing ComfyUI 0.34.0 runtime. Saved API graphs include guide loading, VAE control encoding, adapter loading and control application before sampling. Logs report 224 attached model patches on guided jobs; all jobs completed without a node execution error. The pinned model's source exposes the diffusion-model wrapper and `first` projection used by this integration.

This is execution and source evidence, not proof that the control contribution has the intended strength inside every denoising step. No internal activation instrumentation, official-example reproduction, synthetic-guide comparison or sampling sweep was performed. Compatibility versus guide distribution versus recipe remains unresolved.

Recommended follow-up: before changing artistic prompts or building animation, reproduce one adapter-author example as a positive control. A subsequent geometric-control test can then distinguish integration failure from poor handling of the synthetic sphere. An outline-conditioned model is a separate alternative requiring a new agreed comparison.

## Runtime, cost and preservation

| Output | Recorded job time |
| --- | ---: |
| Seed 21001 baseline, including cold model loading | 83.508 s |
| Seed 21001 left / centre / right | 10.729 / 7.064 / 7.046 s |
| Seed 21101 warm baseline | 6.321 s |
| Seed 21101 left / centre / right | 9.392 / 7.125 / 7.118 s |

Owned RTX 4090 lifetime was approximately 13.65 minutes at $0.74/hour: **$0.1684 estimated compute**, excluding storage. The live billing query had not posted records for this Pod; zero returned records are not a zero-cost invoice. Warm guided execution was 7–11 seconds per image. These timings do not include all client transfer and session preparation overhead and should not be generalized to the three-step animation loop.

All eight generated images fully decoded at 1024×1024 and matched their remote SHA256 hashes. The run also preserves exact API graphs, histories, guide originals, silhouette masks, model metadata/hashes, pinned upstream custom-node source, runtime information and logs. The queue was empty before cleanup. Eleven verified input/output duplicates and two temporary integration symlinks were removed from shared storage. The owned Pod was deleted, a live listing returned no Pods, and the retained 50 GB `deforum-models` volume remains.

Local evidence: ignored `runs/v001/`; presentation artifacts: ignored `exports/v001/`. [Execution summary](execution-summary.json). No animation, Remotion project or recurrent pipeline change was made.

## Reproduce the local comparison

From the repository root:

```sh
uv run --script apps/comfyui/projects/watermelon-depth/run.py review \
  --folder apps/comfyui/projects/watermelon-depth/runs/v001
```

For a new inference session, use a new run directory with `prepare`, then `run --deployment PATH` with an explicitly active receipt and the verified adapter installed. Preserve existing run folders. The closed deployment is not reusable.
