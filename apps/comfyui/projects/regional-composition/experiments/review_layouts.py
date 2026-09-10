# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Verify the eight-image layout archive and build labeled comparisons."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from run_baseline import PROJECT, write_json
from run_layouts import EXPORT, LAYOUTS, SLOTS, prompts, targets
from run_refinement import latent_tensor_hash


def review(folders):
    targets()
    inventory=[]; indexed={}
    for folder in folders:
        folder=folder.resolve();receipt=json.loads((folder/'submission.json').read_text())
        assert receipt['variant']=='krea-layouts' and receipt['remote_hashes_verified']
        key=(receipt['layout'],receipt['seed']);assert key not in indexed
        files=json.loads((folder/'files.json').read_text());assert len(files)==4
        graph=json.loads((folder/'workflow.api.json').read_text())
        samplers=[n['inputs'] for n in graph.values() if n['class_type']=='KSampler']
        assert len(samplers)==2
        for field in ('seed','latent_image','steps','cfg','sampler_name','scheduler','denoise'):
            assert samplers[0][field]==samplers[1][field]
        assert samplers[0]['seed']==receipt['seed']
        masks=[n for n in graph.values() if n['class_type']=='ConditioningSetMask'];assert len(masks)==3
        complete=graph[samplers[0]['positive'][0]]['inputs']['text']
        for subject,mask in zip(prompts(receipt['layout']).values(),masks):
            assert subject in complete
            assert subject in graph[mask['inputs']['conditioning'][0]]['inputs']['text']
        for name,digest in receipt['source_hashes'].items():
            assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==digest
        history=json.loads((folder/'history.json').read_text())
        times={kind:data.get('timestamp') for kind,data in history['status']['messages']}
        entry={'run':str(folder.relative_to(PROJECT)),'layout':receipt['layout'],'seed':receipt['seed'],
               'matched_sampling_and_subject_text':True,'job_seconds':(times['execution_success']-times['execution_start'])/1000,'files':[]}
        images={}
        for item in files:
            path=folder/item['local'];assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
            label=item['filename'].split('_')[0]
            if path.suffix=='.png':
                with Image.open(path) as im:
                    im.load();assert im.size==(1024,1024)
                images[label]=path
                entry['files'].append(item)
            else:
                assert path.suffix=='.latent'
                entry['files'].append({**item,'tensor':latent_tensor_hash(path)})
        assert set(images)=={'complete','regional'}
        indexed[key]=images;inventory.append(entry)
    assert set(indexed)=={(layout,seed) for layout in LAYOUTS for seed in (21001,21101)}
    font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
    small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',19)
    for layout in LAYOUTS:
        sheet=Image.new('RGB',(1384,1168),'#18202a');draw=ImageDraw.Draw(sheet)
        draw.text((16,15),f'Layout {layout}: same target, two methods, two seeds',font=font,fill='white')
        with Image.open(EXPORT/f'target-{layout}.png') as target:
            sheet.paste(target.resize((320,320),Image.Resampling.LANCZOS),(16,64))
        y=415
        for color,slot_name in LAYOUTS[layout].items():
            draw.text((18,y),f'{color.capitalize()} robot: {slot_name}',font=small,fill='white');y+=30
        draw.text((18,535),'Red: flower',font=small,fill='#ef6969')
        draw.text((18,565),'Blue: open umbrella',font=small,fill='#67abff')
        draw.text((18,595),'Yellow: flag',font=small,fill='#e8ce64')
        for row,seed in enumerate((21001,21101)):
            for col,label in enumerate(('complete','regional')):
                x=344+col*520;y=94+row*558
                draw.text((x,y-44),'One complete prompt' if label=='complete' else 'Masked regional prompts',font=font,fill='white')
                draw.text((x,y-19),f'Seed {seed}',font=small,fill='#c4cdd6')
                with Image.open(indexed[(layout,seed)][label]) as im:
                    sheet.paste(im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(x,y))
        sheet.save(EXPORT/f'comparison-{layout}.png')
    write_json(EXPORT/'inventory.json',inventory)
    write_json(PROJECT/'experiments/krea-layouts-inventory.json',inventory)
    print(json.dumps({'images':8,'latents':8,'export':str(EXPORT)}))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('folders',nargs=4,type=Path)
    review(p.parse_args().folders)
