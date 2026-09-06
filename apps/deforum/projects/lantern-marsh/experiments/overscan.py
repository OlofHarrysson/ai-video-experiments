"""Lantern marsh recipe; shared modules own generation, transport and archives."""

import argparse
from pathlib import Path
import sys

APP = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(APP))
import editing
import experiment
import serverless_client

WIDTH, HEIGHT = 1280, 720
FRAMES, SEED = 24, 143
CAMERA_STEP = 0.004
CROP = {'width': 1024, 'height': 576, 'x': 128, 'y': 72}
PROMPT = (
    'a moonlit marsh at blue hour, close tall reeds and a hanging copper lantern '
    'framing the left foreground, a winding wooden boardwalk over still water '
    'leading toward a distant small domed astronomical observatory, tiny amber '
    'lanterns along the boardwalk, luminous blue mushrooms, low violet mist, '
    'a crescent moon, cinematic wide composition, clear foreground middle ground '
    'and distant background, atmospheric dark fantasy illustration, textured '
    'painterly brushwork, deep teal and indigo with warm amber light'
)


def reference_graph():
    graph = experiment.make_graph(.4, FRAMES, 'reference')
    graph['2']['inputs']['text'] = PROMPT
    graph['12']['inputs']['prompts'] = '0: ' + PROMPT
    graph['4']['inputs'].update(width=WIDTH, height=HEIGHT)
    graph['5']['inputs']['seed'] = SEED
    graph['7']['inputs'].update(width=WIDTH, height=HEIGHT, seed=SEED)
    graph['8']['inputs'].update(zoom='0:(1)', rotation_3d_z='0:(0)')
    graph['10']['inputs']['end_frame'] = 1
    return graph


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('phase', choices=['reference', 'guide', 'feedback'])
    parser.add_argument('--parent-run', help='Collected reference run in lantern-marsh.')
    args = parser.parse_args()
    project = experiment.project_for_run('lantern-marsh', 'overscan')
    metadata = {'recipe': 'lantern-marsh/overscan', 'phase': args.phase,
                'planned_crop': CROP, 'denoise': .4, 'camera_step': CAMERA_STEP}
    if args.phase == 'reference':
        serverless_client.submit(project, 'overscan', reference_graph(), 1,
                                 {**metadata, 'start_frame': 0, 'end_frame': 1})
        return
    if not args.parent_run:
        parser.error('--parent-run is required for guide and feedback')
    parent = (project / 'runs' / args.parent_run).resolve()
    if parent.parent != (project / 'runs').resolve():
        parser.error('Parent must be a run in this project')
    graph, anchor, lineage = editing.continuation(parent, 0, FRAMES - 1)
    graph = experiment.depth_camera_graph(graph, args.phase == 'guide', FRAMES,
                                         translation_x=CAMERA_STEP)
    serverless_client.submit(project, 'overscan', graph, FRAMES,
                             {**lineage, **metadata}, anchor)


if __name__ == '__main__':
    main()
