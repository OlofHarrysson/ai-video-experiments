"""E07: immutable depth guide and native Seedream independent frame edits."""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import urllib.request

from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
APP = PROJECT.parents[1]
sys.path.insert(0, str(APP))
import editing
import experiment
import serverless_client as client

FRAMES, WIDTH, HEIGHT, STEP = 32, 1280, 720, .002
MODEL = 'seedream-v4-edit'
REFERENCE = PROJECT / 'references/assets/seedream-v001/anchor.png'
SOURCE = APP / 'projects/seedream-motion/references/assets/seedream-v001/anchor.png'
PROMPT = ('Repair this depth-warped animation frame with minimal changes. Fill only black missing-image gaps and small torn edges with plausible continuation of the surrounding painted scene. '
          'Preserve the exact camera viewpoint, composition, positions, contours and sizes of every existing object. '
          'Keep the large copper lantern on the left, winding boardwalk, blue mushrooms, distant small domed observatory, crescent moon, indigo sky, violet mist and warm amber lighting. '
          'Match the original detailed textured painterly brushwork and colors. Do not redesign objects, add objects, move the camera or change the framing. Return a complete landscape image.')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def guide():
    experiment.project_for_run(PROJECT.name, 'e07-native-edit')
    (PROJECT / 'runs').mkdir(exist_ok=True)
    REFERENCE.parent.mkdir(parents=True, exist_ok=True)
    if not REFERENCE.exists():
        shutil.copyfile(SOURCE, REFERENCE)
    assert digest(SOURCE) == digest(REFERENCE)
    graph = experiment.make_graph(.4, FRAMES, 'e07-guide')
    graph.pop('4'); graph.pop('5')
    graph['6'] = {'class_type': 'LoadImage', 'inputs': {'image': 'anchor.png'}}
    graph['7']['inputs'].update(width=WIDTH, height=HEIGHT, seed=143)
    graph = experiment.depth_camera_graph(graph, True, FRAMES, translation_x=STEP)
    folder = client.submit(PROJECT, 'e07-native-edit', graph, FRAMES,
        {'phase': 'guide', 'anchor_sha256': digest(REFERENCE), 'camera_step': STEP,
         'recipe_sha256': digest(Path(__file__))}, REFERENCE)
    print(folder, flush=True)


def edit_frame(index, run, source_run):
    folder = run / f'frame-{index:04d}'
    folder.mkdir(exist_ok=True)
    if (folder / 'result.json').exists():
        return json.loads((folder / 'result.json').read_text())
    receipt = json.loads((source_run / 'submission.json').read_text())
    manifest = json.loads((source_run / 'cloud' / receipt['cloud_attempt'] / 'manifest.json').read_text())
    item = sorted([x for x in manifest['files'] if x['relative_path'].startswith('11/')], key=lambda x:x['relative_path'])[index]
    source = source_run / 'frames' / f'{index:04d}.png'
    assert digest(source) == item['sha256']
    config = receipt['deployment']
    if not (folder / 'submit-response.json').exists():
        if (folder / 'request.json').exists():
            raise RuntimeError(f'Uncertain prior submission frame {index}; inspect before resubmitting')
        # RunPod network-volume S3 does not support presigned GET URLs.
        # Carry this owned image directly to the same authorized image endpoint.
        url = 'data:image/png;base64,' + base64.b64encode(source.read_bytes()).decode()
        payload = {'input': {'prompt': PROMPT, 'images': [url], 'size':'2048*1152', 'enable_safety_checker': True}}
        # Reserve all requests at $0.10 each; 31 edits remain below the $4 study cap.
        assert len(list(run.glob('frame-*/request.json'))) < 40
        client.save(folder / 'request.json', payload)
        client.save(folder / 'submission.json', {'source_frame':index,'source_sha256':digest(source), 'source_key':item['key'], 'submitted_at':stamp(), 'model':MODEL})
        try:
            result = client.api(MODEL, 'run', payload)
        except Exception as error:
            client.save(folder / 'submission-error.json', {'error': str(error), 'retry':False})
            raise
        client.save(folder / 'submit-response.json', result)
    result = json.loads((folder / 'submit-response.json').read_text())
    job_id = result['id']
    deadline = time.monotonic() + 1800
    while result.get('status') not in ('COMPLETED','FAILED','CANCELLED','TIMED_OUT'):
        if time.monotonic() > deadline:
            raise TimeoutError(f'Collect existing frame {index}, job {job_id}; do not resubmit')
        time.sleep(3)
        result = client.api(MODEL, 'status/' + job_id)
        client.save(folder / 'job-status.json', result)
    client.save(folder / 'job-status.json', result)
    if result['status'] != 'COMPLETED':
        raise RuntimeError(f'Frame {index}: {result["status"]}; inspect saved response')
    output = result['output']
    url = output.get('result') or output.get('image_url')
    if isinstance(url, list):
        assert len(url) == 1
        url = url[0]
    if not isinstance(url, str):
        raise ValueError(f'Unexpected output shape for frame {index}')
    original = folder / 'original.image'
    if not original.exists():
        request = urllib.request.Request(url, headers={'User-Agent':'deforum-experiment/0.2'})
        with urllib.request.urlopen(request, timeout=120) as response:
            data = response.read()
        original.write_bytes(data)
    with Image.open(original) as image:
        dimensions = list(image.size)
        if abs(image.width/image.height - WIDTH/HEIGHT) > .025:
            raise ValueError(f'Unexpected aspect {dimensions}; preserved original, no silent crop')
        normalized = run / 'frames' / f'{index:04d}.png'
        image.convert('RGB').resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(normalized)
    summary = {'frame':index,'job_id':job_id,'source_sha256':digest(source),
        'actual_dimensions':dimensions,'original_sha256':digest(original),'normalized_sha256':digest(normalized),
        'cost':output.get('cost'),'execution_ms':result.get('executionTime'),'delay_ms':result.get('delayTime'),
        'collected_at':stamp()}
    client.save(folder / 'result.json', summary)
    print(json.dumps(summary), flush=True)
    return summary


def edits(source_name, phase):
    source_run = PROJECT / 'runs' / source_name
    receipt = json.loads((source_run / 'submission.json').read_text())
    assert receipt.get('collected_at') and receipt['frames'] == FRAMES
    run = PROJECT / 'runs' / ('e07-native-inline-' + source_name)
    run.mkdir(exist_ok=True)
    (run / 'frames').mkdir(exist_ok=True)
    if not (run / 'lineage.json').exists():
        client.save(run / 'lineage.json', {'guide_run':source_name,'model':MODEL,'prompt':PROMPT,'anchor_original':True,
            'generated_fps':8,'delivery_fps':24,'normalized_dimensions':[WIDTH,HEIGHT], 'recipe_sha256':digest(Path(__file__))})
        shutil.copyfile(source_run / 'frames/0000.png', run / 'frames/0000.png')
    indices = [1,31] if phase == 'smoke' else list(range(1,FRAMES))
    if phase == 'complete':
        assert all((run / f'frame-{i:04d}/result.json').exists() for i in [1,31]), 'Review smoke frames first'
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(lambda index:edit_frame(index,run,source_run), indices))
    if phase == 'complete':
        export = PROJECT / 'exports/e07-native-seedream-v001'
        export.mkdir(parents=True, exist_ok=False)
        editing.encode(run / 'frames', export / 'preview.mp4')
        results = [json.loads((run / f'frame-{i:04d}/result.json').read_text()) for i in range(1,FRAMES)]
        client.save(export / 'cut.json', {'source_run':run.name,'guide_run':source_name,'frames':32,'original_anchor_frames':1,
            'seedream_edit_frames':31,'duration_seconds':4,'fps_source':8,'fps_delivery':24,
            'reported_public_cost_usd':sum(float(x['cost'] or 0) for x in results), 'results':results})
        print(export / 'preview.mp4', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase',choices=['guide','smoke','complete'])
    parser.add_argument('--guide-run')
    args = parser.parse_args()
    if args.phase == 'guide':
        guide()
    else:
        edits(args.guide_run,args.phase)
