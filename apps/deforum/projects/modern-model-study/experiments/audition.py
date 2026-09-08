"""Same-model opening, edit probes and a cadence-3 twist. Run from apps/deforum."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

APP = Path(__file__).resolve().parents[3]
PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP))
sys.path.insert(0, str(APP/'projects/motion-guide-study/experiments'))
import numpy as np
from PIL import Image
import editing
import modern_workflows as workflows
import serverless_client as transport
import spatial_sequence as motion

OUT = PROJECT/'exports/audition-v001'
SEED, FPS, CADENCE, FRAMES = 92731, 12, 3, 36
PROMPTS = {
 'klein': 'A hand-inked science-fiction illustration. A lone small explorer stands beneath a huge porous alien arch. One flame-shaped light floats inside the opening. Curled cables and perforated stone frame deep teal space. Thick black contours, fine engraved hatching and flat colors in burnt orange, pale cyan and ivory. Wide composition with the explorer near the lower center.',
 'krea': 'An intricate surreal science-fiction illustration drawn in black ink with flat screen-printed colors. A tiny solitary explorer in an ivory spacesuit stands near the lower center of a wide landscape, beneath a gigantic asymmetrical arch of perforated coral-like stone and coiling cables. A single orange flame-shaped light hangs in the arch opening. The architecture curls inward around the light, with hundreds of small holes, delicate hatching and interlocking organic contours. Deep teal space and pale cyan distant ridges show through the arch. Burnt orange highlights, ivory paper-colored stone, clear black outlines, finely drawn details and broad quiet areas of flat color. The drawing fills the entire frame.'
}
EDIT = 'Add two fine branching ink strokes inside the existing orange flame. Keep the flame\'s outer silhouette. Keep every other contour, bent shape, tilted pose, object position, color and the framing exactly as in the reference image. Retain the same hand-inked illustration style.'
OPENING_PROMPTS = {
 'klein': [PROMPTS['klein'], PROMPTS['klein']+' The arch fills the upper two thirds of the image, with clustered circular cavities and tightly curled stone tendrils. Fine black lines describe the rough surface. The orange light contrasts with the cool landscape. The explorer is small enough to establish the enormous scale of the arch. The illustration extends to every edge.'],
 'krea': ['An ink-drawn surreal science-fiction landscape in flat burnt orange, ivory and deep teal. A tiny spacesuited explorer stands beneath an enormous arch of porous stone and coiling cables. One flame-shaped light hangs inside the arch. Intricate black hatching and organic contours, quiet flat-color space beyond, wide full-frame composition.', PROMPTS['krea']],
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2)+'\n'
    if p.exists() and p.read_text() != text:
        raise ValueError(f'Refusing changed record: {p}')
    if not p.exists():
        p.write_text(text)


def copy(source, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert sha(target) == sha(source), target
    else:
        shutil.copyfile(source, target)


def image(p, rgb):
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        assert np.array_equal(np.asarray(Image.open(p).convert('RGB')), rgb), p
    else:
        Image.fromarray(rgb).save(p)


def run(name, graph, source=None):
    matches = sorted((PROJECT/'runs').glob('*-'+name+'-1f'))
    # A human/agent must inspect an expired request and explicitly record the
    # absence of outputs before permitting a replacement submission.
    active = []
    for folder in matches:
        resolution = folder/'resubmission-resolution.json'
        if resolution.exists():
            decision = json.loads(resolution.read_text())
            assert decision['action'] == 'resubmit-expired-queue-with-no-outputs'
            assert decision['cloud_objects'] == 0 and decision['workers'] == 0
        else:
            active.append(folder)
    matches = active
    if matches:
        if len(matches) != 1:
            raise RuntimeError(f'Multiple attempts need explicit review: {name}')
        folder = matches[0]
        assert json.loads((folder/'workflow.api.json').read_text()) == graph
        if source:
            assert sha(folder/'anchor.png') == sha(source)
        receipt = json.loads((folder/'submission.json').read_text())
        if not receipt.get('job_id'):
            raise RuntimeError(f'Uncertain submission; inspect {folder}')
        transport.collect(folder)
        return folder
    return transport.submit(PROJECT, name, graph, 1, source=source, lineage={
        'study': 'modern-model-audition-v001',
        'models_sha256': sha(APP/'serverless/modern-models.json'),
        'graph_builder_sha256': sha(Path(workflows.__file__)),
        'source_sha256': sha(source) if source else None,
    })


def openings(model):
    for index in range(2):
        g = workflows.graph(model, OPENING_PROMPTS[model][index], SEED)
        folder = run(f'audition-{model}-opening-{index}', g)
        copy(folder/'frames/0000.png', OUT/model/f'opening-{index}.png')


def select(model, index):
    source = OUT/model/f'opening-{index}.png'
    save(OUT/model/'selection.json', {'index': index, 'sha256': sha(source), 'prompt': OPENING_PROMPTS[model][index]})
    copy(source, OUT/model/'opening.png')
    rgb = np.asarray(Image.open(source).convert('RGB'))
    for f in range(FRAMES):
        image(OUT/model/f'motion-only/frames/{f:04d}.png', motion.warp(rgb, 0, f))
    target = OUT/model/'motion-only/preview.mp4'
    if not target.exists():
        editing.encode(target.parent/'frames', target, fps=FPS)
    # Mid-shot warp is deliberately visible; separate from the small first cadence step.
    image(OUT/model/'probe-warp.png', motion.warp(rgb, 0, 18))


def probe(model, instruction=False, denoise=.45):
    label = 'instruction' if instruction else 'scene'
    name = f'{label}-d{round(denoise*100):03d}' if model == 'krea' else label
    prompt = EDIT if instruction else json.loads((OUT/model/'selection.json').read_text())['prompt']
    g = workflows.graph(model, prompt, SEED+1, editing=True, denoise=denoise)
    folder = run(f'audition-{model}-probe-{name}', g, OUT/model/'probe-warp.png')
    copy(folder/'frames/0000.png', OUT/model/f'probe-{name}.png')


def feedback(model, instruction, denoise, until):
    label = 'instruction' if instruction else 'scene'
    name = label if model == 'klein' else f'{label}-d{round(denoise*100):03d}'
    root = OUT/model/name
    root.mkdir(parents=True, exist_ok=True)
    prompt = EDIT if instruction else json.loads((OUT/model/'selection.json').read_text())['prompt']
    save(root/'manifest.json', {'model': model, 'prompt': prompt, 'denoise': None if model=='klein' else denoise,
        'fps': FPS, 'cadence': CADENCE, 'frames': FRAMES, 'seed': SEED,
        'opening_sha256': sha(OUT/model/'opening.png'),
        'motion_source': str(Path(motion.__file__).relative_to(APP)), 'motion_sha256': sha(Path(motion.__file__)),
        'cadence_method': 'warp both neighboring generated anchors to output time, then blend; intermediate frames never feed generation',
        'graph': workflows.graph(model, prompt, SEED+1, editing=True, denoise=denoise)})
    copy(OUT/model/'opening.png', root/'anchors/0000.png')
    for f in range(3, min(until, FRAMES)+1, 3):
        source = root/f'warped-inputs/{f:04d}.png'
        rgb = np.asarray(Image.open(root/f'anchors/{f-3:04d}.png').convert('RGB'))
        image(source, motion.warp(rgb, f-3, f))
        g = workflows.graph(model, prompt, SEED+f//3, editing=True, denoise=denoise)
        folder = run(f'audition-{model}-{name}-{f:04d}', g, source)
        copy(folder/'frames/0000.png', root/f'anchors/{f:04d}.png')
        save(root/f'anchor-{f:04d}.json', {'run': str(folder.relative_to(PROJECT)), 'sha256': sha(folder/'frames/0000.png')})
        print(f'{model} {name}: {f//3}/12 anchors', flush=True)
    if until >= FRAMES:
        finish(root)


def finish(root):
    rows = []
    for f in range(FRAMES):
        a = f//3*3; b = a+3; alpha = (f-a)/3
        left = np.asarray(Image.open(root/f'anchors/{a:04d}.png').convert('RGB'))
        if not alpha:
            rgb = left
        else:
            right = np.asarray(Image.open(root/f'anchors/{b:04d}.png').convert('RGB'))
            rgb = np.rint(motion.warp(left, a, f)*(1-alpha)+motion.warp(right, b, f)*alpha).astype('uint8')
        p = root/f'cadence/frames/{f:04d}.png'; image(p, rgb)
        rows.append({'frame': f, 'sha256': sha(p), 'left': a, 'right': b, 'blend': alpha})
    save(root/'cadence/manifest.json', {'fps': FPS, 'frames': rows})
    target = root/'cadence/preview.mp4'
    if not target.exists():
        editing.encode(target.parent/'frames', target, fps=FPS)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=('openings', 'select', 'probe', 'feedback'))
    p.add_argument('model', choices=tuple(PROMPTS)); p.add_argument('--index', type=int, choices=(0,1), default=0)
    p.add_argument('--instruction', action='store_true'); p.add_argument('--denoise', type=float, default=.45)
    p.add_argument('--until', type=int, default=24); a = p.parse_args()
    if a.stage == 'openings': openings(a.model)
    elif a.stage == 'select': select(a.model, a.index)
    elif a.stage == 'probe': probe(a.model, a.instruction, a.denoise)
    else: feedback(a.model, a.instruction, a.denoise, a.until)
