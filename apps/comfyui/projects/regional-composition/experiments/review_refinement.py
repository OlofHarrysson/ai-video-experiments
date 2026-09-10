# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Produce matched-size comparisons and crop pages from verified refinement runs."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageOps

from review_baseline import sheet
from run_baseline import PROJECT, write_json
from run_refinement import only_file


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runs', type=Path, nargs='+', required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    dest = PROJECT/'exports'/args.version; dest.mkdir(parents=True, exist_ok=False)
    records = [(folder.resolve(), json.loads((folder/'submission.json').read_text())) for folder in args.runs]
    seeds = sorted({r['seed_offset'] for _, r in records})
    manifest = []
    for seed in seeds:
        selected = [(f,r) for f,r in records if r['seed_offset']==seed]
        base = next((f for f,r in selected if r['mode']=='base'), selected[0][0])
        entries = [('Regional original, 1024', only_file(base, 'regional_*.png'))]
        large = [(f,r) for f,r in selected if r['mode']=='refine' and r['size']==2048]
        if large:
            entries.append(('Latent enlarged, no sampling', only_file(large[0][0], 'enlarged-without-refinement_*.png')))
        for folder, receipt in sorted(selected, key=lambda item:(-item[1]['size'],item[1]['denoise'])):
            if receipt['mode']!='refine':
                continue
            if not receipt.get('remote_hashes_verified'):
                raise ValueError('Run not verified')
            lineage = json.loads((folder/'lineage-check.json').read_text())
            if not lineage['identical'] or not lineage.get('latent_tensor_identical'):
                raise ValueError('First stage differs')
            entries.append((f"Global {receipt['size']}, denoise {receipt['denoise']:.2f}",
                            only_file(folder,'global-refined_*.png')))
        label = f'seed{21001+seed}'
        sheet(entries, 3 if len(entries)>4 else 2, 512, dest/(label+'-comparison.png'))
        crops=[]
        for i,(title,path) in enumerate(entries):
            with Image.open(path) as im:
                factor=im.width/1024
                # Same scene-space window spans both foreground objects.
                box=tuple(round(v*factor) for v in (96,352,960,928))
                target=dest/f'{label}-crop-{i:02}.png'
                crop=im.crop(box)
                crop.save(target)
                preview=dest/f'{label}-crop-preview-{i:02}.png'
                ImageOps.pad(crop.convert('RGB'),(512,512),method=Image.Resampling.LANCZOS,color='#18202a').save(preview)
            crops.append((title,preview))
            manifest.append({'title':title,'seed':21001+seed,'source':str(path.relative_to(PROJECT)),
                             'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
        sheet(crops, 3 if len(crops)>4 else 2, 512, dest/(label+'-details.png'))
    write_json(dest/'review.json',{'images':manifest,'note':'Overview resized with Lanczos to equal display size. Detail windows use matching scene coordinates and preserve aspect ratio with letterboxing. Individual crop PNGs retain source resolution.'})
    print(json.dumps({'export':str(dest),'images':len(manifest)}))


if __name__=='__main__':
    main()
