"""Verify feedback/noise lineage and prepare review artifacts for the noise study."""
import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
import correlated_noise as study
import dynamic_journey_finish as finish

OUT = study.OUT


def pixels(p):
    return np.asarray(Image.open(p).convert('RGB'))


def check_generation():
    rows=[]; ids=[]
    for case,rho in study.CASES.items():
        root=OUT/case;config=json.loads((root/'config.json').read_text())
        assert sorted(int(p.stem) for p in (root/'anchors').glob('*.png'))==list(range(0,96,6))
        assert study.base.sha(root/'anchors/0000.png')==study.base.sha(OUT/'source/seed.png')
        previous_noise=None
        for f in range(6,96,6):
            rec=json.loads((root/f'anchor-{f:04d}.json').read_text()); run=OUT/rec['run']
            parent=root/f'anchors/{f-6:04d}.png'; target=root/f'anchors/{f:04d}.png'
            assert rec['parent_sha256']==rec['initialization_sha256']==study.base.sha(parent)==study.base.sha(run/'anchor.png')
            assert rec['output_sha256']==study.base.sha(target)==study.base.sha(run/'frames/0000.png')
            expected=study.graph(config,f//6-1)
            assert json.loads((run/'workflow.api.json').read_text())==expected
            actual=json.loads((run/'workflow.executed.json').read_text())
            uploaded=json.loads((run/'upload.json').read_text())
            expected['20']['inputs']['image']='/'.join(filter(None,[uploaded.get('subfolder'),uploaded['name']]))
            assert actual==expected
            hist=json.loads((run/'history.json').read_text())
            assert hist['status']['completed'] and hist['prompt'][2]==actual
            ids.append(json.loads((run/'submit-response.json').read_text())['prompt_id'])
            diagnostic=OUT/'diagnostics'/case/f'{f//6-1:04d}.npz'
            with np.load(diagnostic) as d:eps=d['noise'].copy()
            nr=json.loads(diagnostic.with_suffix('.json').read_text())
            assert nr['noise_sha256']==hashlib.sha256(eps.tobytes()).hexdigest()
            assert nr['index']==f//6-1 and nr['base_seed']==study.SEED and nr['correlation']==rho
            assert abs(float(eps.std())-1)<.01 and abs(float(eps.mean()))<.01
            measured=None if previous_noise is None else float(np.corrcoef(previous_noise.ravel(),eps.ravel())[0,1])
            if measured is not None:assert abs(measured-rho)<.01
            if case=='correlated' and previous_noise is not None:
                with np.load(OUT/'diagnostics/independent'/diagnostic.name) as d:eta=d['noise']
                # Array arithmetic follows float32 scalar behavior used by Torch.
                expected_eps=np.float32(rho)*previous_noise+np.float32(np.sqrt(1-rho*rho))*eta
                np.testing.assert_allclose(eps,expected_eps,atol=5e-7,rtol=1e-6)
            previous_noise=eps
            change=np.abs(pixels(target).astype(np.float32)-pixels(parent).astype(np.float32)).mean()/255
            rows.append({'case':case,'frame':f,'noise_index':nr['index'],'noise_std':float(eps.std()),
                'noise_correlation_with_previous':measured,'painting_mean_absolute_change':float(change)})
    assert len(ids)==len(set(ids))==30
    assert np.array_equal(pixels(OUT/'independent/anchors/0006.png'),pixels(OUT/'correlated/anchors/0006.png'))
    assert json.loads((OUT/'sampler-parity.json').read_text())['pixel_identical']
    report={'verified':True,'recurrent_jobs':30,'same_first_repaint':True,
            'native_sampler_parity':True,'noise_variance_and_recurrence_verified':True,'rows':rows}
    study.base.save(OUT/'generation-check.json',report)
    print('Verified all 30 recurrent jobs, actual noise statistics, recurrence and sampler parity')


def diagnostic_media():
    archive=study.base.APP/'work/correlated-noise-session/final/remote-media'
    for case in study.CASES:
        folder=OUT/'diagnostics'/case
        for f in (6,12,48,90):
            rec=json.loads((OUT/case/f'anchor-{f:04d}.json').read_text())
            hist=json.loads((OUT/rec['run']/'history.json').read_text())
            item=hist['outputs']['48']['images'][0]
            source=archive/item['type']/item.get('subfolder','')/item['filename']
            target=folder/f'noisy-preview-{f:04d}.png'
            if target.exists():assert study.base.sha(target)==study.base.sha(source)
            else:shutil.copy2(source,target)
        frames=folder/'noise-frames';frames.mkdir(exist_ok=True)
        for i in range(16):
            board=Image.new('RGB',(768,512),'#181818');draw=ImageDraw.Draw(board)
            title='Opening: no new noise yet' if i==0 else f'{case} | actual noise channel 0 | painting {i}'
            if i:
                with np.load(folder/f'{i-1:04d}.npz') as d:channel=d['noise'].reshape(-1,*d['noise'].shape[-2:])[0]
                im=Image.fromarray(np.uint8(np.clip((channel+3)/6,0,1)*255)).convert('RGB')
                im=im.resize((672,448),Image.Resampling.NEAREST)
                board.paste(im,(48,38))
            draw.text((20,12),title,fill='white')
            draw.text((20,494),'Fixed grayscale: -3 black / 0 gray / +3 white. Not a motion guide.',fill='white')
            board.save(frames/f'{i:04d}.png')
        video=folder/'noise.mp4'
        if not video.exists():
            subprocess.run(['ffmpeg','-v','error','-n','-framerate','4','-i',str(frames/'%04d.png'),
                '-vf','fps=24','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
    for f in (12,48,90):
        board=Image.new('RGB',(1536,730),'#161616');draw=ImageDraw.Draw(board)
        for row,case in enumerate(study.CASES):
            paths=[OUT/case/f'anchors/{f-6:04d}.png',OUT/'diagnostics'/case/f'noisy-preview-{f:04d}.png',OUT/case/f'anchors/{f:04d}.png']
            for col,(p,label) in enumerate(zip(paths,['Previous painting','Noisy latent: approximate decode','Next painting'])):
                im=Image.open(p).convert('RGB');im.thumbnail((512,341));board.paste(im,(col*512,row*365+24))
                draw.text((col*512+8,row*365+6),f'{case} {f/24:.2f}s | {label}',fill='white')
        board.save(OUT/f'noise-walkthrough-{f:04d}.jpg')
    # Same-time source paintings; no interpolation in this overview.
    for start in (0,48):
        board=Image.new('RGB',(1536,730),'#161616');draw=ImageDraw.Draw(board)
        for row,case in enumerate(study.CASES):
            for col,f in enumerate((start,start+18,start+42)):
                im=Image.open(OUT/case/f'anchors/{f:04d}.png');im.thumbnail((512,341))
                board.paste(im,(col*512,row*365+24));draw.text((col*512+8,row*365+6),f'{case} | {f/24:.2f}s',fill='white')
        board.save(OUT/f'paintings-matched-{start:04d}.jpg')


def finish_stage(stage):
    finish.d.OUT=OUT
    for case in study.CASES:finish.run(case,stage)


def check_delivery():
    rows=[]
    for case in study.CASES:
        root=OUT/case; path=root/'section-016/rife'; video=path/'preview.mp4'
        manifest=json.loads((path/'manifest.json').read_text())
        assert manifest['status']=='complete' and manifest['anchors_verified']
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries',
            'stream=width,height,r_frame_rate,duration,nb_frames','-of','json',str(video)]))['streams'][0]
        assert info=={'width':1536,'height':1024,'r_frame_rate':'24/1','duration':'4.000000','nb_frames':'96'}
        for f in range(96):
            if f%6==0 or f>90:
                assert np.array_equal(pixels(path/f'frames/{f:04d}.png'),pixels(root/f'anchors/{min(f,90):04d}.png'))
        rows.append({'case':case,'sha256':study.base.sha(video),'paintings_retained':16,**info})
    study.base.save(OUT/'delivery-check.json',{'verified':True,'videos':rows,'interpolation':'RIFE 4.25 scale 1, outside feedback'})
    print('Verified both four-second 24fps videos and all painting/tail positions')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=['verify','diagnostics','pair','full','delivery']);args=p.parse_args()
    if args.stage=='verify':check_generation()
    elif args.stage=='diagnostics':diagnostic_media()
    elif args.stage=='delivery':check_delivery()
    else:finish_stage(args.stage)
