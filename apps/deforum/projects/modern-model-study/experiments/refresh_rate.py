"""Two versus four recurrent paintings per second, with a lower-noise treatment."""
import argparse
import json
import shutil
from pathlib import Path
import dynamic_journey as journey
import dynamic_journey_finish as finish

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'exports/refresh-rate-v001'
CONFIGS = HERE / 'refresh-rate-configs'
CASES = {'two-current': (12, 1.), 'four-current': (6, 1.), 'four-lower': (6, .85)}


def configure():
    journey.OUT = OUT
    journey.base.OUT = OUT


def prepare():
    original = json.loads((HERE / 'cfg-audition-configs/cfg-10.json').read_text())
    for case, (cadence, scale) in CASES.items():
        config = {**original, 'case': case, 'cfg': 1., 'cadence': cadence}
        ramp = config.pop('transition_ramp')
        config['noise_schedule'] = [{'at': .5 + i*.5, 'noise': n*scale} for i,n in enumerate(ramp)]
        config['settle_noise'] *= scale
        # Preserve the historical seeds at shared timestamps; inserted quarter-seconds get separate seeds.
        config['seeds_by_frame'] = {str(f): original['seed'] + (f//12 if f%12 == 0 else 100000+f//6)
                                    for f in range(cadence,156,cadence)}
        journey.base.save(CONFIGS / f'{case}.json', config)
    target = OUT / 'source/seed.png'
    target.parent.mkdir(parents=True,exist_ok=True)
    source = journey.APP / original['source']
    if target.exists():
        assert journey.base.sha(target) == journey.base.sha(source)
    else:
        shutil.copy2(source,target)
    configs = {case: json.loads((CONFIGS/f'{case}.json').read_text()) for case in CASES}
    a,b,c = configs.values()
    for f in range(6,156,6):
        t=f/24
        pb,sb=journey.recipe(b,t);pc,sc=journey.recipe(c,t)
        assert pb == pc
        assert all(abs(lo-hi*.85)<1e-12 for hi,lo in zip(sb,sc))
        assert b['seeds_by_frame'][str(f)] == c['seeds_by_frame'][str(f)]
        if f%12 == 0:
            pa,sa=journey.recipe(a,t);po,so=journey.recipe(original,t)
            assert pa == pb == po and sa == sb == so
            assert a['seeds_by_frame'][str(f)] == b['seeds_by_frame'][str(f)] == original['seed']+f//12
    assert all(config['phrases']==original['phrases'] and config['prompt_schedule']==original['prompt_schedule'] for config in configs.values())
    print('Preflight passed: legacy half-second recipe preserved; time-based controls and common-time seeds matched.')


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stage',choices=['prepare','render','sheets','pair','full'])
    p.add_argument('--case',choices=CASES)
    p.add_argument('--deployment',type=Path)
    args=p.parse_args();configure()
    if args.stage=='prepare':prepare()
    else:
        if args.stage=='render':
            if not args.deployment:p.error('render requires --deployment')
            journey.base.pod_client.DEPLOYMENT=args.deployment.resolve()
        for case in ([args.case] if args.case else CASES):
            if args.stage=='render':journey.render(json.loads((CONFIGS/f'{case}.json').read_text()),None)
            else:finish.run(case,'prepare' if args.stage=='sheets' else args.stage)
