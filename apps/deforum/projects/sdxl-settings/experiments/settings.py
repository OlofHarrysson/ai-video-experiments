"""Prepare/check locally; parent submits three SDXL stills via shared transport."""

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
APP = PROJECT.parents[1]
GRAPH_PATH = HERE / 'settings-v001.api.json'
SETTINGS_PATH = HERE / 'settings-v001.settings.json'
WIDTH, HEIGHT, SEED = 1024, 576, 143
CHECKPOINT = 'sd_xl_base_1.0.safetensors'
VARIANTS = (('baseline', 28, 6.5), ('fewer-steps', 20, 6.5),
            ('lower-guidance', 28, 5.0))
PROMPT = (
    'a moonlit marsh at blue hour, close tall reeds and a hanging copper lantern '
    'framing the left foreground, a winding wooden boardwalk over still water '
    'leading toward a distant small domed astronomical observatory, tiny amber '
    'lanterns along the boardwalk, luminous blue mushrooms, low violet mist, '
    'a crescent moon, cinematic wide composition, clear foreground middle ground '
    'and distant background, atmospheric dark fantasy illustration, textured '
    'painterly brushwork, deep teal and indigo with warm amber light'
)
NEGATIVE = ('blurry, low quality, watermark, text, jpeg artifacts, deformed, '
            'washed out, oversaturated, plain background, low contrast')


def node(kind, **inputs):
    return {'class_type': kind, 'inputs': inputs}


def build():
    graph = {
        '1': node('CheckpointLoaderSimple', ckpt_name=CHECKPOINT),
        '2': node('CLIPTextEncode', text=PROMPT, clip=['1', 1]),
        '3': node('CLIPTextEncode', text=NEGATIVE, clip=['1', 1]),
        '4': node('EmptyLatentImage', width=WIDTH, height=HEIGHT, batch_size=1),
    }
    variants = []
    for index, (name, steps, cfg) in enumerate(VARIANTS):
        sampler, decoder = str(20 + index * 2), str(21 + index * 2)
        graph[sampler] = node(
            'KSampler', model=['1', 0], positive=['2', 0], negative=['3', 0],
            latent_image=['4', 0], seed=SEED, steps=steps, cfg=cfg,
            sampler_name='dpmpp_2m', scheduler='karras', denoise=1.0)
        graph[decoder] = node('VAEDecode', samples=[sampler, 0], vae=['1', 2])
        variants.append({'frame_index': index, 'file': f'frames/{index:04d}.png',
                         'variant': name, 'steps': steps, 'cfg': cfg,
                         'sampler_node': sampler, 'decoder_node': decoder})
    graph['30'] = node('ImageBatch', image1=['21', 0], image2=['23', 0])
    graph['31'] = node('ImageBatch', image1=['30', 0], image2=['25', 0])
    graph['11'] = node('SaveImage', images=['31', 0],
                       filename_prefix='sdxl-settings/settings-v001')
    metadata = {
        'recipe': 'sdxl-settings/settings-v001', 'media_kind': 'standalone-stills',
        'expected_frames': 3, 'checkpoint': CHECKPOINT,
        'width': WIDTH, 'height': HEIGHT, 'seed': SEED,
        'sampler_name': 'dpmpp_2m', 'scheduler': 'karras', 'denoise': 1.0,
        'positive_prompt': PROMPT, 'negative_prompt': NEGATIVE,
        'variants': variants,
    }
    return graph, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'check', 'submit'])
    args = parser.parse_args()
    graph, metadata = build()
    if args.action == 'prepare':
        if GRAPH_PATH.exists() or SETTINGS_PATH.exists():
            parser.error('Prepared files already exist; preserve this recipe version')
        for path, value in ((GRAPH_PATH, graph), (SETTINGS_PATH, metadata)):
            with path.open('x') as output:
                output.write(json.dumps(value, indent=2) + '\n')
        print('Prepared settings-v001 graph and ordered metadata; no network calls.')
        return
    for path, expected in ((GRAPH_PATH, graph), (SETTINGS_PATH, metadata)):
        if json.loads(path.read_text()) != expected:
            parser.error(f'Prepared artifact differs from recipe: {path.name}')
    if not (HERE / 'settings.md').is_file():
        parser.error('Experiment note must exist before submission')
    digest = hashlib.sha256(GRAPH_PATH.read_bytes()).hexdigest()
    if args.action == 'check':
        print(f'Local check passed: 3 stills, 76 steps, graph SHA-256 {digest}')
        return
    # Imports and all paid/network actions happen only for explicit submit.
    sys.path.insert(0, str(APP))
    import serverless_client
    serverless_client.submit(PROJECT, 'settings', graph, 3,
                             {'settings_comparison': metadata,
                              'prepared_graph_sha256': digest})


if __name__ == '__main__':
    main()
