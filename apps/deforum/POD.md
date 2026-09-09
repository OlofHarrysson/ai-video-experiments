# Modern-model ComfyUI Pods

Use a short-lived ComfyUI Pod with the retained **deforum-models** 50 GB standard network volume in **EU-RO-1**. The volume is explicitly authorized to persist between sessions; delete finished experiment Pods, **keep this volume**. Storage is approximately **$3.50/month** with compute off. Private volume/deployment receipts live in `work/persistent-model-volume/`.

## Start a session

1. Inspect existing Pods and resolve the volume by name; read its ID and data center from RunPod. Check current RTX 4090 availability and price in that data center.
2. Create one Secure Cloud RTX 4090 Pod in the volume's data center with the volume mounted at `/workspace`, 150 GB container disk, `8188/http` and `22/tcp`, and `PUBLIC_KEY` set to the existing SSH public key. Use the tested official image:

   `runpod/comfyui:cuda12.8@sha256:498e3c4ac7ef5071214badb1681d82ab3a8f922b1055742ae692fa02cd3b59ff`

3. Wait for SSH and the template’s ComfyUI startup. The retained installation starts automatically as ComfyUI 0.34.0; confirm `/system_stats`. The preparation scripts and model manifest already live in `/workspace/modern-model-session/`. Copy updated scripts only when an intentional repository change requires it.
4. On the Pod, run:

   ```bash
   python3 /workspace/modern-model-session/prepare_pod_models.py --krea-only --verify-only
   ```

   This verifies all three cached Krea files and links them into ComfyUI. The template’s existing Python environment is retained on the volume; Torch/CUDA remain inherited from the image. A missing or corrupt file fails explicitly; it does not silently download another copy. For initial population or an intentionally added model, omit `--verify-only`. Keep the full manifest's pinned revisions and SHA256 checks.

5. Verify `/system_stats`, then submit a real graph. Use the existing `pod_client.py` and the experiment's own deployment receipt. Prompt and motion changes need no infrastructure rebuild. Keep an experiment's feedback loop on the Pod when its existing runner supports it to avoid per-frame Mac transfers; download results promptly.

For a **new empty volume**, copy `setup_modern_pod.py`, `prepare_pod_models.py` and `serverless/modern-models.json` into `/workspace/modern-model-session/`. Run `setup_modern_pod.py` once after the template has started, and run `prepare_pod_models.py --krea-only` to populate weights. These two independent preparations may run concurrently. The setup script pins ComfyUI to the established 0.34.0 commit and installs its small dependency update into the template’s existing environment; it is not needed at each Pod creation.


The first fresh container may still need a multi-minute image pull. Mounted weights remove repeated Hugging Face downloads, not container setup or loading models into GPU memory. Do not mix a new image/CUDA stack into the persisted runtime without checking compatibility.

S3 access is verified at `https://s3api-eu-ro-1.runpod.io/` (region `EU-RO-1`, bucket = the volume ID). This permits reading receipts and recovering archived outputs even when GPU capacity is unavailable. Resolve credentials using the existing ignored `.env`; never copy credentials into scripts or documentation.

## End a session

Download and hash-check every generated output and experiment receipt. Confirm an empty queue, then delete only the experiment's owned Pod. Verify deletion and **retain deforum-models**. Model files and runtime remain on the volume; source media and final renders also remain local under the project. Clear only verified, owned scratch/output files when space is needed; preserve the reusable models/runtime.

## Trial

[Persistent-volume experiment](projects/modern-model-study/experiments/persistent-model-volume.md) owns the startup/reuse measurements. This workflow uses the official container and existing graph/transport tools; it does not introduce a custom image build or another serving layer.
