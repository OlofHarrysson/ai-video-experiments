"""Two bounded controls: anchor interpolation preparation and cadence-two feedback."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
import turbo_transitions as t
from feedback_timing import FeedbackTiming
from fractions import Fraction

a = t.a
OUT = a.PROJECT/'exports/turbo-smoothing-v001'
CONTROL = t.OUT/'tail-3'
START, COUNT, CADENCE = 36, 36, 2
a.transport.DEPLOYMENT = a.APP/'work/turbo-smoothing-session/deployment.json'


def prepare():
    for i, f in enumerate(range(START, START+COUNT, 3)):
        a.copy(CONTROL/f'anchors/{f:04d}.png', OUT/f'rife-sources/{i:04d}.png')
    a.save(OUT/'source-map.json', {
        str(i): {'source': str((CONTROL/f'anchors/{f:04d}.png').relative_to(a.PROJECT)),
                 'sha256': a.sha(CONTROL/f'anchors/{f:04d}.png'), 'global_frame': f}
        for i,f in enumerate(range(START,START+COUNT,3))})


def render(cadence=CADENCE, out=OUT, study='turbo-smoothing-v001', *, timing=None, graph_factory=None, build_frames=True):
    timing=timing or FeedbackTiming(fps=12,repaint_seconds=Fraction(cadence,12),interpolate=False)
    make_graph=graph_factory or (lambda seed: t.graph(3,seed))
    cadence,start,count=timing.cadence,timing.start,timing.count
    root=out/f'cadence-{cadence}'
    (a.PROJECT/'runs').mkdir(parents=True,exist_ok=True)
    a.copy(CONTROL/f'anchors/{START:04d}.png',root/f'anchors/{start:04d}.png')
    a.save(root/'manifest.json', {'cadence':cadence,'fps':timing.fps,'frames':count,'start_frame':start,
        'tail':3,'first_repaint_seed':t.SEED+13,'seed_policy':'increment once per repaint',
        'opening_sha256':a.sha(root/f'anchors/{start:04d}.png'),
        'motion_runner_sha256':a.sha(Path(t.__file__)), 'runner_sha256':a.sha(Path(__file__)),
        'graph':make_graph(t.SEED+13),'intermediates':'previous generated anchor warped; no blend'})
    for i,f in enumerate(range(start+cadence,start+count,cadence),1):
        parent=root/f'anchors/{f-cadence:04d}.png';source=root/f'warped-inputs/{f:04d}.png'
        a.image(source,t.warp_at_time(np.asarray(Image.open(parent).convert('RGB')),timing.seconds(f-cadence),timing.seconds(f)))
        graph=make_graph(t.SEED+12+i)
        name=f'{study}-cadence-{cadence}-{f:04d}'
        matches=list((a.PROJECT/'runs').glob('*-'+name+'-1f'))
        if matches:
            assert len(matches)==1
            run=matches[0]
            assert json.loads((run/'workflow.api.json').read_text())==graph
            assert a.sha(run/'anchor.png')==a.sha(source)
            a.transport.collect(run)
        else:
            run=a.transport.submit(a.PROJECT,name,graph,1,source=source,
                lineage={'parent_sha256':a.sha(parent),'frame':f,'repaint_index':i})
        output=root/f'anchors/{f:04d}.png';a.copy(run/'frames/0000.png',output)
        a.save(root/f'anchor-{f:04d}.json',{'run':str(run.relative_to(a.PROJECT)),
            'parent_sha256':a.sha(parent),'initialization_sha256':a.sha(source),
            'output_sha256':a.sha(output),'seed':t.SEED+12+i})
        print('Cadence',cadence,':',i,'/',len(range(start+cadence,start+count,cadence)),flush=True)
    if not build_frames:
        return
    for local in range(count):
        f=start+local;anchor=start+local//cadence*cadence
        a.image(root/f'frames/{local:04d}.png',t.warp_at_time(np.asarray(Image.open(root/f'anchors/{anchor:04d}.png').convert('RGB')),timing.seconds(anchor),timing.seconds(f)))
    a.save(root/'frame-hashes.json',{p.name:a.sha(p) for p in sorted((root/'frames').glob('*.png'))})
    if not (root/'preview.mp4').exists():a.editing.encode(root/'frames',root/'preview.mp4',fps=timing.fps)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('case',choices=['prepare','render'])
    prepare() if parser.parse_args().case=='prepare' else render()
