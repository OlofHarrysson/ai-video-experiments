"""Six-second recurrent Krea shots with 0.5s and 1s repaint intervals."""
import argparse
from fractions import Fraction
import turbo_smoothing as s
from feedback_timing import FeedbackTiming

OUT=s.a.PROJECT/'exports/repaint-intervals-v001'
INTERVALS=('0.5','1')
s.a.transport.DEPLOYMENT=s.a.APP/'work/repaint-interval-session/deployment.json'


def timing(interval):
    return FeedbackTiming(repaint_seconds=Fraction(interval),duration_seconds=Fraction(6))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('interval',choices=INTERVALS)
    s.render(out=OUT,study='repaint-intervals-v001',timing=timing(parser.parse_args().interval))
