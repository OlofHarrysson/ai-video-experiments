"""Run with the Pod's Python: verify/add SDXL without changing ComfyUI."""
import hashlib
import json
import subprocess
import time
from pathlib import Path

COMFY = Path('/workspace/runpod-slim/ComfyUI')
CHECKPOINT = 'sd_xl_base_1.0.safetensors'
REVISION = '462165984030d82259a11f4367a4eed129e94a7b'
SHA256 = '31e35c80fc4829d14f90153f4c74cd59c90b779f6afe05a74cd6120b893f7e5b'
RECEIPT = Path('/workspace/regional-composition-session/model.json')


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    start = time.monotonic()
    path = COMFY/'models/checkpoints'/CHECKPOINT
    if not path.parent.exists():
        raise RuntimeError('Wait for the official ComfyUI installation before preparing SDXL')
    downloaded = not path.exists()
    if downloaded:
        temporary = path.with_suffix('.safetensors.part')
        url = f'https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/{REVISION}/{CHECKPOINT}'
        subprocess.run(['curl', '--fail', '--location', '--retry', '2', '--silent', '--show-error',
                        '--output', str(temporary), url], check=True)
        if digest(temporary) != SHA256:
            raise RuntimeError('Downloaded checkpoint SHA-256 mismatch')
        temporary.rename(path)
    elif digest(path) != SHA256:
        raise RuntimeError('Existing checkpoint SHA-256 mismatch; no file overwritten')
    receipt = {'checkpoint': CHECKPOINT, 'revision': REVISION, 'sha256': SHA256,
               'bytes': path.stat().st_size, 'downloaded': downloaded,
               'seconds': round(time.monotonic()-start, 3),
               'comfyui_commit': subprocess.check_output(['git', '-C', str(COMFY), 'rev-parse', 'HEAD'], text=True).strip()}
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    main()
