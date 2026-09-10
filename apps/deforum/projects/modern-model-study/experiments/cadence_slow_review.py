"""Validate feedback and compare four raw cadence timelines at equal time."""
import json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import cadence_slow as c
import cadence_spacing_review as v

s,a,OUT=c.s,c.s.a,c.OUT


def main():
    for cadence in c.CASES:v.prepare(cadence,out=OUT)
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23)
    sources=[(3,s.CONTROL),*[(x,OUT/f'cadence-{x}') for x in c.CASES]]
    root=OUT/'comparison'
    for frame in range(36):
        canvas=Image.new('RGB',(1536,1108),'#15191d');draw=ImageDraw.Draw(canvas)
        for i,(cadence,source) in enumerate(sources):
            x,y=(i%2)*768,(i//2)*554
            canvas.paste(Image.open(source/f'frames/{frame:04d}.png').convert('RGB').resize((768,512),Image.Resampling.LANCZOS),(x,y+42))
            draw.text((x+12,y+9),f'Cadence {cadence} | repaint every {cadence/12:.2f}s',font=font,fill='white')
        a.image(root/f'frames/{frame:04d}.png',np.asarray(canvas))
    target=root/'preview.mp4'
    if not target.exists():a.editing.encode(root/'frames',target,fps=12)
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(target)]))['streams'][0]
    assert info['nb_read_frames']=='72' and info['avg_frame_rate']=='24/1' and float(info['duration'])==3
    a.save(root/'manifest.json',{'probe':info,'interpolation':False,'frame_hashes':{p.name:a.sha(p) for p in sorted((root/'frames').glob('*.png'))},
        'panels':[{'cadence':x,'source':str(p.relative_to(a.PROJECT))} for x,p in sources]})


if __name__=='__main__':main()
