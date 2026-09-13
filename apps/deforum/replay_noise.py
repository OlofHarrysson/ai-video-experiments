"""Recorded-state replay for a single-painting diagnostic, not recurrent animation."""
import math


def perturb_noise(original, direction, amount):
    if not 0 <= amount < 1:
        raise ValueError('Perturbation must be in [0, 1)')
    if original.shape != direction.shape:
        raise ValueError('Noise arrays must share a shape')
    if amount == 0:
        return original.clone()
    return math.sqrt(1 - amount * amount) * original + amount * direction


class ReplayNoise:
    def __init__(self, original, direction, seed, amount):
        self.original, self.direction = original, direction
        self.seed, self.amount = seed, amount

    def generate_noise(self, latent):
        import hashlib
        import json
        from pathlib import Path
        import numpy as np
        import folder_paths
        if latent['samples'].shape != self.original.shape:
            raise ValueError('Recorded noise and latent shapes differ')
        noise = perturb_noise(self.original, self.direction, self.amount)
        arrays = {'noise': noise.cpu().numpy(), 'input_latent': latent['samples'].cpu().numpy(),
                  'direction': self.direction.cpu().numpy()}
        path = Path(folder_paths.get_output_directory()) / 'state-replay-v001' / f'{round(self.amount*1000):04d}.npz'
        path.parent.mkdir(exist_ok=True)
        if path.exists():
            with np.load(path) as saved:
                for k, v in arrays.items():
                    if not np.array_equal(saved[k], v): raise RuntimeError('Recorded state collision')
        else:
            np.savez_compressed(path, **arrays)
            path.with_suffix('.json').write_text(json.dumps({'amount': self.amount, 'direction_seed': self.seed,
                'shape': list(noise.shape), 'noise_std': float(noise.std()),
                'noise_sha256': hashlib.sha256(arrays['noise'].tobytes()).hexdigest()}, indent=2))
        return noise


class DeforumReplaySource:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required': {'amount': ('FLOAT', {'default': 0., 'min': 0., 'max': .99, 'step': .005}),
            'direction_seed': ('INT', {'default': 927182, 'min': 0, 'max': 2**64-1})}}

    RETURN_TYPES = ('LATENT', 'NOISE')
    FUNCTION = 'load'
    CATEGORY = 'deforum/experiments'

    def load(self, amount, direction_seed):
        from pathlib import Path
        import numpy as np
        import torch
        import comfy.sample
        import folder_paths
        with np.load(Path(folder_paths.get_input_directory())/'state-replay-v001.npz') as data:
            z = torch.from_numpy(data['input_latent'].copy())
            eps = torch.from_numpy(data['noise'].copy())
        if list(z.shape) != [1,16,1,128,192] or z.shape != eps.shape:
            raise ValueError('Unexpected source tensor format')
        direction = comfy.sample.prepare_noise(z, direction_seed)
        return {'samples': z}, ReplayNoise(eps, direction, direction_seed, amount)


NODE_CLASS_MAPPINGS = {'DeforumReplaySource': DeforumReplaySource}
