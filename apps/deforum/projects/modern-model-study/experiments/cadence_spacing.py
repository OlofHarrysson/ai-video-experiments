"""Cadence 4 and 5, retaining the selected three-interval recurrent sampler."""
import argparse
import turbo_smoothing as s

OUT=s.a.PROJECT/'exports/cadence-spacing-v001'
s.a.transport.DEPLOYMENT=s.a.APP/'work/cadence-spacing-session/deployment.json'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('cadence',type=int,choices=[4,5])
    s.render(cadence=p.parse_args().cadence,out=OUT,study='cadence-spacing-v001')
