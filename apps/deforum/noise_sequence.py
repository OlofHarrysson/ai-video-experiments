"""Reproducible unit-variance noise sequences for a bounded ComfyUI experiment."""
import math


def noise_at(prepare, latent, base_seed, index, correlation):
    """AR(1) over independent standard-normal innovations, without renormalizing samples.

    Index zero is shared by every correlation setting. Rebuilding from seeds keeps
    the result independent of ComfyUI cache order and interrupted/resumed jobs.
    ``prepare(latent, seed)`` is ComfyUI's native prepare_noise in production.
    """
    if not isinstance(index, int) or not 0 <= index <= 1000:
        raise ValueError('Noise index must be an integer from 0 to 1000')
    if not 0 <= correlation <= 1:
        raise ValueError('Correlation must be between zero and one')
    if not 0 <= base_seed <= 2**64 - 1001:
        raise ValueError('Seed range must fit uint64')
    if correlation == 0:
        return prepare(latent, base_seed + index)
    value = prepare(latent, base_seed)
    innovation_scale = math.sqrt(1 - correlation**2)
    for step in range(1, index + 1):
        value = correlation * value + innovation_scale * prepare(latent, base_seed + step)
    return value


class RecordedNoise:
    def __init__(self, seed, index, correlation, tag):
        self.base_seed, self.index, self.correlation, self.tag = seed, index, correlation, tag
        self.seed = seed + index

    def generate_noise(self, latent):
        import hashlib
        import json
        import re
        from pathlib import Path
        import numpy as np
        import comfy.sample
        import folder_paths

        if not re.fullmatch(r'[a-z0-9-]+', self.tag):
            raise ValueError('Diagnostic tag must be a simple slug')
        if 'batch_index' in latent or 'noise_mask' in latent:
            raise ValueError('This study supports one unmasked image only')
        z = latent['samples']
        if z.shape[0] != 1 or z.is_nested:
            raise ValueError('This study supports one ordinary latent tensor')
        eps = noise_at(comfy.sample.prepare_noise, z, self.base_seed, self.index, self.correlation)
        root = Path(folder_paths.get_output_directory()) / 'deforum-noise-study' / self.tag
        root.mkdir(parents=True, exist_ok=True)
        path = root / f'{self.index:04d}.npz'
        arrays = {'noise': eps.detach().cpu().numpy(), 'input_latent': z.detach().cpu().float().numpy()}
        if path.exists():
            with np.load(path) as saved:
                for key, value in arrays.items():
                    if not np.array_equal(saved[key], value):
                        raise RuntimeError(f'Diagnostic collision: {path}, {key}')
        else:
            np.savez_compressed(path, **arrays)
            row = {'base_seed': self.base_seed, 'index': self.index, 'correlation': self.correlation,
                   'sampling_seed': self.seed, 'shape': list(eps.shape),
                   'mean': float(eps.mean()), 'std': float(eps.std()),
                   'noise_sha256': hashlib.sha256(arrays['noise'].tobytes()).hexdigest(),
                   'meaning': 'Actual Gaussian noise passed into the sampler; input_latent is before model-space processing'}
            path.with_suffix('.json').write_text(json.dumps(row, indent=2) + '\n')
        return eps


class DeforumRecordedNoise:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'seed': ('INT', {'default': 918273, 'min': 0, 'max': 2**64-1001}),
            'index': ('INT', {'default': 0, 'min': 0, 'max': 1000}),
            'correlation': ('FLOAT', {'default': .85, 'min': 0., 'max': 1., 'step': .01}),
            'tag': ('STRING', {'default': 'correlated-v001'})}}
    RETURN_TYPES = ('NOISE',)
    FUNCTION = 'make'
    CATEGORY = 'deforum/experiments'

    def make(self, seed, index, correlation, tag):
        return (RecordedNoise(seed, index, correlation, tag),)


NODE_CLASS_MAPPINGS = {'DeforumRecordedNoise': DeforumRecordedNoise}
