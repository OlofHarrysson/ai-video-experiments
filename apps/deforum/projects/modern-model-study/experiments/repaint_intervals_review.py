"""Verify 24fps feedback and finish six-second shots with unchanged RIFE settings."""
import argparse,copy,json,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import repaint_intervals as study
from cathedral_review import assert_warp_matches

a,t,OUT=study.s.a,study.s.t,study.OUT
BASELINE=a.PROJECT/'exports/turbo-smoothing-v001/rife-raw/manifest.json'


def encode(root):
    target=root/'preview.mp4'
    if not target.exists():a.editing.encode(root/'frames',target,fps=24)
    p=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_streams','-of','json',str(target)]))['streams'][0]
    assert p['nb_read_frames']=='144' and p['avg_frame_rate']=='24/1' and float(p['duration'])==6
    return p


def prepare(interval):
    clock=study.timing(interval);root=OUT/f'cadence-{clock.cadence}';rows=[]
    assert a.sha(root/f'anchors/{clock.start:04d}.png')==a.sha(study.s.CONTROL/'anchors/0036.png')
    for i,f in enumerate(range(clock.start,clock.start+clock.count,clock.cadence)):
        anchor=root/f'anchors/{f:04d}.png';a.copy(anchor,root/f'rife-sources/{i:04d}.png')
        if not i:continue
        record=json.loads((root/f'anchor-{f:04d}.json').read_text());run=a.PROJECT/record['run']
        parent=root/f'anchors/{f-clock.cadence:04d}.png';source=root/f'warped-inputs/{f:04d}.png'
        assert a.sha(parent)==record['parent_sha256']
        assert a.sha(source)==record['initialization_sha256']==a.sha(run/'anchor.png')
        assert a.sha(anchor)==record['output_sha256']==a.sha(run/'frames/0000.png')
        expected=t.graph(3,t.SEED+12+i);assert json.loads((run/'workflow.api.json').read_text())==expected
        executed=copy.deepcopy(json.loads((run/'workflow.executed.json').read_text()))
        executed['20']['inputs']['image']='anchor.png';assert executed==expected
        history=json.loads((run/'history.json').read_text());assert history['status']['completed'] and history['status']['status_str']=='success'
        assert_warp_matches(t.warp_at_time(np.asarray(Image.open(parent).convert('RGB')),clock.seconds(f-clock.cadence),clock.seconds(f)),np.asarray(Image.open(source).convert('RGB')))
        events=dict(history['status']['messages']);rows.append({'frame':f,'elapsed_seconds':(f-clock.start)/24,'graph_seconds':(events['execution_success']['timestamp']-events['execution_start']['timestamp'])/1000})
    assert len(rows)==(clock.count-1)//clock.cadence
    hashes=json.loads((root/'frame-hashes.json').read_text());assert len(hashes)==144
    for name,digest in hashes.items():assert a.sha(root/'frames'/name)==digest
    for local in (0,1,clock.cadence-1,clock.cadence,clock.cadence+1,143):
        f=clock.start+local;anchor=clock.start+local//clock.cadence*clock.cadence
        assert_warp_matches(t.warp_at_time(np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')),clock.seconds(anchor),clock.seconds(f)),np.asarray(Image.open(root/f'frames/{local:04d}.png').convert('RGB')))
    a.save(root/'verification.json',{'verified':True,'repaints':rows,'probe':encode(root),'checks':'all graphs and feedback hashes, every anchor warp, all raw-frame hashes, selected native 24fps warps and full output timing'})


def finish(interval):
    clock=study.timing(interval);base=OUT/f'cadence-{clock.cadence}';raw=base/'rife-raw';root=base/'interpolated'
    receipt=json.loads((raw/'manifest.json').read_text());reference=json.loads(BASELINE.read_text())
    assert receipt['status']=='complete' and receipt['anchors_verified']
    assert receipt['settings']['source_fps']==24/clock.cadence and receipt['settings']['multiplier']==clock.cadence and receipt['settings']['output_fps']==24
    ignore={'source_fps','output_fps','multiplier','timesteps'}
    assert {k:v for k,v in receipt['settings'].items() if k not in ignore}=={k:v for k,v in reference['settings'].items() if k not in ignore}
    for key in ('commit','weights_sha256','bundle_sha256','code_sha256'):assert receipt['provenance'][key]==reference['provenance'][key]
    for row in receipt['output_frames']:assert a.sha(raw/row['file'])==row['sha256']
    last=(clock.count-1)//clock.cadence*clock.cadence;rows=[]
    for i in range(clock.count):
        source=raw/f'frames/{i:04d}.png' if i<last else base/f'frames/{i:04d}.png'
        a.copy(source,root/f'frames/{i:04d}.png')
        rows.append({'frame':i,'seconds':i/24,'source':str(source.relative_to(a.PROJECT)),'sha256':a.sha(source)})
    for i,f in enumerate(range(clock.start,clock.start+clock.count,clock.cadence)):
        np.testing.assert_array_equal(np.asarray(Image.open(root/f'frames/{i*clock.cadence:04d}.png')),np.asarray(Image.open(base/f'anchors/{f:04d}.png')))
    a.save(root/'manifest.json',{'frames':rows,'probe':encode(root),'anchors_pixel_identical':True,'final_warp_starts_seconds':last/24,'repaint_seconds':float(clock.repaint_seconds),'rife_receipt_sha256':a.sha(raw/'manifest.json'),'feedback_generation_changed':False})


def compare():
    root=OUT/'comparison';font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',23)
    for i in range(144):
        canvas=Image.new('RGB',(1536,554),'#15191d');draw=ImageDraw.Draw(canvas)
        for x,c,label in [(0,12,'Repaint every 0.5s | cadence 12 + RIFE'),(768,24,'Repaint every 1s | cadence 24 + RIFE')]:
            canvas.paste(Image.open(OUT/f'cadence-{c}/interpolated/frames/{i:04d}.png').convert('RGB').resize((768,512),Image.Resampling.LANCZOS),(x,42))
            draw.text((x+12,9),label,font=font,fill='white')
        a.image(root/f'frames/{i:04d}.png',np.asarray(canvas))
    a.save(root/'manifest.json',{'probe':encode(root),'panels':[{'cadence':c,'repaint_seconds':c/24,'source':f'cadence-{c}/interpolated'} for c in (12,24)],'frame_hashes':{p.name:a.sha(p) for p in sorted((root/'frames').glob('*.png'))}})


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','finish']);args=p.parse_args()
    for interval in study.INTERVALS:(prepare if args.action=='prepare' else finish)(interval)
    if args.action=='finish':compare()
