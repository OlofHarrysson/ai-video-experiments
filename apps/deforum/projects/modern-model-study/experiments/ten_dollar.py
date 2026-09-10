"""Self-contained recurrent Krea shot runner for the ten-dollar creative session."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

import numpy as np
from PIL import Image

APP = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(APP))
import pod_client
from modern_workflows import graph, node
from spatial_warp import remap_rgb

OUT = Path(__file__).resolve().parents[1] / 'exports/ten-dollar-v001'
FPS, CADENCE = 24, 12
SIGMAS = [0.6, 0.512844085693, 0.310901075602, 0.0]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert json.loads(path.read_text()) == data, path
    else:
        path.write_text(json.dumps(data, indent=2) + '\n')


def ease(t, start, end):
    u = np.clip((t-start)/(end-start), 0, 1)
    return u*u*(3-2*u)


def transform(points, seconds, motion, inverse=False):
    """Invertible radial twist then similarity transform, in image-height units.

    Each phrase gives its total displacement; time controls its eased progress.
    Radial twist preserves radius, so negating its angle is the exact inverse.
    """
    center = np.array(motion.get('center', [0.75, 0.5]))
    progress = ease(seconds, 0, motion.get('settle', 2.5))
    late = ease(seconds, *motion.get('travel_window', [3.0, 6.0]))
    shift = np.array(motion.get('travel', [0, 0])) * late
    scale = 1 + motion.get('zoom', 0.12) * progress
    angle = np.deg2rad(motion.get('turn', 20)) * progress
    radius = motion.get('radius', 0.7)
    q = (points-center-shift)/scale if inverse else points-center
    theta = angle*np.exp(-np.sum(q*q, axis=-1)/(radius*radius))
    if inverse:
        theta = -theta
    c, s = np.cos(theta), np.sin(theta)
    rotated = np.stack([q[..., 0]*c-q[..., 1]*s, q[..., 0]*s+q[..., 1]*c], -1)
    return center + rotated if inverse else center + rotated*scale + shift


def warp(rgb, start, end, motion):
    if start == end:
        return rgb.copy()
    h, w = rgb.shape[:2]
    y, x = np.mgrid[:h, :w].astype(np.float32)
    points = np.stack([x/h, y/h], -1)
    original = transform(points, end, motion, inverse=True)
    coords = transform(original, start, motion)*h
    return remap_rgb(rgb, coords.astype(np.float32))


def repaint_graph(prompt, seed, sigmas=SIGMAS):
    g = graph('krea', prompt, seed)
    del g['6']
    g['20'] = node('LoadImage', image='anchor.png')
    g['24'] = node('VAEEncode', pixels=['20', 0], vae=['3', 0])
    g['42'] = node('KSamplerSelect', sampler_name='euler')
    g['43'] = node('ManualSigmas', sigmas=', '.join(f'{v:.12f}' for v in sigmas))
    g['9'] = node('SamplerCustom', model=['1', 0], add_noise=True, noise_seed=seed,
        cfg=1., positive=['4', 0], negative=['5', 0], sampler=['42', 0],
        sigmas=['43', 0], latent_image=['24', 0])
    return g


def submit_once(name, g, source=None, lineage=None):
    (OUT/'runs').mkdir(parents=True, exist_ok=True)
    matches = list((OUT/'runs').glob('*-'+name+'-1f'))
    if matches:
        assert len(matches) == 1
        run = matches[0]
        assert json.loads((run/'workflow.api.json').read_text()) == g
        if source:
            assert sha(run/'anchor.png') == sha(source)
        pod_client.collect(run)
        return run
    return pod_client.submit(OUT, name, g, 1, source=source, lineage=lineage)


def render(config, stage):
    case = config['case']
    root = OUT/case
    save(root/'config.json', config)
    (root/'anchors').mkdir(parents=True, exist_ok=True)
    start_frame = config.get('branch_frame', 0)
    if start_frame:
        prefix = OUT/config['prefix_source']
        original = json.loads((prefix/'config.json').read_text())
        assert original['motion'] == config['motion'] and original['seed'] == config['seed']
        copied = {}
        for f in range(0, start_frame+1, CADENCE):
            src = prefix/f'anchors/{f:04d}.png'
            shutil.copyfile(src, root/f'anchors/{f:04d}.png')
            copied[str(f)] = sha(src)
            if f:
                shutil.copyfile(prefix/f'anchor-{f:04d}.json', root/f'anchor-{f:04d}.json')
                (root/'warped-inputs').mkdir(exist_ok=True)
                shutil.copyfile(prefix/f'warped-inputs/{f:04d}.png', root/f'warped-inputs/{f:04d}.png')
        save(root/'prefix.json', {'source': config['prefix_source'], 'through_frame':start_frame,
            'source_config_sha256':sha(prefix/'config.json'), 'painting_sha256':copied})
    if not (root/'anchors/0000.png').exists():
        if config.get('opening_source'):
            source = OUT/config['opening_source']/'anchors/0000.png'
            shutil.copyfile(source, root/'anchors/0000.png')
            save(root/'opening.json', {'source': str(source.relative_to(OUT)), 'sha256': sha(source)})
        else:
            g = graph('krea', config['prompts'][0]['text'], config['seed'])
            g['6']['inputs'].update(width=1536, height=1024)
            g['11']['inputs']['filename_prefix'] = 'ten-dollar/'+case+'/opening'
            run = submit_once('ten-dollar-'+case+'-opening', g)
            shutil.copyfile(run/'frames/0000.png', root/'anchors/0000.png')
            save(root/'opening.json', {'run': str(run.relative_to(OUT)), 'sha256': sha(root/'anchors/0000.png')})
    if stage == 'opening':
        return
    for f in range(start_frame+CADENCE, round(config['duration']*FPS), CADENCE):
        seconds = f/FPS
        parent = root/f'anchors/{f-CADENCE:04d}.png'
        source = root/f'warped-inputs/{f:04d}.png'
        source.parent.mkdir(exist_ok=True)
        rgb = np.asarray(Image.open(parent).convert('RGB'))
        Image.fromarray(warp(rgb, seconds-.5, seconds, config['motion'])).save(source)
        prompt = [p for p in config['prompts'] if p['at'] <= seconds][-1]['text']
        sigmas = config.get('sigmas', SIGMAS)
        for schedule in config.get('sigma_schedule', []):
            if schedule['at'] <= seconds:
                sigmas = schedule['values']
        seed = config['seed'] + f//CADENCE
        g = repaint_graph(prompt, seed, sigmas)
        g['11']['inputs']['filename_prefix'] = 'ten-dollar/'+case
        run = submit_once(f'ten-dollar-{case}-{f:04d}', g, source,
            {'parent_sha256': sha(parent), 'frame': f, 'seconds': seconds, 'seed': seed,
             'initialization': 'warped previous generated painting', 'case': case})
        output = root/f'anchors/{f:04d}.png'
        shutil.copyfile(run/'frames/0000.png', output)
        save(root/f'anchor-{f:04d}.json', {'run': str(run.relative_to(OUT)), 'seed': seed,
            'parent_sha256': sha(parent), 'initialization_sha256': sha(source), 'output_sha256': sha(output)})
        print(f'{case}: {seconds:.1f}s / {config["duration"]}s', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('config', type=Path)
    p.add_argument('--deployment', type=Path, required=True)
    p.add_argument('--stage', choices=['opening', 'animation'], default='animation')
    args = p.parse_args()
    pod_client.DEPLOYMENT = args.deployment.resolve()
    render(json.loads(args.config.read_text()), args.stage)
