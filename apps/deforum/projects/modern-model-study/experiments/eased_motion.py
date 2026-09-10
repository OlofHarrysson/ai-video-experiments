"""Branch from the six-second Oracle painting, comparing continuous and eased motion."""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
import motion_oracle as previous

a, t, s = previous.a, previous.t, previous.s
OUT = a.PROJECT / 'exports/eased-motion-v001'
BASELINE = previous.branch('high3') / 'cadence-24'
SESSION = a.APP / 'work/eased-motion-session'
LEVELS = ('continuous', 'ease')
BRANCH_SECOND = 6
HOLD_SECOND = 8


def timing():
    return previous.timing()


def branch(case):
    assert case in LEVELS
    return OUT / case


def motion_time(seconds, case):
    assert case in LEVELS
    local = float(seconds) - previous.START_SECONDS
    if not 0 <= local <= 12:
        raise ValueError('Global time must be in [3,15] seconds')
    if case == 'continuous' or local <= BRANCH_SECOND:
        return float(seconds)
    u = min((local - BRANCH_SECOND) / (HOLD_SECOND - BRANCH_SECOND), 1.0)
    return previous.START_SECONDS + BRANCH_SECOND + 2 * (u - u**3 + 0.5*u**4)


def coordinates_at_time(start, end, width=1536, height=1024, case='ease'):
    return previous.coordinates_at_time(motion_time(start, case), motion_time(end, case), width, height)


def warp_at_time(rgb, start, end, case='ease'):
    start, end = motion_time(start, case), motion_time(end, case)
    if start == end:
        return rgb.copy()
    return previous.warp_at_time(rgb, start, end)


def graph(case, seed):
    g = previous.graph('high3', seed)
    second = seed - (t.SEED + 12)
    if second > BRANCH_SECOND:
        g['11']['inputs']['filename_prefix'] = 'eased-motion/' + case
    return g


def initialize(case):
    root = branch(case) / 'cadence-24'
    manifest = json.loads((BASELINE / 'manifest.json').read_text())
    manifest.update({'source_manifest_sha256': a.sha(BASELINE / 'manifest.json'),
        'case': case, 'branch_second': BRANCH_SECOND, 'hold_second': HOLD_SECOND,
        'source': str(BASELINE.relative_to(a.PROJECT)), 'runner_sha256': a.sha(Path(__file__)),
        'motion': {'source': previous.settings(), 'schedule': case,
                   'description': 'effective motion time; smooth deceleration 6–8s, then hold' if case == 'ease' else 'unchanged continuous'}})
    a.save(root / 'manifest.json', manifest)
    for second in range(BRANCH_SECOND + 1):
        f = 72 + second * 24
        a.copy(BASELINE / f'anchors/{f:04d}.png', root / f'anchors/{f:04d}.png')
        if second:
            for name in (f'anchor-{f:04d}.json', f'warped-inputs/{f:04d}.png'):
                a.copy(BASELINE / name, root / name)
    return root


def render(deployment):
    a.transport.DEPLOYMENT = Path(deployment).resolve()
    json.loads(a.transport.DEPLOYMENT.read_text())
    (OUT / 'runs').mkdir(parents=True, exist_ok=True)
    clock = timing()
    for case in LEVELS:
        root = initialize(case)
        for second in range(BRANCH_SECOND + 1, 12):
            f = 72 + second * 24
            parent = root / f'anchors/{f-24:04d}.png'
            source = root / f'warped-inputs/{f:04d}.png'
            a.image(source, warp_at_time(np.asarray(Image.open(parent).convert('RGB')),
                clock.seconds(f-24), clock.seconds(f), case))
            seed = t.SEED + 12 + second
            g = graph(case, seed)
            name = f'eased-motion-v001-{case}-{f:04d}'
            matches = list((OUT / 'runs').glob('*-' + name + '-1f'))
            if matches:
                assert len(matches) == 1
                run = matches[0]
                assert json.loads((run / 'workflow.api.json').read_text()) == g
                assert a.sha(run / 'anchor.png') == a.sha(source)
                a.transport.collect(run)
            else:
                run = a.transport.submit(OUT, name, g, 1, source=source,
                    lineage={'parent_sha256': a.sha(parent), 'frame': f, 'repaint_index': second,
                             'case': case, 'preserved_opening_through_seconds': BRANCH_SECOND})
            output = root / f'anchors/{f:04d}.png'
            a.copy(run / 'frames/0000.png', output)
            a.save(root / f'anchor-{f:04d}.json', {'run': str(run.relative_to(a.PROJECT)),
                'parent_sha256': a.sha(parent), 'initialization_sha256': a.sha(source),
                'output_sha256': a.sha(output), 'seed': seed})
            print(f'{case}: repaint {second}s complete', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--deployment', required=True)
    render(p.parse_args().deployment)
