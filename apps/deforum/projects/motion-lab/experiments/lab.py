"""Small immutable recipe variants for the September motion lab."""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import sys

PROJECT = Path(__file__).resolve().parents[1]
APP = PROJECT.parents[1]
sys.path.insert(0, str(APP))
import experiment
import editing
import serverless_client

WIDTH, HEIGHT, FRAMES, SEED = 1280, 720, 40, 143
SOURCE = APP / 'projects/seedream-motion/references/assets/seedream-v001/anchor.png'
REFERENCE = PROJECT / 'references/assets/seedream-v001/anchor.png'
RECIPES = {
    'e02-flat-push': {'camera': 'flat', 'denoise': .25},
    'e03-depth-push': {'camera': 'depth', 'denoise': .25},
    'e04-sparse-repaint': {'camera': 'flat', 'denoise': .25, 'cadence': 3},
    'e05-stronger-repaint': {'camera': 'flat', 'denoise': .4},
    'e06-depth-approach': {'camera': 'depth', 'denoise': .25, 'cadence': 3, 'z': -.012},
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def graph_for(name):
    config = RECIPES[name]
    prompt_path = APP / 'projects/lantern-marsh/experiments/overscan.py'
    prompt = next(ast.literal_eval(n.value) for n in ast.parse(prompt_path.read_text()).body
                  if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PROMPT' for t in n.targets))
    graph = experiment.make_graph(config['denoise'], FRAMES, name)
    graph.pop('4'); graph.pop('5')
    graph['6'] = {'class_type': 'LoadImage', 'inputs': {'image': 'anchor.png'}}
    graph['2']['inputs']['text'] = prompt
    graph['12']['inputs']['prompts'] = '0: ' + prompt
    graph['7']['inputs'].update(width=WIDTH, height=HEIGHT, seed=SEED)
    graph['8']['inputs'].update(rotation_3d_z='0:(0)', zoom='0:(1.008)')
    graph['10']['inputs'].update(start_frame=0, end_frame=FRAMES, noise=0, sharpen=0, cfg=5)
    graph['10']['inputs']['cadence'] = config.get('cadence', 1)
    if config['camera'] == 'depth':
        graph = experiment.depth_camera_graph(graph, False, FRAMES, translation_x=0)
        graph['8']['inputs']['translation_z'] = f"0:({config.get('z', .02)})"
    return graph

def run(name):
    experiment.project_for_run(PROJECT.name, name)
    REFERENCE.parent.mkdir(parents=True, exist_ok=True)
    if not REFERENCE.exists():
        shutil.copyfile(SOURCE, REFERENCE)
    if digest(REFERENCE) != digest(SOURCE):
        raise ValueError('Reference changed')
    folder = serverless_client.submit(PROJECT, name, graph_for(name), FRAMES,
        {'recipe': RECIPES[name], 'anchor_sha256': digest(REFERENCE),
         'recipe_sha256': digest(Path(__file__)), 'model_role': 'Seedream source, SDXL repaint'}, REFERENCE)
    export = editing.assemble(PROJECT, name+'-v001', [{'run': folder.name, 'in': 0, 'out': FRAMES}])
    print(export / 'preview.mp4', flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', choices=list(RECIPES))
    run(parser.parse_args().experiment)
