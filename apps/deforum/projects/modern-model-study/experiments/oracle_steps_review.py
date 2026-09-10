"""Verify and compare twelve-second Oracle schedule experiments."""
import argparse
import oracle_steps as study
import starting_noise_review as review

LABELS={name:f'Noise {sigma} | {steps} steps' for name,(sigma,steps) in study.CASES.items()}


def caption(seconds):
    if seconds<1:return 'cathedral'
    if seconds<2:return 'to Oracle'
    return 'Oracle'


def compare(levels=study.LEVELS,name='all-four'):
    review.compare(levels,name,study=study,labels=LABELS,caption_at=caption)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build-raw','prepare','finish','compare']);p.add_argument('--level',choices=study.LEVELS);args=p.parse_args()
    if args.action=='build-raw':review.build_raw(study=study)
    elif args.action=='compare':compare()
    else:
        for level in ([args.level] if args.level else study.LEVELS):
            (review.prepare if args.action=='prepare' else review.finish)(level,study=study)
