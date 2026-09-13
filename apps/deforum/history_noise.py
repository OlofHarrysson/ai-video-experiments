"""Recorded clean-latent history and noise for the stationary recurrence probe."""
from pathlib import Path
import re

from noise_sequence import noise_at


def mix_recent(values, use_history):
    if not 1 <= len(values) <= 3:
        raise ValueError('Expected one to three recent image latents')
    if any(v.shape != values[0].shape for v in values):
        raise ValueError('History shapes differ')
    if not use_history or len(values) == 1:
        return values[0], [1.] + [0.] * (len(values)-1)
    weights = [.7, .2, .1][:len(values)]
    total = sum(weights)
    weights = [v/total for v in weights]
    mixed = values[0] * weights[0]
    for value, weight in zip(values[1:], weights[1:]):
        mixed = mixed + value * weight
    return mixed, weights


class HistoryNoise:
    def __init__(self, values, weights, seed, index, correlation, case):
        self.values, self.weights = values, weights
        self.base_seed, self.index, self.correlation, self.case = seed, index, correlation, case
        self.seed = seed + index

    def generate_noise(self, latent):
        import numpy as np
        import comfy.sample
        import folder_paths
        import json
        z = latent['samples']
        eps = noise_at(comfy.sample.prepare_noise, z, self.base_seed, self.index, self.correlation)
        arrays = {'noise': eps.cpu().numpy(), 'input_latent': z.cpu().float().numpy(),
                  'weights': np.asarray(self.weights, dtype=np.float64)}
        arrays.update({f'history_{i}': v.cpu().float().numpy() for i, v in enumerate(self.values)})
        root = Path(folder_paths.get_output_directory())/'history-recurrence-v001'/self.case
        root.mkdir(parents=True, exist_ok=True)
        path = root/f'{self.index:04d}.npz'
        if path.exists():
            with np.load(path) as saved:
                if set(saved.files) != set(arrays): raise RuntimeError('Diagnostic keys changed')
                for key,value in arrays.items():
                    if not np.array_equal(saved[key],value): raise RuntimeError(f'Diagnostic collision: {key}')
        else:
            np.savez_compressed(path, **arrays)
            path.with_suffix('.json').write_text(json.dumps({'case':self.case,'index':self.index,
                'seed':self.seed,'correlation':self.correlation,'weights':self.weights,
                'shape':list(z.shape),'std':float(eps.std())},indent=2))
        return eps


class DeforumHistorySource:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'current':('LATENT',), 'use_history':('BOOLEAN',{'default':False}),
            'seed':('INT',{'default':918273,'min':0,'max':2**64-1001}),
            'index':('INT',{'default':0,'min':0,'max':1000}),
            'correlation':('FLOAT',{'default':0.,'min':0.,'max':1.}),
            'case':('STRING',{'default':'fresh'})},
            'optional':{'older':('LATENT',),'oldest':('LATENT',)}}
    RETURN_TYPES=('LATENT','NOISE')
    FUNCTION='make'
    CATEGORY='deforum/experiments'

    def make(self,current,use_history,seed,index,correlation,case,older=None,oldest=None):
        if not re.fullmatch('[a-z0-9-]+',case): raise ValueError('Invalid case slug')
        if oldest is not None and older is None: raise ValueError('Missing older history')
        latents=[x for x in (current,older,oldest) if x is not None]
        if any(set(x) != {'samples'} for x in latents): raise ValueError('Only plain image latents supported')
        values=[x['samples'] for x in latents]
        mixed,weights=mix_recent(values,use_history)
        return {'samples':mixed},HistoryNoise(values,weights,seed,index,correlation,case)


NODE_CLASS_MAPPINGS={'DeforumHistorySource':DeforumHistorySource}
