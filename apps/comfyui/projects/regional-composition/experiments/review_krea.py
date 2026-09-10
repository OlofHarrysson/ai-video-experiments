# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Archive checks and a two-seed, three-column Krea comparison sheet."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from run_baseline import PROJECT, write_json
from run_refinement import latent_tensor_hash

LABELS = ('complete', 'regional', 'refined')
TITLES = ('One complete prompt', 'Masked regional prompts', 'Regional + global refinement')


def review(folders, name='krea-comparison-v001'):
    OUT = PROJECT/'exports'/name
    OUT.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 23)
    small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 18)
    sheet = Image.new('RGB', (1568, 1140), '#171b20')
    draw = ImageDraw.Draw(sheet)
    inventory = []
    for row, folder in enumerate(folders):
        folder = folder.resolve()
        receipt = json.loads((folder/'submission.json').read_text())
        assert receipt['remote_hashes_verified']
        graph = json.loads((folder/'workflow.api.json').read_text())
        files = json.loads((folder/'files.json').read_text())
        assert len(files)==6
        regional_save = next(n for n in graph.values() if n['class_type']=='SaveLatent' and n['inputs']['filename_prefix'].endswith('/regional'))
        refined_sampler = next(n for n in graph.values() if n['class_type']=='SamplerCustom')
        assert refined_sampler['inputs']['latent_image'] == regional_save['inputs']['samples']
        first = [n['inputs'] for n in graph.values() if n['class_type']=='KSampler']
        assert len(first)==2 and all(n['seed']==receipt['seed'] for n in first)
        assert first[0]['latent_image']==first[1]['latent_image']
        entry = {'run':str(folder.relative_to(PROJECT)), 'seed':receipt['seed'],
                 'regional_latent_directly_initializes_refinement':True, 'files':[]}
        for col, label in enumerate(LABELS):
            matches = [a for a in files if a['filename'].startswith(label+'_') and a['filename'].endswith('.png')]
            assert len(matches)==1
            item = matches[0]
            path = folder/item['local']
            assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
            with Image.open(path) as im:
                im.load(); assert im.size==(1024,1024)
                im=im.convert('RGB')
                sheet.paste(im.resize((512,512),Image.Resampling.LANCZOS),(8+col*520,54+row*566))
            draw.text((12+col*520,8+row*566),TITLES[col],font=font,fill='white')
            draw.text((12+col*520,33+row*566),f'Seed {receipt["seed"]} · 1024 × 1024',font=small,fill='#bcc8d2')
            entry['files'].append(item)
        for item in files:
            if item['filename'].endswith('.latent'):
                path=folder/item['local']
                assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
                entry['files'].append({**item,'tensor':latent_tensor_hash(path)})
        inventory.append(entry)
    sheet.save(OUT/'comparison.png')
    write_json(OUT/'inventory.json',inventory)
    write_json(PROJECT/'experiments'/f'{name}-inventory.json',inventory)
    print(OUT/'comparison.png')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('folders',nargs=2,type=Path)
    p.add_argument('--name',default='krea-comparison-v001')
    args=p.parse_args()
    review(args.folders,args.name)
