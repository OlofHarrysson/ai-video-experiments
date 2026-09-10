"""Verify cadence branches and assemble RIFE with unchanged anchor timing."""
import argparse,copy,json
import numpy as np
from PIL import Image
import cadence_spacing as c
import turbo_smoothing_review as v
from cathedral_review import assert_warp_matches

s,a,t,OUT=c.s,c.s.a,c.s.t,c.OUT


def prepare(cadence):
    root=OUT/f'cadence-{cadence}';rows=[]
    assert a.sha(root/'anchors/0036.png')==a.sha(s.CONTROL/'anchors/0036.png')
    for i,f in enumerate(range(36,72,cadence)):
        anchor=root/f'anchors/{f:04d}.png'
        a.copy(anchor,root/f'rife-sources/{i:04d}.png')
        if i==0:continue
        record=json.loads((root/f'anchor-{f:04d}.json').read_text());run=a.PROJECT/record['run']
        parent=root/f'anchors/{f-cadence:04d}.png';source=root/f'warped-inputs/{f:04d}.png'
        assert a.sha(parent)==record['parent_sha256']
        assert a.sha(source)==record['initialization_sha256']==a.sha(run/'anchor.png')
        assert a.sha(anchor)==record['output_sha256']==a.sha(run/'frames/0000.png')
        expected=t.graph(3,t.SEED+12+i)
        assert json.loads((run/'workflow.api.json').read_text())==expected
        actual=copy.deepcopy(json.loads((run/'workflow.executed.json').read_text()))
        actual['20']['inputs']['image']='anchor.png';assert actual==expected
        history=json.loads((run/'history.json').read_text())
        assert history['status']['completed'] and history['status']['status_str']=='success'
        assert_warp_matches(t.warp(np.asarray(Image.open(parent).convert('RGB')),f-cadence,f),np.asarray(Image.open(source).convert('RGB')))
        events=dict(history['status']['messages'])
        rows.append({'frame':f,'seconds':(events['execution_success']['timestamp']-events['execution_start']['timestamp'])/1000})
    assert len(rows)==(35//cadence)
    hashes=json.loads((root/'frame-hashes.json').read_text());assert len(hashes)==36
    for name,digest in hashes.items():assert a.sha(root/'frames'/name)==digest
    for local in (0,1,cadence-1,cadence,cadence+1,35):
        f=36+local;anchor=36+local//cadence*cadence
        assert_warp_matches(t.warp(np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')),anchor,f),np.asarray(Image.open(root/f'frames/{local:04d}.png').convert('RGB')))
    v.encode(root)
    a.save(root/'verification.json',{'verified':True,'repaints':rows,'checks':'all graphs and feedback hashes, every anchor warp, frame hashes, selected cadence frames and 3-second timing'})


def finish(cadence):
    base=OUT/f'cadence-{cadence}';raw=base/'rife-raw';root=base/'interpolated'
    receipt=json.loads((raw/'manifest.json').read_text())
    assert receipt['status']=='complete' and receipt['anchors_verified']
    for row in receipt['output_frames']:assert a.sha(raw/row['file'])==row['sha256']
    last=(35//cadence)*cadence*2
    frames=[]
    for i in range(72):
        source=raw/f'frames/{i:04d}.png' if i<last else base/f'frames/{i//2:04d}.png'
        a.copy(source,root/f'frames/{i:04d}.png')
        frames.append({'index':i,'source':str(source.relative_to(a.PROJECT)),'sha256':a.sha(source)})
    for i,f in enumerate(range(36,72,cadence)):
        assert np.array_equal(np.asarray(Image.open(root/f'frames/{i*cadence*2:04d}.png')),
                              np.asarray(Image.open(base/f'anchors/{f:04d}.png')))
    probe=v.encode(root)
    a.save(root/'manifest.json',{'probe':probe,'frames':frames,'anchors_pixel_identical':True,
        'final_original_interval_starts_at':last/24,'rife_receipt_sha256':a.sha(raw/'manifest.json'),
        'feedback_generation_changed':False})
    v.compare(str(cadence),root/'frames',f'Cadence {cadence} + RIFE',24,output_root=OUT,
        left_frames=a.PROJECT/'exports/turbo-smoothing-v001/interpolation/frames',left_fps=24,
        left_label='Your preferred cadence 3 + RIFE')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','finish']);p.add_argument('cadence',type=int,choices=[4,5]);args=p.parse_args()
    (prepare if args.action=='prepare' else finish)(args.cadence)
