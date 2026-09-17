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

5. Preflight the experiment runner's imports, then verify `/system_stats` and submit a real graph. The migrated early-settle runner uses `deforum_lab.infrastructure.pod.PodClient` with the experiment's explicit deployment receipt; historical runners still use `pod_client.py`. Prompt and motion changes need no infrastructure rebuild. Keep an experiment's feedback loop on the Pod when its existing runner supports it to avoid per-frame Mac transfers; download results promptly.

The migrated runner is verified on a short-lived Pod: [transition-frequency](projects/modern-model-study/experiments/transition-frequency/README.md) completed 28 paintings on 2026-09-14 with a separate uv environment. Transfer `pyproject.toml`, `uv.lock`, `README.md`, `src/deforum_lab/`, the selected experiment, and its required configuration/source paintings into an owned session app directory. Run `uv sync --locked --no-dev --python python3` there, then use `uv run --locked --no-dev` for imports, the experiment's `--help`, and execution. This installs the runner dependencies without modifying ComfyUI's Torch/CUDA environment. The selected lock preserves NumPy, Pillow and OpenCV versions; verify the actual runtime before inference.

Keep ComfyUI's diagnostic nodes and the separate local RIFE environment on their established paths. Remote generation needs only its selected input assets; full historical comparisons may require a larger local archive and can run after download. Exclude `.venv`, `.git` and `__pycache__` from result archives.

For a **new empty volume**, copy `setup_modern_pod.py`, `prepare_pod_models.py` and `serverless/modern-models.json` into `/workspace/modern-model-session/`. Run `setup_modern_pod.py` once after the template has started, and run `prepare_pod_models.py --krea-only` to populate weights. These two independent preparations may run concurrently. The setup script pins ComfyUI to the established 0.34.0 commit and installs its small dependency update into the template’s existing environment; it is not needed at each Pod creation.


The first fresh container may still need a multi-minute image pull. Mounted weights remove repeated Hugging Face downloads, not container setup or loading models into GPU memory. Do not mix a new image/CUDA stack into the persisted runtime without checking compatibility.

S3 access is verified at `https://s3api-eu-ro-1.runpod.io/` (region `EU-RO-1`, bucket = the volume ID). This permits reading receipts and recovering archived outputs even when GPU capacity is unavailable. Resolve credentials using the existing ignored `.env`; never copy credentials into scripts or documentation.

## Working storage

Keep cumulative generation work in an owned directory on the adequately sized container disk, and keep the reusable model cache on the network volume. Download and hash-check completed passages promptly; container files disappear with the Pod. ComfyUI inputs and outputs may still consume the network-volume quota and require verified, session-owned duplicate cleanup.

During The Cartographer’s Dream, a 50 GB network-volume quota caused `Disk quota exceeded` while `df` reported hundreds of terabytes free for the shared backing filesystem. Aggregate `df` capacity did not describe the account quota. The quiescent owned worktree was copied to the 150 GB container disk, every file and symlink was verified, and the original path was retained as a symlink before generation resumed. The project's [production notebook](projects/cartographers-dream/experiments/baseline.md#storage-recovery) records this recovery.

## End a session

Download and hash-check every generated output and experiment receipt. Confirm an empty queue, then delete only the experiment's owned Pod. Verify deletion and **retain deforum-models**. Model files and runtime remain on the volume; source media and final renders also remain local under the project. Clear only verified, owned scratch/output files when space is needed; preserve the reusable models/runtime.

Create Mac transfer archives with `COPYFILE_DISABLE=1 tar --no-xattrs` to omit AppleDouble metadata sidecars. When extracting onto the network volume, use `tar --no-same-owner` so extraction does not attempt unsupported ownership changes. Inspect the template's actual startup process before restarting ComfyUI; this image does not provide `supervisorctl`.

## Trial

[Persistent-volume experiment](projects/modern-model-study/experiments/persistent-model-volume.md) owns the startup/reuse measurements. This workflow uses the official container and existing graph/transport tools; it does not introduce a custom image build or another serving layer.
