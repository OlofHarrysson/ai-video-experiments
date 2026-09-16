"""Finish new frozen cases using the accepted 1.5x, 24 fps RIFE recipe."""
import argparse
from retime import retime
from moving_tail import finish

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('cases',nargs='+');p.add_argument('--through-frame',type=int);a=p.parse_args()
 for case in a.cases:
  for stage in ('pair','full','check'):retime(case,stage,last_frame=a.through_frame)
  finish(case,last_frame=a.through_frame)
