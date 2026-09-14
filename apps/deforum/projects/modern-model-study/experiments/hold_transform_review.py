"""Bounded visual review and a labeled chat comparison for the moving hold test."""
import argparse
import json
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import hold_transform as h


def sheet(rows, target, size=(640, 426)):
    board = Image.new('RGB', (size[0]*2, (size[1]+28)*len(rows)), '#181818')
    draw = ImageDraw.Draw(board)
    font = ImageFont.load_default(size=17)
    for row, pair in enumerate(rows):
        for col, (im, label) in enumerate(pair):
            im = im.copy(); im.thumbnail(size)
            x, y = col*size[0], row*(size[1]+28)
            board.paste(im, (x,y+28)); draw.text((x+8,y+5), label, font=font, fill='white')
    target.parent.mkdir(parents=True, exist_ok=True)
    board.save(target)


def sources():
    configs = {c:json.loads((h.OUT/c/'config.json').read_text()) for c in h.CASES}
    metrics = []
    for start in range(0,16,4):
        rows = []
        for i in range(start,start+4):
            pair = []
            for case in h.CASES:
                frame=i*12; image=Image.open(h.OUT/case/f'anchors/{frame:04d}.png')
                scene,sigmas=h.journey.recipe(configs[case],i*.5)
                noise_label = 'shared source' if i == 0 else f'noise {sigmas[0]:.2f}'
                pair.append((image,f'{case} | {i*.5:.1f}s | {noise_label}'))
                if i:
                    before=np.asarray(Image.open(h.OUT/case/f'warped-inputs/{frame:04d}.png')).astype(float)
                    metrics.append({'case':case,'frame':frame,'seconds':i*.5,
                        'repaint_change_rgb':float(np.abs(np.asarray(image).astype(float)-before).mean()/255)})
            rows.append(pair)
        sheet(rows,h.OUT/f'review/paintings-{start//4+1}.jpg')
    (h.OUT/'review/repaint-change.json').write_text(json.dumps(metrics,indent=2))
    for label,frames,crop in [('early',[0,12,24,36],(256,192,896,618)),
                              ('late',[144,156,168,180],(640,256,1280,682))]:
        rows=[[(Image.open(h.OUT/c/f'anchors/{f:04d}.png').crop(crop),f'{c} | {f/24:.1f}s | native crop')
               for c in h.CASES] for f in frames]
        sheet(rows,h.OUT/f'review/{label}-detail.jpg')


def delivery():
    # Consecutive full-size crop frames around the largest average repaint change.
    metrics=json.loads((h.OUT/'review/repaint-change.json').read_text())
    strongest=max(range(12,181,12),key=lambda f:sum(r['repaint_change_rgb'] for r in metrics if r['frame']==f))
    frames=list(range(strongest-7,strongest+1))
    for start in range(0,8,4):
        rows=[[(Image.open(h.OUT/c/f'section-016/rife/frames/{f:04d}.png').crop((448,256,1088,682)),
                f'{c} | frame {f} | {f/24:.3f}s') for c in h.CASES] for f in frames[start:start+4]]
        sheet(rows,h.OUT/f'review/transition-{start//4+1}.jpg')
    header=h.OUT/'comparison-header.png'
    im=Image.new('RGB',(1536,30),'#181818');draw=ImageDraw.Draw(im);font=ImageFont.load_default(size=20)
    draw.text((12,4),'USUAL HOLD 0.60 / 0.64',fill='white',font=font)
    draw.text((780,4),'LOW HOLD 0.10 - SAME TRANSFORMATION RAMP',fill='white',font=font)
    im.save(header)
    output=h.OUT/'comparison.mp4'
    if not output.exists():
        subprocess.run(['ffmpeg','-v','error','-n','-loop','1','-framerate','24','-i',str(header),
            '-i',str(h.OUT/'usual-hold/section-016/rife/preview.mp4'),
            '-i',str(h.OUT/'low-hold/section-016/rife/preview.mp4'),
            '-filter_complex','[1:v]scale=768:512[l];[2:v]scale=768:512[r];[l][r]hstack[v];[0:v][v]vstack[out]',
            '-map','[out]','-frames:v','192','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',
            '-movflags','+faststart',str(output)],check=True)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(output),'-f','null','-'],check=True)
    (h.OUT/'review/selection.json').write_text(json.dumps({'largest_repaint_frame':strongest,
        'consecutive_delivery_frames':frames,'note':'RGB change measures redraw, not aesthetic quality.'},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['sources','delivery']);args=p.parse_args()
    h.configure()
    sources() if args.stage=='sources' else delivery()
