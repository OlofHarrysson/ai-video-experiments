"""Verify feedback lineage and assemble identical finishing for the noise sweep."""
import argparse, copy, json, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import starting_noise as study
from spatial_warp import remap_rgb
from cathedral_review import assert_warp_matches
from repaint_intervals_review import encode

a,t=study.s.a,study.s.t
LABELS={'control':'Current | starting noise 0.655','0.62':'Starting noise 0.62','0.60':'Starting noise 0.60','0.56':'Starting noise 0.56'}
REFERENCE=study.BASELINE/'rife-raw/manifest.json'


def base(level):
    return study.branch(level)/'cadence-24'


def build_raw():
    """Reconstruct diagnostic frames from anchors, sharing time-only maps across cases."""
    clock=study.timing()
    for local in range(144):
        f=clock.start+local;anchor=clock.start+local//24*24
        coords=None if f==anchor else t.coordinates_at_time(clock.seconds(anchor),clock.seconds(f))
        for level in study.LEVELS:
            root=base(level);target=root/f'frames/{local:04d}.png'
            if target.exists():continue
            rgb=np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB'))
            a.image(target,rgb if coords is None else remap_rgb(rgb,coords))
        if local%24==0:print('Raw frames',local,'/144',flush=True)
    for level in study.LEVELS:
        root=base(level)
        a.save(root/'frame-hashes.json',{p.name:a.sha(p) for p in sorted((root/'frames').glob('*.png'))})
        encode(root)


def prepare(level):
    root=base(level);clock=study.timing();rows=[]
    assert a.sha(root/'anchors/0072.png')==a.sha(study.BASELINE/'anchors/0072.png')
    for i,f in enumerate(range(clock.start,clock.start+clock.count,clock.cadence)):
        anchor=root/f'anchors/{f:04d}.png'
        a.copy(anchor,root/f'rife-sources/{i:04d}.png')
        if not i:continue
        record=json.loads((root/f'anchor-{f:04d}.json').read_text());run=a.PROJECT/record['run']
        parent=root/f'anchors/{f-24:04d}.png';source=root/f'warped-inputs/{f:04d}.png'
        assert a.sha(parent)==record['parent_sha256']
        assert a.sha(source)==record['initialization_sha256']==a.sha(run/'anchor.png')
        assert a.sha(anchor)==record['output_sha256']==a.sha(run/'frames/0000.png')
        expected=study.graph(level,t.SEED+12+i)
        assert json.loads((run/'workflow.api.json').read_text())==expected
        executed=copy.deepcopy(json.loads((run/'workflow.executed.json').read_text()))
        executed['20']['inputs']['image']='anchor.png';assert executed==expected
        history=json.loads((run/'history.json').read_text())
        assert history['status']['completed'] and history['status']['status_str']=='success'
        before=np.asarray(Image.open(source).convert('RGB'));after=np.asarray(Image.open(anchor).convert('RGB'))
        assert_warp_matches(t.warp_at_time(np.asarray(Image.open(parent).convert('RGB')),clock.seconds(f-24),clock.seconds(f)),before)
        events=dict(history['status']['messages'])
        rows.append({'frame':f,'seconds':i,'graph_seconds':(events['execution_success']['timestamp']-events['execution_start']['timestamp'])/1000,
                     'warped_input_to_repaint_mae_rgb255':float(np.abs(after.astype(float)-before).mean()),
                     'mean_rgb':after.mean(axis=(0,1)).tolist(),'std_rgb':after.std(axis=(0,1)).tolist()})
    assert len(rows)==5
    hashes=json.loads((root/'frame-hashes.json').read_text());assert len(hashes)==144
    for name,digest in hashes.items():assert a.sha(root/'frames'/name)==digest
    for local in (0,1,23,24,25,119,120,143):
        f=clock.start+local;anchor=clock.start+local//24*24
        assert_warp_matches(t.warp_at_time(np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')),clock.seconds(anchor),clock.seconds(f)),np.asarray(Image.open(root/f'frames/{local:04d}.png').convert('RGB')))
    a.save(root/'verification.json',{'verified':True,'level':level,'repaints':rows,'probe':encode(root),
           'checks':'all requested/executed graphs, seeds, feedback lineage, every repaint warp, all frame hashes and selected native-24fps intermediate warps'})
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',19)
    canvas=Image.new('RGB',(1152,568),'#15191d');draw=ImageDraw.Draw(canvas)
    for i,f in enumerate(range(72,193,24)):
        x=(i%3)*384;y=(i//3)*284
        with Image.open(root/f'anchors/{f:04d}.png') as im:canvas.paste(im.resize((384,256),Image.Resampling.LANCZOS),(x,y+28))
        draw.text((x+8,y+3),f'{level} | painting at {i}s',font=font,fill='white')
    a.image(root/'review/anchors.png',np.asarray(canvas))
    print('VERIFIED',level,flush=True)


def finish(level):
    root=base(level);raw=root/'rife-raw';out=root/'interpolated'
    receipt=json.loads((raw/'manifest.json').read_text());reference=json.loads(REFERENCE.read_text())
    assert receipt['status']=='complete' and receipt['anchors_verified'] and receipt['source_hashes_and_mtimes_preserved']
    assert receipt['settings']==reference['settings']
    for key in ('commit','weights_sha256','bundle_sha256','code_sha256'):assert receipt['provenance'][key]==reference['provenance'][key]
    for row in receipt['sources']:assert a.sha(Path(row['file']))==row['sha256']
    for row in receipt['output_frames']:assert a.sha(raw/row['file'])==row['sha256']
    rows=[]
    for i in range(144):
        source=raw/f'frames/{i:04d}.png' if i<120 else root/f'frames/{i:04d}.png'
        a.copy(source,out/f'frames/{i:04d}.png')
        rows.append({'frame':i,'seconds':i/24,'source':str(source.relative_to(a.PROJECT)),'sha256':a.sha(source)})
    for i,f in enumerate(range(72,193,24)):
        np.testing.assert_array_equal(np.asarray(Image.open(out/f'frames/{i*24:04d}.png')),np.asarray(Image.open(root/f'anchors/{f:04d}.png')))
    p=encode(out);assert (p['width'],p['height'])==(1536,1024)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(out/'preview.mp4'),'-f','null','-'],check=True)
    a.save(out/'manifest.json',{'frames':rows,'probe':p,'anchors_pixel_identical':True,'final_warp_starts_seconds':5,
           'repaint_seconds':1,'rife_receipt_sha256':a.sha(raw/'manifest.json'),'feedback_generation_changed':False})
    print('FINISHED',level,flush=True)


def compare(levels,name):
    out=study.OUT/name;columns=2;rows=(len(levels)+1)//2
    font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23)
    for i in range(144):
        canvas=Image.new('RGB',(1536,554*rows),'#15191d');draw=ImageDraw.Draw(canvas)
        for index,level in enumerate(levels):
            x=index%columns*768;y=index//columns*554
            with Image.open(base(level)/f'interpolated/frames/{i:04d}.png') as im:canvas.paste(im.resize((768,512),Image.Resampling.LANCZOS),(x,y+42))
            draw.text((x+12,y+9),LABELS[level],font=font,fill='white')
        a.image(out/f'frames/{i:04d}.png',np.asarray(canvas))
    a.save(out/'manifest.json',{'probe':encode(out),'levels':levels,'frame_hashes':{p.name:a.sha(p) for p in sorted((out/'frames').glob('*.png'))}})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build-raw','prepare','finish','compare']);p.add_argument('--level',choices=study.LEVELS);args=p.parse_args()
    if args.action=='build-raw':build_raw()
    elif args.action=='compare':compare(study.LEVELS,'all-four')
    else:
        for level in ([args.level] if args.level else study.LEVELS):(prepare if args.action=='prepare' else finish)(level)
