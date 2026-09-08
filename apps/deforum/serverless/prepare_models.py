"""Download verified modern weights to worker-local storage before ComfyUI starts."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time

# Large model transfers use local disk; the mounted volume archives generated outputs.
CACHE = Path('/comfyui/modern-model-cache')
MODELS = Path('/comfyui/models')
MANIFEST = Path('/modern-models.json')
os.environ.setdefault('HF_XET_HIGH_PERFORMANCE', '1')


def main():
    from huggingface_hub import hf_hub_download
    if not os.path.ismount('/runpod-volume'):
        raise RuntimeError('Mount the output archive volume before worker startup')
    CACHE.mkdir(exist_ok=True)
    with (CACHE/'.prepare.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for asset in json.loads(MANIFEST.read_text()):
            target = CACHE/asset['destination']
            target.parent.mkdir(parents=True, exist_ok=True)
            receipt = target.with_suffix('.verified.json')
            ready = target.exists() and target.stat().st_size == asset['size'] and receipt.exists() and json.loads(receipt.read_text()) == asset
            if not ready:
                started = time.monotonic()
                print('Downloading to local disk:', asset['destination'], flush=True)
                temporary = Path(hf_hub_download(repo_id=asset['repo'], revision=asset['revision'], filename=asset['source'], local_dir=CACHE/'.downloads'))
                with temporary.open('rb') as source:
                    digest = hashlib.file_digest(source, 'sha256').hexdigest()
                if temporary.stat().st_size != asset['size'] or digest != asset['sha256']:
                    raise RuntimeError(f"Checksum mismatch: {asset['destination']}; preserved downloaded file")
                temporary.replace(target)
                receipt.write_text(json.dumps(asset, indent=2)+'\n')
                print('Download and verification seconds:', round(time.monotonic()-started, 2), flush=True)
            link = MODELS/asset['destination']
            link.parent.mkdir(parents=True, exist_ok=True)
            if not link.is_symlink():
                link.symlink_to(target)
            if link.resolve() != target.resolve():
                raise RuntimeError(f'Model path conflict: {link}')
            print('Verified ready:', asset['destination'], flush=True)


if __name__ == '__main__':
    main()
