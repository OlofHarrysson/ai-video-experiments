"""Matched moving-shot comparison: usual versus low-noise scene holding."""
import argparse
import json
from pathlib import Path
import shutil

import dynamic_journey as journey
import dynamic_journey_finish as finish
from prompt_bridges import SHELL_BUILDINGS, HOLLOW_SHELL

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'exports/hold-transform-v001'
CONFIGS = HERE / 'hold-transform-configs'
CASES = ('usual-hold', 'low-hold')


def configure():
    journey.OUT = OUT
    journey.base.OUT = OUT


def prepare():
    original = json.loads((HERE / 'transition-ramp-configs/higher-peak.json').read_text())
    snail = json.loads((HERE / 'ten-dollar-configs/clock-pulse.json').read_text())['prompts'][1]['text']
    ramp = original['transition_ramp']
    for case in CASES:
        hold = .1 if case == 'low-hold' else .6
        ending = .1 if case == 'low-hold' else .64
        config = {
            'case': case, 'seed': 773401, 'duration': 8., 'cadence': 12, 'cfg': 1.,
            'source': original['source'],
            'scenes': [{'at': 0, 'name': 'brass-snail', 'prompt': snail}],
            'prompt_schedule': [
                {'at': 0, 'name': 'brass-snail', 'prompt': snail},
                {'at': 2, 'name': 'shell-with-buildings', 'prompt': SHELL_BUILDINGS},
                {'at': 3, 'name': 'hollow-architectural-shell', 'prompt': HOLLOW_SHELL},
                {**original['scenes'][0], 'at': 4},
            ],
            'noise_schedule': [
                {'at': 0, 'noise': hold}, {'at': 1.5, 'noise': hold},
                *[{'at': 2 + i*.5, 'noise': n} for i,n in enumerate(ramp)],
                {'at': 6.5, 'noise': ending}, {'at': 8, 'noise': ending},
            ],
            'phrases': [
                {'start': 0, 'duration': 4.5, 'center': [.6,.47], 'zoom': .75,
                 'turn': 32, 'radius': .8, 'travel': [-.10,.04]},
                {'start': 4, 'duration': 3.5, 'center': [.95,.48], 'zoom': .08,
                 'turn': -14, 'radius': .85, 'travel': [.07,-.025]},
            ],
        }
        journey.base.save(CONFIGS / f'{case}.json', config)
    source = journey.APP / original['source']
    target = OUT / 'source/seed.png'
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert journey.base.sha(target) == journey.base.sha(source)
    else:
        shutil.copy2(source, target)


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
