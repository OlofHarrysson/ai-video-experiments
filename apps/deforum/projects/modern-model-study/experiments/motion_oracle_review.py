"""Isolated motion shim for actual warps, lineage, RIFE finishing and comparisons."""
import argparse
import json
import subprocess
from types import SimpleNamespace
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import motion_oracle as study
import starting_noise_review as shared

a, t = study.a, study.t
# Only this process's harness binding changes; no shared source or runner mutation.
shared.t = SimpleNamespace(**{**vars(t), 'coordinates_at_time':study.coordinates_at_time,
                             'warp_at_time':study.warp_at_time})
shared.REFERENCE = study.BASELINE/'rife-raw/manifest.json'


def checks():
    clock = study.timing()
    assert (clock.fps,clock.cadence,clock.count,clock.start)==(24,24,288,72)
    x,y=np.meshgrid(np.linspace(-50,562,97),np.linspace(-50,370,67))
    errors=[]; determinants=[]; rows=[]
    for local in (0,1,2,4,7,10,12):
        mx,my=study.mapping_at_time(x,y,local+3)
        rx,ry=study.mapping_at_time(mx,my,local+3,True)
        errors.append(float(np.max(np.hypot(rx-x,ry-y))))
        eps=0.01
        px,py=study.mapping_at_time(x+eps,y,local+3)
        qx,qy=study.mapping_at_time(x,y+eps,local+3)
        det=((px-mx)*(qy-my)-(qx-mx)*(py-my))/eps**2
        determinants.append(float(det.min()))
    assert max(errors)<0.005, errors
    assert min(determinants)>0, determinants
    grid=np.stack(np.meshgrid(np.arange(384),np.arange(256)),axis=-1)
    for i in range(12):
        new=study.coordinates_at_time(3+i,4+i,384,256)
        old=t.coordinates_at_time(3+i,4+i,384,256)
        new_dist=np.linalg.norm(new-grid,axis=-1)*4
        old_dist=np.linalg.norm(old-grid,axis=-1)*4
        rows.append({'local_second':i,'new_mean_px_per_second':float(new_dist.mean()),
                     'new_p95_px_per_second':float(np.percentile(new_dist,95)),
                     'baseline_mean_px_per_second':float(old_dist.mean())})
        assert new_dist.mean()>2
        xx,yy=study.mapping_at_time(x,y,4+i,True)
        xx,yy=study.mapping_at_time(xx,yy,3.5+i)
        xx,yy=study.mapping_at_time(xx,yy,3.5+i,True)
        xx,yy=study.mapping_at_time(xx,yy,3+i)
        dx,dy=study.mapping_at_time(x,y,4+i,True)
        dx,dy=study.mapping_at_time(dx,dy,3+i)
        assert np.max(np.hypot(xx-dx,yy-dy))<0.005
    for i in range(1,12):
        g=study.graph('high3',t.SEED+12+i)
        expected=study.previous.graph('high3',t.SEED+12+i)
        g['11']['inputs']['filename_prefix']=expected['11']['inputs']['filename_prefix']
        assert g==expected
        assert g['20']['inputs']['image']=='anchor.png'
    assert rows[7]['baseline_mean_px_per_second']<0.001
    source=np.asarray(Image.open(study.BASELINE/'anchors/0072.png').convert('RGB'))
    np.testing.assert_array_equal(study.warp_at_time(source,3,3),source)
    report={'passed':True,'graph_calls_verified':11,'roundtrip_max_virtual_units':max(errors),
            'sampled_min_jacobian':min(determinants),'motion':study.settings(),'one_second_inverse_displacement':rows,
            'notes':'Displacement sampled at 384x256 then scaled to native 1536x1024; not optical flow or subject tracking.'}
    a.save(study.OUT/'local-checks.json',report)
    print(json.dumps(report,indent=2))


def runner_smoke():
    """Exercise all 11 runner iterations with mocked I/O and transport; no network."""
    from tempfile import TemporaryDirectory
    from unittest.mock import patch
    study.SESSION.mkdir(parents=True,exist_ok=True)
    test_image=Image.fromarray(np.arange(24*16*3,dtype=np.uint8).reshape(16,24,3))
    with TemporaryDirectory(dir=study.SESSION) as temp:
        deployment=study.Path(temp)/'deployment.json';deployment.write_text('{}')
        with patch.object(a,'copy'), patch.object(a,'save'), patch.object(a,'sha',return_value='mock-digest'), \
             patch.object(a,'image') as save_image, patch.object(study.Image,'open',return_value=test_image), \
             patch.object(a.transport,'submit') as submit, patch.object(a.transport,'collect') as collect:
            submit.side_effect=lambda project,name,*args,**kwargs:project/'runs'/name
            study.render(deployment,'LOCAL-MOCK-NO-INFERENCE')
            assert submit.call_count==11 and collect.call_count==0
            assert save_image.call_count==11
            for i,call in enumerate(submit.call_args_list,1):
                assert call.args[0]==study.OUT and call.args[3]==1
                assert call.args[2]==study.graph('high3',t.SEED+12+i)
                assert call.kwargs['lineage']['repaint_index']==i
                assert str(call.kwargs['source']).endswith(f'warped-inputs/{72+i*24:04d}.png')
                expected=study.warp_at_time(np.asarray(test_image),2+i,3+i)
                np.testing.assert_array_equal(save_image.call_args_list[i-1].args[1],expected)
    a.save(study.OUT/'runner-smoke.json',{'passed':True,'mocked_submissions':11,'real_network_calls':0,
        'checks':'exact graph/seed and actual specialized warp at all 11 timestamp pairs; scoped archive destination'})
    print('RUNNER SMOKE PASSED: 11 mocked calls, zero network')


def preview():
    clock=study.timing();root=study.OUT/'motion-only'
    source=study.BASELINE/'anchors/0072.png'
    rgb=np.asarray(Image.open(source).convert('RGB').resize((768,512),Image.Resampling.LANCZOS))
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',22)
    for i in range(clock.count):
        target=root/f'frames/{i:04d}.png'
        if target.exists():continue
        canvas=Image.new('RGB',(1536,554),'#15191d'); draw=ImageDraw.Draw(canvas)
        for j,(label,warp) in enumerate((('Baseline: settles at 7s',t.warp_at_time),('Continuous twist + expansion',study.warp_at_time))):
            result=warp(rgb,3,3+i/24)
            canvas.paste(Image.fromarray(result),(j*768,42))
            draw.text((j*768+12,9),f'{label} | {i/24:.2f}s',font=font,fill='white')
        a.image(target,np.asarray(canvas))
        if i%48==0:print('Motion preview',i,'/288',flush=True)
    p=shared.encode(root,clock)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(root/'preview.mp4'),'-f','null','-'],check=True)
    a.save(root/'manifest.json',{'source_sha256':a.sha(source),'probe':p,'motion':study.settings(),
             'each_frame_from':'same initial artwork, one direct warp, no diffusion','video_sha256':a.sha(root/'preview.mp4'),
             'full_decode_passed':True,'runner_sha256':a.sha(study.Path(study.__file__))})


def prepare():
    shared.prepare('high3',study=study)
    root=shared.base('high3',study);rows=[]
    for i in range(1,12):
        f=72+i*24
        parent=np.asarray(Image.open(root/f'anchors/{f-24:04d}.png').convert('RGB'))
        source=np.asarray(Image.open(root/f'warped-inputs/{f:04d}.png').convert('RGB'))
        delta=float(np.abs(source.astype(float)-parent).mean())
        assert delta>0
        rows.append({'repaint':i,'parent_to_warp_mae_rgb255':delta})
    a.save(root/'motion-verification.json',{'passed':True,'actual_motion_runner_sha256':a.sha(study.Path(study.__file__)),
             'all_repaint_inputs_moved':rows,'uses_specialized_warp_in_shared_review':True})


def finish():
    root=shared.base('high3',study);receipt=json.loads((root/'rife-raw/manifest.json').read_text())
    assert len(receipt['sources'])==12
    for i,row in enumerate(receipt['sources']):
        assert row['sha256']==a.sha(root/f'rife-sources/{i:04d}.png')
    shared.finish('high3',study=study)
    assert a.sha(root/'interpolated/frames/0264.png') != a.sha(root/'interpolated/frames/0287.png'), 'Frozen final tail'


def compare():
    proxy=SimpleNamespace(OUT=study.OUT,timing=study.timing,
        branch=lambda case: study.BASELINE.parent if case=='baseline' else study.branch('high3'))
    shared.compare(('baseline','motion'),'baseline-comparison',study=proxy,
        labels={'baseline':'Baseline: settles at 7s','motion':'Continuous twist + expansion'})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['check','runner-smoke','preview','build-raw','prepare','finish','compare']);args=p.parse_args()
    {'check':checks,'runner-smoke':runner_smoke,'preview':preview,'build-raw':lambda:shared.build_raw(study=study),
     'prepare':prepare,'finish':finish,'compare':compare}[args.action]()
