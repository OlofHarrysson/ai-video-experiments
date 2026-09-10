"""Finish archived half-second paintings locally using the pinned RIFE path."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess

from PIL import Image, ImageDraw
import ten_dollar as t


def prepare(case):
    root = t.OUT/case
    config = json.loads((root/'config.json').read_text())
    anchors = sorted((root/'anchors').glob('*.png'))
    assert len(anchors) == round(config['duration']*2)
    assert [int(p.stem) for p in anchors] == list(range(0, round(config['duration']*24), 12))
    source = root/'interpolation-source'
    source.mkdir(exist_ok=True)
    for i, p in enumerate(anchors):
        dest = source/f'{i:04d}.png'
        if dest.exists():
            assert t.sha(dest) == t.sha(p)
        else:
            shutil.copy2(p, dest)
    for start in range(0, len(anchors), 8):
        page = anchors[start:start+8]
        board = Image.new('RGB', (1024, ((len(page)+1)//2)*370), '#171717')
        draw = ImageDraw.Draw(board)
        for i, path in enumerate(page):
            x, y = i%2*512, i//2*370
            draw.text((x+10,y+8), f'{case}  {int(path.stem)/24:.1f}s', fill='white')
            image = Image.open(path); image.thumbnail((512,341))
            board.paste(image,(x,y+27))
        board.save(root/f'paintings-{start//8+1:02d}.jpg')
    return root, source, len(anchors)


def run(case, stage):
    root, source, count = prepare(case)
    if stage == 'prepare':
        return
    py = t.APP/'work/rife-session/.venv/bin/python'
    args = [str(py), str(t.APP/'interpolate.py'), str(source), str(root/('first-pair' if stage=='pair' else 'rife')),
        '--source-frames',str(count),'--source-fps','2','--multiplier','12']
    if stage == 'pair':
        args += ['--pair-only']
    else:
        args += ['--validated-pair',str(root/'first-pair/manifest.json')]
    subprocess.run(args, check=True)
    if stage == 'full':
        output=root/'rife'
        # Every final native tail is stationary: all spatial phrases have settled.
        config=json.loads((root/'config.json').read_text())
        assert config['duration']-.5 >= max(config['motion']['settle'],config['motion']['travel_window'][1])
        for i, p in enumerate(sorted(source.glob('*.png'))):
            assert t.sha(p) == t.sha(output/f'frames/{i*12:04d}.png')
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(output/'preview.mp4'),'-f','null','-'],check=True)
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames',
            '-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(output/'preview.mp4')]))['streams'][0]
        assert info['r_frame_rate']=='24/1' and int(info['nb_read_frames'])==count*12
        t.save(root/'delivery-check.json',{'verified':True,'all_paintings_retained':count,'video':info,
            'video_sha256':t.sha(output/'preview.mp4'),'interpolation':'RIFE 4.25 scale 1, eleven predictions between each painting',
            'final_tail':'half-second stationary native hold; motion already settled'})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case');p.add_argument('--stage',choices=['prepare','pair','full'],required=True)
    args=p.parse_args();run(args.case,args.stage)
