"""Bounded still-image audition; no animation or reference conditioning."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

APP = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(APP))
import pod_client
from experiment import save_json
from modern_workflows import graph, node

PROJECT = Path(__file__).resolve().parents[1]
SESSION = APP / 'work/opening-art-session'
OUT = PROJECT / 'exports/opening-art-v001'
SEED = 491731
PROMPTS = {
    'oracle': (
        'A surreal visionary artwork, a close frontal portrait of a porcelain mechanical oracle. '
        'The large face occupies the middle half of a wide composition, with luminous turquoise eyes, '
        'delicate ivory ceramic skin and an enigmatic calm expression. Its crown opens into an impossible '
        'maze of tiny black-and-white architectural chambers, curved chrome ribs and translucent cyan glass. '
        'The temples dissolve into coiled shell forms and elaborate interlocking machine filigree. '
        'Around the head, concentric ornamental structures recede through deep black cavities, like a living '
        'cathedral made of circuitry. Small amber lights punctuate the cyan and ivory palette. Strong sculptural '
        'side lighting reveals glossy ceramic, brushed metal and fine engraved textures. Dense, meticulously '
        'crafted detail surrounds a clearly readable face; the extreme foreground is large and the background '
        'falls into deep layered space. A strange, elegant album-cover painting with tactile three-dimensional '
        'forms, expressive asymmetrical details and a dramatic black backdrop.'
    ),
    'cathedral': (
        'A richly painted surreal living cathedral viewed from inside a vast organic chamber. '
        'A huge curling ivory arch rises close to the viewer on the left and twists overhead; its surfaces '
        'transform between carved bone, coral polyps, copper machinery and intricate miniature buildings. '
        'At the center a glowing amber seed floats above a dark pool, framed by several progressively smaller '
        'arches that spiral into a deep turquoise abyss. Broad sculptural foreground forms frame countless '
        'delicate tendrils and tiny illuminated windows farther away. Vermilion coral folds and oxidized copper '
        'filigree run through the architecture like veins. Pools of near-black shadow separate the layers. '
        'Warm light from the seed grazes the ribs while cold teal light seeps from distant openings. '
        'Painterly visionary science-fiction art, intricate but readable, dramatic depth, tactile mineral '
        'textures, a feeling of ancient intelligence continuously growing into new structures. Wide composition '
        'with the luminous seed slightly right of center and the sweeping arch dominating the foreground.'
    ),
    'moth': (
        'An elaborate surreal mechanical moth suspended in a dark botanical sanctuary, filling most of a wide '
        'image. Its sculptural body resembles a carved ivory mask merging with an orchid, and its broad open '
        'wings are made of overlapping translucent jade petals, engraved brass ribs and jewel-like sapphire '
        'inlays. The wing tips curl into impossible miniature staircases and spiraling shell chambers. '
        'Tiny vermilion veins thread through the glass, while delicate copper antennae curve across the upper '
        'foreground. Behind it, large shadowy leaves and carved organic pillars recede into a deep black-green '
        'space. A narrow warm light from above catches the edges of the filigree; cool cyan light shines through '
        'the translucent wings. An intricate visionary painting of an impossible living sculpture, rich material '
        'contrast, crisp focal detail and softly disappearing distant forms. The large coherent silhouette is '
        'surrounded by strange branching details that invite close inspection.'
    ),
}


def build(case):
    if case == 'control':
        template = json.loads((SESSION / 'official-krea-t2i.json').read_text())
        root = next(n for n in template['nodes'] if n['id'] == 30)
        sub = next(s for s in template['definitions']['subgraphs'] if s['id'] == root['type'])
        system = next(n for n in sub['nodes'] if n['id'] == 18)['widgets_values'][0]
        prompt = root['widgets_values'][0]
        g = graph('krea', prompt, root['widgets_values'][6])
        g['6']['inputs'].update(width=1024, height=1024)
        g['30'] = node('TextGenerate', clip=['2', 0], prompt=system + prompt,
                       max_length=512, sampling_mode='on', thinking=False, use_default_template=True,
                       **{'sampling_mode.temperature': .7, 'sampling_mode.top_k': 64,
                          'sampling_mode.top_p': .95, 'sampling_mode.min_p': .05,
                          'sampling_mode.repetition_penalty': 1.05, 'sampling_mode.seed': 0,
                          'sampling_mode.presence_penalty': 0.})
        g['31'] = node('PreviewAny', source=['30', 0])
        g['4']['inputs']['text'] = ['31', 0]
    else:
        model, concept = case.split('-', 1)
        g = graph(model, PROMPTS[concept], SEED)
        g['6']['inputs'].update(width=1536, height=1024)
        if model == 'klein':
            g['13']['inputs'].update(width=1536, height=1024)
    g['11']['inputs']['filename_prefix'] = 'opening-art/' + case
    return g


def main():
    choices = ['control'] + [m + '-' + c for m in ('krea', 'klein') for c in PROMPTS]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('case', choices=choices)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    g = build(args.case)
    target = OUT / args.case
    if args.prepare_only:
        save_json(SESSION / (args.case + '.api.json'), g)
        print('Prepared', args.case)
        return
    target.mkdir(parents=True, exist_ok=False)
    pod_client.DEPLOYMENT = SESSION / 'deployment.json'
    receipt = {'case': args.case, 'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'model_manifest_sha256': hashlib.sha256((APP / 'serverless/modern-models.json').read_bytes()).hexdigest(),
               'purpose': 'opening artwork only; no feedback or animation'}
    if args.case == 'control':
        receipt['template_sha256'] = hashlib.sha256((SESSION / 'official-krea-t2i.json').read_bytes()).hexdigest()
    run = pod_client.submit(PROJECT, 'opening-art-' + args.case, g, 1, lineage=receipt)
    images = sorted((run / 'frames').glob('*.png'))
    assert len(images) == 1
    shutil.copyfile(images[0], target / 'image.png')
    save_json(target / 'source.json', {'run': str(run.relative_to(PROJECT)), **receipt,
                                     'image_sha256': hashlib.sha256(images[0].read_bytes()).hexdigest()})
    print(target / 'image.png', flush=True)


if __name__ == '__main__':
    main()
