"""Matched paintings, delivery crops, and a compact video comparison."""
import argparse
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont

import early_settle as e
from hold_transform_review import sheet


def sources():
    old,new=e.OLD,e.OUT/e.CASE
    for page in range(2):
        frames=list(range(96,181,12))[page*4:(page+1)*4]
        rows=[[(Image.open(root/f'anchors/{f:04d}.png'),f'{label} | frame {f} | {f/24:.1f}s')
                for label,root in [('Previous',old),('Earlier settling',new)]] for f in frames]
        sheet(rows,e.OUT/f'review/paintings-{page+1}.jpg')
    frames=(96,108,120,132,180)
    rows=[[(Image.open(root/f'anchors/{f:04d}.png').crop((768,256,1408,682)),
            f'{label} | frame {f} | native detail') for label,root in [('Previous',old),('Earlier settling',new)]] for f in frames]
    sheet(rows,e.OUT/'review/architecture-detail.jpg')


def delivery():
    old,new=e.OLD/'section-016/rife',e.OUT/e.CASE/'section-016/rife'
    for start in (103,115):
        frames=list(range(start,start+6))
        rows=[[(Image.open(root/f'frames/{f:04d}.png').crop((768,256,1408,682)),
                f'{label} | frame {f} | {f/24:.3f}s') for label,root in [('Previous',old),('Earlier settling',new)]] for f in frames]
        sheet(rows,e.OUT/f'review/delivery-{start}.jpg',size=(480,320))
    header=e.OUT/'comparison-header.png';im=Image.new('RGB',(1536,30),'#181818');d=ImageDraw.Draw(im);font=ImageFont.load_default(size=20)
    d.text((12,4),'PREVIOUS - SETTLES AT 6.5s',fill='white',font=font)
    d.text((780,4),'NEW - STARTS SETTLING AT 4.5s',fill='white',font=font);im.save(header)
    video=e.OUT/'comparison.mp4'
    if not video.exists():
        subprocess.run(['ffmpeg','-v','error','-n','-loop','1','-framerate','24','-i',str(header),
            '-i',str(old/'preview.mp4'),'-i',str(new/'preview.mp4'),'-filter_complex',
            '[1:v]scale=768:512[l];[2:v]scale=768:512[r];[l][r]hstack[v];[0:v][v]vstack[out]',
            '-map','[out]','-frames:v','192','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',
            '-movflags','+faststart',str(video)],check=True)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-count_frames',
        '-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(video)]))['streams'][0]
    assert info['r_frame_rate']=='24/1' and info['nb_read_frames']=='192'
    (e.OUT/'review/comparison-check.json').write_text(json.dumps({'verified':True,'video':info,'sha256':e.base.sha(video)},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['sources','delivery']);a=p.parse_args()
    sources() if a.stage=='sources' else delivery()
