"""Verify no-motion lineage and expose reconstruction, redraw and warp differences."""
import copy
import json
import subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import repaint_diagnosis as d

FONT = '/System/Library/Fonts/Helvetica.ttc'


def rgb(p):
    return np.asarray(Image.open(p).convert('RGB'))


def metrics(im, reference):
    gray=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
    return {'mean_absolute_difference_from_opening':float(np.abs(im.astype(float)-reference.astype(float)).mean()),
        'edge_energy':float(cv2.Laplacian(gray,cv2.CV_32F).var()),
        'mean_gray':float(gray.mean()),'gray_std':float(gray.std()),
        'mean_saturation':float(cv2.cvtColor(im,cv2.COLOR_RGB2HSV)[:,:,1].mean())}


def panel(paths, labels, cycle=None, crop=None):
    canvas=Image.new('RGB',(1536,1104),'#15191d');draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype(FONT,23)
    for j,(path,label) in enumerate(zip(paths,labels)):
        x,y=j%2*768,j//2*552
        im=Image.open(path).convert('RGB')
        if crop:im=im.crop(crop)
        canvas.paste(im.resize((768,512),Image.Resampling.LANCZOS),(x,y+40))
        draw.text((x+12,y+8),label+(f' | cycle {cycle}' if cycle is not None else ''),font=font,fill='white')
    return np.asarray(canvas)


def local():
    base=d.OUT/'warp-review';labels=['One warp from original','Eleven accumulated warps','Existing warp + repaint 0.10']
    font=ImageFont.truetype(FONT,20)
    for i in range(12):
        paths=[d.OUT/f'warp-once/anchors/{i:04d}.png',d.OUT/f'warp-repeated/anchors/{i:04d}.png',
            d.a.PROJECT/f'exports/krea-low-repaint-v001/d010/anchors/{i*3:04d}.png']
        canvas=Image.new('RGB',(1536,382),'#15191d');draw=ImageDraw.Draw(canvas)
        for j,p in enumerate(paths):
            im=Image.open(p).convert('RGB');canvas.paste(im.resize((512,342),Image.Resampling.LANCZOS),(j*512,40))
            draw.text((j*512+8,10),labels[j],font=font,fill='white')
        d.a.image(base/f'frames/{i:04d}.png',np.asarray(canvas))
    if not (base/'preview.mp4').exists():d.a.editing.encode(base/'frames',base/'preview.mp4',fps=4)
    once=rgb(d.OUT/'warp-once/anchors/0011.png');repeated=rgb(d.OUT/'warp-repeated/anchors/0011.png')
    results={'once':metrics(once,once),'repeated':metrics(repeated,once)}
    d.a.save(base/'diagnostics.json',results)
    print('Warp controls',results)


def main():
    reference=rgb(d.SOURCE); records=[];checks=[]
    for case in d.CASES:
        root=d.OUT/case
        assert d.a.sha(root/'anchors/0000.png')==d.a.sha(d.SOURCE)
        for i in range(25):
            output=root/f'anchors/{i:04d}.png';im=rgb(output)
            assert im.shape==reference.shape
            previous=rgb(root/f'anchors/{i-1:04d}.png') if i else im
            step_change=float(np.abs(im.astype(float)-previous.astype(float)).mean())
            records.append({'case':case,'cycle':i,'mean_absolute_change_from_previous':step_change,**metrics(im,reference)})
            assert d.a.sha(output)==d.a.sha(root/f'frames/{i:04d}.png')
            if not i:continue
            rec=json.loads((root/f'round-{i:04d}.json').read_text());run=d.a.PROJECT/rec['run']
            assert rec['input_sha256']==d.a.sha(root/f'anchors/{i-1:04d}.png')==d.a.sha(run/'anchor.png')
            assert rec['output_sha256']==d.a.sha(output)==d.a.sha(run/'frames/0000.png')
            requested=json.loads((run/'workflow.api.json').read_text());assert requested==d.graph(case,d.opening.SEED+i)
            actual=json.loads((run/'workflow.executed.json').read_text());normalized=copy.deepcopy(actual)
            normalized['20']['inputs']['image']='anchor.png';assert requested==normalized
            if case=='vae-only':assert '9' not in actual and actual['10']['inputs']['samples']==['24',0]
            else:assert actual['9']['inputs']['latent_image']==['24',0]
            hist=json.loads((run/'history.json').read_text());assert hist['status']['completed'] and hist['status']['status_str']=='success'
            checks.append({'case':case,'cycle':i,'output_sha256':d.a.sha(output)})
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(root/'preview.mp4')]))['streams'][0]
        assert probe['nb_frames']=='150' and probe['r_frame_rate']=='24/1'
    d.a.save(d.OUT/'verification.json',{'verified':True,'jobs':len(checks),'lineage':checks,'no_motion_in_all_remote_inputs':True})
    d.a.save(d.OUT/'diagnostics.json',{'meaning':'change, detail and color diagnostics, not aesthetic scores','results':records})
    labels=['Original held unchanged','Encoding/decoding only','Repaint 0.10, no movement','Repaint 0.30, no movement']
    target=d.OUT/'comparison/preview.mp4'
    for i in range(25):
        paths=[d.SOURCE]+[d.OUT/f'{case}/anchors/{i:04d}.png' for case in ['vae-only','repaint010','repaint030']]
        d.a.image(target.parent/f'frames/{i:04d}.png',panel(paths,labels,cycle=i))
        if i in [0,1,4,11,24]:
            d.a.image(d.OUT/f'review/cycle-{i:02d}.png',panel(paths,labels,cycle=i))
            d.a.image(d.OUT/f'review/detail-{i:02d}.png',panel(paths,labels,cycle=i,crop=(240,100,1008,612)))
    if not target.exists():d.a.editing.encode(target.parent/'frames',target,fps=4)
    local()
    print('Verified',len(checks),'jobs; comparison saved')


if __name__=='__main__':
    import sys
    local() if '--local' in sys.argv else main()
