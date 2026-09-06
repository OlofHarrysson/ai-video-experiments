"""Prepare a lossless guide strip locally; submit it through the shared client."""

import argparse
import copy
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import sys

from PIL import Image

APP = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
sys.dont_write_bytecode = True
import serverless_client

EXPERIMENT = 'independent-redraw'
FRAMES = 8
STEPS, CFG, DENOISE = 28, 6.5, 0.4
PROMPT = (
    'a moonlit marsh at blue hour, close tall reeds and a hanging copper lantern '
    'framing the left foreground, a winding wooden boardwalk over still water '
    'leading toward a distant small domed astronomical observatory, tiny amber '
    'lanterns along the boardwalk, luminous blue mushrooms, low violet mist, '
    'a crescent moon, cinematic wide composition, clear foreground middle ground '
    'and distant background, atmospheric dark fantasy illustration, textured '
    'painterly brushwork, deep teal and indigo with warm amber light'
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    with path.open('x') as output:
        json.dump(value, output, indent=2)
        output.write('\n')


def build_graph(parent, width, height, indices):
    graph = {key: copy.deepcopy(parent[key]) for key in ('1', '2', '3')}
    graph['6'] = {'class_type': 'LoadImage', 'inputs': {'image': 'anchor.png'}}
    seed = parent['7']['inputs']['seed']
    previous = None
    for order, index in enumerate(indices):
        crop, encode, sample, decode = [str(100 + 4 * order + i) for i in range(4)]
        graph[crop] = {'class_type': 'ImageCrop', 'inputs': {
            'image': ['6', 0], 'x': order * width, 'y': 0, 'width': width, 'height': height}}
        graph[encode] = {'class_type': 'VAEEncode', 'inputs': {
            'pixels': [crop, 0], 'vae': ['1', 2]}}
        graph[sample] = {'class_type': 'KSampler', 'inputs': {
            'model': ['1', 0], 'positive': ['2', 0], 'negative': ['3', 0],
            'latent_image': [encode, 0], 'seed': seed + index,
            'steps': STEPS, 'cfg': CFG, 'denoise': DENOISE,
            'sampler_name': 'dpmpp_2m', 'scheduler': 'karras'}}
        graph[decode] = {'class_type': 'VAEDecode', 'inputs': {
            'samples': [sample, 0], 'vae': ['1', 2]}}
        if previous is None:
            previous = [decode, 0]
        else:
            batch = str(200 + order)
            graph[batch] = {'class_type': 'ImageBatch', 'inputs': {
                'image1': previous, 'image2': [decode, 0]}}
            previous = [batch, 0]
    graph['11'] = {'class_type': 'SaveImage', 'inputs': {
        'images': previous, 'filename_prefix': 'guide-redraw'}}
    return graph


def prepare(guide_run, start=0):
    guide_run = guide_run.resolve()
    if start < 0:
        raise ValueError('Start frame must be nonnegative')
    receipt = json.loads((guide_run / 'submission.json').read_text())
    parent = json.loads((guide_run / 'workflow.api.json').read_text())
    if not receipt.get('collected_at') or receipt.get('phase') != 'guide':
        raise ValueError('Require a collected camera-only guide run')
    if receipt.get('project') != 'lantern-marsh' or parent['10']['class_type'] != 'DifforumGuideBuilder':
        raise ValueError('Require the lantern-marsh Difforum guide')
    if parent['2']['inputs']['text'] != PROMPT:
        raise ValueError('Guide prompt differs from the frozen lantern recipe')
    if parent['1']['inputs']['ckpt_name'] != 'sd_xl_base_1.0.safetensors':
        raise ValueError('Require the SDXL base checkpoint')
    indices = list(range(start, start + FRAMES))
    if indices[-1] >= receipt['frames']:
        raise ValueError('Guide must contain all eight consecutive selected positions')
    sources = [guide_run / 'frames' / f'{i:04d}.png' for i in indices]
    images = []
    for path in sources:
        with Image.open(path) as opened:
            if opened.mode != 'RGB':
                raise ValueError(f'Require RGB guide PNG: {path}')
            images.append(opened.copy())
    width, height = images[0].size
    if any(im.size != (width, height) for im in images) or width % 8 or height % 8:
        raise ValueError('All guide sizes must match and be divisible by eight')
    if width > 1280 or height > 720:
        raise ValueError('This bounded experiment supports guides up to 1280x720')
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    bundle = PROJECT / 'references' / 'assets' / f'{stamp}-guides-{start:04d}'
    bundle.mkdir(parents=True, exist_ok=False)
    frozen = bundle / 'guides'
    frozen.mkdir()
    strip = Image.new('RGB', (width * FRAMES, height))
    rows = []
    base_seed = parent['7']['inputs']['seed']
    for order, (index, source, im) in enumerate(zip(indices, sources, images)):
        target = frozen / f'{order:04d}.png'
        shutil.copyfile(source, target)
        strip.paste(im, (order * width, 0))
        rows.append({'output_frame': order, 'guide_frame': index, 'seed': base_seed + index,
                     'source': str(source), 'local': str(target.relative_to(bundle)),
                     'sha256': digest(source)})
    strip.save(bundle / 'anchor.png')
    with Image.open(bundle / 'anchor.png') as packed:
        for order, im in enumerate(images):
            crop = packed.crop((order * width, 0, (order + 1) * width, height))
            if crop.tobytes() != im.tobytes():
                raise RuntimeError('Guide strip round-trip changed pixels')
    shutil.copyfile(guide_run / 'workflow.api.json', bundle / 'guide-workflow.api.json')
    shutil.copyfile(Path(__file__), bundle / 'recipe.py')
    graph = build_graph(parent, width, height, indices)
    write_json(bundle / 'workflow.api.json', graph)
    lineage = {'recipe': 'guide-redraw/independent-redraw', 'phase': 'independent-redraw',
               'guide_run': str(guide_run), 'guide_job_id': receipt.get('job_id'),
               'reference_run': receipt.get('parent_run'), 'reference_sha256': receipt.get('parent_sha256'),
               'guide_workflow_sha256': digest(bundle / 'guide-workflow.api.json'),
               'workflow_sha256': digest(bundle / 'workflow.api.json'),
               'recipe_sha256': digest(bundle / 'recipe.py'),
               'input_bundle': str(bundle), 'strip_sha256': digest(bundle / 'anchor.png'),
               'width': width, 'height': height, 'frames': FRAMES,
               'steps': STEPS, 'cfg': CFG, 'denoise': DENOISE,
               'seed_mode': 'base seed plus original guide index', 'frame_map': rows,
               'includes_anchor': False, 'feedback': False,
               'start_frame': start, 'end_frame': start + FRAMES,
               'guide_packaging': 'horizontal RGB PNG; crop before VAE; pixel-exact round-trip verified'}
    write_json(bundle / 'lineage.json', lineage)
    return bundle


def submit(bundle):
    bundle = bundle.resolve()
    if bundle.parent != (PROJECT / 'references' / 'assets').resolve():
        raise ValueError('Bundle must belong to this project')
    lineage = json.loads((bundle / 'lineage.json').read_text())
    for filename, key in [('anchor.png', 'strip_sha256'), ('workflow.api.json', 'workflow_sha256'),
                          ('recipe.py', 'recipe_sha256'), ('guide-workflow.api.json', 'guide_workflow_sha256')]:
        if digest(bundle / filename) != lineage[key]:
            raise ValueError(f'Frozen input changed: {filename}')
    for row in lineage['frame_map']:
        if digest(bundle / row['local']) != row['sha256']:
            raise ValueError('Frozen guide changed')
    # Shared submission waits for collection. Claim before it to avoid uncertain resubmissions.
    write_json(bundle / 'submission-attempt.json', {
        'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'recovery': 'Inspect project runs; collect an existing job, never resubmit this bundle.'})
    graph = json.loads((bundle / 'workflow.api.json').read_text())
    folder = serverless_client.submit(PROJECT, EXPERIMENT, graph, FRAMES, lineage,
                                      source=bundle / 'anchor.png')
    write_json(bundle / 'collected-run.json', {'run': str(folder)})
    return folder


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    prep = commands.add_parser('prepare', help='Local only: preserve guides and freeze API graph')
    prep.add_argument('--guide-run', required=True, type=Path)
    prep.add_argument('--start-frame', type=int, default=0)
    send = commands.add_parser('submit', help='Paid: submit exactly one prepared bundle')
    send.add_argument('--bundle', required=True, type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        print(prepare(args.guide_run, args.start_frame))
    else:
        print(submit(args.bundle))


if __name__ == '__main__':
    main()
