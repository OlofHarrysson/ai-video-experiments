"""Ten-second twist/expansion and matched branches using native Turbo tails."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
import turbo_schedule_motion as old
from spatial_warp import remap_rgb

a, opening = old.a, old.opening
OUT = a.PROJECT/'exports/turbo-transitions-v001'
FPS, CADENCE, WIDTH, HEIGHT, SEED = 12, 3, 1536, 1024, old.SEED
FRAMES, BRANCH_START, BRANCH_FRAMES = 120, 36, 36
EXPANSION_CENTER, EXPANSION_RADIUS, EXPANSION_AMOUNT = (220.,190.), 105., .9
TWIST_AMOUNT = 1.1
a.transport.DEPLOYMENT = a.APP/'work/turbo-transition-session/deployment.json'


def parameters_at_time(t):
    return TWIST_AMOUNT*a.motion.smooth(t/5), EXPANSION_AMOUNT*a.motion.smooth((t-3)/7)


def parameters(frame):
    return parameters_at_time(frame/FPS)


def expansion(x,y,amount,inverse=False):
    dx,dy=x-EXPANSION_CENTER[0],y-EXPANSION_CENTER[1]
    radius=np.hypot(dx,dy)
    def forward(r):return r*(1+amount*np.exp(-r*r/(2*EXPANSION_RADIUS**2)))
    if inverse:
        lo,hi=radius/(1+amount),radius.copy()
        for _ in range(25):
            mid=(lo+hi)/2;less=forward(mid)<radius
            lo,hi=np.where(less,mid,lo),np.where(less,hi,mid)
        target=(lo+hi)/2
    else:target=forward(radius)
    scale=np.divide(target,radius,out=np.ones_like(radius),where=radius>1e-9)
    return EXPANSION_CENTER[0]+dx*scale,EXPANSION_CENTER[1]+dy*scale


def mapping_at_time(x,y,seconds,inverse=False):
    twist,grow=parameters_at_time(seconds)
    if inverse:
        x,y=expansion(x,y,grow,True)
        return a.motion.twist(x,y,-twist)
    x,y=a.motion.twist(x,y,twist)
    return expansion(x,y,grow)


def mapping(x,y,frame,inverse=False):
    return mapping_at_time(x,y,frame/FPS,inverse)


def coordinates_at_time(start,end,width=WIDTH,height=HEIGHT):
    x,y=np.meshgrid(np.arange(width,dtype=np.float64)*512/width,np.arange(height,dtype=np.float64)*320/height)
    x,y=mapping_at_time(x,y,end,True);x,y=mapping_at_time(x,y,start)
    return np.stack((x*width/512,y*height/320),axis=-1).astype(np.float32)


def coordinates(start,end,width=WIDTH,height=HEIGHT):
    return coordinates_at_time(start/FPS,end/FPS,width,height)


def warp_at_time(rgb,start,end):
    if start==end:return rgb.copy()
    h,w=rgb.shape[:2]
    return remap_rgb(rgb,coordinates_at_time(start,end,w,h))


def warp(rgb,start,end):
    return warp_at_time(rgb,start/FPS,end/FPS)


def graph(tail,seed):
    assert tail in (1,2,3)
    g=old.graph('turbo-tail',seed)
    g['41']['inputs']['step']=8-tail
    g['11']['inputs']['filename_prefix']=f'turbo-transitions/tail-{tail}'
    return g


def initial(tail):
    return opening.OUT/'krea-cathedral/image.png' if tail==1 else OUT/f'tail-1/anchors/{BRANCH_START:04d}.png'


def render(tail):
    (a.PROJECT/'runs').mkdir(parents=True,exist_ok=True)
    start,count=(0,FRAMES) if tail==1 else (BRANCH_START,BRANCH_FRAMES)
    root=OUT/f'tail-{tail}';source=initial(tail)
    a.copy(source,root/f'anchors/{start:04d}.png')
    a.save(root/'manifest.json',{'tail':tail,'start_frame':start,'frames':count,'fps':FPS,'cadence':CADENCE,
        'seed':SEED,'opening_sha256':a.sha(source),'graph':graph(tail,SEED+start//3+1),
        'runner_sha256':a.sha(Path(__file__)),'model_manifest_sha256':a.sha(a.APP/'serverless/modern-models.json'),
        'initialization':'warped previous generated RGB anchor','intermediates':'previous anchor warped; no blend',
        'resampling':'Lanczos4 reflected border','expansion_center':EXPANSION_CENTER,
        'expansion_radius':EXPANSION_RADIUS,'expansion_amount':EXPANSION_AMOUNT,'twist_amount':TWIST_AMOUNT})
    for f in range(start+CADENCE,start+count,CADENCE):
        parent=root/f'anchors/{f-CADENCE:04d}.png';warped=root/f'warped-inputs/{f:04d}.png'
        a.image(warped,warp(np.asarray(Image.open(parent).convert('RGB')),f-CADENCE,f))
        g=graph(tail,SEED+f//CADENCE);name=f'turbo-transitions-v001-tail-{tail}-{f:04d}'
        found=list((a.PROJECT/'runs').glob('*-'+name+'-1f'))
        if found:
            assert len(found)==1;run=found[0]
            assert json.loads((run/'workflow.api.json').read_text())==g and a.sha(run/'anchor.png')==a.sha(warped)
            a.transport.collect(run)
        else:
            run=a.transport.submit(a.PROJECT,name,g,1,source=warped,lineage={'parent_sha256':a.sha(parent),'frame':f,'tail':tail})
        output=root/f'anchors/{f:04d}.png';a.copy(run/'frames/0000.png',output)
        a.save(root/f'anchor-{f:04d}.json',{'run':str(run.relative_to(a.PROJECT)),'parent_sha256':a.sha(parent),
            'initialization_sha256':a.sha(warped),'output_sha256':a.sha(output)})
        print('tail',tail,'frame',f,'complete',flush=True)
    for local in range(count):
        f=start+local;anchor=f//CADENCE*CADENCE
        a.image(root/f'frames/{local:04d}.png',warp(np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')),anchor,f))
    a.save(root/'frame-hashes.json',{p.name:a.sha(p) for p in sorted((root/'frames').glob('*.png'))})
    if not (root/'preview.mp4').exists():a.editing.encode(root/'frames',root/'preview.mp4',fps=FPS)
    print('COMPLETE tail',tail,flush=True)


def preview():
    root=OUT/'motion-only';source=opening.OUT/'krea-cathedral/image.png'
    rgb=np.asarray(Image.open(source).convert('RGB').resize((768,512),Image.Resampling.LANCZOS))
    for f in range(FRAMES):a.image(root/f'frames/{f:04d}.png',warp(rgb,0,f))
    if not (root/'preview.mp4').exists():a.editing.encode(root/'frames',root/'preview.mp4',fps=FPS)
    a.save(root/'manifest.json',{'source_sha256':a.sha(source),'frames':FRAMES,'fps':FPS,'each_frame_from':'original; no repaint','runner_sha256':a.sha(Path(__file__))})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=['preview','1','2','3']);args=p.parse_args()
    preview() if args.case=='preview' else render(int(args.case))
