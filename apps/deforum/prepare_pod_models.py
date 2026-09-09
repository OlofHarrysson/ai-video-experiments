"""On a ComfyUI Pod: fetch pinned weights with visible byte progress."""
import argparse
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
    downloaded = not target.exists()
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
    return {'destination': asset['destination'], 'sha256': digest, 'bytes': asset['size'],
            'downloaded': downloaded, 'seconds': round(time.monotonic()-started, 3)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--krea-only', action='store_true', help='Prepare only the current Krea model family.')
    parser.add_argument('--verify-only', action='store_true', help='Fail if a cached model is missing; never download.')
    args = parser.parse_args()
    assets = json.loads((ROOT/'modern-models.json').read_text())
    if args.krea_only:
        assets = [asset for asset in assets if asset['repo'] == 'Comfy-Org/Krea-2']
        if len(assets) != 3:
            raise RuntimeError('Expected exactly three pinned Krea assets')
    if args.verify_only:
        for asset in assets:
            if not (ROOT/'weights'/asset['destination']).is_file():
                raise FileNotFoundError(asset['destination'])
    started = time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(fetch, assets))
    (ROOT/'verified-models.json').write_text(json.dumps({
        'seconds': round(time.monotonic()-started, 3), 'models': records}, indent=2)+'\n')
    print('ALL MODELS VERIFIED', flush=True)
