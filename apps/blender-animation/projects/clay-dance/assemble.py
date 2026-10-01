# /// script
# requires-python = ">=3.11"
# ///
"""Preserve a checked groove prefix and join newly rendered later dance sections.

This is an explicit v003 -> v004 edit, not a general render-cache implementation.
The builder and puppet toolkit must match byte-for-byte, and all 72 source poses
must be identical. Every retained image is copied and verified by SHA-256.
"""
import hashlib
import json
import shutil
from pathlib import Path

ROOT=Path(__file__).resolve().parent
OLD=ROOT/'output/v003'
NEW=ROOT/'output/v004'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def assemble():
    for name in ['build.py','clay_stage.py']:
        assert digest(OLD/'source'/name)==digest(NEW/'source'/name),name
    before=json.loads((OLD/'motion.json').read_text())
    after=json.loads((NEW/'motion.json').read_text())
    assert before['samples'][:72]==after['samples'][:72]
    assert all(s['move']=='groove' for s in after['samples'][:72])
    tail=NEW/'tail-frames'
    manifest=json.loads((tail/'manifest.json').read_text())
    assert manifest['frames']==list(range(145,433,2))
    assert manifest['percentage']==100 and manifest['samples']==48
    assert manifest['fps']==12
    out=NEW/'final-frames'
    if out.exists():raise FileExistsError(out)
    out.mkdir()
    lineage=[]
    for i in range(216):
        source=OLD/'final-frames'/f'{i:04d}.png' if i<72 else tail/f'{i-72:04d}.png'
        target=out/f'{i:04d}.png'
        shutil.copy2(source,target)
        sha=digest(source)
        assert digest(target)==sha
        lineage.append({'native_frame':1+2*i,'source':str(source.relative_to(ROOT)),'sha256':sha})
    manifest.update({'scene':str(NEW/'clay-dance.blend'),'frames':list(range(1,433,2)),
                     'lineage':lineage,'reuse_evidence':'The v003/v004 builder and clay toolkit are byte-identical; the first 72 pose records are identical. Retained prefix was rendered at 100%, 48 samples; remaining poses use the completed v004 render manifest.'})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('ASSEMBLED',len(lineage),'verified poses')


if __name__=='__main__':assemble()
