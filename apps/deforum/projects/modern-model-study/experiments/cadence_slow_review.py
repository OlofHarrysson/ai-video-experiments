"""Validate feedback and compare four raw or interpolated timelines at equal time."""
import argparse,json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import cadence_slow as c
import cadence_spacing_review as v

s,a,OUT=c.s,c.s.a,c.OUT


def main(interpolated=False):
    for cadence in c.CASES:
        if interpolated:v.finish(cadence,out=OUT,make_comparison=False)
        else:v.prepare(cadence,out=OUT)
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23)
    sources=[(3,s.CONTROL),*[(x,OUT/f'cadence-{x}') for x in c.CASES]]
    if interpolated:
        sources=[(3,a.PROJECT/'exports/turbo-smoothing-v001/interpolation'),
                 *[(x,OUT/f'cadence-{x}/interpolated') for x in c.CASES]]
    root=OUT/('comparison-rife' if interpolated else 'comparison')
    for frame in range(72 if interpolated else 36):
        canvas=Image.new('RGB',(1536,1108),'#15191d');draw=ImageDraw.Draw(canvas)
        for i,(cadence,source) in enumerate(sources):
            x,y=(i%2)*768,(i//2)*554
            canvas.paste(Image.open(source/f'frames/{frame:04d}.png').convert('RGB').resize((768,512),Image.Resampling.LANCZOS),(x,y+42))
            draw.text((x+12,y+9),f'Cadence {cadence}{" + RIFE" if interpolated else ""} | repaint every {cadence/12:.2f}s',font=font,fill='white')
        a.image(root/f'frames/{frame:04d}.png',np.asarray(canvas))
    target=root/'preview.mp4'
    if not target.exists():a.editing.encode(root/'frames',target,fps=24 if interpolated else 12)
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(target)]))['streams'][0]
    assert info['nb_read_frames']=='72' and info['avg_frame_rate']=='24/1' and float(info['duration'])==3
    a.save(root/'manifest.json',{'probe':info,'interpolation':interpolated,'frame_hashes':{p.name:a.sha(p) for p in sorted((root/'frames').glob('*.png'))},
        'panels':[{'cadence':x,'source':str(p.relative_to(a.PROJECT))} for x,p in sources]})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--interpolated',action='store_true')
    main(parser.parse_args().interpolated)
