#!/usr/bin/env bash
# Run over SSH on the official RunPod ComfyUI CUDA 12.8 image.
set -euo pipefail

COMFY_DIR=/workspace/runpod-slim/ComfyUI
DIFFORUM_COMMIT=1d750efd3c1d1dda792b8ef6c14b06a14a69f879
MODEL_REVISION=462165984030d82259a11f4367a4eed129e94a7b
MODEL_SHA256=31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b
MODEL_NAME=sd_xl_base_1.0.safetensors
PYTHON="$COMFY_DIR/.venv-cu128/bin/python"
NODE_DIR="$COMFY_DIR/custom_nodes/difforum"
MODEL_PATH="$COMFY_DIR/models/checkpoints/$MODEL_NAME"

test -x "$PYTHON"
if [[ ! -d "$NODE_DIR" ]]; then
    git clone https://github.com/chillithebillis/Difforum.git "$NODE_DIR"
    git -C "$NODE_DIR" checkout --detach "$DIFFORUM_COMMIT"
fi
test "$(git -C "$NODE_DIR" rev-parse HEAD)" = "$DIFFORUM_COMMIT"
"$PYTHON" -m pip install -r "$NODE_DIR/requirements.txt"

if [[ ! -f "$MODEL_PATH" ]]; then
    curl --fail --location --retry 2 --output "$MODEL_PATH.part" \
        "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/$MODEL_REVISION/$MODEL_NAME"
    printf '%s  %s\n' "$MODEL_SHA256" "$MODEL_PATH.part" | sha256sum --check
    mv "$MODEL_PATH.part" "$MODEL_PATH"
fi
printf '%s  %s\n' "$MODEL_SHA256" "$MODEL_PATH" | sha256sum --check
"$PYTHON" -c 'import torch, numpy; print("CUDA:", torch.cuda.is_available(), "GPU:", torch.cuda.get_device_name())'
echo 'Pinned Difforum and SDXL are installed. Check /object_info; restart this Pod if the new nodes are not registered.'
