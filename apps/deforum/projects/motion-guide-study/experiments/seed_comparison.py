"""Same-model seed study. Run with uv run --env-file .env --with pillow python.
Stages: opening, preview, continue; use experiment.py collect for interrupted jobs.
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
import editing
import serverless_client

SEED, WIDTH, HEIGHT, FPS, FRAMES = 7301, 1024, 576, 8, 48
STEPS, CFG, DENOISE, ZOOM = 18, 4.5, 0.58, 1.002
PROMPT = ('an immense hollow alien portal with a broad perforated ivory rim and a dark teal mechanical exoskeleton, '
          'a vast empty unobstructed black opening through its center, asymmetrical porous structures and curled cables around the rim, '
          'a tiny lone explorer standing beneath it, small terracotta orange nebula wisps in the lower left, '
          'deep black space surrounding the portal, richly detailed hand drawn science fiction art, '
          'bold science fiction comic book illustration, thick confident black ink contours, '
          'intricate engraved hatching and crisp small line details, flat cel shaded colors, '
          'deep black background, petrol teal shadows, pale cyan and ivory highlights, '
          'burnt orange accent shapes, restricted orange teal cream palette, graphic poster composition')
NEGATIVE = ('photograph, 3d render, glossy plastic, soft shading, blurry, muddy, washed out, pastel, text, lettering, '
            'watermark, logo, simple icon, flat white ring, gray monochrome, spokes, wheel, hub, clock, solid orange background')
OUT = PROJECT / 'exports/seed-v001'
MODES = ('fixed', 'increment')


def node(kind, **inputs):
    return {'class_type': kind, 'inputs': inputs}


def base():
    return {'1': node('CheckpointLoaderSimple', ckpt_name='sd_xl_base_1.0.safetensors'),
        '21': node('LoraLoader', model=['1', 0], clip=['1', 1], lora_name='xl_more_art-full_v1.safetensors',
                   strength_model=1.1, strength_clip=1.1),
        '2': node('CLIPTextEncode', clip=['21', 1], text=PROMPT),
        '3': node('CLIPTextEncode', clip=['21', 1], text=NEGATIVE)}


def opening_graph():
    g = base()
    g['4'] = node('EmptyLatentImage', width=WIDTH, height=HEIGHT, batch_size=1)
    g['5'] = node('KSampler', model=['21', 0], positive=['2', 0], negative=['3', 0],
                  latent_image=['4', 0], seed=SEED, steps=STEPS, cfg=CFG,
                  sampler_name='dpmpp_2m', scheduler='karras', denoise=1.0)
    g['6'] = node('VAEDecode', samples=['5', 0], vae=['1', 2])
    g['11'] = node('SaveImage', images=['6', 0], filename_prefix='seed-study/opening')
    return g


def pair_graph(start, end):
    g = base()
    g['6'] = node('LoadImage', image='anchor.png')
    g['7'] = node('DifforumAnimSetup', width=WIDTH, height=HEIGHT, fps=FPS, max_frames=FRAMES, seed=SEED)
    g['8'] = node('DifforumCamera', params=['7', 0], mode='2d', fov=45.0,
                  translation_x='0:(0)', translation_y='0:(0)', translation_z='0:(0)',
                  rotation_3d_x='0:(0)', rotation_3d_y='0:(0)', rotation_3d_z='0:(0)', zoom=f'0:({ZOOM})')
    g['9'] = node('DifforumSchedule', params=['7', 0], schedule=f'0:({DENOISE})', easing='linear')
    for i, mode in enumerate(MODES):
        crop, sampler = str(30+i), str(40+i)
        g[crop] = node('ImageCrop', image=['6', 0], width=WIDTH, height=HEIGHT, x=i*WIDTH, y=0)
        g[sampler] = node('DifforumFeedbackSampler', model=['21', 0], positive=['2', 0], negative=['3', 0],
            vae=['1', 2], params=['7', 0], camera=['8', 0], init_image=[crop, 0], strength_schedule=['9', 0],
            steps=STEPS, cfg=CFG, sampler_name='dpmpp_2m', scheduler='karras', color_coherence=0.0,
            color_mode='lab', symmetry='none', symmetry_segments=6, cadence=1, seed_mode=mode,
            noise=0.0, sharpen=0.0, border='reflection', start_frame=start, end_frame=end)
    g['50'] = node('ImageBatch', image1=['40', 0], image2=['41', 0])
    g['11'] = node('SaveImage', images=['50', 0], filename_prefix='seed-study/paired')
    return g


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pixel_sha(path):
    from PIL import Image
    with Image.open(path) as im:
        return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()


def record(stage, run):
    (OUT / f'{stage}-run.json').write_text(json.dumps({'run': str(run.relative_to(PROJECT))}, indent=2)+'\n')


def packed(paths, target):
    from PIL import Image
    canvas = Image.new('RGB', (WIDTH*2, HEIGHT))
    for i, path in enumerate(paths):
        with Image.open(path) as im:
            if im.size != (WIDTH, HEIGHT):
                raise ValueError('Unexpected source dimensions')
            canvas.paste(im.convert('RGB'), (i*WIDTH, 0))
    canvas.save(target)


def review():
    import subprocess
    common = [sys.executable, str(APP / 'video_review.py'), str(OUT / 'fixed/continue.mp4'),
              '--compare', str(OUT / 'increment/continue.mp4'), '--label', 'Fixed seed',
              '--compare-label', 'Changing seed', '--output-root', str(OUT / 'reviews'),
              '--columns', '4', '--page-size', '12']
    subprocess.run(common + ['--overview', '6', '--max-frames', '12'], check=True)
    early = ['--overview', '0', '--max-frames', '24']
    for f in range(12):
        early += ['--at', str(f / FPS)]
    subprocess.run(common + early, check=True)


def run(stage):
    if stage == 'opening':
        OUT.mkdir(parents=True, exist_ok=False)
        folder = serverless_client.submit(PROJECT, 'seed-opening', opening_graph(), 1,
            lineage={'sequence_kind': 'one original opening still', 'seed': SEED, 'study': 'same-model-seed-comparison'})
        record(stage, folder)
        shutil.copyfile(folder / 'frames/0000.png', OUT / 'opening.png')
        return
    if (OUT / f'{stage}-run.json').exists():
        raise FileExistsError('Stage already completed; preserve it')
    start, end = (0, 4) if stage == 'preview' else (3, FRAMES)
    sources = [OUT / 'opening.png']*2 if stage == 'preview' else [
        OUT / f'{mode}/frames/0003.png' for mode in MODES]
    source = OUT / f'{stage}-inputs.png'
    if source.exists():
        raise FileExistsError('Prepared stage exists; inspect receipts and collect rather than resubmit')
    packed(sources, source)
    n = end-start
    folder = serverless_client.submit(PROJECT, f'seed-{stage}-paired', pair_graph(start, end), n*2,
        source=source, lineage={'study': 'same-model-seed-comparison',
            'sequence_kind': 'two branches concatenated for transport; split before playback',
            'branch_order': list(MODES), 'branch_start': start, 'branch_end_exclusive': end,
            'source_sha256': [sha(p) for p in sources],
            'sampling_seeds': {m: [SEED if m == 'fixed' else SEED+f for f in range(start+1, end)] for m in MODES},
            'checkpoint_boundary': 'Both reload an 8-bit PNG at frame 3' if start else None})
    record(stage, folder)
    for branch, mode in enumerate(MODES):
        frames = OUT / mode / 'frames'
        frames.mkdir(parents=True, exist_ok=True)
        for i in range(n):
            src, dst = folder / f'frames/{branch*n+i:04d}.png', frames / f'{start+i:04d}.png'
            if dst.exists():
                if pixel_sha(src) != pixel_sha(dst):
                    raise ValueError('Continuation anchor changed')
            else:
                shutil.copyfile(src, dst)
        editing.encode(frames, OUT / mode / f'{stage}.mp4', fps=FPS)
    if stage == 'preview':
        assert pixel_sha(OUT / 'fixed/frames/0000.png') == pixel_sha(OUT / 'increment/frames/0000.png') == pixel_sha(OUT / 'opening.png')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=('opening', 'preview', 'continue', 'check', 'review'))
    args = p.parse_args()
    if args.stage == 'check':
        g = pair_graph(0, 4)
        a, b = g['40']['inputs'].copy(), g['41']['inputs'].copy()
        assert a.pop('seed_mode') == 'fixed' and b.pop('seed_mode') == 'increment'
        a.pop('init_image'); b.pop('init_image')
        assert a == b
        assert a['noise'] == a['sharpen'] == a['color_coherence'] == 0
        assert all(opening_graph()[k] == g[k] for k in base())
        assert pair_graph(3, FRAMES)['41']['inputs']['start_frame'] == 3
        print('Matched controls, common model/conditioning and absolute continuation indexing verified.')
    elif args.stage == 'review':
        review()
    else:
        run(args.stage)
