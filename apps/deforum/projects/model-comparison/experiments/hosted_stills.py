"""One-image public API recipes, frozen requests, bounded spend and recovery."""

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.request
import uuid

PROJECT = Path(__file__).resolve().parents[1]
RUNS = PROJECT / 'runs'
PROMPT_SOURCE = PROJECT.parent / 'lantern-marsh/experiments/overscan.py'
BUDGETS = {'runpod': 5, 'fal': 2}
RESERVATION_USD = 1
MODELS = {
    'flux-dev': {
        'provider': 'runpod', 'endpoint': 'black-forest-labs-flux-1-dev',
        'version': 'FLUX.1 dev (hosted revision not exposed)',
        'estimated_usd': .03,
        'source': 'https://console.runpod.io/hub/playground/image/black-forest-labs-flux-1-dev',
        'params': {'aspect': 'landscape', 'seed': 143,
                   'num_inference_steps': 28, 'guidance': 7.5, 'image_format': 'png'},
    },
    'seedream-4': {
        'provider': 'runpod', 'endpoint': 'seedream-v4-t2i',
        'version': 'Seedream 4.0 (hosted revision not exposed)',
        'estimated_usd': .027,
        'source': 'https://docs.runpod.io/public-endpoints/models/seedream-4-t2i',
        'params': {'size': '2048*1152', 'seed': 143, 'enable_safety_checker': True},
    },
    'flux-2-pro': {
        'provider': 'fal', 'endpoint': 'fal-ai/flux-2-pro',
        'version': 'FLUX.2 pro (hosted revision not exposed)',
        'estimated_usd': .03,
        'source': 'https://fal.ai/models/fal-ai/flux-2-pro/api',
        'params': {'image_size': {'width': 1280, 'height': 720}, 'seed': 143,
                   'output_format': 'png', 'enable_safety_checker': True, 'sync_mode': False},
    },
    'seedream-5-lite': {
        'provider': 'fal', 'endpoint': 'fal-ai/bytedance/seedream/v5/lite/text-to-image',
        'version': 'Seedream 5.0 Lite (hosted revision not exposed)',
        'estimated_usd': .035,
        'source': 'https://fal.ai/models/fal-ai/bytedance/seedream/v5/lite/text-to-image/api',
        'params': {'image_size': {'width': 2560, 'height': 1440}, 'num_images': 1,
                   'max_images': 1, 'enable_safety_checker': True, 'sync_mode': False},
    },
}


def save(path, value):
    with path.open('x') as file:
        json.dump(value, file, indent=2)
        file.write('\n')


def prompt():
    # Read the literal without importing the parent's runner or transport.
    for node in ast.parse(PROMPT_SOURCE.read_text()).body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == 'PROMPT' for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise RuntimeError('No literal PROMPT in lantern-marsh source')


def credentials(provider):
    key = (os.environ.get('RUNPOD_API_KEY') if provider == 'runpod' else
           os.environ.get('FAL_KEY') or os.environ.get('FAL_API_KEY'))
    if not key:
        raise RuntimeError('Missing ' + ('RUNPOD_API_KEY' if provider == 'runpod' else
                                       'FAL_KEY (also accepts FAL_API_KEY)'))
    return ('Bearer ' if provider == 'runpod' else 'Key ') + key


def api(url, auth, payload=None):
    # Never send provider credentials to returned image/download URLs.
    allowed = ('https://api.runpod.ai/v2/', 'https://queue.fal.run/')
    if not url.startswith(allowed):
        raise RuntimeError('Unexpected API URL host')
    request = urllib.request.Request(url, data=None if payload is None else
                                     json.dumps(payload).encode(), headers={
                                         'Authorization': auth, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        # Preserve status only: avoid reflecting authentication headers or key values.
        raise RuntimeError(f'HTTP {error.code}; do not retry an ambiguous POST') from None


def submit(model):
    spec = MODELS[model]
    auth = credentials(spec['provider'])
    RUNS.mkdir(parents=True, exist_ok=True)
    # An exclusive project lock makes concurrent budget reservations safe.
    lock = RUNS / '.submission-lock'
    with lock.open('x'):
        pass
    try:
        reserved = sum(json.loads(p.read_text())['reserved_usd']
                       for p in RUNS.glob('*/reservation.json')
                       if json.loads(p.read_text())['provider'] == spec['provider'])
        if reserved + RESERVATION_USD > BUDGETS[spec['provider']]:
            raise RuntimeError('Project provider budget exhausted; no request submitted')
        run = RUNS / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') +
                      '-' + model + '-' + uuid.uuid4().hex[:8])
        run.mkdir()
        inputs = {**spec['params'], 'prompt': prompt()}
        save(run / 'request.json', inputs)
        save(run / 'receipt.json', {**spec, 'model': model, 'created_at':
             datetime.now(timezone.utc).isoformat(), 'prompt_source':
             'apps/deforum/projects/lantern-marsh/experiments/overscan.py',
             'prompt_source_sha256': hashlib.sha256(PROMPT_SOURCE.read_bytes()).hexdigest(),
             'recipe_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
        save(run / 'reservation.json', {'provider': spec['provider'],
                                       'reserved_usd': RESERVATION_USD})
    finally:
        lock.unlink()
    print('Preserved run:', run, flush=True)
    base = ('https://api.runpod.ai/v2/' if spec['provider'] == 'runpod' else
            'https://queue.fal.run/') + spec['endpoint']
    try:
        result = api(base + '/run' if spec['provider'] == 'runpod' else base,
                     auth, {'input': inputs} if spec['provider'] == 'runpod' else inputs)
    except Exception as error:
        save(run / 'submission-error.json', {'type': type(error).__name__,
                                            'action': 'Reconcile provider history; never auto-resubmit'})
        raise
    save(run / 'submission.json', result)
    print('Submitted. Recover with collect', run.name, flush=True)
    collect(run)


def collect(run):
    if (run / 'artifacts.json').exists():
        for item in json.loads((run / 'artifacts.json').read_text()):
            if hashlib.sha256((run / item['file']).read_bytes()).hexdigest() != item['sha256']:
                raise RuntimeError('Preserved artifact hash mismatch')
        print('Verified existing outputs:', run)
        return
    receipt = json.loads((run / 'receipt.json').read_text())
    submission = json.loads((run / 'submission.json').read_text())
    auth = credentials(receipt['provider'])
    if receipt['provider'] == 'runpod':
        status_url = ('https://api.runpod.ai/v2/' + receipt['endpoint'] +
                      '/status/' + submission['id'])
    else:
        status_url = submission['status_url']
    deadline = time.monotonic() + 600
    while not (run / 'result.json').exists():
        status = api(status_url, auth)
        save(run / ('status-' + str(time.time_ns()) + '.json'), status)
        if status['status'] == 'COMPLETED':
            result = status if receipt['provider'] == 'runpod' else api(submission['response_url'], auth)
            save(run / 'result.json', result)
            break
        if status['status'] in ('FAILED', 'CANCELLED', 'TIMED_OUT'):
            raise RuntimeError('Generation ' + status['status'] + '; response preserved')
        if time.monotonic() >= deadline:
            raise RuntimeError('Still pending; use collect to resume without resubmitting')
        print('Job:', status['status'], flush=True)
        time.sleep(5)
    result = json.loads((run / 'result.json').read_text())
    output = result['output'] if receipt['provider'] == 'runpod' else result
    urls = ([output['result']] if receipt['provider'] == 'runpod' else
            [item['url'] for item in output['images']])
    artifacts = []
    for i, url in enumerate(urls):
        path = run / f'original-{i:02d}.png'
        if not path.exists() and path.with_suffix('.jpg').exists():
            path = path.with_suffix('.jpg')
        if not path.exists():
            with urllib.request.urlopen(url, timeout=60) as response:
                raw = response.read()
            # Seedream may return JPEG despite no selectable output format.
            suffix = '.png' if raw.startswith(b'\x89PNG') else '.jpg' if raw.startswith(b'\xff\xd8') else None
            if not suffix:
                raise RuntimeError('Unexpected image format; result URL preserved')
            path = path.with_suffix(suffix)
            if not path.exists():
                with path.open('xb') as file:
                    file.write(raw)
        artifacts.append({'file': path.name, 'source_url': url,
                          'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    save(run / 'artifacts.json', artifacts)
    print('Saved originals:', run, 'reported cost:', output.get('cost', 'not returned'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'run', 'collect'])
    parser.add_argument('target', nargs='?')
    args = parser.parse_args()
    if args.action == 'plan':
        print(json.dumps({'models': MODELS, 'prompt': prompt(), 'budgets_usd': BUDGETS}, indent=2))
    elif args.action == 'run':
        if args.target not in MODELS:
            parser.error('Choose a named model from plan')
        submit(args.target)
    else:
        run = (RUNS / (args.target or '')).resolve()
        if run.parent != RUNS.resolve():
            parser.error('collect requires an existing run name in this project')
        collect(run)


if __name__ == '__main__':
    main()
