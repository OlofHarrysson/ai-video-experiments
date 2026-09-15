"""Freeze a new continuation while preserving every parent painting through a boundary."""
import argparse
from run import lab

def freeze(parent,case,through,duration,events,noise=None,phrases=None):
 config=lab.read(lab.OUT/parent/'config.json')
 config.pop('opening',None)
 config.update(case=case,duration=duration,prefix_root=str((lab.OUT/parent).relative_to(lab.APP)),prefix_through=through)
 config['painting_frames']=list(range(0,round(duration*24),12))
 config['prompt_schedule']=[e for e in config['prompt_schedule'] if e['at']<=through/24]+events
 if noise is not None:config['noise_schedule']=[e for e in config['noise_schedule'] if e['at']<=through/24]+noise
 if phrases is not None:config['phrases']=phrases
 config['seeds_by_frame']={str(f):config['seed']+1000+f for f in config['painting_frames'][1:]}
 lab.save(lab.HERE/'configs'/f'{case}.json',config)
 return config
