"""Cadence 7, 10 and 15 with the selected recurrent three-interval sampler."""
import argparse
import turbo_smoothing as s

OUT=s.a.PROJECT/'exports/cadence-slow-v001'
CASES=(7,10,15)
s.a.transport.DEPLOYMENT=s.a.APP/'work/cadence-slow-session/deployment.json'

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('cadence',type=int,choices=CASES)
    s.render(cadence=p.parse_args().cadence,out=OUT,study='cadence-slow-v001')
