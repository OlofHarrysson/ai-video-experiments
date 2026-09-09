"""Verify matched schedule recipes and render a compact comparison."""
import copy
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import turbo_schedule as p
from repaint_diagnosis_review import metrics


def pair(paths, labels, cycle=None, crop=None):
    canvas=Image.new('RGB',(1536,552),'#15191d');draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23)
    for j,(path,label) in enumerate(zip(paths,labels)):
        im=Image.open(path).convert('RGB')
        if crop:im=im.crop(crop)
        canvas.paste(im.resize((768,512),Image.Resampling.LANCZOS),(j*768,40))
        draw.text((j*768+12,8),label+(f' | cycle {cycle}' if cycle is not None else ''),font=font,fill='white')
    return np.asarray(canvas)


def main():
    a=p.d.a;ref=np.asarray(Image.open(p.d.SOURCE).convert('RGB'));records=[];checks=[]
    schedules=json.loads((a.APP/'work/turbo-schedule-session/unpacked/receipts/schedules.json').read_text())
    assert schedules['turbo-tail'][0]==schedules['small-updates'][0]
    assert len(schedules['turbo-tail'])==2 and len(schedules['small-updates'])==9
    assert schedules['turbo-tail'][-1]==schedules['small-updates'][-1]==0
    for case in p.CASES:
        root=p.OUT/case;m=json.loads((root/'manifest.json').read_text());run=a.PROJECT/m['run']
        g=p.graph(case);assert json.loads((run/'workflow.api.json').read_text())==m['graph']==g
        actual=json.loads((run/'workflow.executed.json').read_text());normal=copy.deepcopy(actual)
        normal['20']['inputs']['image']='anchor.png';assert normal==g
        hist=json.loads((run/'history.json').read_text());assert hist['status']['completed'] and hist['status']['status_str']=='success'
        assert a.sha(run/'anchor.png')==m['source_sha256']==a.sha(p.d.SOURCE)
        assert sum(n['class_type']=='VAEEncode' for n in g.values())==1
        for i in range(1,25):
            n=g[str(100+i)]['inputs'];assert n['latent_image']==(['24',0] if i==1 else [str(99+i),0])
            assert n['noise_seed']==p.d.opening.SEED+i and n['add_noise'] is True
            assert n['sigmas']==['41',1] and n['sampler']==['42',0]
        for i in range(25):
            path=root/f'anchors/{i:04d}.png';assert a.sha(path)==m['outputs'][str(i)]
            if i:assert a.sha(path)==a.sha(run/f'frames/{i-1:04d}.png')
            im=np.asarray(Image.open(path).convert('RGB'));assert im.shape==ref.shape
            records.append({'case':case,'cycle':i,**metrics(im,ref)})
            a.copy(path,root/f'frames/{i:04d}.png')
        if not (root/'preview.mp4').exists():a.editing.encode(root/'frames',root/'preview.mp4',fps=4)
        checks.append({'case':case,'cycles':24,'vae_encodes':1,'sigmas':schedules[case]})
    left=p.graph('turbo-tail');right=p.graph('small-updates')
    for key in ['40','41','11']:del left[key],right[key]
    assert left==right
    labels=['Eight small updates','Turbo final step']
    for i in range(25):
        paths=[p.OUT/f'small-updates/anchors/{i:04d}.png',p.OUT/f'turbo-tail/anchors/{i:04d}.png']
        im=pair(paths,labels,cycle=i);a.image(p.OUT/f'comparison/frames/{i:04d}.png',im)
        if i in [0,1,4,11,24]:
            a.image(p.OUT/f'review/cycle-{i:02d}.png',im)
            a.image(p.OUT/f'review/detail-{i:02d}.png',pair(paths,labels,cycle=i,crop=(240,100,1008,612)))
    target=p.OUT/'comparison/preview.mp4'
    if not target.exists():a.editing.encode(target.parent/'frames',target,fps=4)
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(target)]))['streams'][0]
    assert info['nb_frames']=='150' and info['r_frame_rate']=='24/1'
    a.save(p.OUT/'verification.json',{'verified':True,'matched_starting_noise':True,'checks':checks})
    a.save(p.OUT/'diagnostics.json',{'meaning':'change and contrast, not aesthetic scores','results':records})
    print(json.dumps(checks,indent=2))


if __name__=='__main__':main()
