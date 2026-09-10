"""Use the shared noise-study review with the eight-second prompt schedule."""
import argparse
import prompt_noise as study
import starting_noise_review as review

LABELS={level:'Noise '+level for level in study.LEVELS}


def caption(seconds):
    if seconds<3:return 'cathedral'
    if seconds<4:return 'transition toward moth'
    return 'moth prompt'


def compare(levels=study.LEVELS,name='all-four'):
    review.compare(levels,name,study=study,labels=LABELS,caption_at=caption)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build-raw','prepare','finish','compare']);p.add_argument('--level',choices=study.LEVELS);args=p.parse_args()
    if args.action=='build-raw':review.build_raw(study=study)
    elif args.action=='compare':compare()
    else:
        for level in ([args.level] if args.level else study.LEVELS):
            (review.prepare if args.action=='prepare' else review.finish)(level,study=study)
