"""Image-space diagnostics; these do not measure subjective temporal quality."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
PROJECT=Path(__file__).resolve().parents[1]

def main(study):
    folder=PROJECT/'exports'/f'{study}-v001'
    images=[np.asarray(Image.open(p).convert('RGB'),dtype=np.float32)/255 for p in sorted((folder/'frames').glob('*.png'))]
    assert len(images)==40
    rows=[]
    for i,(a,b) in enumerate(zip(images,images[1:]),1):
        rows.append({'source_frame':i,'time_seconds':i/8,'mean_absolute_change':float(np.mean(np.abs(b-a)))})
    data={'warning':'Unregistered pixel changes conflate camera movement, generation noise and scene change. Not a flicker score.',
          'largest_changes':sorted(rows,key=lambda r:r['mean_absolute_change'],reverse=True)[:6],
          'mean_change_excluding_anchor_transition':float(np.mean([r['mean_absolute_change'] for r in rows[1:]])),
          'frames':rows}
    path=folder/'pixel-change.json'
    with path.open('x') as f: json.dump(data,f,indent=2)
    print(json.dumps({k:v for k,v in data.items() if k!='frames'},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('study');main(p.parse_args().study)
