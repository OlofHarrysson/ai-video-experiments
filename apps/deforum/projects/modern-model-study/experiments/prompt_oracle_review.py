"""Use the shared review harness and compare the simple prompt with archived high3."""
import argparse
from types import SimpleNamespace

import numpy as np
from PIL import Image
import prompt_oracle as study
import starting_noise_review as review

review.REFERENCE = study.BASELINE / 'rife-raw/manifest.json'


def prepare(case):
    review.prepare(case, study=study)
    root = review.base(case, study)
    for frame in (72, 96):
        with Image.open(root / f'anchors/{frame:04d}.png') as candidate:
            with Image.open(study.BASELINE / f'anchors/{frame:04d}.png') as baseline:
                np.testing.assert_array_equal(np.asarray(candidate), np.asarray(baseline))
    study.s.a.save(root / 'common-start-verification.json', {
        'opening_pixel_identical': True, 'first_repaint_pixel_identical': True,
        'baseline': str(study.BASELINE.relative_to(study.s.a.PROJECT)),
    })


def compare():
    comparison = SimpleNamespace(
        OUT=study.OUT, timing=study.timing,
        branch=lambda case: study.BASELINE.parent if case == 'baseline' else study.branch(case),
    )
    review.compare(('baseline', 'simple'), 'baseline-vs-simple', study=comparison,
                   labels={'baseline': 'Original Oracle | noise 0.6 / 3 steps',
                           'simple': 'Simplified Oracle | noise 0.6 / 3 steps'},
                   caption_at=lambda seconds: 'cathedral' if seconds < 1 else
                   ('to Oracle' if seconds < 2 else 'Oracle'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build-raw', 'prepare', 'finish', 'compare'])
    parser.add_argument('--level', choices=study.LEVELS, default='simple')
    args = parser.parse_args()
    if args.action == 'build-raw':
        review.build_raw(study=study)
    elif args.action == 'prepare':
        prepare(args.level)
    elif args.action == 'finish':
        review.finish(args.level, study=study)
    else:
        compare()
