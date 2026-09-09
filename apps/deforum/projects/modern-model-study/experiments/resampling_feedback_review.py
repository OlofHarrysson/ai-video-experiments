"""Verify the Lanczos feedback probe and compare the preserved bilinear control."""
import copy
import json
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import resampling_feedback as c
from cathedral_review import assert_warp_matches


def main():
    rows = []
    for strength in c.STRENGTHS:
        root = c.OUT / strength
        assert c.a.sha(root/'anchors/0000.png') == c.a.sha(c.opening.OUT/'krea-cathedral/image.png')
        for f in range(3, c.FRAMES, 3):
            record = json.loads((root/f'anchor-{f:04d}.json').read_text())
            run = c.a.PROJECT / record['run']
            prior = root/f'anchors/{f-3:04d}.png'
            source = root/f'warped-inputs/{f:04d}.png'
            output = root/f'anchors/{f:04d}.png'
            assert c.a.sha(prior) == record['parent_sha256']
            assert c.a.sha(source) == c.a.sha(run/'anchor.png') == record['initialization_sha256']
            assert c.a.sha(output) == c.a.sha(run/'frames/0000.png') == record['output_sha256']
            requested = json.loads((run/'workflow.api.json').read_text())
            assert requested == c.graph(strength, c.SEED+f//3)
            executed = json.loads((run/'workflow.executed.json').read_text())
            normalized = copy.deepcopy(executed)
            normalized['20']['inputs']['image'] = 'anchor.png'
            assert normalized == requested
            assert executed['9']['inputs']['latent_image'] == ['24', 0]
            assert Image.open(output).size == (c.WIDTH, c.HEIGHT)
            if f in (3, 18, 33):
                rebuilt = c.warp(np.asarray(Image.open(prior).convert('RGB')), f-3, f)
                assert_warp_matches(rebuilt, np.asarray(Image.open(source).convert('RGB')))
            history = json.loads((run/'history.json').read_text())
            assert history['status']['completed'] and history['status']['status_str'] == 'success'
            messages = history['status']['messages']
            start = next(v['timestamp'] for k,v in messages if k == 'execution_start')
            end = next(v['timestamp'] for k,v in messages if k == 'execution_success')
            rows.append({'strength': strength, 'frame': f,
                         'execution_seconds': (end-start)/1000, 'run': record['run']})
        hashes = json.loads((root/'frame-hashes.json').read_text())
        assert len(hashes) == c.FRAMES
        for name, digest in hashes.items():
            assert c.a.sha(root/'frames'/name) == digest
        # Verify a cadence boundary and its neighboring warp-only images.
        for f in (23,24,25):
            anchor = f//3*3
            expected = c.warp(np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')), anchor, f)
            assert_warp_matches(expected, np.asarray(Image.open(root/f'frames/{f:04d}.png').convert('RGB')))
        info = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(root/'preview.mp4')]))['streams'][0]
        assert info['nb_frames'] == '72' and info['r_frame_rate'] == '24/1'

    c.a.save(c.OUT/'verification.json', {'verified': True, 'anchors': len(rows), 'results': rows,
        'checks': 'all input/output hashes and executed graphs; sampled warp reconstruction; cadence boundaries; delivery frames'})
    sources=[c.a.PROJECT/'exports/krea-low-repaint-v001/d010',c.OUT/'lanczos010']
    labels=['Current bilinear warp | repaint 0.10','Lanczos warp | repaint 0.10']
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23)
    target=c.OUT/'comparison/preview.mp4'
    for f in range(c.FRAMES):
        canvas=Image.new('RGB',(1536,552),'#15191d');draw=ImageDraw.Draw(canvas)
        for j,root in enumerate(sources):
            im=Image.open(root/f'frames/{f:04d}.png').convert('RGB')
            canvas.paste(im.resize((768,512),Image.Resampling.LANCZOS),(j*768,40))
            draw.text((j*768+12,8),labels[j],font=font,fill='white')
        c.a.image(target.parent/f'frames/{f:04d}.png',np.asarray(canvas))
    if not target.exists():c.a.editing.encode(target.parent/'frames',target,fps=c.FPS)
    c.a.save(target.parent/'manifest.json',{'labels':labels,'sources':[str(p.relative_to(c.a.PROJECT)) for p in sources],
        'source_manifest_hashes':[c.a.sha(p/'manifest.json') for p in sources]})
    print('Verified eleven Lanczos feedback anchors and comparison')


if __name__=='__main__':main()
