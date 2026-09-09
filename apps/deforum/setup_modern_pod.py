"""Prepare the pinned modern-model runtime on the official CUDA 12.8 ComfyUI Pod.

Run on the Pod after the template has started. Reuses a persistent workspace;
large Torch/CUDA dependencies remain inherited from the container image.
"""
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import time
import urllib.request

COMFY = Path('/workspace/runpod-slim/ComfyUI')
ROOT = Path('/workspace/modern-model-session')
COMMIT = '12d5279438bfefc058a269eae805ceab6047777f'
PYTHON = COMFY / '.venv-cu128/bin/python'


def run():
    started = time.monotonic()
    deadline = started + 600
    while True:
        try:
            with urllib.request.urlopen('http://127.0.0.1:8188/system_stats', timeout=3) as response:
                json.load(response)
            break
        except (OSError, ValueError):
            if time.monotonic() > deadline:
                raise TimeoutError('Official ComfyUI startup did not finish')
            time.sleep(5)
    ROOT.mkdir(parents=True, exist_ok=True)
    current = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=COMFY, text=True).strip()
    if current != COMMIT:
        subprocess.run(['git', 'fetch', 'origin', COMMIT], cwd=COMFY, check=True)
        subprocess.run(['git', 'checkout', '--detach', COMMIT], cwd=COMFY, check=True)
    requirements = '\n'.join(line for line in (COMFY/'requirements.txt').read_text().splitlines()
                             if not line.startswith('comfyui-workflow-templates')) + '\n'
    fingerprint = hashlib.sha256(requirements.encode()).hexdigest()
    marker = ROOT/'runtime-ready.json'
    reuse = PYTHON.exists() and marker.exists() and json.loads(marker.read_text()) == {
        'commit': COMMIT, 'requirements_sha256': fingerprint, 'python': str(PYTHON)}
    if not reuse:
        if not PYTHON.exists():
            subprocess.run(['python3.12', '-m', 'venv', '--system-site-packages', str(PYTHON.parent.parent)], check=True)
        req = ROOT/'runtime-requirements.txt'
        req.write_text(requirements)
        subprocess.run([str(PYTHON), '-m', 'pip', 'install', '-r', str(req)], cwd=COMFY, check=True)
        marker.write_text(json.dumps({'commit': COMMIT, 'requirements_sha256': fingerprint,
                                     'python': str(PYTHON)}))
    # Stop only ComfyUI processes in this installation. Other services are untouched.
    for line in subprocess.check_output(['ps', '-eo', 'pid,args'], text=True).splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) != 2 or 'main.py' not in parts[1]:
            continue
        pid = int(parts[0])
        try:
            if Path(f'/proc/{pid}/cwd').resolve() != COMFY:
                continue
            os.kill(pid, signal.SIGTERM)
            for _ in range(30):
                if not Path(f'/proc/{pid}').exists():
                    break
                time.sleep(1)
            else:
                raise RuntimeError(f'ComfyUI process {pid} did not stop')
        except ProcessLookupError:
            pass
    with (ROOT/'comfy.log').open('a') as log:
        process = subprocess.Popen([str(PYTHON), 'main.py', '--listen', '0.0.0.0', '--port', '8188',
                                    '--enable-cors-header'], cwd=COMFY, stdin=subprocess.DEVNULL,
                                   stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    deadline = time.monotonic() + 180
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError('ComfyUI exited; inspect modern-model-session/comfy.log')
        try:
            with urllib.request.urlopen('http://127.0.0.1:8188/system_stats', timeout=3) as response:
                stats = json.load(response)
            receipt = {'seconds': round(time.monotonic()-started, 3), 'reused_dependencies': reuse,
                       'commit': COMMIT, 'stats': stats}
            (ROOT/'runtime-timing.json').write_text(json.dumps(receipt, indent=2)+'\n')
            print(json.dumps(receipt), flush=True)
            return
        except (OSError, ValueError):
            time.sleep(2)
    raise TimeoutError('Pinned ComfyUI did not become ready')


if __name__ == '__main__':
    run()
