"""Native ComfyUI graphs for the bounded Klein/Krea audition.

Source recipes and pinned weights: serverless/modern-models.json and
projects/modern-model-study/experiments/baseline.md. No custom nodes.
"""
WIDTH, HEIGHT = 1024, 576


def node(kind, **inputs):
    return {'class_type': kind, 'inputs': inputs}


def graph(model, prompt, seed, *, editing=False, denoise=.45):
    if model not in ('klein', 'krea'):
        raise ValueError(model)
    klein = model == 'klein'
    g = {
        '1': node('UNETLoader', unet_name='flux-2-klein-4b.safetensors' if klein else 'krea2_turbo_fp8_scaled.safetensors', weight_dtype='default'),
        '2': node('CLIPLoader', clip_name='qwen_3_4b.safetensors' if klein else 'qwen3vl_4b_fp8_scaled.safetensors', type='flux2' if klein else 'krea2', device='default'),
        '3': node('VAELoader', vae_name='flux2-vae.safetensors' if klein else 'qwen_image_vae.safetensors'),
        '4': node('CLIPTextEncode', clip=['2', 0], text=prompt),
        '5': node('ConditioningZeroOut', conditioning=['4', 0]),
        '6': node('EmptyFlux2LatentImage' if klein else 'EmptyLatentImage', width=WIDTH, height=HEIGHT, batch_size=1),
        '10': node('VAEDecode', samples=['9', 0], vae=['3', 0]),
        '11': node('SaveImage', images=['10', 0], filename_prefix='modern-models/'+model),
    }
    if editing:
        g['20'] = node('LoadImage', image='anchor.png')
        g['21'] = node('VAEEncode', pixels=['20', 0], vae=['3', 0])
    if klein:
        positive, negative = ['4', 0], ['5', 0]
        if editing:
            g['22'] = node('ReferenceLatent', conditioning=positive, latent=['21', 0])
            g['23'] = node('ReferenceLatent', conditioning=negative, latent=['21', 0])
            positive, negative = ['22', 0], ['23', 0]
        g['7'] = node('CFGGuider', model=['1', 0], positive=positive, negative=negative, cfg=1.)
        g['8'] = node('RandomNoise', noise_seed=seed)
        g['12'] = node('KSamplerSelect', sampler_name='euler')
        g['13'] = node('Flux2Scheduler', steps=4, width=WIDTH, height=HEIGHT)
        g['9'] = node('SamplerCustomAdvanced', noise=['8', 0], guider=['7', 0], sampler=['12', 0], sigmas=['13', 0], latent_image=['6', 0])
    else:
        g['9'] = node('KSampler', model=['1', 0], positive=['4', 0], negative=['5', 0], latent_image=['21', 0] if editing else ['6', 0], seed=seed, steps=8, cfg=1., sampler_name='euler', scheduler='simple', denoise=denoise if editing else 1.)
    return g
