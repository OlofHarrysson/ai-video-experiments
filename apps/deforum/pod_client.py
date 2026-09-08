"""Submit native ComfyUI graphs to a session Pod; collect each result locally."""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import shlex
import subprocess
import time
import urllib.request
import uuid

from experiment import collect, request, save_json

DEPLOYMENT = Path(__file__).resolve().parent/'work/modern-pod-session/deployment.json'


def submit(project, experiment, graph, frames, lineage=None, source=None, reference=None):
    config = json.loads(DEPLOYMENT.read_text())
    base = config['base_url']
    stats = request(base, '/system_stats')
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    folder = project/'runs'/f'{stamp}-{experiment}-{frames}f'
    folder.mkdir(exist_ok=False)
    save_json(folder/'workflow.api.json', graph)
    save_json(folder/'system-stats.json', stats)
    actual = copy.deepcopy(graph)
    receipt = {'transport': 'comfyui-pod', 'pod_id': config['pod_id'], 'base_url': base,
               'frames': frames, 'submitted_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               **(lineage or {})}
    save_json(folder/'submission.json', receipt)
    for source_path, node_id, local_name, upload_name, timing_name in (
        (source, '20', 'anchor.png', 'upload.json', 'upload_seconds'),
        (reference, '30', 'reference.png', 'upload-reference.json', 'reference_upload_seconds'),
    ):
        if source_path is None:
            continue
        upload_started = time.monotonic()
        shutil.copyfile(source_path, folder/local_name)
        boundary = uuid.uuid4().hex
        remote_name = folder.name+('.png' if node_id == '20' else '-reference.png')
        upload_transport = config.get('upload_transport', 'http')
        if upload_transport == 'ssh':
            remote_path = config['remote_input_dir'].rstrip('/')+'/'+remote_name
            host = 'root@'+config['ssh_host']
            subprocess.run(['scp', '-i', config['ssh_identity'], '-P', str(config['ssh_port']),
                str(folder/local_name), host+':'+remote_path], check=True, timeout=60)
            result = subprocess.run(['ssh', '-i', config['ssh_identity'], '-p', str(config['ssh_port']),
                host, 'sha256sum '+shlex.quote(remote_path)], check=True, capture_output=True, text=True, timeout=30)
            digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
            if result.stdout.split()[0] != digest:
                raise RuntimeError('Uploaded image checksum mismatch')
            uploaded = {'name': remote_name, 'subfolder': '', 'type': 'input',
                        'transport': 'ssh', 'sha256': digest}
        elif upload_transport == 'http':
            body = (f'--{boundary}\r\nContent-Disposition: form-data; name="image"; filename="{remote_name}"\r\n'
                    'Content-Type: image/png\r\n\r\n').encode()+source_path.read_bytes()+f'\r\n--{boundary}--\r\n'.encode()
            req = urllib.request.Request(base+'/upload/image', data=body,
                headers={'Content-Type': 'multipart/form-data; boundary='+boundary,
                         'User-Agent': 'deforum-experiment/0.2'})
            with urllib.request.urlopen(req, timeout=60) as response:
                uploaded = json.load(response)
        else:
            raise ValueError(f'Unknown upload transport: {upload_transport}')
        save_json(folder/upload_name, uploaded)
        receipt[timing_name] = round(time.monotonic()-upload_started, 3)
        actual[node_id]['inputs']['image'] = '/'.join(filter(None, [uploaded.get('subfolder'), uploaded['name']]))
    save_json(folder/'workflow.executed.json', actual)
    # Accepted requests are never automatically resubmitted after a connection failure.
    try:
        prompt_started = time.monotonic()
        result = request(base, '/prompt', {'prompt': actual, 'client_id': folder.name})
    except Exception as error:
        save_json(folder/'submission-error.json', {'error': str(error), 'action': 'Inspect remote queue/history before retrying.'})
        raise
    save_json(folder/'submit-response.json', result)
    if result.get('node_errors') or not result.get('prompt_id'):
        raise RuntimeError(f'ComfyUI rejected graph; inspect {folder}')
    receipt['prompt_id'] = result['prompt_id']
    receipt['prompt_submit_seconds'] = round(time.monotonic()-prompt_started, 3)
    save_json(folder/'submission.json', receipt)
    print(f'Submitted {result["prompt_id"]}: {folder.name}', flush=True)
    collect(folder)
    save_json(folder/'frame-hashes.json', {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((folder/'frames').glob('*.png'))})
    return folder
