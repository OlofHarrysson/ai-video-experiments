"""Compare unchanged Oracle text with an owl prompt after the accepted eight-second opening."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import numpy as np
from PIL import Image
import eased_motion as previous
from feedback_timing import FeedbackTiming

a, t = previous.a, previous.t
OUT = a.PROJECT / 'exports/owl-transition-v001'
BASELINE = previous.branch('ease') / 'cadence-24'
LEVELS = ('oracle', 'owl')
BRANCH_SECOND = 8
DURATION = 14
OWL_PROMPT = (
    'A surreal visionary artwork, a close portrait of a porcelain mechanical owl. '
    'A single large owl head fills the central circular opening, tilted diagonally inside concentric architectural rings. '
    'Two luminous turquoise glass eyes sit within broad round facial discs of overlapping ivory ceramic feathers. '
    'A short sharply hooked beak projects between the eyes; layered sculptural feathers form the forehead and cheeks. '
    'The owl is a clearly recognizable bird with an alert, enigmatic gaze. Its crown opens into an impossible '
    'maze of tiny black-and-white architectural chambers, curved chrome ribs and translucent cyan glass. '
    'Around the head, concentric ornamental structures recede through deep black cavities, like a living '
    'cathedral made of circuitry. Small amber lights punctuate the cyan and ivory palette. Strong sculptural '
    'side lighting reveals glossy ceramic, brushed metal and fine engraved textures. Dense, meticulously '
    'crafted detail surrounds a clearly readable owl; the extreme foreground is large and the background '
    'falls into deep layered space. A strange, elegant album-cover painting with tactile three-dimensional '
    'forms, expressive asymmetrical details and a dramatic black backdrop.'
)


def timing():
    return FeedbackTiming(repaint_seconds=Fraction(1), duration_seconds=Fraction(DURATION))


def branch(case):
    assert case in LEVELS
    return OUT / case


def warp_at_time(rgb, start, end):
    return previous.warp_at_time(rgb, min(float(start),11), min(float(end),11), 'ease')


def coordinates_at_time(start, end, width=1536, height=1024):
    return previous.coordinates_at_time(min(float(start),11), min(float(end),11), width, height, 'ease')


def graph(case, seed):
    assert case in LEVELS
    second = seed - (t.SEED + 12)
    assert 1 <= second < DURATION
    if second <= BRANCH_SECOND:
        return previous.graph('ease', seed)
    # The saved 8s recipe is already Oracle-conditioned. Extend its seed sequence
    # without extending the older experiment's bounded scene scheduler.
    g = previous.graph('ease', t.SEED + 12 + BRANCH_SECOND)
    g['9']['inputs']['noise_seed'] = seed
    if case == 'owl':
        g['4']['inputs']['text'] = OWL_PROMPT
    g['11']['inputs']['filename_prefix'] = 'owl-transition/' + case
    return g


def initialize(case):
    root = branch(case) / 'cadence-24'
    manifest = json.loads((BASELINE/'manifest.json').read_text())
    manifest.update({'frames': timing().count, 'source_manifest_sha256': a.sha(BASELINE/'manifest.json'),
        'case': case, 'branch_second': BRANCH_SECOND, 'source': str(BASELINE.relative_to(a.PROJECT)),
        'runner_sha256': a.sha(Path(__file__)), 'motion': 'accepted eased path; spatial hold after 8s',
        'prompts': {'oracle': graph('oracle',t.SEED+21)['4']['inputs']['text'], 'owl': OWL_PROMPT},
        'prompt_schedule': {i: ('cathedral' if i==1 else (case if i>8 else 'oracle')) for i in range(1,DURATION)}})
    a.save(root/'manifest.json', manifest)
    for second in range(BRANCH_SECOND+1):
        f=72+24*second
        a.copy(BASELINE/f'anchors/{f:04d}.png',root/f'anchors/{f:04d}.png')
        if second:
            for name in (f'anchor-{f:04d}.json',f'warped-inputs/{f:04d}.png'):
                a.copy(BASELINE/name,root/name)
    return root


def render(deployment):
    a.transport.DEPLOYMENT=Path(deployment).resolve()
    json.loads(a.transport.DEPLOYMENT.read_text())
    (OUT/'runs').mkdir(parents=True,exist_ok=True)
    clock=timing()
    for case in LEVELS:
        root=initialize(case)
        for second in range(BRANCH_SECOND+1,DURATION):
            f=72+24*second;seed=t.SEED+12+second
            parent=root/f'anchors/{f-24:04d}.png';source=root/f'warped-inputs/{f:04d}.png'
            a.image(source,warp_at_time(np.asarray(Image.open(parent).convert('RGB')),clock.seconds(f-24),clock.seconds(f)))
            g=graph(case,seed);name=f'owl-transition-v001-{case}-{f:04d}'
            matches=list((OUT/'runs').glob('*-'+name+'-1f'))
            if matches:
                assert len(matches)==1
                run=matches[0]
                assert json.loads((run/'workflow.api.json').read_text())==g
                assert a.sha(run/'anchor.png')==a.sha(source)
                a.transport.collect(run)
            else:
                run=a.transport.submit(OUT,name,g,1,source=source,lineage={
                    'parent_sha256':a.sha(parent),'frame':f,'repaint_index':second,
                    'case':case,'preserved_opening_through_seconds':BRANCH_SECOND})
            output=root/f'anchors/{f:04d}.png';a.copy(run/'frames/0000.png',output)
            a.save(root/f'anchor-{f:04d}.json',{'run':str(run.relative_to(a.PROJECT)),
                'parent_sha256':a.sha(parent),'initialization_sha256':a.sha(source),
                'output_sha256':a.sha(output),'seed':seed})
            print(f'{case}: repaint {second}s complete',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--deployment',required=True)
    render(p.parse_args().deployment)
