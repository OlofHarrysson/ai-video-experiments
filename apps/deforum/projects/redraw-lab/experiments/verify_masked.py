"""Verify E10 preserves every source pixel outside its expanded repair mask."""
import json
from pathlib import Path
import numpy as np
from PIL import Image
PROJECT=Path(__file__).resolve().parents[1]

def dilate_cross(mask, steps=8):
    for _ in range(steps):
        padded=np.pad(mask,1)
        mask=np.maximum.reduce([padded[1:-1,1:-1],padded[:-2,1:-1],
            padded[2:,1:-1],padded[1:-1,:-2],padded[1:-1,2:]])
    return mask

def main():
    rows=[]
    for path in sorted((PROJECT/'runs').glob('*/submission.json')):
        r=json.load(open(path))
        if r['experiment']!='e10' or not r.get('collected_at'):continue
        guide=PROJECT/'runs'/r['guide_run']
        gr=json.load(open(guide/'submission.json'))
        for local,global_index in enumerate(range(r['start_frame'],r['end_frame'])):
            mask_path=guide/'cloud'/gr['cloud_attempt']/'34'/f'frame_{global_index+1:05d}_.png'
            coverage=np.asarray(Image.open(mask_path).convert('L'))
            assert set(np.unique(coverage)) <= {0,255}
            mask=dilate_cross(coverage==0)
            source=np.asarray(Image.open(guide/'frames'/f'{global_index:04d}.png'))
            output=np.asarray(Image.open(path.parent/'frames'/f'{local:04d}.png'))
            assert np.array_equal(source[~mask],output[~mask]),global_index
            rows.append({'frame':global_index,'outside_mask_pixels_identical':True,
                'guide_uncovered_fraction':float(np.mean(coverage==0)),
                'expanded_repair_fraction':float(np.mean(mask))})
    rows.sort(key=lambda r:r['frame'])
    print(json.dumps({'verified_frames':len(rows),'sampled':[r for r in rows if r['frame'] in (0,7,13,26,39)]},indent=2))
    if len(rows)==40:
        target=PROJECT/'exports/e10-v001/mask-verification.json'
        with target.open('x') as f:json.dump(rows,f,indent=2)

if __name__=='__main__':main()
