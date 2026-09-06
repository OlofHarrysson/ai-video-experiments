"""Submit at most two existing-recipe redraw jobs at once; never retry a POST."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import study

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--study',required=True,choices=['e08','e09','e10'])
    p.add_argument('--guide-run',required=True)
    p.add_argument('--starts',nargs='+',type=int,default=[0,8,16,24,32])
    a=p.parse_args()
    study.STUDY=a.study
    study.FIXED_SEED=a.study in ('e09','e10')
    study.DENOISE=1.0 if a.study=='e10' else .2
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda start:study.run('redraw',a.guide_run,start),a.starts))
