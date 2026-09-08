"""Populate the session volume before starting ComfyUI; never download during a job."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess

CACHE = Path('/runpod-volume/deforum-models')
MODELS = Path('/comfyui/models')
MANIFEST = Path('/modern-models.json')


def main():
    if not os.path.ismount('/runpod-volume'):
        raise RuntimeError('Mount the session network volume before worker startup')
    CACHE.mkdir(exist_ok=True)
    with (CACHE/'.prepare.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        for asset in json.loads(MANIFEST.read_text()):
            target = CACHE/asset['destination']
            target.parent.mkdir(parents=True, exist_ok=True)
            receipt = target.with_suffix('.verified.json')
            ready = target.exists() and target.stat().st_size == asset['size'] and receipt.exists() and json.loads(receipt.read_text()) == asset
            if not ready:
                temporary = target.with_suffix('.partial')
                url = f"https://huggingface.co/{asset['repo']}/resolve/{asset['revision']}/{asset['source']}"
                print('Downloading', asset['destination'], flush=True)
                subprocess.run(['wget', '--continue', '--progress=dot:giga', '--timeout=60', '--tries=3', '-O', str(temporary), url], check=True)
                with temporary.open('rb') as source:
                    digest = hashlib.file_digest(source, 'sha256').hexdigest()
                if temporary.stat().st_size != asset['size'] or digest != asset['sha256']:
                    raise RuntimeError(f"Checksum mismatch: {asset['destination']}; preserved partial file")
                temporary.replace(target)
                receipt.write_text(json.dumps(asset, indent=2)+'\n')
            link = MODELS/asset['destination']
            link.parent.mkdir(parents=True, exist_ok=True)
            if not link.is_symlink():
                link.symlink_to(target)
            if link.resolve() != target:
                raise RuntimeError(f'Model path conflict: {link}')
            print('Verified ready:', asset['destination'], flush=True)


if __name__ == '__main__':
    main()
