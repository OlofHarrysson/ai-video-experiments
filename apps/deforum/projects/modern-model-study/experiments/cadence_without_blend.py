"""Reassemble the preserved audition anchors without mixing neighboring images."""
import argparse
import json
import numpy as np
from PIL import Image
import audition as study


def assemble(model):
    branch = 'instruction' if model == 'klein' else 'scene-d045'
    source = study.OUT/model/branch
    out = source/'cadence-unblended'
    original = json.loads((source/'cadence/manifest.json').read_text())
    records = []
    for f in range(study.FRAMES):
        anchor = f//study.CADENCE*study.CADENCE
        path = source/f'anchors/{anchor:04d}.png'
        rgb = np.asarray(Image.open(path).convert('RGB'))
        warped = study.motion.warp(rgb, anchor, f)
        target = out/f'frames/{f:04d}.png'
        study.image(target, warped)
        if f == anchor:
            assert study.sha(target) == original['frames'][f]['sha256']
        records.append({'frame': f, 'anchor': anchor, 'anchor_sha256': study.sha(path),
                        'sha256': study.sha(target)})
    study.save(out/'manifest.json', {'fps': study.FPS, 'cadence': study.CADENCE,
        'method': 'warp previous generated anchor only; no blend or new inference',
        'source_manifest_sha256': study.sha(source/'manifest.json'), 'frames': records})
    if not (out/'preview.mp4').exists():
        study.editing.encode(out/'frames', out/'preview.mp4', fps=study.FPS)
    print(out/'preview.mp4')


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('model', choices=('klein', 'krea', 'both'))
    model = p.parse_args().model
    for name in ('klein', 'krea') if model == 'both' else (model,):
        assemble(name)
