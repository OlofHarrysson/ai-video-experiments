"""E01: preserved Seedream keyframes, three SDXL shots, and timed-frame review."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
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

WIDTH, HEIGHT, FRAMES = 1280, 720, 32
SOURCE = APP / 'projects/model-comparison/runs/20260906T215118Z-seedream-4-f5a8fd86'
ENDPOINT = 'seedream-v4-edit'
STYLE = 'textured painterly dark fantasy illustration, deep teal and indigo with warm amber light, violet mist, visible brushwork, no text'
SHOTS = {
    'invitation': 'a hanging copper lantern in the left foreground, moonlit marsh and a winding wooden boardwalk leading toward a small distant domed astronomical observatory, luminous blue mushrooms, crescent moon, ' + STYLE,
    'signal': 'a closer view from the same wooden boardwalk toward the domed astronomical observatory, a continuous bright amber glowing trail along the boardwalk leading to the glowing observatory door, luminous blue mushrooms, moonlit marsh, ' + STYLE,
    'reveal': 'a close view of the domed astronomical observatory at the end of the boardwalk, the dome opened into a giant circular portal showing a luminous impossible garden of floating islands and waterfalls under a golden sky, blue mushrooms in the moonlit marsh foreground, ' + STYLE,
}
EDITS = {
    'signal': 'Create the next shot in this same film. Preserve the painterly brushwork, blue and amber palette, marsh, boardwalk and small observatory design. Move the viewpoint halfway down the boardwalk, so the observatory is substantially larger and centered and the large foreground hanging lantern is outside the frame. A bright continuous amber ribbon of light runs along the middle of the wooden boardwalk and terminates at the now intensely glowing observatory doorway. Clear amber signal against dark blue surroundings. Same moonlit world. Landscape widescreen image, no text.',
    'reveal': 'Create the final reveal shot in this same film. Preserve the painterly brushwork, blue and amber palette, boardwalk and recognizable domed observatory architecture. The camera has arrived near the observatory at the end of the boardwalk; the observatory occupies most of the middle of the composition. Its dome has split open to reveal a large circular magical portal. Inside that portal is an impossible lush garden of floating rocky islands with cascading waterfalls beneath a luminous golden sky. Surrounding marsh remains blue night with luminous blue mushrooms. An amber trail on the boardwalk leads through the doorway. Strong visual contrast between the enclosed impossible golden world and the dark marsh. Landscape widescreen image, no text.',
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    target = PROJECT / 'references/assets/invitation'
    target.mkdir(exist_ok=False)
    source = SOURCE / 'original-00.jpg'
    shutil.copyfile(source, target / 'original.jpg')
    Image.open(source).convert('RGB').resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(target / 'anchor.png')
    client.save(target / 'lineage.json', {'source': str(source), 'source_sha256': sha(source), 'anchor_sha256': sha(target / 'anchor.png'), 'resize': [WIDTH, HEIGHT]})


def keyframe(shot):
    if shot not in EDITS:
        raise ValueError('Choose signal or reveal')
    folder = PROJECT / 'references/assets' / shot
    folder.mkdir(exist_ok=False)
    source_url = json.loads((SOURCE / 'artifacts.json').read_text())[0]['source_url']
    inputs = {'prompt': EDITS[shot], 'images': [source_url], 'size': '2048*1152', 'enable_safety_checker': True}
    client.save(folder / 'request.json', {'endpoint': ENDPOINT, 'input': inputs, 'source_sha256': sha(SOURCE / 'original-00.jpg')})
    try:
        submission = client.api(ENDPOINT, 'run', {'input': inputs})
    except Exception as error:
        client.save(folder / 'submission-error.json', {'error_type': type(error).__name__, 'action': 'Reconcile request; do not resubmit automatically'})
        raise
    client.save(folder / 'submission.json', submission)
    print('Keyframe job:', shot, submission['id'], flush=True)
    collect_keyframe(shot)


def collect_keyframe(shot):
    folder = PROJECT / 'references/assets' / shot
    job_id = json.loads((folder / 'submission.json').read_text())['id']
    deadline = time.monotonic() + 900
    while not (folder / 'result.json').exists():
        result = client.api(ENDPOINT, 'status/' + job_id)
        client.save(folder / 'status.json', result)
        print(shot, result['status'], flush=True)
        if result['status'] == 'COMPLETED':
            client.save(folder / 'result.json', result)
            break
        if result['status'] in {'FAILED', 'TIMED_OUT', 'CANCELLED'}:
            raise RuntimeError('Terminal keyframe failure; response preserved')
        if time.monotonic() > deadline:
            raise TimeoutError('Use collect-keyframe; no resubmission')
        time.sleep(5)
    result = json.loads((folder / 'result.json').read_text())
    url = result['output']['result']
    original = folder / 'original.jpg'
    if not original.exists():
        with urllib.request.urlopen(url, timeout=60) as response:
            raw = response.read()
        with original.open('xb') as output:
            output.write(raw)
    im = Image.open(original).convert('RGB')
    anchor = folder / 'anchor.png'
    if not anchor.exists():
        im.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(anchor)
    client.save(folder / 'lineage.json', {'job_id': job_id, 'original_sha256': sha(original), 'original_dimensions': list(im.size), 'anchor_sha256': sha(anchor), 'resize': [WIDTH, HEIGHT], 'reported_cost_usd': result['output'].get('cost')})
    print('Collected:', folder, flush=True)


def shot_graph(shot):
    graph = experiment.make_graph(.24, FRAMES, 'story-' + shot)
    graph.pop('4'); graph.pop('5')
    graph['6'] = {'class_type': 'LoadImage', 'inputs': {'image': 'anchor.png'}}
    graph['2']['inputs']['text'] = SHOTS[shot]
    graph['12']['inputs']['prompts'] = '0: ' + SHOTS[shot]
    graph['7']['inputs'].update(width=WIDTH, height=HEIGHT, seed=143)
    graph['8']['inputs'].update(zoom='0:(1.015)', rotation_3d_z='0:(0)')
    graph['10']['inputs'].update(start_frame=0, end_frame=FRAMES, steps=24, cfg=5.0, noise=0.0, sharpen=0.0)
    return graph


def render(shot):
    experiment.project_for_run(PROJECT.name, 'story')
    source = PROJECT / 'references/assets' / shot / 'anchor.png'
    run = client.submit(PROJECT, 'story', shot_graph(shot), FRAMES,
                        {'shot': shot, 'experiment_id': 'E01', 'source_sha256': sha(source), 'recipe_sha256': sha(Path(__file__)), 'includes_anchor': True}, source)
    print('Shot collected:', shot, run, flush=True)


def assemble():
    ranges = []
    for shot in SHOTS:
        candidates = []
        for path in (PROJECT / 'runs').glob('*/submission.json'):
            receipt = json.loads(path.read_text())
            if receipt.get('shot') == shot and receipt.get('collected_at'):
                candidates.append(path.parent)
        if len(candidates) != 1:
            raise ValueError(f'Explicit selection needed for {shot}: {len(candidates)} collected runs')
        ranges.append({'run': candidates[0].name, 'in': 0, 'out': FRAMES})
    export = editing.assemble(PROJECT, 'e01-v001', ranges)
    print(export / 'preview.mp4')


def review():
    video = PROJECT / 'exports/e01-v001/preview.mp4'
    subprocess.run([sys.executable, str(APP / 'video_review.py'), str(video),
                    '--overview', '0', '--at', '0', '--at', '2', '--at', '6',
                    '--at', '10', '--at', '11.875', '--event', 'signal cut=4',
                    '--event', 'reveal cut=8', '--before', '.125', '--after', '.125'], check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'keyframe', 'collect-keyframe', 'render', 'assemble', 'review'])
    parser.add_argument('shot', nargs='?', choices=list(SHOTS))
    args = parser.parse_args()
    if args.action in {'keyframe', 'collect-keyframe', 'render'} and not args.shot:
        parser.error('A shot is required')
    if args.action == 'prepare': prepare()
    elif args.action == 'keyframe': keyframe(args.shot)
    elif args.action == 'collect-keyframe': collect_keyframe(args.shot)
    elif args.action == 'render': render(args.shot)
    elif args.action == 'assemble': assemble()
    elif args.action == 'review': review()
