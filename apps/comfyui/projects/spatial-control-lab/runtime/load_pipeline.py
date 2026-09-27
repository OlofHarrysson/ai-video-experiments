"""Qwen-Image-2.1-Fun-Controlnet-Union — structural control + inpainting for Qwen-Image 2.1 on ZeroGPU.

Inference follows VideoX-Fun's `examples/qwenimage21_fun/predict_t2i_control.py` /
`predict_i2i_inpaint.py` 1:1 (same pipeline code, vendored under `qwen21_fun/`): the control branch
checkpoint is loaded with strict=False-equivalent semantics on top of the base Qwen-Image-2.1
transformer, inputs are resized to the canvas the same way `get_image_latent` does, 40 steps,
guidance 1.0 (CFG-distilled), control_context_scale 1.0.
"""

import os

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")



import glob  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import time  # noqa: E402

import cv2  # noqa: E402

import numpy as np  # noqa: E402
import torch  # noqa: E402
from accelerate import init_empty_weights  # noqa: E402
from diffusers import FlowMatchEulerDiscreteScheduler  # noqa: E402
from huggingface_hub import hf_hub_download, snapshot_download  # noqa: E402
from PIL import Image  # noqa: E402
from safetensors.torch import load_file  # noqa: E402
from transformers import Qwen3VLForConditionalGeneration, Qwen3VLProcessor  # noqa: E402

from qwen21_fun import (  # noqa: E402
    AutoencoderKLQwenImage21,
    QwenImage21ControlPipeline,
    QwenImage21ControlTransformer2DModel,
)

BASE_ID = "Qwen/Qwen-Image-2.1"
CONTROL_ID = "alibaba-pai/Qwen-Image-2.1-Fun-Controlnet-Union"
CONTROL_FILE = "Qwen-Image-2.1-Fun-Controlnet-Union.safetensors"
DTYPE = torch.bfloat16
MAX_SEED = 2**31 - 1
EXAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")

# --------------------------------------------------------------------------------------
# Model loading (module scope, eager .to("cuda") — ZeroGPU streams it to the GPU per call)
# --------------------------------------------------------------------------------------

print("[load] downloading weights …", flush=True)
base_dir = snapshot_download(
    BASE_ID, revision="790c92633540aa0cb11d9abf19eb46d861714758",
    allow_patterns=["transformer/*", "text_encoder/*", "vae/*", "processor/*", "scheduler/*", "model_index.json"],
)
control_path = hf_hub_download(CONTROL_ID, CONTROL_FILE, revision="8a4702014d4dabb5f896fcba917e2ee0a961465f")

print("[load] transformer (base + control branch) …", flush=True)
with open(os.path.join(base_dir, "transformer", "config.json")) as f:
    tcfg = {k: v for k, v in json.load(f).items() if not k.startswith("_")}
# == config/qwenimage21/qwenimage21_control.yaml: control_layers [0, 2, …, 30], control_in_dim 129
tcfg.update(control_layers=list(range(0, tcfg["num_layers"], 2)), control_in_dim=129)
with init_empty_weights():
    transformer = QwenImage21ControlTransformer2DModel.from_config(tcfg)
state_dict = {}
for shard in sorted(glob.glob(os.path.join(base_dir, "transformer", "*.safetensors"))):
    state_dict.update(load_file(shard))
n_base = len(state_dict)
state_dict.update(load_file(control_path))
missing, unexpected = transformer.load_state_dict(state_dict, strict=False, assign=True)
print(f"[load] base keys={n_base} total={len(state_dict)} missing={len(missing)} unexpected={len(unexpected)}", flush=True)
if missing:
    raise RuntimeError(f"transformer weights missing: {missing[:10]}")
del state_dict
transformer = transformer.to(DTYPE).eval()

print("[load] vae / text encoder / processor …", flush=True)
vae = AutoencoderKLQwenImage21.from_pretrained(base_dir, subfolder="vae", torch_dtype=DTYPE).eval()
# The VAE decoder upcasts in its upsamplers; a one-shot ~1.8 MP RGBA decode hit the allocator assert
# ("NVML_SUCCESS == r INTERNAL ASSERT FAILED") next to ~39 GB of resident weights. Tile only big canvases.
vae.enable_tiling(
    tile_sample_min_height=1280,
    tile_sample_min_width=1280,
    tile_sample_stride_height=1024,
    tile_sample_stride_width=1024,
)
text_encoder = Qwen3VLForConditionalGeneration.from_pretrained(
    base_dir, subfolder="text_encoder", dtype=DTYPE
).eval()
# The pipeline only reads hidden states; the 1.2 GB vocab projection is dead weight.
text_encoder.lm_head = torch.nn.Identity()
processor = Qwen3VLProcessor.from_pretrained(base_dir, subfolder="processor")
scheduler = FlowMatchEulerDiscreteScheduler.from_pretrained(base_dir, subfolder="scheduler")

pipe = QwenImage21ControlPipeline(
    vae=vae, text_encoder=text_encoder, processor=processor, transformer=transformer, scheduler=scheduler
)
pipe.to("cuda")
print("[load] pipeline ready", flush=True)
