"""RunPod job transport and volume-backed collection for the experiment CLI."""

import base64
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
import urllib.error
import urllib.request

import boto3
from botocore.config import Config

import editing

DEPLOYMENT = Path(__file__).resolve().parent / 'work/serverless-deployment.json'
WAIT_SECONDS = 1800


def save(path, value):
    path.write_text(json.dumps(value, indent=2)+'\n')


def api(endpoint, route, data=None):
    key = os.environ['RUNPOD_API_KEY']
    req = urllib.request.Request(f'https://api.runpod.ai/v2/{endpoint}/{route}',
          data=None if data is None else json.dumps(data).encode(),
          headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json',
                   'User-Agent': 'deforum-experiment/0.2'})
    # A submission is never automatically retried after an uncertain response.
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def storage(deployment):
    return boto3.client('s3', endpoint_url=deployment['s3_endpoint'],
        region_name=deployment['data_center'],
        aws_access_key_id=os.environ['RUNPOD_S3_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['RUNPOD_S3_SECRET_ACCESS_KEY'],
        config=Config(signature_version='s3v4', s3={'addressing_style': 'path'},
                      retries={'max_attempts': 3}, connect_timeout=15, read_timeout=60))


def submit(project, experiment, graph, frames, lineage=None, source=None, deployment=DEPLOYMENT):
    config = json.loads(deployment.read_text())
    if not all(os.environ.get(k) for k in ('RUNPOD_API_KEY', 'RUNPOD_S3_ACCESS_KEY_ID',
                                         'RUNPOD_S3_SECRET_ACCESS_KEY')):
        raise ValueError('RunPod API and S3 credentials must be set before submission')
    # Prove local access to persistent storage before paying for inference.
    storage(config).list_objects_v2(Bucket=config['volume_id'], MaxKeys=1)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    name = f'{stamp}-{experiment}-{frames}f'
    folder = project / 'runs' / name
    folder.mkdir(exist_ok=False)
    save(folder / 'workflow.api.json', graph)
    receipt = {'transport': 'runpod-serverless', 'project': project.name,
               'experiment': experiment, 'frames': frames, 'generated_fps': 8,
               'delivery_fps': 24, 'deployment': config, 'run': name,
               'submitted_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               **(lineage or {})}
    save(folder / 'submission.json', receipt)
    images = []
    if source:
        shutil.copyfile(source, folder / 'anchor.png')
        images = [{'name': 'anchor.png', 'image': base64.b64encode(source.read_bytes()).decode()}]
    payload = {'input': {'project': project.name, 'run': name, 'workflow': graph,
                        'images': images, 'expected_frames': frames},
               'policy': {'executionTimeout': 600000, 'ttl': 1800000}}
    result = api(config['endpoint_id'], 'run', payload)
    save(folder / 'submit-response.json', result)
    if not result.get('id'):
        raise RuntimeError(f'No job ID returned; inspect {folder} before submitting again')
    receipt['job_id'] = result['id']
    save(folder / 'submission.json', receipt)
    print(f'Submitted {result["id"]}; receipts: {folder}', flush=True)
    collect(folder)
    return folder


def manifest_keys(client, config, prefix):
    result = []
    paginator = client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=config['volume_id'], Prefix=prefix):
        result.extend(x['Key'] for x in page.get('Contents', []) if x['Key'].endswith('/manifest.json'))
    return sorted(result)


def download_attempt(client, config, key, folder):
    manifest_bytes = client.get_object(Bucket=config['volume_id'], Key=key)['Body'].read()
    manifest = json.loads(manifest_bytes)
    attempt = manifest['attempt']
    if len(attempt) != 32 or any(c not in '0123456789abcdef' for c in attempt):
        raise ValueError('Invalid attempt ID in manifest')
    archive = folder / 'cloud' / attempt
    archive.mkdir(parents=True, exist_ok=True)
    prefix = key.removesuffix('manifest.json')
    for item in manifest['files']:
        relative = Path(item['relative_path'])
        if relative.is_absolute() or '..' in relative.parts or not relative.parts:
            raise ValueError('Unsafe manifest path')
        if item['key'] != prefix + relative.as_posix():
            raise ValueError('Manifest key is outside this attempt')
        target = archive / relative
        if target.exists():
            data = target.read_bytes()
        else:
            data = client.get_object(Bucket=config['volume_id'], Key=item['key'])['Body'].read()
        if len(data) != item['size'] or hashlib.sha256(data).hexdigest() != item['sha256']:
            raise ValueError(f'Archive checksum failed: {item["key"]}')
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as output:
                output.write(data)
    target = archive / 'manifest.json'
    if target.exists() and target.read_bytes() != manifest_bytes:
        raise ValueError('An archived manifest has changed')
    if not target.exists():
        target.write_bytes(manifest_bytes)
    return archive, manifest


def collect(folder):
    receipt = json.loads((folder / 'submission.json').read_text())
    if receipt.get('collected_at'):
        files = [folder / 'preview.mp4'] + [folder / 'frames' / f'{i:04d}.png'
                                          for i in range(receipt['frames'])]
        if not all(p.is_file() and p.stat().st_size for p in files):
            raise RuntimeError('Completed archive is missing assets; restore from the cloud archive')
        print(f'Already collected: {folder / "preview.mp4"}', flush=True)
        return
    config = receipt['deployment']
    client = storage(config)
    prefix = f'deforum/projects/{receipt["project"]}/runs/{receipt["run"]}/attempts/'
    deadline = time.monotonic() + WAIT_SECONDS
    last_status = None
    while time.monotonic() < deadline:
        keys = manifest_keys(client, config, prefix)
        if keys:
            break
        if not receipt.get('job_id'):
            raise RuntimeError('Submission response was lost; inspect endpoint jobs before resubmitting')
        status = api(config['endpoint_id'], f'status/{receipt["job_id"]}')
        save(folder / 'job-status.json', status)
        if status.get('status') != last_status:
            last_status = status.get('status')
            print(f'Job: {last_status}', flush=True)
        if last_status in ('FAILED', 'CANCELLED', 'TIMED_OUT'):
            raise RuntimeError(f'Job {last_status}; preserve the receipt and inspect remote logs/partial archive')
        time.sleep(5)
    else:
        raise TimeoutError('Local wait expired; job/volume are preserved. Reconnect with collect.')
    attempts = [download_attempt(client, config, key, folder) for key in keys]
    successful = [(path, manifest) for path, manifest in attempts if not manifest['error']]
    if len(successful) != 1:
        raise RuntimeError(f'Preserved {len(attempts)} attempts, {len(successful)} successful; select/review before making a cut')
    archive, manifest = successful[0]
    if manifest['frames'] != receipt['frames']:
        raise RuntimeError('Unexpected main frame count')
    frames = folder / 'frames'
    frames.mkdir(exist_ok=True)
    for i, source in enumerate(sorted((archive / '11').glob('*.png'))):
        target = frames / f'{i:04d}.png'
        if target.exists() and target.read_bytes() != source.read_bytes():
            raise ValueError('Existing collected frame differs; refusing overwrite')
        if not target.exists():
            shutil.copyfile(source, target)
    if not (folder / 'preview.mp4').exists():
        temporary = folder / 'preview.encoding.mp4'
        if temporary.exists():
            raise RuntimeError('Incomplete encoding exists; inspect it before reconnecting')
        editing.encode(frames, temporary)
        temporary.rename(folder / 'preview.mp4')
    receipt['collected_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    receipt['cloud_attempt'] = manifest['attempt']
    save(folder / 'submission.json', receipt)
    print(f'Saved {receipt["frames"]} frames, cloud receipts and {folder / "preview.mp4"}', flush=True)
