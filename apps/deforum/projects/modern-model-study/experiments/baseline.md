# Klein and Krea audition

## Current outcome

The approved Pod retry completed both models: [results and videos](pod-results.md). All 32 generated images are local and the Pod is deleted. The following failed-setup notes describe the preceding serverless attempt.

## Serverless outcome — 2026-09-08

**Blocked before inference. No opening images, repaint probes or videos were generated.** The workflows and model-specific prompts are prepared, but their GPU behavior and visual quality remain untested. The endpoint is paused at min/max 0, zero workers and Pods were verified, and the owned volume was detached and deleted after verifying the output prefix contained zero objects. Both request receipts and preparation diagnostics remain local in ignored `runs/` and `work/modern-model-session/`.

The first accepted opening request expired while queued; a replacement request was explicitly cancelled while still queued. Do not blindly resubmit either receipt. The active deployment file was moved to the closed session receipts, preventing reuse of the deleted volume.

Olof approved resuming on a short-lived ComfyUI Pod, and authorizes this deployment choice for future experiments when convenient. The Pod attempt below keeps these same model recipes. Keep the same-model opening/feedback requirement and the existing spatial controls. Avoid another container rebuild until the transfer bottleneck is understood.

## Question

Can either model preserve a locally warped drawing while adding interesting detail across repeated feedback? Does an explicit next-frame edit instruction help, or cause unwanted reinterpretation?

## Approach

Olof authorized both candidates, model-specific prompts, and same-model opening/feedback. Keep spatial motion independent of the generator. Do not transfer SDXL LoRAs, CFG, negative prompts or denoise values as universal defaults.

1. Generate two openings per model and inspect before choosing one.
2. Warp the selected opening and inspect a single repaint. Klein uses native reference-latent editing. Krea starts with conventional partial img2img and a full scene description; one instruction-worded probe tests a hypothesis, not documented native editing support.
3. Inspect eight feedback anchors, then extend viable runs to the familiar three-second, 12 fps, cadence-3 twist. Preserve motion-only previews and every generation.
4. Review overview frames and an every-frame interval. Surface one clip per model with a short explanation. No RIFE, depth, optical flow, additional pixel noise or regional masks.

## Source recipes

- [BFL prompt construction](https://docs.bfl.ai/guides/prompting_unified_building), [single-reference editing](https://docs.bfl.ai/guides/prompting_editing_single_reference), and [technical notes](https://docs.bfl.ai/guides/prompting_unified_technical): describe concrete visual attributes; specify what changes and what remains. Avoid generic quality filler.
- [Krea prompting](https://github.com/krea-ai/krea-2/blob/main/docs/prompting.md): use natural-language descriptions with concrete details. Automated prompt enhancement stays disabled so the saved prompt is the actual prompt.
- ComfyUI official templates at `7c25a3c586484601f94b7e8f8b14c23b2c95a096`: `image_flux2_klein_image_edit_4b_distilled.json` and `image_krea2_turbo_t2i.json`.
- Assets/revisions/checksums: [worker manifest](../../../serverless/modern-models.json). Klein uses verified BF16 distilled weights instead of the template's FP8 filename; this may affect memory and speed. Krea uses FP8 scaled weights.

Klein: four steps, Euler, Flux2 scheduler, CFG 1, reference conditioning for edits. Krea: eight steps, Euler/simple, CFG 1; full denoise for opening, partial denoise as an experimental feedback adaptation. Dimensions 1024×576 for both. These are model-and-workflow auditions; different editing mechanisms prevent an isolated checkpoint ranking.

Klein's template rescales the reference to approximately one megapixel. Here input and output stay at the existing 1024×576 dimensions so the spatial maps and saved pixels retain their geometry. This is an explicit template adaptation; the model receives the whole warped frame as its reference. Krea's fractional-denoise schedule is also an adaptation, because its source recipe demonstrates full-denoise generation, not this recurrent img2img use.

## Execution

Runnable from `apps/deforum` with `uv run --env-file .env --with pillow==12.1.0 --with opencv-python-headless==4.12.0.88 python projects/modern-model-study/experiments/audition.py` followed by a stage and model:

- `openings klein` / `openings krea`: concise and detailed descriptions, matched seed within each model.
- `select MODEL --index 0`: preserve the selected opening and motion-only preview.
- `probe klein --instruction`: native edit of a deliberately visible mid-twist input.
- `probe krea` / `probe krea --instruction`: matched scene-description versus imperative-prompt partial repaint.
- `feedback klein --instruction --until 24` and `feedback krea --until 24`: eight anchors; increase to `--until 36` after inspection to complete three seconds.

The active runner uses `pod_client.py` with the session URL in ignored `work/modern-pod-session/deployment.json`; the closed receipt must not be reused after Pod deletion. It reconnects to an existing accepted Pod prompt and refuses changed graphs or source images. An uncertain submission requires inspection; it is never silently retried. [Four API graphs](workflows/) make the minimal model recipes inspectable. Actual runs preserve their exact selected prompt and graph separately.

Prepared 2026-09-08. New models require a worker image build and cold download; settings/prompt changes thereafter reuse that image. Original SDXL container recipe is preserved as `serverless/Dockerfile.sdxl`. Actual runtime evidence and results will be added after execution.

The first worker build (`addbb3c96`) downloaded and checksum-verified all six assets and passed ComfyUI's CPU startup test, but hit RunPod's **1800-second build limit** during OCI tarball export. No inference job was submitted. The model assets total 34.77 GB. The second packaging attempt kept the container small and downloaded weights to a temporary 50 GB network volume before starting ComfyUI. That attempt was superseded by the local-disk recipe below. Output archives use the separate `deforum/projects/` prefix.

The lean build `3ce60df86` succeeded. The first host spent over 20 minutes pulling its base container; another host started in under a minute. Direct `wget` into the network volume then slowed below 1 MB/s. An 8 MiB S3 write probe took 27.35 seconds, although that cross-region API timing does not isolate POSIX volume throughput. Preparation was stopped before any inference. `ede338e16` changes downloads to worker-local disk through Hugging Face’s existing loader, retains checksum verification, and keeps only outputs on network storage. This tests a suspected I/O bottleneck; it is not yet a proven diagnosis. The existing 50 GB volume is retained for this session because volumes cannot be shrunk; a fresh output-only session needs only 10 GB.

The `ede338e16` build succeeded, including Hugging Face/Xet imports and the ComfyUI CPU startup check. Two worker hosts started that image, but neither reported completing its first 7.75 GB weight file: one was observed for about 14 minutes and the other for six minutes. No byte-level progress was exposed by this SDK download path, so these logs establish no completed transfer, not proof of zero transferred bytes or a confirmed cause. Both were stopped at 17:37 UTC. The output-prefix verification found zero objects. All model-cache partials were reproducible public weights and were deleted with owned storage. The final account refresh showed approximately $0.62 lower balance, $45.07 remaining and a current spend rate of $0/hour. Billing can settle later, so the balance difference is an observed session cost rather than a final invoice. Local runner imports, graph links and the saved Klein edit graph were rechecked after cleanup; no GPU test is implied.

## Pod attempt

Approved 2026-09-08. Official CUDA 12.8 ComfyUI template, one RTX 4090, direct API submission and immediate local collection through `pod_client.py`. The Pod boots ComfyUI 0.26.2 (`b7ac98aafe41c8c8593b9f21238dab58a90424c6`), torch 2.10.0+cu128; its live node catalog includes the required Klein and Krea types. This differs from the serverless runtime and is recorded per run. `prepare_pod_models.py` downloads pinned weights with progress and checksum verification. Existing cancelled serverless receipts are preserved; Pod attempts use distinct run names.

### Early Pod observations

Klein concise opening selected for the asymmetrical arch and flame detail. Matched mid-twist probes use the same source/seed. The instruction probe preserves the warped layout but places branches outside the flame despite an inside-only request. The scene-description probe also preserves layout, but pushes orange saturation. After eight instruction-feedback anchors, the arch/explorer remain recognizable and follow the twist; highlights and saturation accumulate, with softened fine texture. These are sampled-frame findings, not a playback verdict. Continue to 12 anchors to expose the progression in a short clip.

Krea detailed opening selected for its asymmetrical silhouette, porous arch and quieter palette. Its scene-description repaint at denoise 0.45 retains the major content but straightens the deliberately tilted explorer. The matched instruction prompt removes the explorer and converts the architecture toward flame/branch forms. Reject that instruction wording for this img2img recipe; it is not evidence of native edit support. Continue the scene-description branch at 0.45 for the short comparison.
