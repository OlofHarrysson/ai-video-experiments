"""On a ComfyUI Pod: fetch pinned weights with visible byte progress."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess
import time

ROOT = Path('/workspace/modern-model-session')
MODELS = Path('/workspace/runpod-slim/ComfyUI/models')


def fetch(asset):
    target = ROOT/'weights'/asset['destination']
    target.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    if not target.exists():
        partial = target.with_suffix('.partial')
        url = f"https://huggingface.co/{asset['repo']}/resolve/{asset['revision']}/{asset['source']}"
        process = subprocess.Popen(['curl', '--fail', '--location', '--silent', '--show-error',
            '--retry', '2', '--connect-timeout', '30', '--max-time', '1200', '--continue-at', '-',
            '--output', str(partial), url])
        while process.poll() is None:
            size = partial.stat().st_size if partial.exists() else 0
            print(asset['destination'], f'{size/1e9:.2f}/{asset["size"]/1e9:.2f} GB', flush=True)
            time.sleep(15)
        if process.returncode:
            raise RuntimeError(f"Download failed: {asset['destination']}, curl {process.returncode}")
    else:
        partial = target
    with partial.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    if partial.stat().st_size != asset['size'] or digest != asset['sha256']:
        raise RuntimeError(f"Checksum mismatch: {asset['destination']}")
    if partial != target:
        partial.rename(target)
    link = MODELS/asset['destination']
    link.parent.mkdir(parents=True, exist_ok=True)
    if not link.is_symlink():
        link.symlink_to(target)
    assert link.resolve() == target.resolve()
    print('VERIFIED', asset['destination'], round(time.monotonic()-started, 2), 'seconds', flush=True)


if __name__ == '__main__':
    assets = json.loads((ROOT/'modern-models.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(fetch, assets))
    print('ALL MODELS VERIFIED', flush=True)
