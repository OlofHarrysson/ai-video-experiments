"""Three-interval recurrent Krea branches varying only the first sigma."""
import argparse
from fractions import Fraction
import turbo_smoothing as s
from feedback_timing import FeedbackTiming

OUT=s.a.PROJECT/'exports/starting-noise-v001'
LEVELS=('control','0.62','0.60','0.56')
BASELINE=s.a.PROJECT/'exports/repaint-intervals-v001/cadence-24'
s.a.transport.DEPLOYMENT=s.a.APP/'work/starting-noise-session/deployment.json'


def timing():
    return FeedbackTiming(repaint_seconds=Fraction(1),duration_seconds=Fraction(6))


def graph(level,seed):
    assert level in LEVELS
    g=s.t.graph(3,seed)
    if level=='control':return g
    g['43']=s.a.workflows.node('SetFirstSigma',sigmas=['41',1],sigma=float(level))
    g['9']['inputs']['sigmas']=['43',0]
    return g


def branch(level):
    return OUT/('sigma-'+level.replace('.',''))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('level',choices=LEVELS)
    level=parser.parse_args().level
    s.render(out=branch(level),study='starting-noise-v001-'+level.replace('.',''),
             timing=timing(),graph_factory=lambda seed:graph(level,seed),build_frames=False)
