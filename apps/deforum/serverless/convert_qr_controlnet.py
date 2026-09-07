"""Normalize the four remaining Diffusers names in Civitai version 165780.

Mapping: ComfyUI v0.34.0 comfy/utils.py UNET_MAP_BASIC. Tensor bytes are
copied unchanged; only the safetensors JSON header is renamed.
"""

import json
from pathlib import Path
import shutil
import struct
import sys


def convert(source, target):
    mapping = {
        f"add_embedding.linear_{layer}.{kind}": f"label_emb.0.{index}.{kind}"
        for layer, index in ((1, 0), (2, 2))
        for kind in ("weight", "bias")
    }
    with source.open("rb") as src:
        header = json.loads(src.read(struct.unpack("<Q", src.read(8))[0]))
        if not all(k in header and v not in header for k, v in mapping.items()):
            raise ValueError("Unexpected QR ControlNet format; refusing conversion")
        header = {mapping.get(k, k): v for k, v in header.items()}
        encoded = json.dumps(header, separators=(",", ":")).encode()
        encoded += b" " * (-len(encoded) % 8)
        with target.open("xb") as dst:
            dst.write(struct.pack("<Q", len(encoded)))
            dst.write(encoded)
            shutil.copyfileobj(src, dst, length=1024 * 1024)


if __name__ == "__main__":
    convert(Path(sys.argv[1]), Path(sys.argv[2]))
