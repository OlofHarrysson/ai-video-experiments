"""Keep initialized feedback fixed; add optional native reference conditioning."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
import audition as a
import conditioning as previous

OUT=a.PROJECT/'exports/additive-reference-v001'
MANIFEST=Path(__file__).with_name('conditioning-models.json')
FRAMES,FPS,CADENCE=24,12,3
a.transport.DEPLOYMENT=a.APP/'work/additive-reference-session/deployment.json'


def graph(model,prompt,seed,*,initialized=True,reference=False):
    if reference and not initialized:
        raise ValueError('This study adds reference conditioning to initialized feedback')
    n=a.workflows.node
    if model=='klein':
        g=a.workflows.graph(model,prompt,seed)
        if reference:
            g['30']=n('LoadImage',image='reference.png')
            g['31']=n('VAEEncode',pixels=['30',0],vae=['3',0])
            g['32']=n('ReferenceLatent',conditioning=['4',0],latent=['31',0])
            g['33']=n('ReferenceLatent',conditioning=['5',0],latent=['31',0])
            g['7']['inputs'].update(positive=['32',0],negative=['33',0])
        if initialized:
            g['13']['inputs']['steps']=40
            g['25']=n('SplitSigmas',sigmas=['13',0],step=36)
            g['9']['inputs']['sigmas']=['25',1]
    elif model=='krea':
        # Same model, LoRA and text-encoding node in both arms, including opening.
        g=previous.graph(model,prompt,seed,reference=True)
        del g['20']
        del g['21']['inputs']['image1']
        if reference:
            g['30']=n('LoadImage',image='reference.png')
            g['21']['inputs']['image1']=['30',0]
        if initialized:
            g['13']['inputs']['denoise']=.45
    else:
        raise ValueError(model)
    if initialized:
        g['20']=n('LoadImage',image='anchor.png')
        g['24']=n('VAEEncode',pixels=['20',0],vae=['3',0])
        g['9']['inputs']['latent_image']=['24',0]
        del g['6']
    return g


def run(name,g,source=None,reference=None):
    name='additive-reference-v001-'+name
    matches=list((a.PROJECT/'runs').glob('*-'+name+'-1f'))
    if matches:
        assert len(matches)==1
        folder=matches[0]
        assert json.loads((folder/'workflow.api.json').read_text())==g
        for p,filename in ((source,'anchor.png'),(reference,'reference.png')):
            if p is not None: assert a.sha(p)==a.sha(folder/filename)
        assert json.loads((folder/'submission.json').read_text()).get('prompt_id'),folder
        a.transport.collect(folder)
        return folder
    return a.transport.submit(a.PROJECT,name,g,1,source=source,reference=reference,lineage={
        'study':'additive-reference-v001','models_sha256':a.sha(MANIFEST),
        'runner_sha256':a.sha(Path(__file__)),'transport_sha256':a.sha(Path(a.transport.__file__)),
        'source_sha256':a.sha(source) if source else None,
        'reference_sha256':a.sha(reference) if reference else None})


def warp(rgb,start,end):
    return a.motion.warp(rgb,start*1.5,end*1.5)


def opening(model):
    folder=run(model+'-opening',graph(model,a.PROMPTS[model],a.SEED,initialized=False))
    target=OUT/model/'opening.png';a.copy(folder/'frames/0000.png',target)
    return target


def probe(model,reference):
    label='reference' if reference else 'baseline'
    original=opening(model);source=OUT/model/'probe-warp.png'
    a.image(source,warp(np.asarray(Image.open(original).convert('RGB')),0,12))
    folder=run(f'{model}-probe-{label}',graph(model,a.PROMPTS[model],a.SEED+1,reference=reference),source,original if reference else None)
    a.copy(folder/'frames/0000.png',OUT/model/f'probe-{label}.png')


def sequence(model,reference,until):
    label='reference' if reference else 'baseline';root=OUT/model/label
    original=opening(model);a.copy(original,root/'anchors/0000.png')
    a.save(root/'manifest.json',{'model':model,'reference_enabled':reference,
        'initialization':'VAEEncode of warped previous generated anchor',
        'reference_policy':'previous generated anchor before warp' if reference else None,
        'prompt':a.PROMPTS[model],'seed':a.SEED,'fps':FPS,'cadence':CADENCE,'frames':FRAMES,
        'motion_time_scale':1.5,'motion_sha256':a.sha(Path(a.motion.__file__)),
        'models_sha256':a.sha(MANIFEST),'opening_sha256':a.sha(original),
        'intermediates':'warp previous anchor only; no blend',
        'graph':graph(model,a.PROMPTS[model],a.SEED+1,reference=reference)})
    for f in range(3,min(until,FRAMES-1)+1,3):
        prior=root/f'anchors/{f-3:04d}.png';source=root/f'warped-inputs/{f:04d}.png'
        a.image(source,warp(np.asarray(Image.open(prior).convert('RGB')),f-3,f))
        folder=run(f'{model}-{label}-{f:04d}',graph(model,a.PROMPTS[model],a.SEED+f//3,reference=reference),source,prior if reference else None)
        a.copy(folder/'frames/0000.png',root/f'anchors/{f:04d}.png')
        a.save(root/f'anchor-{f:04d}.json',{'run':str(folder.relative_to(a.PROJECT)),
            'sha256':a.sha(folder/'frames/0000.png'),'initialization_sha256':a.sha(source),
            'reference_sha256':a.sha(prior) if reference else None})
        print(model,label,f//3,'/ 7',flush=True)
    if until>=FRAMES-1:
        for f in range(FRAMES):
            anchor=f//3*3
            a.image(root/f'frames/{f:04d}.png',warp(np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')),anchor,f))
        if not (root/'preview.mp4').exists():a.editing.encode(root/'frames',root/'preview.mp4',fps=FPS)
        a.save(root/'frame-hashes.json',{p.name:a.sha(p) for p in sorted((root/'frames').glob('*.png'))})
        print(root/'preview.mp4',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=('opening','probe','sequence'))
    p.add_argument('model',choices=('klein','krea'))
    p.add_argument('--reference',action='store_true');p.add_argument('--until',type=int,default=23)
    args=p.parse_args()
    if args.stage=='opening':opening(args.model)
    elif args.stage=='probe':probe(args.model,args.reference)
    else:sequence(args.model,args.reference,args.until)
