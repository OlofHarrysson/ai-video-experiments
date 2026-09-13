"""Audit actual recurrent inputs/noise and render raw, held-painting diagnostics."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
import history_recurrence as study

OUT=study.OUT


def read(p):return json.loads(p.read_text())
def pixels(p):return np.asarray(Image.open(p).convert('RGB'))


def verify():
    archive=study.base.APP/'work/history-recurrence-session/render/remote-media'
    rows=[];ids=[];all_noise={};baseline_matches=[]
    for case,(rho,use_history) in study.CASES.items():
        root=OUT/case;diagnostics=root/'diagnostics';diagnostics.mkdir(exist_ok=True)
        past=[];prev_eps=None
        assert read(root/'config.json')==study.config(case)
        assert study.base.sha(root/'anchors/0000.png')==study.base.sha(study.base.APP/study.previous.SOURCE)
        for index in range(study.CYCLES):
            f=(index+1)*6;r=read(root/f'anchor-{f:04d}.json');run=OUT/r['run']
            current=root/f'anchors/{index*6:04d}.png';output=root/f'anchors/{f:04d}.png'
            assert r['parent_sha256']==study.base.sha(current)==study.base.sha(run/'anchor.png')
            assert r['output_sha256']==study.base.sha(output)==study.base.sha(run/'frames/0000.png')
            expected=study.graph(case,index)
            assert read(run/'workflow.api.json')==expected
            upload=read(run/'upload.json');expected['20']['inputs']['image']='/'.join(filter(None,[upload.get('subfolder'),upload['name']]))
            assert read(run/'workflow.executed.json')==expected
            history=read(run/'history.json');assert history['status']['completed'] and history['prompt'][2]==expected
            ids.append(read(run/'submit-response.json')['prompt_id'])
            count=min(index+1,3) if use_history else 1
            refs=[root/f'anchors/{(index-age)*6:04d}.png' for age in range(count)]
            assert r['history_sha256']==[study.base.sha(p) for p in refs]
            for age,p in enumerate(refs):
                assert study.base.sha(archive/f'input/history-recurrence-v001/{case}/{index-age:04d}.png')==study.base.sha(p)
            original=archive/f'output/history-recurrence-v001/{case}/{index:04d}.npz'
            dest=diagnostics/original.name
            if dest.exists():assert study.base.sha(dest)==study.base.sha(original)
            else:shutil.copy2(original,dest)
            with np.load(dest) as d:
                states=[d[f'history_{i}'].copy() for i in range(count)]
                weights=([.7,.2,.1][:count] if use_history else [1.]);weights=np.asarray(weights)/sum(weights)
                np.testing.assert_allclose(d['weights'],weights,atol=1e-15)
                mixed=states[0] if count==1 else sum(s*np.float32(w) for s,w in zip(states,weights))
                np.testing.assert_allclose(d['input_latent'],mixed,atol=2e-6,rtol=1e-6)
                for age in range(1,count):assert np.array_equal(states[age],past[-age])
                eps=d['noise'].copy();std=float(eps.std());assert abs(std-1)<.01
                assert eps.shape==d['input_latent'].shape==(1,16,1,128,192)
                past.append(states[0]);all_noise[case,index]=eps
            correlation=None if prev_eps is None else float(np.corrcoef(eps.ravel(),prev_eps.ravel())[0,1])
            if correlation is not None:assert abs(correlation-rho)<.01
            prev_eps=eps
            change=float(np.abs(pixels(output).astype(float)-pixels(current)).mean()/255)
            rows.append({'case':case,'index':index,'weights':weights.tolist(),'noise_std':std,
                         'adjacent_noise_correlation':correlation,'rgb_mean_absolute_change':change})
            if case=='fresh':baseline_matches.append(np.array_equal(pixels(output),pixels(study.previous.OUT/f'independent/anchors/{f:04d}.png')))
    assert len(ids)==len(set(ids))==60
    for index in range(study.CYCLES):
        for a,b in [('fresh','history-fresh'),('gentle','history-gentle')]:
            assert np.array_equal(all_noise[a,index],all_noise[b,index])
        if index:
            expected=np.float32(.995)*all_noise['gentle',index-1]+np.float32(np.sqrt(1-.995**2))*all_noise['fresh',index]
            np.testing.assert_allclose(all_noise['gentle',index],expected,atol=5e-7,rtol=1e-6)
    for case in study.CASES:
        assert np.array_equal(pixels(OUT/case/'anchors/0006.png'),pixels(OUT/'fresh/anchors/0006.png'))
    result={'verified':True,'jobs':60,'recurrent':True,'actual_history_mix_verified':True,
            'actual_noise_recurrence_verified':True,'all_first_repaints_identical':True,
            'historical_control_pixel_matches':baseline_matches,'rows':rows}
    study.base.save(OUT/'generation-check.json',result)
    print('Verified60 jobs, exact history weights/lineage and noise recurrence; historical matches:',sum(baseline_matches))


def media():
    receipts=[]
    for case in study.CASES:
        root=OUT/case;dest=root/'raw';frames=dest/'frames';frames.mkdir(parents=True,exist_ok=True)
        paintings=[root/f'anchors/{i*6:04d}.png' for i in range(16)]
        roles=[]
        for f in range(96):
            p=paintings[f//6];target=frames/f'{f:04d}.png'
            if target.exists():assert study.base.sha(target)==study.base.sha(p)
            else:target.symlink_to(p.resolve())
            roles.append({'index':f,'time_seconds':f/24,'kind':'anchor' if f%6==0 else 'hold','source_index':f//6})
        video=dest/'preview.mp4'
        subprocess.run(['ffmpeg','-y','-v','error','-framerate','24','-i',str(frames/'%04d.png'),
                        '-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
        subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(video),'-f','null','-'],check=True)
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0',
            '-show_entries','stream=width,height,r_frame_rate,nb_read_frames,duration','-of','json',str(video)]))['streams'][0]
        assert info=={'width':1536,'height':1024,'r_frame_rate':'24/1','duration':'4.000000','nb_read_frames':'96'}
        study.base.save(dest/'manifest.json',{'status':'complete','video_sha256':study.base.sha(video),
            'output_frames':roles,'provenance':{'model':'Krea recurrent painting; raw holds, no interpolation'},
            'source_samples':[{'frame':i*6,'sha256':study.base.sha(p)} for i,p in enumerate(paintings)]})
        receipts.append({'case':case,**info,'sha256':study.base.sha(video)})
    study.base.save(OUT/'delivery-check.json',{'verified':True,'raw':True,'clips':receipts})
    for frame_set,name in [([0,24,54,90],'overview'),([72,78,84,90],'late-consecutive')]:
        board=Image.new('RGB',(4*480,4*348),'#171717');draw=ImageDraw.Draw(board)
        for row,case in enumerate(study.CASES):
            for col,f in enumerate(frame_set):
                im=Image.open(OUT/case/f'anchors/{f:04d}.png').convert('RGB').resize((480,320),Image.Resampling.LANCZOS)
                x,y=col*480,row*348;board.paste(im,(x,y+28))
                draw.text((x+10,y+8),f'{case} | painting {f//6} | {f/24:.2f}s',fill='white')
        board.save(OUT/f'{name}.jpg',quality=94)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['verify','media']);args=p.parse_args()
    verify() if args.stage=='verify' else media()
