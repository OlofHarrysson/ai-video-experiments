"""Assemble matched 24fps comparisons and verify feedback provenance."""
import argparse
import copy
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import turbo_smoothing as s

a, t, OUT = s.a, s.t, s.OUT


def encode(root):
    output=root/'preview.mp4'
    if not output.exists():
        subprocess.run(['ffmpeg','-v','error','-n','-framerate','24','-i',str(root/'frames/%04d.png'),
            '-frames:v','72','-an','-c:v','libx264','-crf','18','-preset','slow',
            '-pix_fmt','yuv420p','-movflags','+faststart',str(output)],check=True)
    stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(output)]))['streams'][0]
    assert stream['nb_read_frames']=='72' and stream['avg_frame_rate']=='24/1' and float(stream['duration'])==3
    return stream


def compare(kind, right_frames, right_label, right_fps):
    root=OUT/f'compare-{kind}'
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23)
    for i in range(72):
        canvas=Image.new('RGB',(1536,554),'#15191d');draw=ImageDraw.Draw(canvas)
        for x,path,label in [(0,s.CONTROL/f'frames/{i//2:04d}.png','Original: repaint every 3 frames'),
                             (768,right_frames/f'{i if right_fps==24 else i//2:04d}.png',right_label)]:
            canvas.paste(Image.open(path).convert('RGB').resize((768,512),Image.Resampling.LANCZOS),(x,42))
            draw.text((x+12,9),label,font=font,fill='white')
        a.image(root/f'frames/{i:04d}.png',np.asarray(canvas))
    encode(root)


def rife():
    raw=OUT/'rife-raw';root=OUT/'interpolation'
    manifest=json.loads((raw/'manifest.json').read_text())
    assert manifest['status']=='complete' and manifest['anchors_verified']
    for row in manifest['output_frames']:
        assert a.sha(raw/row['file'])==row['sha256']
    rows=[]
    for i in range(72):
        source=raw/f'frames/{i:04d}.png' if i<66 else s.CONTROL/f'frames/{i//2:04d}.png'
        a.copy(source,root/f'frames/{i:04d}.png')
        rows.append({'frame':i,'source':str(source.relative_to(a.PROJECT)),'sha256':a.sha(source),
            'kind':('anchor' if i%6==0 else 'RIFE') if i<66 else 'original final warp interval'})
    for i in range(12):
        assert np.array_equal(np.asarray(Image.open(root/f'frames/{i*6:04d}.png')),
                              np.asarray(Image.open(s.CONTROL/f'anchors/{36+i*3:04d}.png')))
    stream=encode(root)
    a.save(root/'manifest.json',{'fps':24,'frames':rows,'probe':stream,
        'rife_manifest_sha256':a.sha(raw/'manifest.json'),'feedback_generation_changed':False,
        'tail':'last quarter-second uses original warp-only frames; no extrapolation'})
    compare('interpolation',root/'frames','Same repaints, RIFE between them',24)


def cadence():
    root=OUT/'cadence-2';rows=[]
    for i,f in enumerate(range(38,72,2),1):
        record=json.loads((root/f'anchor-{f:04d}.json').read_text());run=a.PROJECT/record['run']
        parent=root/f'anchors/{f-2:04d}.png';source=root/f'warped-inputs/{f:04d}.png'
        assert a.sha(parent)==record['parent_sha256']
        assert a.sha(source)==record['initialization_sha256']==a.sha(run/'anchor.png')
        assert a.sha(root/f'anchors/{f:04d}.png')==record['output_sha256']==a.sha(run/'frames/0000.png')
        expected=t.graph(3,t.SEED+12+i)
        assert json.loads((run/'workflow.api.json').read_text())==expected
        actual=copy.deepcopy(json.loads((run/'workflow.executed.json').read_text()))
        actual['20']['inputs']['image']='anchor.png';assert actual==expected
        history=json.loads((run/'history.json').read_text());assert history['status']['completed'] and history['status']['status_str']=='success'
        if i in (1,9,17):
            from cathedral_review import assert_warp_matches
            assert_warp_matches(t.warp(np.asarray(Image.open(parent).convert('RGB')),f-2,f),np.asarray(Image.open(source).convert('RGB')))
        events=dict(history['status']['messages'])
        rows.append({'frame':f,'seconds':(events['execution_success']['timestamp']-events['execution_start']['timestamp'])/1000})
    assert a.sha(root/'anchors/0036.png')==a.sha(s.CONTROL/'anchors/0036.png')
    hashes=json.loads((root/'frame-hashes.json').read_text());assert len(hashes)==36
    for name,digest in hashes.items():assert a.sha(root/'frames'/name)==digest
    encode(root)
    a.save(root/'verification.json',{'verified':True,'repaints':rows,'same_opening':True,
        'checks':'all requested/executed graphs, parent/input/output hashes, successful histories, selected reconstructed warps, frame hashes and video timing'})
    compare('cadence',root/'frames','Repaint every 2 frames; same recipe',12)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=['rife','cadence']);args=p.parse_args()
    rife() if args.case=='rife' else cadence()
