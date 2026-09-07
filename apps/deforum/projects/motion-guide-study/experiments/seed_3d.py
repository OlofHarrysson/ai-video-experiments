"""B's image recipe with a short depth-based camera move; existing nodes only."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import seed_comparison as recipe

APP, PROJECT = recipe.APP, recipe.PROJECT
sys.path.insert(0, str(APP))
import serverless_client

OUT = PROJECT / 'exports/seed-3d-v001'
SOURCE = recipe.OUT / 'opening.png'
TX, YAW, NEAR, FAR = -0.004, 0.035, 2.0, 10.0


def graph(preview):
    g = recipe.pair_graph(0, recipe.FRAMES)
    for key in ('30', '31', '40', '50'):
        del g[key]
    g['41']['inputs']['init_image'] = ['6', 0]
    g['8']['inputs'].update(mode='3d', translation_x=f'0:(0), 1:({TX})',
        rotation_3d_y=f'0:(0), 1:({YAW})', zoom='0:(1)')
    g['60'] = recipe.node('DownloadAndLoadDepthAnythingV2Model',
        model='depth_anything_v2_vits_fp32.safetensors', precision='fp32')
    g['61'] = recipe.node('DepthAnything_V2', da_model=['60', 0], images=['6', 0])
    g['62'] = recipe.node('SaveImage', images=['61', 0], filename_prefix='seed-3d/depth')
    depth = dict(depth=['61', 0], near=NEAR, far=FAR, invert_depth=False, translation_scale=1.0)
    if preview:
        g['41'] = recipe.node('DifforumGuideBuilder', anchor_image=['6', 0], camera=['8', 0],
            params=['7', 0], warp_mode='force_3d', **depth)
        g['63'] = recipe.node('MaskToImage', mask=['41', 1])
        g['64'] = recipe.node('SaveImage', images=['63', 0], filename_prefix='seed-3d/coverage')
        # Camera-only graph needs no SDXL model or prompt encoding.
        for k in ('1', '2', '3', '21', '9'):
            del g[k]
    else:
        g['41']['inputs'].update(depth)
    g['11'] = recipe.node('SaveImage', images=['41', 0], filename_prefix='seed-3d/frames')
    return g


def run(stage):
    preview = stage == 'guide'
    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / stage
    if target.exists():
        raise FileExistsError('Preserve existing stage; collect an interrupted job using its run receipt')
    target.mkdir()
    result = serverless_client.submit(PROJECT, f'seed-3d-{stage}', graph(preview), recipe.FRAMES,
        source=SOURCE, lineage={'study': 'B-recipe-small-3d', 'baseline': 'seed-v001/increment',
            'source_sha256': recipe.sha(SOURCE), 'camera_only': preview,
            'scene_transform_per_step': {'translation_x': TX, 'rotation_y_degrees': YAW},
            'near': NEAR, 'far': FAR, 'depth_policy': 'Depth Anything V2 Small from the initial image; reused through the short loop',
            'seed_policy': '7301 + absolute frame index',
            'comparison_limit': 'Original B reloads PNG at frame 3; this six-second render is one continuous batch'})
    (target / 'run.json').write_text(json.dumps({'run': str(result.relative_to(PROJECT))}, indent=2)+'\n')
    shutil.copytree(result / 'frames', target / 'frames')
    shutil.copyfile(result / 'preview.mp4', target / 'preview.mp4')
    assert recipe.pixel_sha(target / 'frames/0000.png') == recipe.pixel_sha(SOURCE)
    archive = result / 'cloud' / json.loads((result/'submission.json').read_text())['cloud_attempt']
    shutil.copyfile(next((archive/'62').glob('*.png')), target/'depth.png')
    if preview:
        shutil.copytree(archive/'64', target/'coverage')
    print(target / 'preview.mp4')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('stage', choices=('guide', 'repaint', 'check'))
    a = p.parse_args()
    if a.stage == 'check':
        g = graph(False)
        before = recipe.pair_graph(0, recipe.FRAMES)['41']['inputs'].copy()
        after = g['41']['inputs'].copy()
        before.pop('init_image'); after.pop('init_image')
        for k in ('depth','near','far','invert_depth','translation_scale'):
            after.pop(k)
        assert before == after
        assert all(g[k] == recipe.base()[k] for k in recipe.base())
        assert graph(True)['8'] == g['8']
        assert g['8']['inputs']['mode']=='3d' and g['41']['inputs']['depth']==['61',0]
        for node in g.values():
            for value in node['inputs'].values():
                if isinstance(value,list) and len(value)==2 and isinstance(value[0],str):
                    assert value[0] in g, value
        print('B sampling recipe unchanged; real depth input and matching guide/repaint camera verified.')
    else:
        run(a.stage)
