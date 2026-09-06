"""Validate a complete experiment, assemble source ranges, inspect timed frames."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
from PIL import Image
PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT.parents[1]))
import editing
import video_review

def main(study):
    rows=[]
    for p in (PROJECT/'runs').glob('*/submission.json'):
        r=json.loads(p.read_text())
        if r['experiment']==study and r.get('phase')=='redraw':
            assert r.get('collected_at'), f'Uncollected run {p.parent.name}'
            rows.append((r['start_frame'],p.parent,r))
    rows.sort()
    assert [i for i,_,_ in rows]==[0,8,16,24,32]
    assert len({r['guide_run'] for _,_,r in rows})==1
    for start,p,r in rows:
        for f in r['frame_map']:
            src=PROJECT/'runs'/r['guide_run']/'frames'/f"{f['global_frame']:04d}.png"
            assert hashlib.sha256(src.read_bytes()).hexdigest()==f['guide_sha256']
    out=editing.assemble(PROJECT,study+'-v001',[{'run':p.name,'in':0,'out':8} for _,p,_ in rows])
    with Image.open(out/'frames/0000.png') as first, Image.open(PROJECT/'references/assets/seedream-v001/anchor.png') as ref:
        assert first.tobytes()==ref.tobytes()
    review=video_review.review(out/'preview.mp4',times=(0,1.625,3.25,4.875),overview=0,
        events=(('first redrawn frame',.125),),before=.125,after=.125,scene_threshold=.02,max_scenes=3)
    print(json.dumps({'video':str(out/'preview.mp4'),'review':str(review)},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('study'); main(p.parse_args().study)
