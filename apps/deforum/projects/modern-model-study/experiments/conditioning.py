"""Bounded text-only / native-reference comparison. Run from apps/deforum."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
import audition as a

OUT = a.PROJECT/'exports/conditioning-v001'
MANIFEST = Path(__file__).with_name('conditioning-models.json')
FRAMES, FPS, CADENCE = 24, 12, 3
PRESERVE = "Reproduce the reference illustration faithfully. Preserve its warped geometry, object positions, contours, ink texture, exact colors, saturation and brightness. Keep the small explorer, arch and flame unchanged."
a.transport.DEPLOYMENT = a.APP/'work/conditioning-session/deployment.json'


def graph(model, prompt, seed, reference=False):
    if model == 'klein':
        return a.workflows.graph(model, prompt, seed, editing=reference)
    n = a.workflows.node
    g = {
        '1': n('UNETLoader', unet_name='krea2_turbo_int8_convrot.safetensors', weight_dtype='default'),
        '2': n('CLIPLoader', clip_name='qwen3vl_4b_fp8_scaled.safetensors', type='krea2', device='default'),
        '3': n('VAELoader', vae_name='qwen_image_vae.safetensors'),
        '4': n('CLIPTextEncode', clip=['2',0], text=prompt),
        '5': n('ConditioningZeroOut', conditioning=['4',0]),
        '6': n('EmptyLatentImage', width=1024, height=576, batch_size=1),
        '7': n('CFGGuider', model=['14',0], positive=['4',0], negative=['5',0], cfg=1.),
        '8': n('RandomNoise', noise_seed=seed),
        '9': n('SamplerCustomAdvanced', noise=['8',0], guider=['7',0], sampler=['12',0], sigmas=['13',0], latent_image=['6',0]),
        '10': n('VAEDecode', samples=['9',0], vae=['3',0]),
        '11': n('SaveImage', images=['10',0], filename_prefix='conditioning/krea'),
        '12': n('KSamplerSelect', sampler_name='euler'),
        '13': n('BasicScheduler', model=['14',0], scheduler='simple', steps=8, denoise=1.),
        '14': n('ModelSamplingFlux', model=['1',0], max_shift=1.15, base_shift=.5, width=1024, height=576),
    }
    if reference:
        g['15'] = n('LoraLoaderModelOnly', model=['1',0], lora_name='krea2_style_reference.safetensors', strength_model=1.)
        g['14']['inputs']['model'] = ['15',0]
        g['20'] = n('LoadImage', image='anchor.png')
        g['21'] = n('TextEncodeQwenImageEditPlus', clip=['2',0], vae=['3',0], image1=['20',0], prompt=prompt)
        g['22'] = n('FluxKontextMultiReferenceLatentMethod', conditioning=['21',0], reference_latents_method='index_timestep_zero')
        g['7']['inputs']['positive'] = ['22',0]
        g['5']['inputs']['conditioning'] = ['22',0]
        del g['4']
    return g


def run(name, g, source=None):
    name = 'conditioning-v001-'+name
    matches = list((a.PROJECT/'runs').glob('*-'+name+'-1f'))
    if matches:
        assert len(matches) == 1
        folder = matches[0]
        assert json.loads((folder/'workflow.api.json').read_text()) == g
        if source:
            assert a.sha(source) == a.sha(folder/'anchor.png')
        assert json.loads((folder/'submission.json').read_text()).get('prompt_id'), folder
        a.transport.collect(folder)
    else:
        folder = a.transport.submit(a.PROJECT, name, g, 1, source=source, lineage={
            'study':'conditioning-v001', 'models_sha256':a.sha(MANIFEST),
            'runner_sha256':a.sha(Path(__file__)), 'source_sha256':a.sha(source) if source else None})
    return folder


def warp(rgb, start, end):
    return a.motion.warp(rgb, start*1.5, end*1.5)


def opening(model):
    dest = OUT/model/'opening.png'
    folder = run(model+'-opening', graph(model, a.PROMPTS[model], a.SEED))
    a.copy(folder/'frames/0000.png', dest)
    return dest


def sequence(model, mode, until):
    assert mode in ('text', 'reference', 'preserve')
    assert model == 'klein' or mode != 'preserve'
    root = OUT/model/mode
    source = opening(model)
    prompt = PRESERVE if mode == 'preserve' else a.PROMPTS[model]
    a.copy(source, root/'anchors/0000.png')
    a.save(root/'manifest.json', {'model':model, 'mode':mode, 'prompt':prompt,
        'frames':FRAMES, 'fps':FPS, 'cadence':CADENCE, 'seed':a.SEED,
        'motion_time_scale':1.5, 'motion_sha256':a.sha(Path(a.motion.__file__)),
        'models_sha256':a.sha(MANIFEST), 'opening_sha256':a.sha(source),
        'intermediates':'warp previous generated anchor only; no blend',
        'graph':graph(model,prompt,a.SEED+1,mode!='text')})
    for f in range(3, min(until, FRAMES-1)+1, 3):
        previous = root/f'anchors/{f-3:04d}.png'
        guide = root/f'warped-inputs/{f:04d}.png'
        a.image(guide, warp(np.asarray(Image.open(previous).convert('RGB')), f-3, f))
        folder = run(f'{model}-{mode}-{f:04d}', graph(model,prompt,a.SEED+f//3,mode!='text'), guide if mode!='text' else None)
        a.copy(folder/'frames/0000.png', root/f'anchors/{f:04d}.png')
        a.save(root/f'anchor-{f:04d}.json', {'run':str(folder.relative_to(a.PROJECT)), 'sha256':a.sha(folder/'frames/0000.png')})
        print(f'{model} {mode}: {f//3}/7',flush=True)
    if until >= FRAMES-1:
        for f in range(FRAMES):
            anchor = f//3*3
            a.image(root/f'frames/{f:04d}.png',warp(np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')),anchor,f))
        target=root/'preview.mp4'
        if not target.exists():
            a.editing.encode(root/'frames',target,fps=FPS)
        a.save(root/'frame-hashes.json',{p.name:a.sha(p) for p in sorted((root/'frames').glob('*.png'))})
        print(target,flush=True)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('model',choices=('klein','krea'))
    p.add_argument('mode',choices=('text','reference','preserve'))
    p.add_argument('--until',type=int,default=23)
    args=p.parse_args()
    sequence(args.model,args.mode,args.until)
