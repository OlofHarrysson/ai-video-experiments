"""Motion-guide demonstration: deterministic local warp, native ComfyUI repaint.

From apps/deforum:
uv run --python 3.12 --with opencv-python-headless==4.12.0.88 --with pillow==12.1.0 python projects/motion-guide-study/experiments/walkthrough.py prepare
uv run --env-file .env python projects/motion-guide-study/experiments/walkthrough.py repaint marsh
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

PROJECT = Path(__file__).resolve().parents[1]
APP = PROJECT.parents[1]
sys.path.insert(0, str(APP))
WIDTH, HEIGHT = 1024, 576
ASSETS = PROJECT / 'references/assets/v001'
GUIDE = APP / 'projects/reference-studies/references/assets/artist-channel-2026-09-07/hybrid-guides/Circle-Zoom-30s.mp4'
ART = {
    'marsh': {'source': APP / 'projects/seedream-motion/references/assets/seedream-v001/anchor.png',
              'lora': 0.0,
              'prompt': 'a glowing copper lantern hanging from a close willow branch beside a winding wooden boardwalk over a moonlit marsh, blue luminous mushrooms, distant domed observatory, purple mist, crescent moon, teal and amber painterly fantasy landscape, intricate brushwork, atmospheric illustration'},
    'portal': {'source': APP / 'projects/brain-entity-study/exports/p03-rife-24fps/frames/0000.png',
               'lora': 1.1,
               'prompt': 'an immense circular alien mechanical portal, intricate teal and orange engraved rings surrounding an open black center and a glowing orange sun, tiny lone explorer beneath, bold science fiction comic book illustration, thick black ink contours, crisp engraved details, flat cel shaded colors, restricted orange teal cream palette'},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def warp(image, flow, factor=0.8):
    """Forward displacement becomes destination-to-source coordinates for remap."""
    import cv2
    import numpy as np
    h, w = image.shape[:2]
    x, y = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    coordinates = np.stack([x, y], axis=-1) - float(factor) * flow
    return cv2.remap(image, coordinates, None, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101)


def prepare():
    import cv2
    import numpy as np
    from PIL import Image
    ASSETS.mkdir(parents=True, exist_ok=False)
    video = cv2.VideoCapture(str(GUIDE))
    fps = video.get(cv2.CAP_PROP_FPS)
    assert abs(fps - 12) < 1e-6
    frames = {}
    for index in (72, 73, 84):
        video.set(cv2.CAP_PROP_POS_FRAMES, index)
        ok, frame = video.read()
        if not ok:
            raise RuntimeError(f'Missing guide frame {index}')
        frames[index] = cv2.resize(frame, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA)
        cv2.imwrite(str(ASSETS / f'guide-{index}.png'), frames[index])
    video.release()
    manifest = {'guide': str(GUIDE.relative_to(APP)), 'guide_sha256': sha(GUIDE),
                'width': WIDTH, 'height': HEIGHT, 'fps': fps,
                'opencv': cv2.__version__, 'numpy': np.__version__,
                'flow_method': 'DIS Medium', 'flow_factor': 0.8,
                'flow_initialization': 'fresh per pair, no previous-flow warm start',
                'pairs': {}, 'artworks': {}}
    for label, end in [('adjacent', 73), ('visible', 84)]:
        dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        flow = dis.calc(cv2.cvtColor(frames[72], cv2.COLOR_BGR2GRAY),
                        cv2.cvtColor(frames[end], cv2.COLOR_BGR2GRAY), None)
        assert np.isfinite(flow).all()
        np.save(ASSETS / f'flow-{label}.npy', flow)
        magnitude = np.linalg.norm(flow * 0.8, axis=-1)
        vectors = [[x, y, round(float(flow[y, x, 0]), 4), round(float(flow[y, x, 1]), 4)]
                   for y in range(16, HEIGHT, 32) for x in range(16, WIDTH, 32)
                   if np.linalg.norm(flow[y, x]) > 0.15]
        manifest['pairs'][label] = {'from': 72, 'to': end, 'gap_seconds': (end-72)/fps,
            'applied_displacement_p50_px': float(np.percentile(magnitude, 50)),
            'applied_displacement_p95_px': float(np.percentile(magnitude, 95)),
            'applied_displacement_max_px': float(magnitude.max()), 'vectors': vectors}
    for name, spec in ART.items():
        original = Image.open(spec['source']).convert('RGB').resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)
        original.save(ASSETS / f'{name}-original.png')
        image = np.asarray(original)
        packed = Image.new('RGB', (WIDTH*3, HEIGHT))
        packed.paste(original, (0, 0))
        for i, label in enumerate(('adjacent', 'visible'), 1):
            flow = np.load(ASSETS / f'flow-{label}.npy')
            moved = Image.fromarray(warp(image, flow))
            moved.save(ASSETS / f'{name}-{label}-warped.png')
            packed.paste(moved, (WIDTH*i, 0))
        packed.save(ASSETS / f'{name}-packed.png')
        manifest['artworks'][name] = {'source': str(spec['source'].relative_to(APP)),
            'source_sha256': sha(spec['source']), 'prompt': spec['prompt'], 'lora': spec['lora']}
    manifest['files'] = {p.name: sha(p) for p in sorted(ASSETS.iterdir()) if p.is_file()}
    (ASSETS / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(json.dumps({k: {a:b for a,b in v.items() if a != 'vectors'} for k,v in manifest['pairs'].items()}, indent=2))


def node(kind, **inputs):
    return {'class_type': kind, 'inputs': inputs}


def graph(name):
    spec = ART[name]
    g = {'1': node('CheckpointLoaderSimple', ckpt_name='sd_xl_base_1.0.safetensors'),
         '2': node('CLIPTextEncode', clip=['1', 1], text=spec['prompt']),
         '3': node('CLIPTextEncode', clip=['1', 1], text='blurry, muddy, washed out, text, lettering, watermark, logo, photograph, glossy 3d render'),
         '4': node('LoadImage', image='anchor.png')}
    model = ['1', 0]
    if spec['lora']:
        g['5'] = node('LoraLoader', model=model, clip=['1', 1], lora_name='xl_more_art-full_v1.safetensors',
                      strength_model=spec['lora'], strength_clip=spec['lora'])
        model = ['5', 0]
        g['2']['inputs']['clip'] = g['3']['inputs']['clip'] = ['5', 1]
    previous = None
    for i in range(3):
        base = 100 + i*10
        g[str(base)] = node('ImageCrop', image=['4', 0], width=WIDTH, height=HEIGHT, x=i*WIDTH, y=0)
        g[str(base+1)] = node('VAEEncode', pixels=[str(base), 0], vae=['1', 2])
        g[str(base+2)] = node('KSampler', model=model, positive=['2', 0], negative=['3', 0],
            latent_image=[str(base+1), 0], seed=2215137870, steps=18, cfg=4.5,
            sampler_name='dpmpp_2m', scheduler='karras', denoise=0.58)
        g[str(base+3)] = node('VAEDecode', samples=[str(base+2), 0], vae=['1', 2])
        current = [str(base+3), 0]
        if previous:
            g[str(base+4)] = node('ImageBatch', image1=previous, image2=current)
            current = [str(base+4), 0]
        previous = current
    g['11'] = node('SaveImage', images=previous, filename_prefix='motion-guide-repaint')
    return g


def repaint(name):
    import serverless_client
    (PROJECT / 'runs').mkdir(exist_ok=True)
    folder = serverless_client.submit(PROJECT, f'{name}-matched-repaint', graph(name), 3,
        source=ASSETS / f'{name}-packed.png', lineage={'study': 'motion-guide-walkthrough',
        'sequence_kind': 'independent matched still comparisons, not animation',
        'conditions': ['original', 'adjacent', 'visible'],
        'guide_manifest_sha256': sha(ASSETS / 'manifest.json')})
    out = PROJECT / 'exports/v001'
    out.mkdir(parents=True, exist_ok=True)
    for index, label in enumerate(('original', 'adjacent', 'visible')):
        target = out / f'{name}-{label}-repainted.png'
        if target.exists():
            raise FileExistsError(target)
        shutil.copyfile(folder / f'frames/{index:04d}.png', target)
    (out / f'{name}-run.json').write_text(json.dumps({'run': str(folder.relative_to(PROJECT))}, indent=2)+'\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('mode', choices=['prepare', 'repaint'])
    p.add_argument('artwork', choices=list(ART), nargs='?')
    args = p.parse_args()
    if args.mode == 'prepare':
        prepare()
    elif args.artwork:
        repaint(args.artwork)
    else:
        p.error('repaint needs an artwork')
