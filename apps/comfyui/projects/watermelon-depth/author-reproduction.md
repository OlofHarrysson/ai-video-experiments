# Adapter-author example reproduction

2026-09-27. **The author's dog-to-lion example runs successfully and broadly retains the composition, but does not preserve the exact head pose.** This is a useful positive control for the public pipeline, not validation of our ComfyUI integration or synthetic sphere placement.

![Input, extracted depth, generated output](exports/author-v001/comparison.jpg)

## Recipe and provenance

- Original input and prompt from the author's [Hugging Face Space](https://huggingface.co/spaces/Patil/krea-2-depth-controlnet), revision `bf7716320a5b9864f06658dcbc494e098d8b4fc1`: `examples/dog.jpg`, “a majestic lion, golden hour, photorealistic”.
- Submitted to that Space's `/generate` API: eight steps, adapter strength 1, seed 0, randomize seed false. Its source selects Krea 2 Turbo, CFG 0 and timestep shift 1.15. Returned seed: 0. Output and depth: 832×1216.
- Client elapsed time: 19.02 seconds, including service and transfer overhead; not isolated GPU inference time.
- This reproduces an author-provided example recipe. The demo normally randomizes seed, and its VAE encoding samples without a global seed. No claim of pixel-identical reproduction of a published result.
- Author standalone source was preserved at GitHub commit `909682ae0bdd9eb87c8258894c0003224db00d0b`. The hosted source/configuration was inspected; server internals and resolved live model hashes were not independently verified.

## Screening

The input dog occupies the left/lower frame, with its head near the centre and two visible legs. The extracted depth represents that geometry. The output is a lion-like animal in the same broad area, with a similar cropped body and leg arrangement. However, its head faces right and tilts upwards rather than facing the camera and downwards. Its outline is not a close match around the head. Some striped markings also make the animal less naturalistic than the prompt suggests.

Judgment: encouraging evidence for broad composition adherence, insufficient evidence for precise object placement and pose through an animation. This single sample has no unguided baseline, so visual resemblance alone does not measure the adapter's causal contribution. The earlier watermelon failure remains unresolved.

## Execution change and cost

An owned A100 80 GB Pod was provisioned at $1.59/hour to run the unmodified author pipeline with full precision weights. Dependency installation succeeded, but the official full Krea Turbo checkpoint returned a gated-repository HTTP 401. No Hugging Face credential was available locally. No image was generated on this Pod.

The idle Pod was deleted after about four minutes, approximately **$0.11 compute**, excluding container storage; this is an estimate, not a posted invoice. A live listing confirmed no Pods remained. The existing 50 GB `deforum-models` volume was retained and was not mounted or changed during this attempt. The successful image came from the author's public hosted demo; no Fal or additional RunPod generation charge was incurred for it.

## Integration lead, not a diagnosis

Source inspection found that the ComfyUI plugin's `Krea2ControlInputProjection` path retains the base image projection and adds only the adapter's control-half projection. The author's implementation loads the full trained expanded projection, including its image half and bias. The training helper describes this projection as fully trained. This is a concrete implementation difference to investigate, but the checkpoint tensors have not been compared and no corrected-plugin experiment has been run. Quantization, preprocessing, sampling and other differences also remain.

The next useful controlled comparison is this same dog input/depth and prompt through our ComfyUI recipe. Establish that bridge before returning to the synthetic sphere or building Remotion animation.

## Preserved evidence

Ignored `runs/author-v001/` contains original returned WebP files, explicitly converted PNGs, aligned input crop, SHA256 receipts, API parameters/results, hosted runner, preserved upstream source, prepared standalone runner, and installation/download failure logs. `references/assets/author/` retains the original source image and published comparison assets. `exports/author-v001/comparison.jpg` is the screened presentation artifact. The original WebP bytes are preserved; the PNG files are actual PNG conversions.
