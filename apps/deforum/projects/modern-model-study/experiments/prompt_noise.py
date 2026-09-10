"""Recurrent eight-second prompt transition at four proportional noise schedules."""
import argparse
from fractions import Fraction
import turbo_smoothing as s
from feedback_timing import FeedbackTiming

OUT=s.a.PROJECT/'exports/prompt-noise-v001'
BASELINE=s.a.PROJECT/'exports/repaint-intervals-v001/cadence-24'
LEVELS=('0.3','0.4','0.5','0.6')
PROMPTS={key:s.t.opening.PROMPTS[key] for key in ('cathedral','moth')}
SWITCH_SECONDS=4
REFERENCE_SIGMAS=(0.6,0.5128440856933594,0.31090107560157776,0.0)
s.a.transport.DEPLOYMENT=s.a.APP/'work/prompt-noise-session/deployment.json'


def timing():
    return FeedbackTiming(repaint_seconds=Fraction(1),duration_seconds=Fraction(8))


def sigmas(level):
    assert level in LEVELS
    values=[value*float(level)/0.6 for value in REFERENCE_SIGMAS]
    assert len(values)==4 and values[-1]==0 and all(a>b for a,b in zip(values,values[1:]))
    return values


def scene(seed):
    second=seed-(s.t.SEED+12)
    assert 1<=second<=7
    return 'cathedral' if second<SWITCH_SECONDS else 'moth'


def graph(level,seed):
    g=s.t.graph(3,seed)
    del g['40'],g['41']
    g['43']=s.a.workflows.node('ManualSigmas',sigmas=', '.join(f'{v:.12f}' for v in sigmas(level)))
    g['9']['inputs']['sigmas']=['43',0]
    g['4']['inputs']['text']=PROMPTS[scene(seed)]
    g['11']['inputs']['filename_prefix']='prompt-noise/'+level
    return g


def branch(level):
    return OUT/('sigma-'+level.replace('.',''))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('level',choices=LEVELS);level=p.parse_args().level
    s.a.save(branch(level)/'study.json',{'prompts':PROMPTS,'switch_seconds':SWITCH_SECONDS,
        'sigmas':sigmas(level),'schedule_basis':REFERENCE_SIGMAS,'schedule_policy':'proportional to previous 0.60 schedule',
        'repaint_prompt_schedule':{i:scene(s.t.SEED+12+i) for i in range(1,8)},
        'rife_transition_caveat':'first moth painting at 4s is interpolated from cathedral painting at 3s'})
    s.render(out=branch(level),study='prompt-noise-v001-'+level.replace('.',''),timing=timing(),
        graph_factory=lambda seed:graph(level,seed),build_frames=False)
