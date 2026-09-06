"""Seedream reference, a stronger depth camera move, and two SDXL workflows."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

from PIL import Image

PROJECT = Path(__file__).resolve().parents[1]
APP = PROJECT.parents[1]
sys.path.insert(0, str(APP))
import experiment
import serverless_client
from workflow_recipes import independent_redraw_graph

SOURCE = APP / 'projects/model-comparison/runs/20260906T215118Z-seedream-4-f5a8fd86/original-00.jpg'
REFERENCE = PROJECT / 'references/assets/seedream-v001'
WIDTH, HEIGHT, FRAMES, SEED, STEP = 1280, 720, 40, 143, 0.012
PROMPT_SOURCE = APP / 'projects/lantern-marsh/experiments/overscan.py'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    REFERENCE.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(SOURCE, REFERENCE / 'original.jpg')
    with Image.open(SOURCE) as im:
        if im.size != (2560, 1440):
            raise ValueError('Unexpected Seedream source dimensions')
        im.convert('RGB').resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS).save(REFERENCE / 'anchor.png')
    serverless_client.save(REFERENCE / 'reference.json', {
        'source': str(SOURCE.relative_to(APP)), 'source_sha256': digest(SOURCE),
        'anchor_sha256': digest(REFERENCE / 'anchor.png'),
        'transform': 'RGB, Lanczos resize 2560x1440 to 1280x720; no crop'})
    print(REFERENCE)


def camera_graph(preview):
    import ast
    prompt = next(ast.literal_eval(n.value) for n in ast.parse(PROMPT_SOURCE.read_text()).body
                  if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PROMPT' for t in n.targets))
    graph = experiment.make_graph(.4, FRAMES, 'motion')
    graph.pop('4'); graph.pop('5')
    graph['6'] = {'class_type': 'LoadImage', 'inputs': {'image': 'anchor.png'}}
    graph['2']['inputs']['text'] = prompt
    graph['12']['inputs']['prompts'] = '0: ' + prompt
    graph['7']['inputs'].update(width=WIDTH, height=HEIGHT, seed=SEED)
    graph['10']['inputs'].update(start_frame=0, end_frame=FRAMES)
    return experiment.depth_camera_graph(graph, preview, FRAMES, translation_x=STEP)


def run(phase, guide_name, start):
    experiment.project_for_run(PROJECT.name, 'motion')
    ref = json.loads((REFERENCE / 'reference.json').read_text())
    anchor = REFERENCE / 'anchor.png'
    if digest(anchor) != ref['anchor_sha256'] or digest(REFERENCE / 'original.jpg') != ref['source_sha256']:
        raise ValueError('Preserved reference changed')
    metadata = {**ref, 'phase': phase, 'camera_step': STEP, 'start_frame': 0,
                'end_frame': FRAMES, 'includes_anchor': True, 'seed': SEED,
                'recipe_sha256': digest(Path(__file__))}
    graph = camera_graph(phase == 'guide')
    count = FRAMES
    if phase == 'redraw':
        if start not in range(0, FRAMES, 8) or not guide_name:
            raise ValueError('Provide a collected guide and a batch start 0,8,16,24,32')
        guide = (PROJECT / 'runs' / guide_name).resolve()
        if guide.parent != (PROJECT / 'runs').resolve():
            raise ValueError('Guide must belong to this project')
        receipt = json.loads((guide / 'submission.json').read_text())
        if not receipt.get('collected_at') or receipt.get('phase') != 'guide' or receipt['anchor_sha256'] != ref['anchor_sha256']:
            raise ValueError('Require a collected guide from this reference')
        bundle = REFERENCE / (guide_name + f'-batch-{start:02d}')
        bundle.mkdir(exist_ok=False)
        indices = list(range(start, start + 8))
        strip = Image.new('RGB', (8 * WIDTH, HEIGHT))
        mapping = []
        for order, index in enumerate(indices):
            source = guide / 'frames' / f'{index:04d}.png'
            with Image.open(source) as im:
                if im.size != (WIDTH, HEIGHT) or im.mode != 'RGB':
                    raise ValueError('Unexpected guide pixels')
                strip.paste(im, (order * WIDTH, 0))
            mapping.append({'global_frame': index, 'guide_sha256': digest(source), 'seed': SEED + index})
        anchor = bundle / 'anchor.png'
        strip.save(anchor)
        with Image.open(anchor) as packed:
            for order, index in enumerate(indices):
                with Image.open(guide / 'frames' / f'{index:04d}.png') as im:
                    if packed.crop((order*WIDTH, 0, (order+1)*WIDTH, HEIGHT)).tobytes() != im.tobytes():
                        raise ValueError('Guide packing changed pixels')
        graph = independent_redraw_graph(json.loads((guide / 'workflow.api.json').read_text()),
                                          WIDTH, HEIGHT, indices, preserve_anchor=True)
        count = 8
        metadata.update(guide_run=guide.name, start_frame=start, end_frame=start+8,
                        includes_anchor=start == 0, frame_map=mapping, strip_sha256=digest(anchor))
        serverless_client.save(bundle / 'lineage.json', metadata)
    serverless_client.submit(PROJECT, 'motion', graph, count, metadata, anchor)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['prepare', 'guide', 'feedback', 'redraw'])
    parser.add_argument('--guide-run')
    parser.add_argument('--start', type=int, default=0)
    args = parser.parse_args()
    if args.phase == 'prepare':
        prepare()
    else:
        run(args.phase, args.guide_run, args.start)
