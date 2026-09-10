"""Same-runtime unchanged high3 control for the three-direction comparison."""
import argparse
from pathlib import Path
import oracle_steps as previous
s=previous.s
OUT=s.a.PROJECT/'exports/three-directions-control-v001'
BASELINE=previous.OUT/'high3/cadence-24'
LEVELS=('high3',)
def timing():return previous.timing()
def branch(case):
    assert case in LEVELS
    return OUT/case
def graph(case,seed):
    g=previous.graph(case,seed)
    g['11']['inputs']['filename_prefix']='three-directions-control/'+case
    return g
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--deployment',required=True,type=Path);args=p.parse_args()
    s.a.transport.DEPLOYMENT=args.deployment.resolve()
    s.render(out=branch('high3'),study='three-directions-control-v001-high3',timing=timing(),graph_factory=lambda seed:graph('high3',seed),build_frames=False)
