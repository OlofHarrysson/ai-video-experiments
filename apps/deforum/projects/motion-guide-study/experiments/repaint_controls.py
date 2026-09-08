"""Three-second twist: global denoise comparison and one regional-control probe."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageDraw

import spatial_sequence as seq

recipe = seq.recipe
OUT = seq.PROJECT/'exports/repaint-controls-v001'
FRAMES, FPS, CADENCE = 36, 12, 3
DENOISE = {'d035':.35, 'd045':.45, 'd058':.58}
NOISE_STD, FEATHER, NOISE_SEED = .06, 64, 524001


def regions():
    x,y=np.meshgrid(np.arange(recipe.WIDTH),np.arange(recipe.HEIGHT))
    sx=seq.smooth((x-recipe.WIDTH/2+FEATHER/2)/FEATHER)
    sy=seq.smooth((y-recipe.HEIGHT/2+FEATHER/2)/FEATHER)
    return 1-(1-sx)*sy, sx*(1-sy)


def graph(name,frame,denoise):
    g=seq.graph(frame)
    g['6']['inputs']['denoise']=denoise
    g['11']['inputs']['filename_prefix']='repaint-controls/'+name
    if name=='regional':
        g['30']=recipe.node('ImageCrop',image=['4',0],width=recipe.WIDTH,height=recipe.HEIGHT,x=0,y=0)
        g['31']=recipe.node('ImageCrop',image=['4',0],width=recipe.WIDTH,height=recipe.HEIGHT,x=recipe.WIDTH,y=0)
        g['32']=recipe.node('ImageToMask',image=['31',0],channel='red')
        g['33']=recipe.node('SetLatentNoiseMask',samples=['5',0],mask=['32',0])
        g['5']['inputs']['pixels']=['30',0]
        g['6']['inputs']['latent_image']=['33',0]
    return g


def prepare():
    OUT.mkdir(parents=True,exist_ok=False)
    mask,noise=regions()
    Image.fromarray(np.rint(mask*255).astype('uint8')).save(OUT/'sampling-mask.png')
    Image.fromarray(np.rint(noise*255).astype('uint8')).save(OUT/'noise-region.png')
    im=Image.open(seq.OPENING).convert('RGB')
    draw=ImageDraw.Draw(im)
    draw.rectangle((0,recipe.HEIGHT//2,recipe.WIDTH//2-1,recipe.HEIGHT-1),outline='#b3a1ff',width=5)
    draw.rectangle((recipe.WIDTH//2,0,recipe.WIDTH-1,recipe.HEIGHT//2-1),outline='#ffb84f',width=5)
    # Labels sit below the diagnostic image, outside the artwork.
    legend=Image.new('RGB',(recipe.WIDTH,recipe.HEIGHT+60),'#141923');legend.paste(im,(0,0))
    d=ImageDraw.Draw(legend);d.text((14,recipe.HEIGHT+10),'Bottom-left: reduce repainting (purple)',fill='#b3a1ff')
    d.text((recipe.WIDTH//2+14,recipe.HEIGHT+10),'Top-right: add noise (orange)',fill='#ffb84f')
    legend.save(OUT/'region-preview.png')
    seq.save(OUT/'manifest.json',{'frames':FRAMES,'fps':FPS,'cadence':CADENCE,
        'opening_sha256':recipe.sha(seq.OPENING),'script_sha256':recipe.sha(Path(__file__)),
        'motion_script_sha256':recipe.sha(Path(seq.__file__)),
        'denoise':DENOISE,'region_coordinates':'fixed screen quadrants; 64px transitions',
        'noise_std_rgb_0_1':NOISE_STD,'noise_seed':NOISE_SEED,
        'noise_kind':'seeded Gaussian pixel noise shared across RGB before VAE encode',
        'sampling_mask_sha256':recipe.sha(OUT/'sampling-mask.png'),
        'rife':False,'pixel_copyback':False,'feedback_alpha_blend':False})
    for name in DENOISE:
        root=OUT/name
        for sub in ('anchors','warped-inputs','cadence/frames'):(root/sub).mkdir(parents=True)
        shutil.copyfile(seq.OPENING,root/'anchors/0000.png')
        seq.save(root/'manifest.json',{'denoise':DENOISE[name],'graph':graph(name,3,DENOISE[name]),
                                     'kind':'reused reference' if name=='d058' else 'new feedback render'})
    for f in range(3,FRAMES+1,3):
        source=seq.OUT/f'anchors/{f:04d}.png'
        record=json.loads((seq.OUT/f'anchor-{f:04d}.json').read_text())
        assert recipe.sha(source)==record['sha256']
        shutil.copyfile(source,OUT/f'd058/anchors/{f:04d}.png')
        seq.save(OUT/f'd058/anchor-{f:04d}.json',{**record,'reuse_parent':str(seq.OUT.relative_to(seq.APP))})
    motion=OUT/'motion-only/frames';motion.mkdir(parents=True)
    for f in range(FRAMES):shutil.copyfile(seq.OUT/f'motion-only/frames/{f:04d}.png',motion/f'{f:04d}.png')
    recipe.editing.encode(motion,motion.parent/'preview.mp4',fps=FPS)
    finish('d058')


def regional_prepare(base):
    root=OUT/'regional';root.mkdir(exist_ok=False)
    for sub in ('anchors','warped-inputs','clean-warped-inputs','cadence/frames'):(root/sub).mkdir(parents=True)
    shutil.copyfile(seq.OPENING,root/'anchors/0000.png')
    seq.save(root/'manifest.json',{'base':base,'denoise':DENOISE[base],
        'graph':graph('regional',3,DENOISE[base]),'kind':'combined mask and pixel-noise probe',
        'attribution':'two controls change together; neither effect is independently isolated'})


def render(name):
    root=OUT/name;manifest=json.loads((root/'manifest.json').read_text());denoise=manifest['denoise']
    assert manifest['graph']==graph(name,3,denoise)
    mask=np.asarray(Image.open(OUT/'sampling-mask.png').convert('RGB'))
    _,noise_weight=regions()
    for f in range(3,FRAMES+1,3):
        target=root/f'anchors/{f:04d}.png';record=root/f'anchor-{f:04d}.json'
        if target.exists():
            assert recipe.sha(target)==json.loads(record.read_text())['sha256'];continue
        rgb=np.asarray(Image.open(root/f'anchors/{f-3:04d}.png').convert('RGB'))
        moved=seq.warp(rgb,f-3,f)
        if name=='regional':
            clean=root/f'clean-warped-inputs/{f:04d}.png'
            if not clean.exists():Image.fromarray(moved).save(clean)
            rng=np.random.default_rng(NOISE_SEED+f//CADENCE)
            added=rng.standard_normal((recipe.HEIGHT,recipe.WIDTH,1))*NOISE_STD*noise_weight[:,:,None]
            moved=np.rint(np.clip(moved.astype('float32')/255+added,0,1)*255).astype('uint8')
            moved=np.concatenate((moved,mask),axis=1)
        source=root/f'warped-inputs/{f:04d}.png'
        if source.exists():assert np.array_equal(np.asarray(Image.open(source)),moved)
        else:Image.fromarray(moved).save(source)
        run=seq.shared.accepted_run(f'repaint-controls-v001-{name}-{f:04d}',graph(name,f,denoise),1,source,
            {'study':'repaint-controls-v001','variant':name,'timeline_frame':f,'timeline_fps':FPS,
             'cadence':CADENCE,'denoise':denoise,'sampling_seed':recipe.SEED+f//CADENCE})
        rendered=run/'frames/0000.png'
        if not record.exists():seq.save(record,{'run':str(run.relative_to(seq.PROJECT)),'sha256':recipe.sha(rendered)})
        shutil.copyfile(rendered,target)
        print(name,f//3,'/12',flush=True)
    finish(name)


def finish(name):
    root=OUT/name;rows=[]
    for f in range(FRAMES):
        a=f//3*3;b=a+3;alpha=(f-a)/3;target=root/f'cadence/frames/{f:04d}.png'
        if target.exists():raise FileExistsError(target)
        left=root/f'anchors/{a:04d}.png'
        if f==a:shutil.copyfile(left,target)
        else:
            l=seq.warp(np.asarray(Image.open(left).convert('RGB')),a,f)
            r=seq.warp(np.asarray(Image.open(root/f'anchors/{b:04d}.png').convert('RGB')),b,f)
            Image.fromarray(np.rint(l*(1-alpha)+r*alpha).astype('uint8')).save(target)
        rows.append({'frame':f,'sha256':recipe.sha(target),'left':a,'right':b,'blend':alpha})
    seq.save(root/'cadence/manifest.json',{'fps':FPS,'frames':rows})
    recipe.editing.encode(root/'cadence/frames',root/'cadence/preview.mp4',fps=FPS)


def check():
    a=graph('d035',3,.35);b=graph('d045',3,.45)
    a['6']['inputs']['denoise']=b['6']['inputs']['denoise'];a['11']=b['11'];assert a==b
    m,n=regions();assert m[-1,0]==0 and m[0,-1]==1 and n[0,-1]==1
    assert n[-1,0]==n[0,0]==n[-1,-1]==0
    g=graph('regional',3,.45)
    assert not any(v['class_type']=='ImageCompositeMasked' for v in g.values())
    assert g['33']['inputs']['samples']==['5',0] and g['6']['inputs']['latent_image']==['33',0]
    print('Matched denoise graphs, region orientation and sampler-only mask verified.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=('check','prepare','denoise','regional-prepare','regional'))
    p.add_argument('--base',choices=tuple(DENOISE),default='d045');args=p.parse_args()
    if args.stage=='denoise':
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(render,('d035','d045')))
    elif args.stage=='regional-prepare':regional_prepare(args.base)
    elif args.stage=='regional':render('regional')
    else:globals()[args.stage]()
