"""Matched 6.5-second recurrent transition studies using the existing Krea runner."""
import argparse
import json
from pathlib import Path
import shutil

import numpy as np

import dynamic_journey as journey
import dynamic_journey_finish as finish

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'exports/transition-ramps-v001'
CONFIGS = HERE / 'transition-ramp-configs'
CASES = ('control', 'lower', 'longer', 'eased', 'soft-return', 'higher-peak')


def smooth(u):
    return u*u*(3-2*u)


def schedules():
    # Preserve the accepted ramp's normalized progress when lowering its start
    # or stretching it across more paintings. Change the rise curve separately.
    old_progress = [0, .4, .8, 1]
    long_progress = np.interp(np.linspace(0, 1, 6), np.linspace(0, 1, 4), old_progress)
    eased_progress = smooth(np.linspace(0, 1, 6))
    low = lambda progress, peak=.70: [.40 + (peak-.40)*float(u) for u in progress]
    fall = lambda peak: [peak + (.64-peak)*smooth(i/3) for i in range(1, 4)]
    return {
        'control': [.60, .64, .68, .70],
        'lower': low(old_progress),
        'longer': low(long_progress),
        'eased': low(eased_progress),
        'soft-return': low(eased_progress) + fall(.70),
        'higher-peak': low(eased_progress, .78) + fall(.78),
    }


def configure():
    journey.OUT = OUT
    journey.base.OUT = OUT


def prepare():
    original = json.loads((HERE/'dynamic-journey-configs/ramped.json').read_text())
    for case, ramp in schedules().items():
        config = {**original, 'case': case, 'duration': 6.5,
                  'scenes': original['scenes'][:1],
                  'phrases': original['phrases'][:1],
                  'transition_ramp': [round(v, 10) for v in ramp]}
        journey.base.save(CONFIGS/f'{case}.json', config)
    source = journey.APP/original['source']
    target = OUT/'source/seed.png'
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert journey.base.sha(source) == journey.base.sha(target)
    else:
        shutil.copy2(source, target)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
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
                journey.render(json.loads((CONFIGS/f'{case}.json').read_text()), args.through)
            else:
                finish.run(case, 'prepare' if args.stage == 'sheets' else args.stage)
