"""One text-only change to the archived twelve-second high3 Oracle transition."""
import argparse
import copy
import json
from pathlib import Path

import oracle_steps as previous

s = previous.s
OUT = s.a.PROJECT / 'exports/prompt-oracle-v001'
BASELINE = previous.OUT / 'high3/cadence-24'
SESSION = s.a.APP / 'work/prompt-oracle-session'
LEVELS = ('simple',)
PROMPTS = {
    'cathedral': previous.PROMPTS['cathedral'],
    'oracle': (
        'A surreal visionary painting of a porcelain mechanical oracle, seen in a close frontal portrait. '
        'The large, clearly readable face occupies the middle half of a wide composition, with luminous '
        'turquoise eyes, ivory ceramic skin and a calm, enigmatic expression. Curved architectural ribs '
        'frame the head and recede into deep black space, forming a living cathedral around the face. '
        'Translucent cyan glass and small amber lights accent the ivory architecture. Strong sculptural '
        'side lighting gives the face and surrounding ribs tactile three-dimensional form.'
    ),
}
SWITCH_SECONDS = previous.SWITCH_SECONDS


def timing():
    return previous.timing()


def branch(case):
    assert case in LEVELS
    return OUT / case


def graph(case, seed):
    assert case in LEVELS
    result = previous.graph('high3', seed)
    result['4']['inputs']['text'] = PROMPTS[previous.scene(seed)]
    result['11']['inputs']['filename_prefix'] = 'prompt-oracle/' + case
    return result


def preflight(case):
    """Offline graph/asset checks; freeze the candidate without contacting ComfyUI."""
    clock = timing()
    assert clock == previous.timing()
    assert (clock.fps, clock.cadence, clock.count, clock.start) == (24, 24, 288, 72)
    assert s.a.sha(s.CONTROL / f'anchors/{s.START:04d}.png') == s.a.sha(BASELINE / 'anchors/0072.png')
    rows = []
    for second in range(1, 12):
        seed = s.t.SEED + 12 + second
        frame = clock.start + second * clock.cadence
        expected = previous.graph('high3', seed)
        record = json.loads((BASELINE / f'anchor-{frame:04d}.json').read_text())
        archived = json.loads((s.a.PROJECT / record['run'] / 'workflow.api.json').read_text())
        assert archived == expected, f'Baseline source drift at {second}s'
        candidate = graph(case, seed)
        differences = [
            f'{node}.inputs.{key}'
            for node in expected
            for key in expected[node]['inputs']
            if expected[node]['inputs'][key] != candidate[node]['inputs'][key]
        ]
        allowed = ['11.inputs.filename_prefix']
        if second >= SWITCH_SECONDS:
            allowed.append('4.inputs.text')
        assert set(differences) == set(allowed), (second, differences)
        normalized = copy.deepcopy(candidate)
        normalized['11']['inputs']['filename_prefix'] = expected['11']['inputs']['filename_prefix']
        if second >= SWITCH_SECONDS:
            normalized['4']['inputs']['text'] = expected['4']['inputs']['text']
        assert normalized == expected, f'Unexpected graph difference at {second}s'
        rows.append({'seconds': second, 'frame': frame, 'seed': seed,
                     'scene': previous.scene(seed), 'changed_fields': differences,
                     'graph': candidate})
    receipt = {
        'verified': True, 'inference_submitted': False, 'case': case,
        'baseline': str(BASELINE.relative_to(s.a.PROJECT)),
        'opening_sha256': s.a.sha(BASELINE / 'anchors/0072.png'),
        'prompts': PROMPTS, 'baseline_prompts': previous.PROMPTS,
        'switch_seconds': SWITCH_SECONDS, 'repaints': rows,
        'oracle_sigmas': previous.sigmas('high3'),
        'runner_sha256': s.a.sha(Path(__file__)),
        'baseline_runner_sha256': s.a.sha(Path(previous.__file__)),
        'motion_runner_sha256': s.a.sha(Path(s.t.__file__)),
    }
    s.a.save(SESSION / 'preflight.json', receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=LEVELS)
    parser.add_argument('--check', action='store_true', help='Offline preflight only')
    parser.add_argument('--deployment', type=Path, help='Main agent supplied deployment JSON; required for inference')
    args = parser.parse_args()
    if not args.check and (args.deployment is None or not args.deployment.is_file()):
        parser.error('Generation requires --deployment pointing to the main agent supplied JSON')
    receipt = preflight(args.case)
    print('Verified all 11 graphs: first repaint prefix only; Oracle repaints text/prefix only.', flush=True)
    if args.check:
        return
    s.a.transport.DEPLOYMENT = args.deployment.resolve()
    s.a.save(branch(args.case) / 'study.json', {
        'case': args.case, 'prompts': PROMPTS, 'switch_seconds': SWITCH_SECONDS,
        'baseline': receipt['baseline'], 'oracle_start_sigma': 0.6,
        'oracle_sampling_intervals': 3, 'oracle_sigmas': previous.sigmas('high3'),
        'common_first_repaint_sigmas': previous.sigmas('high3'),
        'prompt_schedule': {row['seconds']: row['scene'] for row in receipt['repaints']},
        'preflight_sha256': s.a.sha(SESSION / 'preflight.json'),
        'interpolation': 'first Oracle painting at 2s; RIFE transition begins between 1s and 2s',
    })
    s.render(out=branch(args.case), study='prompt-oracle-v001-' + args.case,
             timing=timing(), graph_factory=lambda seed: graph(args.case, seed), build_frames=False)


if __name__ == '__main__':
    main()
