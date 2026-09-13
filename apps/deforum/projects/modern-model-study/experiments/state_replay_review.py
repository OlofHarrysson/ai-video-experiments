"""Verify a recorded-state parameter sweep and show its actual generated samples."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import state_replay as study

OUT=study.OUT
ROI=(380,240,1150,800)


def pixels(path):return np.asarray(Image.open(path).convert('RGB'))


def verify():
    source=study.SOURCE/'diagnostics/independent/0000.npz'
    with np.load(source) as d:z=d['input_latent'].copy();eps=d['noise'].copy()
    archive=study.base.APP/'work/state-replay-session/finish/remote-media/output/state-replay-v001'
    rows=[];ids=[];direction=None
    for p in sorted((OUT/'samples').glob('*.json')):
        r=json.loads(p.read_text());run=OUT/r['run'];a=r['amount']
        assert r['source_recording_sha256']==study.base.sha(source)
        assert r['output_sha256']==study.base.sha(p.with_suffix('.png'))==study.base.sha(run/'frames/0000.png')
        g=study.graph(a)
        assert json.loads((run/'workflow.api.json').read_text())==g
        assert json.loads((run/'workflow.executed.json').read_text())==g
        h=json.loads((run/'history.json').read_text());assert h['status']['completed'] and h['prompt'][2]==g
        ids.append(json.loads((run/'submit-response.json').read_text())['prompt_id'])
        with np.load(archive/f'{round(a*1000):04d}.npz') as d:
            assert np.array_equal(d['input_latent'],z)
            if direction is None:direction=d['direction'].copy()
            assert np.array_equal(direction,d['direction'])
            expected=np.float32(np.sqrt(1-a*a))*eps+np.float32(a)*direction
            np.testing.assert_allclose(d['noise'],expected,atol=5e-7,rtol=1e-6)
            std=float(d['noise'].std());assert abs(std-1)<.01
            movement=float(np.sqrt(np.mean((np.float32(.6)*(d['noise']-eps))**2)))
        im=pixels(p.with_suffix('.png'));initial=pixels(OUT/'samples/0000.png')
        rows.append({'amount':a,'noise_std':std,'sampling_state_rms_change':movement,
            'rgb_mean_absolute_difference_from_replay':float(np.abs(im.astype(float)-initial).mean()/255)})
    expected=sorted(set(round(a,6) for v in study.PATHS.values() for a in v))
    assert sorted(r['amount'] for r in rows)==expected
    assert len(ids)==len(set(ids))==len(expected)
    assert np.array_equal(pixels(OUT/'samples/0000.png'),pixels(study.SOURCE/'independent/anchors/0006.png'))
    result={'verified':True,'jobs':len(ids),'exact_historical_replay':True,'fixed_source_latent':True,
        'one_fixed_direction':True,'recurrent':False,'rows':rows}
    study.base.save(OUT/'generation-check.json',result)
    print(json.dumps(result,indent=2))


def sheet(amounts,name,crop=False):
    width=640;height=round(width*(ROI[3]-ROI[1])/(ROI[2]-ROI[0])) if crop else round(width*1024/1536)
    canvas=Image.new('RGB',(width*2,(height+34)*((len(amounts)+1)//2)), '#151515')
    draw=ImageDraw.Draw(canvas)
    for i,a in enumerate(amounts):
        im=Image.open(OUT/'samples'/f'{round(a*1000):04d}.png').convert('RGB')
        if crop:im=im.crop(ROI)
        im=im.resize((width,height),Image.Resampling.LANCZOS)
        x=i%2*width;y=i//2*(height+34)
        canvas.paste(im,(x,y+34));draw.text((x+12,y+10),f'Perturbation {a:.3f}',fill='white')
    canvas.save(OUT/name,quality=94)


def media():
    paths={}
    for name,amounts in study.PATHS.items():
        dest=OUT/name;frames=dest/'frames';frames.mkdir(parents=True,exist_ok=True)
        for i,a in enumerate(amounts):
            source=OUT/'samples'/f'{round(a*1000):04d}.png'
            for subframe in range(6):
                target=frames/f'{i*6+subframe:04d}.png'
                if not target.exists():target.symlink_to(source.resolve())
        video=dest/'preview.mp4'
        subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(frames/'%04d.png'),
            '-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
        # Certify only sample timestamps, not any recurrent lineage.
        paths[name]={'source':str(video.relative_to(study.base.APP)),'sample_amounts':amounts,
            'frames':len(amounts)*6,'fps':24,'seconds':len(amounts)/4,'interpolation':'none; repeated samples'}
        decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','rgb24','-'])
        images=np.frombuffer(decoded,np.uint8).reshape(-1,1024,1536,3)
        assert len(images)==78
        errors=[]
        for i,a in enumerate(amounts):
            reference=pixels(OUT/'samples'/f'{round(a*1000):04d}.png')
            err=float(np.abs(images[i*6].astype(np.float32)-reference).mean())
            assert err<3,err
            errors.append(err)
        paths[name]['max_encoded_sample_mae_8bit']=max(errors)
        provenance=[{'index':f,'time_seconds':f/24,'kind':'anchor' if f%6==0 else 'hold',
                     'source_index':f//6,'amount':amounts[f//6]} for f in range(78)]
        manifest={'status':'complete','video_sha256':study.base.sha(video),'output_frames':provenance,
                  'provenance':{'model':'Krea fixed-state parameter sweep; no temporal interpolation'},
                  'source_samples':[{'amount':a,'sha256':study.base.sha(OUT/'samples'/f'{round(a*1000):04d}.png')} for a in amounts]}
        study.base.save(dest/'manifest.json',manifest)
        if name=='wider':
            crop=dest/'detail';crop.mkdir(exist_ok=True)
            detail=crop/'preview.mp4'
            subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(frames/'%04d.png'),
                '-vf','crop=600:600:900:390','-c:v','libx264','-crf','16','-pix_fmt','yuv420p',
                '-movflags','+faststart',str(detail)],check=True)
            check=subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0',
                '-show_entries','stream=nb_read_frames,width,height','-of','json',str(detail)])
            stream=json.loads(check)['streams'][0]
            assert int(stream['nb_read_frames'])==78 and stream['width']==stream['height']==600
            subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(detail),'-f','null','-'],check=True)
            study.base.save(crop/'manifest.json',{**manifest,'video_sha256':study.base.sha(detail),
                'crop_xywh':[900,390,600,600]})
            paths[name]['detail_crop_verified']=True
    study.base.save(OUT/'delivery-check.json',{'verified':True,'paths':paths,'recurrent':False})
    sheet([0,.02,.06,.12,.24],'overview.jpg')
    sheet([0,.02,.06,.12,.24],'details.jpg',crop=True)
    sheet([.18,.20,.22,.24],'consecutive.jpg',crop=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['verify','media','coarse']);a=p.parse_args()
    if a.stage=='verify':verify()
    elif a.stage=='media':media()
    else:
        sheet([0,.02,.06,.12,.24],'coarse.jpg')
        sheet([0,.02,.06,.12,.24],'coarse-details.jpg',crop=True)
