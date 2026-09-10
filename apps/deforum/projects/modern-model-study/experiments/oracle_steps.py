"""Matched Oracle transitions: lower noise with more steps, and one large update."""
import argparse
from fractions import Fraction
import prompt_noise as previous

s=previous.s
OUT=s.a.PROJECT/'exports/oracle-steps-v001'
BASELINE=previous.BASELINE
CASES={'low3':(0.4,3),'low9':(0.4,9),'high3':(0.6,3),'high1':(0.6,1)}
LEVELS=tuple(CASES)
PROMPTS={name:s.t.opening.PROMPTS[name] for name in ('cathedral','oracle')}
SWITCH_SECONDS=2
s.a.transport.DEPLOYMENT=s.a.APP/'work/oracle-steps-session/deployment.json'


def timing():
    return previous.FeedbackTiming(repaint_seconds=Fraction(1),duration_seconds=Fraction(12))


def sigmas(case):
    start,steps=CASES[case]
    if steps==1:return [start,0.0]
    anchors=previous.sigmas(str(start))
    divisions=steps//3
    values=[hi+(lo-hi)*k/divisions for hi,lo in zip(anchors,anchors[1:]) for k in range(divisions)]+[0.0]
    assert len(values)==steps+1 and values[0]==start and all(a>b for a,b in zip(values,values[1:]))
    return values


def scene(seed):
    second=seed-(s.t.SEED+12)
    assert 1<=second<=11
    return 'cathedral' if second<SWITCH_SECONDS else 'oracle'


def graph(case,seed):
    g=s.t.graph(3,seed)
    del g['40'],g['41']
    # Keep the first repaint identical so every transition starts from the same painting.
    values=previous.sigmas('0.6') if scene(seed)=='cathedral' else sigmas(case)
    g['43']=s.a.workflows.node('ManualSigmas',sigmas=', '.join(f'{v:.12f}' for v in values))
    g['9']['inputs']['sigmas']=['43',0]
    g['4']['inputs']['text']=PROMPTS[scene(seed)]
    g['11']['inputs']['filename_prefix']='oracle-steps/'+case
    return g


def branch(case):
    return OUT/case


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('case',choices=LEVELS);case=p.parse_args().case
    s.a.save(branch(case)/'study.json',{'case':case,'prompts':PROMPTS,'switch_seconds':SWITCH_SECONDS,
        'oracle_start_sigma':CASES[case][0],'oracle_sampling_intervals':CASES[case][1],
        'oracle_sigmas':sigmas(case),'common_first_repaint_sigmas':previous.sigmas('0.6'),
        'prompt_schedule':{i:scene(s.t.SEED+12+i) for i in range(1,12)},
        'interpolation':'first Oracle painting at 2s; RIFE transition begins between 1s and 2s'})
    s.render(out=branch(case),study='oracle-steps-v001-'+case,timing=timing(),
        graph_factory=lambda seed:graph(case,seed),build_frames=False)
