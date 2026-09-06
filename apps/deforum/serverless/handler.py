"""Archive ComfyUI outputs on the mounted volume and return a small manifest.

Generation and ComfyUI job handling remain in RunPod's upstream worker.
S3 credentials are only needed on the Mac; the worker writes to its mount.
"""

import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import uuid
import urllib.request

VOLUME = Path('/runpod-volume')
ARCHIVE = VOLUME / 'deforum'


def component(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,150}', value):
        raise ValueError('Invalid archive path component')
    return value


def write_json(path, value):
    with path.open('x') as output:
        json.dump(value, output, indent=2)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())


def archive_job(job, render, archive=ARCHIVE):
    data = job['input']
    project, run = component(data['project']), component(data['run'])
    graph = copy.deepcopy(data['workflow'])
    # A new attempt directory also preserves retries of the same RunPod job.
    prefix = Path('projects') / project / 'runs' / run / 'attempts' / uuid.uuid4().hex
    folder = archive / prefix
    folder.mkdir(parents=True, exist_ok=False)
    write_json(folder / 'request.json', {
        'job_id': job['id'], 'project': project, 'run': run,
        'expected_frames': data['expected_frames'],
    })
    for node_id, node in graph.items():
        if node['class_type'] == 'SaveImage':
            node['inputs']['filename_prefix'] = (prefix / component(node_id) / 'frame').as_posix()
    if graph.get('11', {}).get('class_type') != 'SaveImage':
        raise ValueError('Main frame sequence must be SaveImage node 11')
    images = []
    for index, source in enumerate(data.get('images', [])):
        name = component(source['name'])
        image_bytes = base64.b64decode(source['image'].split(',')[-1], validate=True)
        target = folder / f'input-{index:02d}.png'
        with target.open('xb') as output:
            output.write(image_bytes)
        # Unique input names avoid ComfyUI caching an older image across jobs.
        remote_name = f'{folder.name}-{name}'
        for node in graph.values():
            if node['class_type'] == 'LoadImage' and node['inputs']['image'] == name:
                node['inputs']['image'] = remote_name
        images.append({'name': remote_name, 'image': source['image']})
    write_json(folder / 'workflow.api.json', graph)
    try:
        result = render({'id': job['id'], 'input': {'workflow': graph, 'images': images}})
        # Upstream encodes images for its ordinary API; those bytes stay in-process.
        diagnostics = {k: v for k, v in result.items() if k != 'images'}
    except Exception as error:
        diagnostics = {'error': f'{type(error).__name__}: {error}'}
    write_json(folder / 'diagnostics.json', diagnostics)
    files = []
    for path in sorted(folder.rglob('*')):
        if path.is_file():
            with path.open('rb') as source:
                digest = hashlib.file_digest(source, 'sha256').hexdigest()
                os.fsync(source.fileno())
            files.append({'key': path.relative_to(archive.parent).as_posix(),
                          'relative_path': path.relative_to(folder).as_posix(),
                          'size': path.stat().st_size, 'sha256': digest})
    count = len(list((folder / '11').glob('*.png')))
    error = diagnostics.get('error')
    if diagnostics.get('errors'):
        error = str(diagnostics['errors'])
    if count != data['expected_frames']:
        error = f'Expected {data["expected_frames"]} frames, saved {count}; {error or ""}'
    manifest = {'schema_version': 1, 'job_id': job['id'], 'project': project, 'run': run,
                'attempt': folder.name, 'files': files, 'frames': count, 'error': error}
    write_json(folder / 'manifest.json', manifest)
    key = (Path('deforum') / prefix / 'manifest.json').as_posix()
    if error:
        return {'error': error, 'manifest_key': key}
    return {'manifest_key': key, 'frames': count, 'attempt': folder.name}


def handler(job):
    if not os.path.ismount(VOLUME):
        return {'error': 'A persistent RunPod network volume must be mounted before rendering'}
    import upstream_handler
    def render(request):
        result = upstream_handler.handler(request)
        with urllib.request.urlopen('http://127.0.0.1:8188/system_stats', timeout=15) as response:
            result['runtime'] = json.load(response)
        return result
    return archive_job(job, render)


if __name__ == '__main__':
    import runpod
    runpod.serverless.start({'handler': handler})
