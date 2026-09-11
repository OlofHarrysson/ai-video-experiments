"""Local RIFE finishing and an immutable join to the preserved 3.5-second opening."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

import numpy as np
from PIL import Image, ImageDraw

import dynamic_journey as d


def prepare(case):
    root=d.OUT/case
    files=sorted((root/'anchors').glob('*.png'))
    assert [int(p.stem) for p in files]==list(range(0,len(files)*12,12))
    target=root/f'section-{len(files):03d}'
    source=target/'sources';source.mkdir(parents=True,exist_ok=True)
    for i,p in enumerate(files):
        dest=source/f'{i:04d}.png'
        if dest.exists():assert d.base.sha(dest)==d.base.sha(p)
        else:shutil.copy2(p,dest)
    for start in range(0,len(files),8):
        page=files[start:start+8]
        board=Image.new('RGB',(1024,370*((len(page)+1)//2)),'#171717');draw=ImageDraw.Draw(board)
        for i,p in enumerate(page):
            x,y=i%2*512,i//2*370;im=Image.open(p);im.thumbnail((512,341));board.paste(im,(x,y+25))
            draw.text((x+10,y+6),f'{case} | continuation {int(p.stem)/24:.1f}s',fill='white')
        board.save(target/f'paintings-{start//8+1:02d}.jpg')
    return root,target,source,files


def run(case,stage):
    root,target,source,files=prepare(case)
    if stage=='prepare':return
    if stage in ('pair','full'):
        args=[str(d.APP/'work/rife-session/.venv/bin/python'),str(d.APP/'interpolate.py'),str(source),
            str(target/('pair' if stage=='pair' else 'rife')),'--source-frames',str(len(files)),
            '--source-fps','2','--multiplier','12']
        args+=['--pair-only'] if stage=='pair' else ['--validated-pair',str(target/'pair/manifest.json')]
        subprocess.run(args,check=True)
        return
    config=json.loads((root/'config.json').read_text())
    assert len(files)==round(config['duration']*2)
    points=np.array([[.1,.1],[.5,.5],[1.4,.9]])
    assert np.array_equal(d.mapping(points,config['duration']-.5,config['phrases']),d.mapping(points,config['duration'],config['phrases']))
    old=d.OUT.parent/'ten-dollar-v001/clock-pulse/rife/frames'
    fresh=target/'rife/frames'
    assert d.base.sha(old/'0084.png')==d.base.sha(fresh/'0000.png')
    sources=[old/f'{i:04d}.png' for i in range(84)]+sorted(fresh.glob('*.png'))
    joined=root/'film';(joined/'frames').mkdir(parents=True,exist_ok=False)
    rows=[]
    for i,p in enumerate(sources):
        dest=joined/f'frames/{i:04d}.png';os.link(p,dest)
        rows.append({'index':i,'source':str(p.relative_to(d.OUT.parents[1])), 'sha256':d.base.sha(p)})
    # The shared painting occurs once, exactly at the join; retain all other anchors too.
    expected_paintings=[old/f'{i:04d}.png' for i in range(0,84,12)]+files
    assert len(sources)==24*24
    for i,p in enumerate(expected_paintings):assert d.base.sha(p)==d.base.sha(joined/f'frames/{i*12:04d}.png')
    video=joined/'preview.mp4'
    subprocess.run(['ffmpeg','-v','error','-n','-framerate','24','-i',str(joined/'frames/%04d.png'),
        '-frames:v',str(len(sources)),'-an','-c:v','libx264','-crf','18','-preset','slow','-pix_fmt','yuv420p',
        '-movflags','+faststart',str(video)],check=True)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames',
        '-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(video)]))['streams'][0]
    assert info['r_frame_rate']=='24/1' and int(info['nb_read_frames'])==576
    d.base.save(joined/'delivery-check.json',{'verified':True,'video':info,'paintings_retained':len(expected_paintings),
        'shared_anchor_at_seconds':3.5,'source_frames':rows,'video_sha256':d.base.sha(video),
        'final_tail':'stationary native painting; all motion phrases have settled'})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case');p.add_argument('--stage',choices=['prepare','pair','full','join'],required=True)
    args=p.parse_args();run(args.case,args.stage)
