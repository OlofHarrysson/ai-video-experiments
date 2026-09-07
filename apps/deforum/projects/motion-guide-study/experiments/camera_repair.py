"""Matched camera-gap probes against an archived frame; existing ComfyUI nodes."""
import argparse
import copy
import json
import shutil

import motion_effects as base
import motion_effects_2 as round2
import seed_comparison as recipe

OUT=round2.OUT/'camera-repair'
VARIANTS=('repair-only','prompt-only','repair-and-prompt')


def graph(frame,variant):
    g=base.graph('turn-bank',frame)
    g['11']['inputs']['filename_prefix']='camera-repair/frames'
    if variant!='repair-only':
        prompt=g['2']['inputs']['text']
        prompt=prompt.replace('deep black space surrounding the portal, ',
            'a continuous detailed alien environment surrounding the portal, ')
        prompt=prompt.replace('deep black background, ',
            'illustrated teal clouds, distant terrain and mechanical structures extending to every edge of the image, ')
        g['2']['inputs']['text']=prompt
    if variant!='prompt-only':
        g['80']=recipe.node('InvertMask',mask=['72',1])
        g['81']=recipe.node('SetLatentNoiseMask',samples=['5',0],mask=['80',0])
        settings=copy.deepcopy(g['6']['inputs'])
        settings.update(latent_image=['81',0],denoise=1.0,seed=100000+recipe.SEED+frame)
        g['82']=recipe.node('KSampler',**settings)
        g['83']=recipe.node('VAEDecode',samples=['82',0],vae=['1',2])
        g['84']=recipe.node('ImageCompositeMasked',destination=['72',0],source=['83',0],
            x=0,y=0,resize_source=False,mask=['80',0])
        g['85']=recipe.node('VAEEncode',pixels=['84',0],vae=['1',2])
        g['6']['inputs']['latent_image']=['85',0]
        g['86']=recipe.node('SaveImage',images=['84',0],filename_prefix='camera-repair/filled')
        g['87']=recipe.node('MaskToImage',mask=['80',0])
        g['88']=recipe.node('SaveImage',images=['87',0],filename_prefix='camera-repair/repair-mask')
    return g


def probe(variant):
    OUT.mkdir(parents=True,exist_ok=True)
    source=base.OUT/'turn-bank/repaint/frames/0002.png'
    run=base.accepted_run(f'motion-effects-v002-camera-probe-{variant}',graph(3,variant),1,source,
        {'study':'motion-effects-v002','effect':'camera-probe-'+variant,'frame':3,
         'seed':recipe.SEED+3,'variant':variant,'parent_frame':2})
    target=OUT/'probes'/variant;target.mkdir(parents=True,exist_ok=True)
    if not (target/'run.json').exists():
        base.wave.save(target/'run.json',{'run':str(run.relative_to(base.PROJECT))})
        shutil.copyfile(run/'frames/0000.png',target/'result.png')
    print('Probe complete',variant,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('probe',))
    p.add_argument('--variant',choices=VARIANTS,default='repair-and-prompt')
    a=p.parse_args()
    probe(a.variant)
