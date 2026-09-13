"""Matched recurrent Krea CFG audition; all other controls retain the bridge recipe."""
import argparse
import json
import shutil
from pathlib import Path
import dynamic_journey as journey
import dynamic_journey_finish as finish

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'exports/cfg-audition-v001'
CONFIGS = HERE / 'cfg-audition-configs'
VALUES = {'cfg-08': .8, 'cfg-10': 1., 'cfg-13': 1.3, 'cfg-16': 1.6}
CASES = tuple(VALUES)


def configure():
    journey.OUT = OUT
    journey.base.OUT = OUT


def prepare():
    original = json.loads((HERE / 'prompt-bridge-configs/bridges.json').read_text())
    for case, cfg in VALUES.items():
        journey.base.save(CONFIGS / f'{case}.json', {**original, 'case': case, 'cfg': cfg})
    target = OUT / 'source/seed.png'
    target.parent.mkdir(parents=True, exist_ok=True)
    source = journey.APP / original['source']
    if target.exists():
        assert journey.base.sha(target) == journey.base.sha(source)
    else:
        shutil.copy2(source, target)
    # Check every planned graph: CFG and output name are the only differences.
    for frame in range(12, 156, 12):
        graphs = []
        for case in CASES:
            config = json.loads((CONFIGS / f'{case}.json').read_text())
            scene, sigmas = journey.recipe(config, frame / 24)
            g = journey.base.repaint_graph(scene['prompt'], config['seed'] + frame // 12, sigmas)
            assert g['9']['inputs']['cfg'] == 1.
            g['9']['inputs']['cfg'] = config['cfg']
            assert g['5']['class_type'] == 'ConditioningZeroOut'
            assert g['9']['inputs']['latent_image'] == ['24', 0]
            g['9']['inputs']['cfg'] = 1.
            graphs.append(g)
        assert all(g == graphs[0] for g in graphs)
    print('Prepared four matched configurations; recurrence and negative conditioning unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['prepare', 'render', 'sheets', 'pair', 'full'])
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--deployment', type=Path)
    parser.add_argument('--through', type=float)
    args = parser.parse_args()
    configure()
    if args.stage == 'prepare':
        prepare()
    else:
        if args.stage == 'render':
            if not args.deployment:
                parser.error('render requires --deployment')
            journey.base.pod_client.DEPLOYMENT = args.deployment.resolve()
        for case in ([args.case] if args.case else CASES):
            if args.stage == 'render':
                journey.render(json.loads((CONFIGS / f'{case}.json').read_text()), args.through)
            else:
                finish.run(case, 'prepare' if args.stage == 'sheets' else args.stage)
