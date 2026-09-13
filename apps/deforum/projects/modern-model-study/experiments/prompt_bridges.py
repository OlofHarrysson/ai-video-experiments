"""Compare direct scene text with descriptive stages at the same noise schedule."""
import argparse
import json
from pathlib import Path
import shutil

import dynamic_journey as journey
import dynamic_journey_finish as finish

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'exports/prompt-bridges-v001'
CONFIGS = HERE / 'prompt-bridge-configs'
CASES = ('direct', 'bridges')
STYLE = ('An intricate surreal visionary painting with sculptural architecture, deep layered space, '
         'fine engraved detail, luminous color, dramatic shaded volumes, and a coherent wide cinematic composition.')
LIGHT = 'Warm amber sunlight slices through deep red dust and reveals countless architectural layers.'
SHELL_BUILDINGS = (
    'An enormous brass snail rests on dark stone in a desert canyon. Its large rounded spiral shell '
    'is an inhabited miniature city: tiny angular towers, terraced balconies, glowing windows, '
    'gold mechanical stairways and oxidized copper rooftops are built into the shell. '
    'Its warm metallic spiral remains clearly recognizable, with small deep archways opening between '
    'the buildings. Red canyon walls and sand frame the scene. '
    + LIGHT + ' ' + STYLE)
HOLLOW_SHELL = (
    'An immense hollow spiral pavilion made of brass and oxidized copper stands inside a desert canyon. '
    'The curved outer shell forms an architectural rim around a broad opening. Deep arched bridges, '
    'terraced balconies, gold mechanical stairways and tiny glowing windows line the inside of the spiral. '
    'Through its open center, a winding avenue and angular towers recede far into the canyon. '
    'The opening occupies the center, with tall buildings and red canyon walls framing the sides. '
    + LIGHT + ' ' + STYLE)


def configure():
    journey.OUT = OUT
    journey.base.OUT = OUT


def prepare():
    original = json.loads((HERE / 'transition-ramp-configs/higher-peak.json').read_text())
    destination = original['scenes'][0]
    for case in CASES:
        prompts = [destination] if case == 'direct' else [
            {'at': 0, 'name': 'shell-with-buildings', 'prompt': SHELL_BUILDINGS},
            {'at': 1.5, 'name': 'hollow-architectural-shell', 'prompt': HOLLOW_SHELL},
            {**destination, 'at': 2.5},
        ]
        config = {**original, 'case': case, 'prompt_schedule': prompts}
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
