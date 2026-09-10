"""Review each direction separately against the freshly rendered runtime control."""
import argparse
import three_directions_control as control
import starting_noise_review as shared

def main():
    p=argparse.ArgumentParser();p.add_argument('direction',choices=['control','prompt','motion']);p.add_argument('action',choices=['build-raw','prepare','finish','compare']);args=p.parse_args()
    if args.direction=='control':
        if args.action=='compare':p.error('Control has no independent comparison')
        if args.action=='build-raw':shared.build_raw(study=control)
        else:getattr(shared,args.action)('high3',study=control)
        return
    if args.direction=='prompt':
        import prompt_oracle_review as review
        review.study.BASELINE=control.branch('high3')/'cadence-24'
        if args.action=='build-raw':review.review.build_raw(study=review.study)
        elif args.action=='prepare':review.prepare('simple')
        elif args.action=='finish':review.review.finish('simple',study=review.study)
        else:review.compare()
    else:
        import motion_oracle_review as review
        review.study.BASELINE=control.branch('high3')/'cadence-24'
        if args.action=='build-raw':review.shared.build_raw(study=review.study)
        else:getattr(review,args.action)()
if __name__=='__main__':main()
