# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow>=11"]
# ///
"""Verify the four-image coral archive and build its labeled comparison."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from run_baseline import PROJECT, write_json
from run_coral import EXPORT, MASK_NAME, COMPLETE, make_mask
from run_refinement import latent_tensor_hash


def ancestors(graph, node_id):
    found = {node_id}
    for value in graph[node_id]['inputs'].values():
        if isinstance(value, list): found |= ancestors(graph, value[0])
    return found


def review(folders):
    make_mask()
    inventory = []; indexed = {}
    for folder in folders:
        folder = folder.resolve()
        receipt = json.loads((folder/'submission.json').read_text())
        assert receipt['variant'] == 'krea-coral' and receipt['remote_hashes_verified']
        seed = receipt['seed']; assert seed not in indexed
        graph = json.loads((folder/'workflow.api.json').read_text())
        samplers = [(key,n['inputs']) for key,n in graph.items() if n['class_type']=='KSampler']
        assert len(samplers) == 2
        for field in ('seed','latent_image','steps','cfg','sampler_name','scheduler','denoise'):
            assert samplers[0][1][field] == samplers[1][1][field]
        assert samplers[0][1]['seed'] == seed
        assert graph[samplers[0][1]['positive'][0]]['inputs']['text'] == COMPLETE
        control_types = {graph[key]['class_type'] for key in ancestors(graph, samplers[0][0])}
        assert not control_types & {'LoadImage','ImageToMask','ConditioningSetMask','InvertMask'}
        assert sum(n['class_type']=='ConditioningSetMask' for n in graph.values()) == 2
        assert sum(n['class_type']=='InvertMask' for n in graph.values()) == 1
        mask_hash = hashlib.sha256((folder/MASK_NAME).read_bytes()).hexdigest()
        assert mask_hash == receipt['mask_sha256'] == hashlib.sha256((EXPORT/MASK_NAME).read_bytes()).hexdigest()
        for name,digest in receipt['source_hashes'].items():
            assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == digest
        history = json.loads((folder/'history.json').read_text())
        times = {kind:data.get('timestamp') for kind,data in history['status']['messages']}
        entry = {'run':str(folder.relative_to(PROJECT)), 'seed':seed, 'matched_sampling':True,
            'control_has_no_mask_input':True, 'mask_sha256':mask_hash,
            'job_seconds':(times['execution_success']-times['execution_start'])/1000, 'files':[]}
        files = json.loads((folder/'files.json').read_text()); assert len(files) == 4
        images = {}
        for item in files:
            path = folder/item['local']
            assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
            if path.suffix == '.png':
                with Image.open(path) as im:
                    im.load(); assert im.size == (1024,1024)
                images[item['filename'].split('_')[0]] = path
                entry['files'].append(item)
            else:
                assert path.suffix == '.latent'
                entry['files'].append({**item,'tensor':latent_tensor_hash(path)})
        assert set(images) == {'complete','regional'}
        indexed[seed] = images; inventory.append(entry)
    assert set(indexed) == {21001,21101}
    font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',24)
    small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',19)
    sheet = Image.new('RGB',(1384,1168),'#18202a'); draw = ImageDraw.Draw(sheet)
    draw.text((16,15),'Stone face + coral: verbal placement versus a drawn mask',font=font,fill='white')
    with Image.open(EXPORT/MASK_NAME) as target:
        sheet.paste(target.convert('RGB').resize((320,320),Image.Resampling.LANCZOS),(16,64))
    for y,text in enumerate(['Target coral band','White: coral influence','Black: stone influence','','Mask supplied only to','the regional method.','','Same seeds and sampler.','No reference face.','No refinement pass.']):
        draw.text((18,410+y*29),text,font=small,fill='#d6dce5')
    for row,seed in enumerate((21001,21101)):
        for col,label in enumerate(('complete','regional')):
            x=344+col*520; y=94+row*558
            draw.text((x,y-44),'One complete prompt' if label=='complete' else 'Masked regional prompts',font=font,fill='white')
            draw.text((x,y-19),f'Seed {seed}',font=small,fill='#c4cdd6')
            with Image.open(indexed[seed][label]) as im:
                sheet.paste(im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(x,y))
    sheet.save(EXPORT/'comparison.png')
    write_json(EXPORT/'inventory.json',inventory)
    write_json(PROJECT/'experiments/krea-coral-inventory.json',inventory)
    print(json.dumps({'images':4,'latents':4,'export':str(EXPORT),'job_seconds':[e['job_seconds'] for e in inventory]}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('folders',nargs=2,type=Path)
    review(parser.parse_args().folders)
